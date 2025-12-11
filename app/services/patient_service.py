"""
Сервис для работы с пациентами

Реализует бизнес-логику и функциональные требования из курсовой работы
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from app.models.database import PatientDB
from app.schemas import PatientCreate, PatientUpdate
from app.exceptions import (
    NotFoundException,
    AlreadyExistsException,
    ValidationException,
    BusinessLogicException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class PatientService:
    """
    Сервис для управления пациентами
    
    Операции:
    - Создать нового пациента
    - Получить данные пациента по ID
    - Получить список всех пациентов
    - Редактировать существующего пациента
    - Удалить пациента
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> PatientDB:
        """
        Создание нового пациента
        
        Валидация:
        - Уникальность номера полиса ОМС
        - Все обязательные поля заполнены
        """
        logger.info(f"Попытка создания нового пациента: {patient_data.fio}")
        
        try:
            # Проверка уникальности номера полиса
            existing_patient = self.db.query(PatientDB).filter(
                PatientDB.insurance_number == patient_data.insurance_number
            ).first()
            
            if existing_patient:
                logger.warning(f"Пациент с полисом {patient_data.insurance_number} уже существует")
                raise AlreadyExistsException(
                    f"Пациент с номером полиса ОМС {patient_data.insurance_number} уже зарегистрирован"
                )
            
            # Создание пациента
            db_patient = PatientDB(
                fio=patient_data.fio,
                birth_date=patient_data.birth_date,
                phone=patient_data.phone,
                address=patient_data.address,
                insurance_number=patient_data.insurance_number
            )
            
            self.db.add(db_patient)
            self.db.commit()
            self.db.refresh(db_patient)
            
            logger.info(f"Пациент успешно создан с ID={db_patient.id}")
            return db_patient
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании пациента: {str(e)}")
            raise DatabaseException("Ошибка при создании пациента в базе данных")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при создании пациента: {str(e)}")
            raise
    
    def get_patient_by_id(self, patient_id: int) -> PatientDB:
        """Получение пациента по ID"""
        logger.info(f"Получение пациента с ID={patient_id}")
        
        patient = self.db.query(PatientDB).filter(PatientDB.id == patient_id).first()
        
        if not patient:
            logger.warning(f"Пациент с ID={patient_id} не найден")
            raise NotFoundException("Пациент", patient_id)
        
        return patient
    
    def get_all_patients(self, skip: int = 0, limit: int = 100) -> List[PatientDB]:
        """Получение списка всех пациентов с пагинацией"""
        logger.info(f"Получение списка пациентов (skip={skip}, limit={limit})")
        
        patients = self.db.query(PatientDB).offset(skip).limit(limit).all()
        return patients
    
    def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> PatientDB:
        """
        Обновление данных пациента
        
        Валидация:
        - Пациент должен существовать
        - При изменении полиса проверяется уникальность
        """
        logger.info(f"Обновление пациента с ID={patient_id}")
        
        patient = self.get_patient_by_id(patient_id)
        
        try:
            # Обновляем только те поля, которые переданы
            update_data = patient_data.model_dump(exclude_unset=True)
            
            # Проверка уникальности нового номера полиса, если он изменяется
            if 'insurance_number' in update_data:
                existing = self.db.query(PatientDB).filter(
                    PatientDB.insurance_number == update_data['insurance_number'],
                    PatientDB.id != patient_id
                ).first()
                
                if existing:
                    logger.warning(f"Номер полиса {update_data['insurance_number']} уже используется")
                    raise AlreadyExistsException(
                        f"Номер полиса ОМС {update_data['insurance_number']} уже используется другим пациентом"
                    )
            
            for field, value in update_data.items():
                setattr(patient, field, value)
            
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info(f"Пациент с ID={patient_id} успешно обновлен")
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при обновлении пациента: {str(e)}")
            raise
    
    def delete_patient(self, patient_id: int) -> dict:
        """
        Удаление пациента
        
        Бизнес-правила:
        - При удалении пациента все его приемы также удаляются (каскадное удаление)
        - Система предупреждает о наличии активных приемов
        """
        logger.info(f"Попытка удаления пациента с ID={patient_id}")
        
        patient = self.get_patient_by_id(patient_id)
        
        # Проверка наличия активных (незавершенных) приемов
        from app.models.database import AppointmentDB
        
        active_appointments = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if active_appointments > 0:
            logger.warning(f"У пациента ID={patient_id} есть {active_appointments} активных приемов")
            # Предупреждение, но не блокируем удаление (согласно требованиям)
        
        try:
            self.db.delete(patient)
            self.db.commit()
            
            logger.info(f"Пациент с ID={patient_id} успешно удален (каскадно удалено приемов: {active_appointments})")
            
            return {
                "message": f"Пациент успешно удален",
                "deleted_appointments": active_appointments
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка при удалении пациента: {str(e)}")
            raise DatabaseException("Ошибка при удалении пациента из базы данных")
    
    def get_patient_count(self) -> int:
        """Получение общего количества пациентов"""
        return self.db.query(PatientDB).count()
