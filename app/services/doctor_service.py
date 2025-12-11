"""
Сервис для работы с врачами

Реализует бизнес-логику согласно функциональным требованиям
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from app.models.database import DoctorDB, AppointmentDB
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
        - Специализация из предопределенного списка
        - Стаж работы корректен
        """
        logger.info(f"Попытка создания нового врача: {doctor_data.fio}")
        
        try:
            db_doctor = DoctorDB(
                fio=doctor_data.fio,
                specialization=doctor_data.specialization,
                cabinet_number=doctor_data.cabinet_number,
                phone=doctor_data.phone,
                experience_years=doctor_data.experience_years
            )
            
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
    
    def get_doctors_by_specialization(self, specialization: str) -> List[DoctorDB]:
        """Получение врачей по специализации"""
        logger.info(f"Поиск врачей по специализации: {specialization}")
        
        doctors = self.db.query(DoctorDB).filter(
            DoctorDB.specialization == specialization
        ).all()
        
        return doctors
    
    def update_doctor(self, doctor_id: int, doctor_data: DoctorUpdate) -> DoctorDB:
        """
        Обновление данных врача
        
        Валидация:
        - Врач должен существовать
        - Новые данные валидны
        """
        logger.info(f"Обновление врача с ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        try:
            update_data = doctor_data.model_dump(exclude_unset=True)
            
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
        - При удалении выводится информация о количестве отмененных приемов
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
    
    def get_doctor_active_patients_count(self, doctor_id: int) -> int:
        """
        Подсчет количества активных пациентов врача
        (пациенты с запланированными приемами)
        """
        from sqlalchemy import func, distinct
        
        count = self.db.query(func.count(distinct(AppointmentDB.patient_id))).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.status == "scheduled"
        ).scalar()
        
        return count or 0
    
    def check_doctor_capacity(self, doctor_id: int) -> bool:
        """
        Проверка, может ли врач принять еще пациентов
        (не более 30 активных пациентов одновременно)
        """
        active_patients = self.get_doctor_active_patients_count(doctor_id)
        return active_patients < self.MAX_ACTIVE_PATIENTS
    
    def get_doctor_count(self) -> int:
        """Получение общего количества врачей"""
        return self.db.query(DoctorDB).count()
