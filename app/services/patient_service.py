"""
Сервис для работы с пациентами
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.models.database import PatientDB, AppointmentDB
from app.schemas import PatientCreate, PatientUpdate
from app.exceptions import NotFoundException, AlreadyExistsException, DatabaseException

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
    
    def create_patient(self, data: PatientCreate) -> PatientDB:
        """
        Создание нового пациента
        
        Валидация:
        - Уникальность номера полиса ОМС
        - Все обязательные поля заполнены
        """
        logger.info(f"Попытка создания нового пациента: {data.fio}")
        
        existing = self.db.query(PatientDB).filter(
            PatientDB.insurance_number == data.insurance_number
        ).first()
        
        if existing:
            logger.warning(f"Пациент с полисом {data.insurance_number} уже существует")
            raise AlreadyExistsException(f"Пациент с полисом {data.insurance_number} уже существует")
        
        try:
            patient = PatientDB(
                fio=data.fio,
                birth_date=data.birth_date,
                phone=data.phone,
                address=data.address,
                insurance_number=data.insurance_number
            )
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            logger.info(f"Пациент успешно создан с ID={patient.id}")
            return patient
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании пациента: {str(e)}")
            raise DatabaseException("Ошибка при создании пациента")
    
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
        return self.db.query(PatientDB).offset(skip).limit(limit).all()
    
    def update_patient(self, patient_id: int, data: PatientUpdate) -> PatientDB:
        """
        Обновление данных пациента
        
        Валидация:
        - Пациент должен существовать
        - При изменении полиса проверяется уникальность
        """
        logger.info(f"Обновление пациента с ID={patient_id}")
        
        patient = self.get_patient_by_id(patient_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'insurance_number' in update_data:
            existing = self.db.query(PatientDB).filter(
                PatientDB.insurance_number == update_data['insurance_number'],
                PatientDB.id != patient_id
            ).first()
            if existing:
                logger.warning(f"Полис {update_data['insurance_number']} уже используется")
                raise AlreadyExistsException(f"Полис {update_data['insurance_number']} уже используется")
        
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        self.db.commit()
        self.db.refresh(patient)
        logger.info(f"Пациент с ID={patient_id} успешно обновлен")
        return patient
    
    def delete_patient(self, patient_id: int) -> dict:
        """
        Удаление пациента
        
        Бизнес-правила:
        - При удалении пациента все его приемы также удаляются (каскадное удаление)
        """
        logger.info(f"Попытка удаления пациента с ID={patient_id}")
        
        patient = self.get_patient_by_id(patient_id)
        
        active = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if active > 0:
            logger.warning(f"У пациента ID={patient_id} есть {active} активных приемов")
        
        self.db.delete(patient)
        self.db.commit()
        
        logger.info(f"Пациент с ID={patient_id} успешно удален (каскадно удалено приемов: {active})")
        return {"message": "Пациент удален", "deleted_appointments": active}
