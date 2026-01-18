"""
Сервис для работы с приемами
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time, datetime, timedelta
from typing import List, Optional
import logging

from app.models.database import AppointmentDB, PatientDB, DoctorDB
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.exceptions import (
    NotFoundException, TimeConflictException, 
    MaxAppointmentsExceededException, BusinessLogicException, DatabaseException
)

logger = logging.getLogger(__name__)


class AppointmentService:
    """
    Сервис для управления приемами
    
    Операции:
    - Записать пациента на прием к врачу
    - Получить информацию о приеме
    - Получить все приемы пациента
    - Получить все приемы врача
    - Отменить прием
    - Завершить прием (установить диагноз)
    - Удалить запись о приеме
    """
    
    MAX_APPOINTMENTS_PER_DAY = 20
    MIN_INTERVAL_MINUTES = 20
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_appointment(self, data: AppointmentCreate) -> AppointmentDB:
        """
        Создание новой записи на прием
        
        Валидация и бизнес-правила:
        1. Проверка существования пациента
        2. Проверка существования врача
        3. У врача не может быть двух приемов в одно время
        4. Пациент не может быть записан к двум врачам в одно время
        5. Врач не может иметь более 20 приемов в день
        6. Между приемами должен быть интервал минимум 20 минут
        7. Пациент может быть записан к одному врачу только один раз в день
        """
        logger.info(
            f"Попытка создания приема: patient_id={data.patient_id}, "
            f"doctor_id={data.doctor_id}, дата={data.appointment_date}"
        )
        
        # Проверка пациента
        patient = self.db.query(PatientDB).filter(PatientDB.id == data.patient_id).first()
        if not patient:
            logger.warning(f"Пациент с ID={data.patient_id} не найден")
            raise NotFoundException("Пациент", data.patient_id)
        
        # Проверка врача
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == data.doctor_id).first()
        if not doctor:
            logger.warning(f"Врач с ID={data.doctor_id} не найден")
            raise NotFoundException("Врач", data.doctor_id)
        
        # Конфликт времени врача
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.appointment_time == data.appointment_time,
            AppointmentDB.status == "scheduled"
        ).first()
        if conflict:
            logger.warning(f"Конфликт времени у врача ID={data.doctor_id} на {data.appointment_date} {data.appointment_time}")
            raise TimeConflictException(f"У врача уже есть прием на {data.appointment_date} в {data.appointment_time}")
        
        # Конфликт времени пациента
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == data.patient_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.appointment_time == data.appointment_time,
            AppointmentDB.status == "scheduled"
        ).first()
        if conflict:
            logger.warning(f"Пациент ID={data.patient_id} уже записан на {data.appointment_date} {data.appointment_time}")
            raise TimeConflictException(f"Пациент уже записан на {data.appointment_date} в {data.appointment_time}")
        
        # Лимит приемов в день
        count = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.status == "scheduled"
        ).count()
        if count >= self.MAX_APPOINTMENTS_PER_DAY:
            logger.warning(f"Врач ID={data.doctor_id} достиг лимита приемов на {data.appointment_date}")
            raise MaxAppointmentsExceededException(f"Врач не может принять более {self.MAX_APPOINTMENTS_PER_DAY} пациентов в день")
        
        # Интервал между приемами
        appt_dt = datetime.combine(data.appointment_date, data.appointment_time)
        appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.status == "scheduled"
        ).all()
        
        for appt in appointments:
            existing_dt = datetime.combine(data.appointment_date, appt.appointment_time)
            diff = abs((appt_dt - existing_dt).total_seconds() / 60)
            if 0 < diff < self.MIN_INTERVAL_MINUTES:
                logger.warning(f"Слишком малый интервал между приемами врача ID={data.doctor_id}: {diff} минут")
                raise BusinessLogicException(f"Между приемами должен быть интервал минимум {self.MIN_INTERVAL_MINUTES} минут. Ближайший прием в {appt.appointment_time}.")
        
        # Один пациент - один врач в день
        existing = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == data.patient_id,
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.status == "scheduled"
        ).first()
        if existing:
            logger.warning(f"Пациент ID={data.patient_id} уже записан к врачу ID={data.doctor_id} на {data.appointment_date}")
            raise BusinessLogicException(f"Пациент уже записан к этому врачу на {data.appointment_date}")
        
        try:
            appointment = AppointmentDB(
                patient_id=data.patient_id,
                doctor_id=data.doctor_id,
                appointment_date=data.appointment_date,
                appointment_time=data.appointment_time,
                status=data.status
            )
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            logger.info(f"Прием успешно создан с ID={appointment.id}")
            return appointment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при создании приема: {str(e)}")
            raise DatabaseException("Ошибка при создании приема")
    
    def get_appointment_by_id(self, appointment_id: int) -> AppointmentDB:
        """Получение приема по ID"""
        logger.info(f"Получение приема с ID={appointment_id}")
        
        appointment = self.db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
        if not appointment:
            logger.warning(f"Прием с ID={appointment_id} не найден")
            raise NotFoundException("Прием", appointment_id)
        return appointment
    
    def get_patient_appointments(self, patient_id: int) -> List[AppointmentDB]:
        """Получение всех приемов пациента"""
        logger.info(f"Получение всех приемов пациента ID={patient_id}")
        
        patient = self.db.query(PatientDB).filter(PatientDB.id == patient_id).first()
        if not patient:
            logger.warning(f"Пациент с ID={patient_id} не найден")
            raise NotFoundException("Пациент", patient_id)
        return self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id
        ).order_by(AppointmentDB.appointment_date.desc()).all()
    
    def get_doctor_appointments(self, doctor_id: int, appt_date: Optional[date] = None) -> List[AppointmentDB]:
        """Получение всех приемов врача (опционально за конкретную дату)"""
        logger.info(f"Получение приемов врача ID={doctor_id}")
        
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        if not doctor:
            logger.warning(f"Врач с ID={doctor_id} не найден")
            raise NotFoundException("Врач", doctor_id)
        
        query = self.db.query(AppointmentDB).filter(AppointmentDB.doctor_id == doctor_id)
        if appt_date:
            query = query.filter(AppointmentDB.appointment_date == appt_date)
        return query.order_by(AppointmentDB.appointment_date.desc(), AppointmentDB.appointment_time).all()
    
    def get_doctor_schedule(self, doctor_id: int, appt_date: date) -> List[AppointmentDB]:
        """Получение расписания врача на определенную дату"""
        logger.info(f"Получение расписания врача ID={doctor_id} на дату {appt_date}")
        
        appointments = self.db.query(AppointmentDB).filter(
            and_(
                AppointmentDB.doctor_id == doctor_id,
                AppointmentDB.appointment_date == appt_date
            )
        ).order_by(AppointmentDB.appointment_time).all()
        
        logger.info(f"Найдено {len(appointments)} записей")
        return appointments
    
    def update_appointment(self, appointment_id: int, data: AppointmentUpdate) -> AppointmentDB:
        """
        Обновление приема
        
        Бизнес-правила:
        - Нельзя установить диагноз для отмененного приема
        - Нельзя отменить завершенный прием
        - Прием можно завершить только в день проведения или позже
        """
        logger.info(f"Обновление приема ID={appointment_id}")
        
        appointment = self.get_appointment_by_id(appointment_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'status' in update_data:
            new_status = update_data['status']
            if appointment.status == 'completed' and new_status == 'cancelled':
                logger.warning(f"Попытка отменить завершенный прием ID={appointment_id}")
                raise BusinessLogicException("Нельзя отменить завершенный прием")
            if new_status == 'completed' and appointment.appointment_date > date.today():
                logger.warning(f"Попытка завершить будущий прием ID={appointment_id}")
                raise BusinessLogicException("Прием можно завершить только в день проведения или позже")
        
        if 'diagnosis' in update_data and appointment.status == 'cancelled':
            logger.warning(f"Попытка установить диагноз для отмененного приема ID={appointment_id}")
            raise BusinessLogicException("Нельзя установить диагноз для отмененного приема")
        
        for field, value in update_data.items():
            setattr(appointment, field, value)
        
        self.db.commit()
        self.db.refresh(appointment)
        logger.info(f"Прием ID={appointment_id} успешно обновлен")
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> AppointmentDB:
        """Отменить прием (установить статус cancelled)"""
        logger.info(f"Отмена приема ID={appointment_id}")
        return self.update_appointment(appointment_id, AppointmentUpdate(status="cancelled"))
    
    def complete_appointment(self, appointment_id: int, diagnosis: str) -> AppointmentDB:
        """Завершить прием (установить статус completed и диагноз)"""
        logger.info(f"Завершение приема ID={appointment_id}")
        return self.update_appointment(appointment_id, AppointmentUpdate(status="completed", diagnosis=diagnosis))
    
    def delete_appointment(self, appointment_id: int) -> dict:
        """Удаление записи о приеме"""
        logger.info(f"Удаление приема ID={appointment_id}")
        
        appointment = self.get_appointment_by_id(appointment_id)
        self.db.delete(appointment)
        self.db.commit()
        logger.info(f"Прием ID={appointment_id} успешно удален")
        return {"message": "Прием удален"}
    
    def get_all_appointments(self, skip: int = 0, limit: int = 100) -> List[AppointmentDB]:
        """Получение списка всех приемов"""
        logger.info(f"Получение списка всех приемов (skip={skip}, limit={limit})")
        return self.db.query(AppointmentDB).offset(skip).limit(limit).all()
