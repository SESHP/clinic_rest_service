"""
Сервис для работы с врачами
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.models.database import DoctorDB, AppointmentDB, SpecializationDB, CabinetDB
from app.schemas import DoctorCreate, DoctorUpdate
from app.exceptions import NotFoundException, BusinessLogicException, DatabaseException

logger = logging.getLogger(__name__)


class DoctorService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_doctor(self, data: DoctorCreate) -> DoctorDB:
        # Проверка специализаций
        specializations = self.db.query(SpecializationDB).filter(
            SpecializationDB.id.in_(data.specialization_ids)
        ).all()
        
        if len(specializations) != len(data.specialization_ids):
            found_ids = {s.id for s in specializations}
            missing = set(data.specialization_ids) - found_ids
            raise NotFoundException("Специализация", list(missing)[0])
        
        # Проверка кабинета
        if data.cabinet_id:
            cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == data.cabinet_id).first()
            if not cabinet:
                raise NotFoundException("Кабинет", data.cabinet_id)
        
        try:
            doctor = DoctorDB(
                fio=data.fio,
                cabinet_id=data.cabinet_id,
                phone=data.phone,
                experience_years=data.experience_years
            )
            doctor.specializations = specializations
            
            self.db.add(doctor)
            self.db.commit()
            self.db.refresh(doctor)
            return doctor
        except IntegrityError:
            self.db.rollback()
            raise DatabaseException("Ошибка при создании врача")
    
    def get_doctor_by_id(self, doctor_id: int) -> DoctorDB:
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        if not doctor:
            raise NotFoundException("Врач", doctor_id)
        return doctor
    
    def get_all_doctors(self, skip: int = 0, limit: int = 100) -> List[DoctorDB]:
        return self.db.query(DoctorDB).offset(skip).limit(limit).all()
    
    def get_doctors_by_specialization(self, name: str) -> List[DoctorDB]:
        return self.db.query(DoctorDB).join(DoctorDB.specializations).filter(
            SpecializationDB.name == name
        ).all()
    
    def get_doctors_by_specialization_id(self, spec_id: int) -> List[DoctorDB]:
        return self.db.query(DoctorDB).join(DoctorDB.specializations).filter(
            SpecializationDB.id == spec_id
        ).all()
    
    def get_doctors_by_cabinet(self, cabinet_id: int) -> List[DoctorDB]:
        return self.db.query(DoctorDB).filter(DoctorDB.cabinet_id == cabinet_id).all()
    
    def update_doctor(self, doctor_id: int, data: DoctorUpdate) -> DoctorDB:
        doctor = self.get_doctor_by_id(doctor_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'specialization_ids' in update_data:
            spec_ids = update_data.pop('specialization_ids')
            specializations = self.db.query(SpecializationDB).filter(
                SpecializationDB.id.in_(spec_ids)
            ).all()
            if len(specializations) != len(spec_ids):
                raise NotFoundException("Специализация", "one of ids")
            doctor.specializations = specializations
        
        if 'cabinet_id' in update_data and update_data['cabinet_id']:
            cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == update_data['cabinet_id']).first()
            if not cabinet:
                raise NotFoundException("Кабинет", update_data['cabinet_id'])
        
        for field, value in update_data.items():
            setattr(doctor, field, value)
        
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    def delete_doctor(self, doctor_id: int) -> dict:
        doctor = self.get_doctor_by_id(doctor_id)
        
        scheduled = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if scheduled > 0:
            raise BusinessLogicException(f"У врача {scheduled} запланированных приемов")
        
        self.db.delete(doctor)
        self.db.commit()
        return {"message": "Врач удален"}
    
    def add_specialization(self, doctor_id: int, spec_id: int) -> DoctorDB:
        doctor = self.get_doctor_by_id(doctor_id)
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        
        if not spec:
            raise NotFoundException("Специализация", spec_id)
        if spec in doctor.specializations:
            raise BusinessLogicException("Врач уже имеет эту специализацию")
        
        doctor.specializations.append(spec)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    def remove_specialization(self, doctor_id: int, spec_id: int) -> DoctorDB:
        doctor = self.get_doctor_by_id(doctor_id)
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        
        if not spec:
            raise NotFoundException("Специализация", spec_id)
        if spec not in doctor.specializations:
            raise BusinessLogicException("Врач не имеет этой специализации")
        if len(doctor.specializations) <= 1:
            raise BusinessLogicException("Врач должен иметь хотя бы одну специализацию")
        
        doctor.specializations.remove(spec)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
