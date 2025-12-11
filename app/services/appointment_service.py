"""
Сервис для работы с приемами (записями пациентов к врачам)

Реализует сложную бизнес-логику и все функциональные требования
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, time, datetime, timedelta
from typing import List, Optional
import logging

from app.models.database import AppointmentDB, PatientDB, DoctorDB
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.exceptions import (
    NotFoundException,
    ValidationException,
    TimeConflictException,
    MaxAppointmentsExceededException,
    BusinessLogicException,
    DatabaseException
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
    
    # Константы бизнес-логики
    MAX_APPOINTMENTS_PER_DAY = 20  # Максимум приемов в день у одного врача
    MIN_APPOINTMENT_INTERVAL_MINUTES = 20  # Минимальный интервал между приемами
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentDB:
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
            f"Попытка создания приема: patient_id={appointment_data.patient_id}, "
            f"doctor_id={appointment_data.doctor_id}, дата={appointment_data.appointment_date}"
        )
        
        # 1. Проверка существования пациента
        patient = self.db.query(PatientDB).filter(
            PatientDB.id == appointment_data.patient_id
        ).first()
        
        if not patient:
            logger.warning(f"Пациент с ID={appointment_data.patient_id} не найден")
            raise NotFoundException("Пациент", appointment_data.patient_id)
        
        # 2. Проверка существования врача
        doctor = self.db.query(DoctorDB).filter(
            DoctorDB.id == appointment_data.doctor_id
        ).first()
        
        if not doctor:
            logger.warning(f"Врач с ID={appointment_data.doctor_id} не найден")
            raise NotFoundException("Врач", appointment_data.doctor_id)
        
        # 3. Проверка конфликта времени у врача
        self._check_doctor_time_conflict(
            appointment_data.doctor_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        )
        
        # 4. Проверка конфликта времени у пациента
        self._check_patient_time_conflict(
            appointment_data.patient_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        )
        
        # 5. Проверка максимального количества приемов в день у врача
        self._check_max_appointments_per_day(
            appointment_data.doctor_id,
            appointment_data.appointment_date
        )
        
        # 6. Проверка минимального интервала между приемами
        self._check_minimum_interval(
            appointment_data.doctor_id,
            appointment_data.appointment_date,
            appointment_data.appointment_time
        )
        
        # 7. Проверка: пациент уже записан к этому врачу в этот день
        self._check_patient_doctor_same_day(
            appointment_data.patient_id,
            appointment_data.doctor_id,
            appointment_data.appointment_date
        )
        
        # Все проверки пройдены, создаем запись
        try:
            db_appointment = AppointmentDB(
                patient_id=appointment_data.patient_id,
                doctor_id=appointment_data.doctor_id,
                appointment_date=appointment_data.appointment_date,
                appointment_time=appointment_data.appointment_time,
                status=appointment_data.status,
                diagnosis=None
            )
            
            self.db.add(db_appointment)
            self.db.commit()
            self.db.refresh(db_appointment)
            
            logger.info(f"Прием успешно создан с ID={db_appointment.id}")
            return db_appointment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при создании приема: {str(e)}")
            raise DatabaseException("Ошибка при создании приема в базе данных")
    
    def _check_doctor_time_conflict(self, doctor_id: int, appt_date: date, appt_time: time):
        """Проверка: у врача нет другого приема в это время"""
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.appointment_time == appt_time,
            AppointmentDB.status == "scheduled"
        ).first()
        
        if conflict:
            logger.warning(f"Конфликт времени у врача ID={doctor_id} на {appt_date} {appt_time}")
            raise TimeConflictException(
                f"У врача уже есть прием на {appt_date} в {appt_time}"
            )
    
    def _check_patient_time_conflict(self, patient_id: int, appt_date: date, appt_time: time):
        """Проверка: пациент не записан к другому врачу в это время"""
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.appointment_time == appt_time,
            AppointmentDB.status == "scheduled"
        ).first()
        
        if conflict:
            logger.warning(f"Пациент ID={patient_id} уже записан на {appt_date} {appt_time}")
            raise TimeConflictException(
                f"Пациент уже записан к другому врачу на {appt_date} в {appt_time}"
            )
    
    def _check_max_appointments_per_day(self, doctor_id: int, appt_date: date):
        """Проверка: врач не превысил лимит приемов в день"""
        count = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if count >= self.MAX_APPOINTMENTS_PER_DAY:
            logger.warning(
                f"Врач ID={doctor_id} достиг лимита приемов на {appt_date} ({count}/{self.MAX_APPOINTMENTS_PER_DAY})"
            )
            raise MaxAppointmentsExceededException(
                f"Врач не может принять более {self.MAX_APPOINTMENTS_PER_DAY} пациентов в день. "
                f"На {appt_date} уже {count} записей."
            )
    
    def _check_minimum_interval(self, doctor_id: int, appt_date: date, appt_time: time):
        """Проверка: между приемами минимум 20 минут"""
        # Преобразуем time в datetime для вычислений
        appt_datetime = datetime.combine(appt_date, appt_time)
        min_interval = timedelta(minutes=self.MIN_APPOINTMENT_INTERVAL_MINUTES)
        
        # Ищем приемы в пределах интервала
        all_appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.status == "scheduled"
        ).all()
        
        for appointment in all_appointments:
            existing_datetime = datetime.combine(appt_date, appointment.appointment_time)
            time_diff = abs((appt_datetime - existing_datetime).total_seconds() / 60)
            
            if 0 < time_diff < self.MIN_APPOINTMENT_INTERVAL_MINUTES:
                logger.warning(
                    f"Слишком малый интервал между приемами врача ID={doctor_id}: {time_diff} минут"
                )
                raise BusinessLogicException(
                    f"Между приемами должен быть интервал минимум {self.MIN_APPOINTMENT_INTERVAL_MINUTES} минут. "
                    f"Ближайший прием в {appointment.appointment_time}."
                )
    
    def _check_patient_doctor_same_day(self, patient_id: int, doctor_id: int, appt_date: date):
        """Проверка: пациент не записан к этому врачу в этот день"""
        existing = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id,
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.status == "scheduled"
        ).first()
        
        if existing:
            logger.warning(
                f"Пациент ID={patient_id} уже записан к врачу ID={doctor_id} на {appt_date}"
            )
            raise BusinessLogicException(
                f"Пациент уже записан к этому врачу на {appt_date}"
            )
    
    def get_appointment_by_id(self, appointment_id: int) -> AppointmentDB:
        """Получение приема по ID"""
        logger.info(f"Получение приема с ID={appointment_id}")
        
        appointment = self.db.query(AppointmentDB).filter(
            AppointmentDB.id == appointment_id
        ).first()
        
        if not appointment:
            logger.warning(f"Прием с ID={appointment_id} не найден")
            raise NotFoundException("Прием", appointment_id)
        
        return appointment
    
    def get_patient_appointments(self, patient_id: int) -> List[AppointmentDB]:
        """Получение всех приемов пациента"""
        logger.info(f"Получение всех приемов пациента ID={patient_id}")
        
        # Проверка существования пациента
        patient = self.db.query(PatientDB).filter(PatientDB.id == patient_id).first()
        if not patient:
            raise NotFoundException("Пациент", patient_id)
        
        appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id
        ).order_by(AppointmentDB.appointment_date.desc()).all()
        
        return appointments
    
    def get_doctor_appointments(self, doctor_id: int, appt_date: Optional[date] = None) -> List[AppointmentDB]:
        """Получение всех приемов врача (опционально за конкретную дату)"""
        logger.info(f"Получение приемов врача ID={doctor_id}")
        
        # Проверка существования врача
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        if not doctor:
            raise NotFoundException("Врач", doctor_id)
        
        query = self.db.query(AppointmentDB).filter(AppointmentDB.doctor_id == doctor_id)
        
        if appt_date:
            query = query.filter(AppointmentDB.appointment_date == appt_date)
        
        appointments = query.order_by(
            AppointmentDB.appointment_date.desc(),
            AppointmentDB.appointment_time.asc()
        ).all()
        
        return appointments
    
    def update_appointment(self, appointment_id: int, appointment_data: AppointmentUpdate) -> AppointmentDB:
        """
        Обновление приема
        
        Бизнес-правила:
        - Нельзя установить диагноз для отмененного приема
        - Нельзя отменить завершенный прием
        - Прием можно завершить только в день проведения или позже
        """
        logger.info(f"Обновление приема ID={appointment_id}")
        
        appointment = self.get_appointment_by_id(appointment_id)
        update_data = appointment_data.model_dump(exclude_unset=True)
        
        # Валидация изменения статуса
        if 'status' in update_data:
            new_status = update_data['status']
            
            # Нельзя отменить завершенный прием
            if appointment.status == 'completed' and new_status == 'cancelled':
                logger.warning(f"Попытка отменить завершенный прием ID={appointment_id}")
                raise BusinessLogicException("Нельзя отменить завершенный прием")
            
            # Прием можно завершить только в день проведения или позже
            if new_status == 'completed' and appointment.appointment_date > date.today():
                logger.warning(f"Попытка завершить будущий прием ID={appointment_id}")
                raise BusinessLogicException(
                    "Прием можно завершить только в день его проведения или позже"
                )
        
        # Валидация диагноза
        if 'diagnosis' in update_data:
            # Нельзя установить диагноз для отмененного приема
            if appointment.status == 'cancelled':
                logger.warning(f"Попытка установить диагноз для отмененного приема ID={appointment_id}")
                raise BusinessLogicException("Нельзя установить диагноз для отмененного приема")
        
        try:
            for field, value in update_data.items():
                setattr(appointment, field, value)
            
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info(f"Прием ID={appointment_id} успешно обновлен")
            return appointment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при обновлении приема: {str(e)}")
            raise
    
    def cancel_appointment(self, appointment_id: int) -> AppointmentDB:
        """Отменить прием (установить статус cancelled)"""
        logger.info(f"Отмена приема ID={appointment_id}")
        
        update_data = AppointmentUpdate(status="cancelled")
        return self.update_appointment(appointment_id, update_data)
    
    def complete_appointment(self, appointment_id: int, diagnosis: str) -> AppointmentDB:
        """Завершить прием (установить статус completed и диагноз)"""
        logger.info(f"Завершение приема ID={appointment_id}")
        
        update_data = AppointmentUpdate(status="completed", diagnosis=diagnosis)
        return self.update_appointment(appointment_id, update_data)
    
    def delete_appointment(self, appointment_id: int) -> dict:
        """Удаление записи о приеме"""
        logger.info(f"Удаление приема ID={appointment_id}")
        
        appointment = self.get_appointment_by_id(appointment_id)
        
        try:
            self.db.delete(appointment)
            self.db.commit()
            
            logger.info(f"Прием ID={appointment_id} успешно удален")
            return {"message": "Прием успешно удален"}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при удалении приема: {str(e)}")
            raise DatabaseException("Ошибка при удалении приема из базы данных")
    
    def get_all_appointments(self, skip: int = 0, limit: int = 100) -> List[AppointmentDB]:
        """Получение списка всех приемов"""
        logger.info(f"Получение списка всех приемов (skip={skip}, limit={limit})")
        
        appointments = self.db.query(AppointmentDB).offset(skip).limit(limit).all()
        return appointments

    def get_doctor_schedule(self, doctor_id: int, appointment_date: date) -> List[AppointmentDB]:
        """
        Получение расписания врача на определенную дату
        
        Args:
            doctor_id: ID врача
            appointment_date: Дата для получения расписания
            
        Returns:
            List[AppointmentDB]: Список записей на прием, отсортированный по времени
            
        Example:
            >>> service = AppointmentService(db)
            >>> schedule = service.get_doctor_schedule(doctor_id=1, appointment_date=date(2025, 12, 15))
            >>> print(f"У врача {len(schedule)} записей на эту дату")
        """
        logger.info(f"Получение расписания врача ID={doctor_id} на дату {appointment_date}")
        
        appointments = self.db.query(AppointmentDB).filter(
            and_(
                AppointmentDB.doctor_id == doctor_id,
                AppointmentDB.appointment_date == appointment_date
            )
        ).order_by(AppointmentDB.appointment_time).all()
        
        logger.info(f"Найдено {len(appointments)} записей")
        return appointments
    

   