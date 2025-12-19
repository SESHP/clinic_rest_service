"""
Сервис для работы с врачами

Реализует бизнес-логику согласно функциональным требованиям
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from app.models.database import DoctorDB, AppointmentDB, SpecializationDB, CabinetDB
from app.schemas import DoctorCreate, DoctorUpdate
from app.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessLogicException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class DoctorService:
    """
    Сервис для управления врачами
    
    Операции:
    - Добавить нового врача
    - Получить данные врача по ID
    - Получить список всех врачей
    - Получить врачей по специализации
    - Редактировать данные врача
    - Удалить врача
    """
    
    # Ограничение: один врач не может иметь более 30 активных пациентов
    MAX_ACTIVE_PATIENTS = 30
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_doctor(self, doctor_data: DoctorCreate) -> DoctorDB:
        """
        Создание нового врача
        
        Валидация:
        - Все обязательные поля заполнены
        - Специализации существуют в базе
        - Кабинет существует (если указан)
        """
        logger.info(f"Попытка создания нового врача: {doctor_data.fio}")
        
        # Проверка существования специализаций
        specializations = self.db.query(SpecializationDB).filter(
            SpecializationDB.id.in_(doctor_data.specialization_ids)
        ).all()
        
        if len(specializations) != len(doctor_data.specialization_ids):
            found_ids = {s.id for s in specializations}
            missing_ids = set(doctor_data.specialization_ids) - found_ids
            raise NotFoundException("Специализация", list(missing_ids)[0])
        
        # Проверка существования кабинета
        cabinet = None
        if doctor_data.cabinet_id:
            cabinet = self.db.query(CabinetDB).filter(
                CabinetDB.id == doctor_data.cabinet_id
            ).first()
            
            if not cabinet:
                raise NotFoundException("Кабинет", doctor_data.cabinet_id)
        
        try:
            db_doctor = DoctorDB(
                fio=doctor_data.fio,
                cabinet_id=doctor_data.cabinet_id,
                phone=doctor_data.phone,
                experience_years=doctor_data.experience_years
            )
            
            # Добавляем специализации
            db_doctor.specializations = specializations
            
            self.db.add(db_doctor)
            self.db.commit()
            self.db.refresh(db_doctor)
            
            logger.info(f"Врач успешно создан с ID={db_doctor.id}")
            return db_doctor
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании врача: {str(e)}")
            raise DatabaseException("Ошибка при создании врача в базе данных")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при создании врача: {str(e)}")
            raise
    
    def get_doctor_by_id(self, doctor_id: int) -> DoctorDB:
        """Получение врача по ID"""
        logger.info(f"Получение врача с ID={doctor_id}")
        
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        
        if not doctor:
            logger.warning(f"Врач с ID={doctor_id} не найден")
            raise NotFoundException("Врач", doctor_id)
        
        return doctor
    
    def get_all_doctors(self, skip: int = 0, limit: int = 100) -> List[DoctorDB]:
        """Получение списка всех врачей с пагинацией"""
        logger.info(f"Получение списка врачей (skip={skip}, limit={limit})")
        
        doctors = self.db.query(DoctorDB).offset(skip).limit(limit).all()
        return doctors
    
    def get_doctors_by_specialization(self, specialization_name: str) -> List[DoctorDB]:
        """Получение врачей по названию специализации"""
        logger.info(f"Поиск врачей по специализации: {specialization_name}")
        
        doctors = self.db.query(DoctorDB).join(
            DoctorDB.specializations
        ).filter(
            SpecializationDB.name == specialization_name
        ).all()
        
        return doctors
    
    def get_doctors_by_specialization_id(self, specialization_id: int) -> List[DoctorDB]:
        """Получение врачей по ID специализации"""
        logger.info(f"Поиск врачей по ID специализации: {specialization_id}")
        
        doctors = self.db.query(DoctorDB).join(
            DoctorDB.specializations
        ).filter(
            SpecializationDB.id == specialization_id
        ).all()
        
        return doctors
    
    def get_doctors_by_cabinet(self, cabinet_id: int) -> List[DoctorDB]:
        """Получение врачей по кабинету"""
        logger.info(f"Поиск врачей в кабинете ID={cabinet_id}")
        
        doctors = self.db.query(DoctorDB).filter(
            DoctorDB.cabinet_id == cabinet_id
        ).all()
        
        return doctors
    
    def update_doctor(self, doctor_id: int, doctor_data: DoctorUpdate) -> DoctorDB:
        """
        Обновление данных врача
        
        Валидация:
        - Врач должен существовать
        - Новые специализации и кабинет должны существовать
        """
        logger.info(f"Обновление врача с ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        try:
            update_data = doctor_data.model_dump(exclude_unset=True)
            
            # Обработка специализаций
            if 'specialization_ids' in update_data:
                spec_ids = update_data.pop('specialization_ids')
                specializations = self.db.query(SpecializationDB).filter(
                    SpecializationDB.id.in_(spec_ids)
                ).all()
                
                if len(specializations) != len(spec_ids):
                    found_ids = {s.id for s in specializations}
                    missing_ids = set(spec_ids) - found_ids
                    raise NotFoundException("Специализация", list(missing_ids)[0])
                
                doctor.specializations = specializations
            
            # Проверка кабинета
            if 'cabinet_id' in update_data and update_data['cabinet_id'] is not None:
                cabinet = self.db.query(CabinetDB).filter(
                    CabinetDB.id == update_data['cabinet_id']
                ).first()
                
                if not cabinet:
                    raise NotFoundException("Кабинет", update_data['cabinet_id'])
            
            # Обновляем остальные поля
            for field, value in update_data.items():
                setattr(doctor, field, value)
            
            self.db.commit()
            self.db.refresh(doctor)
            
            logger.info(f"Врач с ID={doctor_id} успешно обновлен")
            return doctor
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при обновлении врача: {str(e)}")
            raise
    
    def delete_doctor(self, doctor_id: int) -> dict:
        """
        Удаление врача
        
        Бизнес-правила:
        - Врач не может быть удален, если у него есть запланированные приемы
        """
        logger.info(f"Попытка удаления врача с ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        # Проверка наличия запланированных приемов
        scheduled_appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if scheduled_appointments > 0:
            logger.warning(f"У врача ID={doctor_id} есть {scheduled_appointments} запланированных приемов")
            raise BusinessLogicException(
                f"Невозможно удалить врача. У него есть {scheduled_appointments} запланированных приемов. "
                f"Необходимо сначала отменить или перенести все запланированные приемы."
            )
        
        # Подсчет завершенных приемов (для статистики)
        total_appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id
        ).count()
        
        try:
            self.db.delete(doctor)
            self.db.commit()
            
            logger.info(f"Врач с ID={doctor_id} успешно удален")
            
            return {
                "message": "Врач успешно удален",
                "total_appointments_history": total_appointments
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при удалении врача: {str(e)}")
            raise DatabaseException("Ошибка при удалении врача из базы данных")
    
    def add_specialization(self, doctor_id: int, specialization_id: int) -> DoctorDB:
        """Добавление специализации врачу"""
        logger.info(f"Добавление специализации ID={specialization_id} врачу ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        specialization = self.db.query(SpecializationDB).filter(
            SpecializationDB.id == specialization_id
        ).first()
        
        if not specialization:
            raise NotFoundException("Специализация", specialization_id)
        
        if specialization in doctor.specializations:
            raise BusinessLogicException("Врач уже имеет эту специализацию")
        
        doctor.specializations.append(specialization)
        self.db.commit()
        self.db.refresh(doctor)
        
        return doctor
    
    def remove_specialization(self, doctor_id: int, specialization_id: int) -> DoctorDB:
        """Удаление специализации у врача"""
        logger.info(f"Удаление специализации ID={specialization_id} у врача ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        specialization = self.db.query(SpecializationDB).filter(
            SpecializationDB.id == specialization_id
        ).first()
        
        if not specialization:
            raise NotFoundException("Специализация", specialization_id)
        
        if specialization not in doctor.specializations:
            raise BusinessLogicException("Врач не имеет этой специализации")
        
        # Проверяем, что останется хотя бы одна специализация
        if len(doctor.specializations) <= 1:
            raise BusinessLogicException("Врач должен иметь хотя бы одну специализацию")
        
        doctor.specializations.remove(specialization)
        self.db.commit()
        self.db.refresh(doctor)
        
        return doctor
    
    def get_doctor_active_patients_count(self, doctor_id: int) -> int:
        """Подсчет количества активных пациентов врача"""
        from sqlalchemy import func, distinct
        
        count = self.db.query(func.count(distinct(AppointmentDB.patient_id))).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.status == "scheduled"
        ).scalar()
        
        return count or 0
    
    def check_doctor_capacity(self, doctor_id: int) -> bool:
        """Проверка, может ли врач принять еще пациентов"""
        active_patients = self.get_doctor_active_patients_count(doctor_id)
        return active_patients < self.MAX_ACTIVE_PATIENTS
    
    def get_doctor_count(self) -> int:
        """Получение общего количества врачей"""
        return self.db.query(DoctorDB).count()