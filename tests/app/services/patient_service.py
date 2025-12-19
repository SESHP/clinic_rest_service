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
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, data: PatientCreate) -> PatientDB:
        existing = self.db.query(PatientDB).filter(
            PatientDB.insurance_number == data.insurance_number
        ).first()
        
        if existing:
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
            return patient
        except IntegrityError:
            self.db.rollback()
            raise DatabaseException("Ошибка при создании пациента")
    
    def get_patient_by_id(self, patient_id: int) -> PatientDB:
        patient = self.db.query(PatientDB).filter(PatientDB.id == patient_id).first()
        if not patient:
            raise NotFoundException("Пациент", patient_id)
        return patient
    
    def get_all_patients(self, skip: int = 0, limit: int = 100) -> List[PatientDB]:
        return self.db.query(PatientDB).offset(skip).limit(limit).all()
    
    def update_patient(self, patient_id: int, data: PatientUpdate) -> PatientDB:
        patient = self.get_patient_by_id(patient_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'insurance_number' in update_data:
            existing = self.db.query(PatientDB).filter(
                PatientDB.insurance_number == update_data['insurance_number'],
                PatientDB.id != patient_id
            ).first()
            if existing:
                raise AlreadyExistsException(f"Полис {update_data['insurance_number']} уже используется")
        
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def delete_patient(self, patient_id: int) -> dict:
        patient = self.get_patient_by_id(patient_id)
        
        active = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        self.db.delete(patient)
        self.db.commit()
        
        return {"message": "Пациент удален", "deleted_appointments": active}
