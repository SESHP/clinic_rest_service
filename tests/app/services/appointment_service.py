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
    MAX_APPOINTMENTS_PER_DAY = 20
    MIN_INTERVAL_MINUTES = 20
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_appointment(self, data: AppointmentCreate) -> AppointmentDB:
        # Проверка пациента
        patient = self.db.query(PatientDB).filter(PatientDB.id == data.patient_id).first()
        if not patient:
            raise NotFoundException("Пациент", data.patient_id)
        
        # Проверка врача
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == data.doctor_id).first()
        if not doctor:
            raise NotFoundException("Врач", data.doctor_id)
        
        # Конфликт времени врача
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.appointment_time == data.appointment_time,
            AppointmentDB.status == "scheduled"
        ).first()
        if conflict:
            raise TimeConflictException(f"У врача уже есть прием на {data.appointment_date} в {data.appointment_time}")
        
        # Конфликт времени пациента
        conflict = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == data.patient_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.appointment_time == data.appointment_time,
            AppointmentDB.status == "scheduled"
        ).first()
        if conflict:
            raise TimeConflictException(f"Пациент уже записан на {data.appointment_date} в {data.appointment_time}")
        
        # Лимит приемов в день
        count = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.status == "scheduled"
        ).count()
        if count >= self.MAX_APPOINTMENTS_PER_DAY:
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
                raise BusinessLogicException(f"Между приемами должен быть интервал минимум {self.MIN_INTERVAL_MINUTES} минут")
        
        # Один пациент - один врач в день
        existing = self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == data.patient_id,
            AppointmentDB.doctor_id == data.doctor_id,
            AppointmentDB.appointment_date == data.appointment_date,
            AppointmentDB.status == "scheduled"
        ).first()
        if existing:
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
            return appointment
        except Exception as e:
            self.db.rollback()
            raise DatabaseException("Ошибка при создании приема")
    
    def get_appointment_by_id(self, appointment_id: int) -> AppointmentDB:
        appointment = self.db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
        if not appointment:
            raise NotFoundException("Прием", appointment_id)
        return appointment
    
    def get_patient_appointments(self, patient_id: int) -> List[AppointmentDB]:
        patient = self.db.query(PatientDB).filter(PatientDB.id == patient_id).first()
        if not patient:
            raise NotFoundException("Пациент", patient_id)
        return self.db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == patient_id
        ).order_by(AppointmentDB.appointment_date.desc()).all()
    
    def get_doctor_appointments(self, doctor_id: int, appt_date: Optional[date] = None) -> List[AppointmentDB]:
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        if not doctor:
            raise NotFoundException("Врач", doctor_id)
        
        query = self.db.query(AppointmentDB).filter(AppointmentDB.doctor_id == doctor_id)
        if appt_date:
            query = query.filter(AppointmentDB.appointment_date == appt_date)
        return query.order_by(AppointmentDB.appointment_date.desc(), AppointmentDB.appointment_time).all()
    
    def get_doctor_schedule(self, doctor_id: int, appt_date: date) -> List[AppointmentDB]:
        return self.db.query(AppointmentDB).filter(
            and_(
                AppointmentDB.doctor_id == doctor_id,
                AppointmentDB.appointment_date == appt_date
            )
        ).order_by(AppointmentDB.appointment_time).all()
    
    def update_appointment(self, appointment_id: int, data: AppointmentUpdate) -> AppointmentDB:
        appointment = self.get_appointment_by_id(appointment_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'status' in update_data:
            new_status = update_data['status']
            if appointment.status == 'completed' and new_status == 'cancelled':
                raise BusinessLogicException("Нельзя отменить завершенный прием")
            if new_status == 'completed' and appointment.appointment_date > date.today():
                raise BusinessLogicException("Прием можно завершить только в день проведения или позже")
        
        if 'diagnosis' in update_data and appointment.status == 'cancelled':
            raise BusinessLogicException("Нельзя установить диагноз для отмененного приема")
        
        for field, value in update_data.items():
            setattr(appointment, field, value)
        
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> AppointmentDB:
        return self.update_appointment(appointment_id, AppointmentUpdate(status="cancelled"))
    
    def complete_appointment(self, appointment_id: int, diagnosis: str) -> AppointmentDB:
        return self.update_appointment(appointment_id, AppointmentUpdate(status="completed", diagnosis=diagnosis))
    
    def delete_appointment(self, appointment_id: int) -> dict:
        appointment = self.get_appointment_by_id(appointment_id)
        self.db.delete(appointment)
        self.db.commit()
        return {"message": "Прием удален"}
    
    def get_all_appointments(self, skip: int = 0, limit: int = 100) -> List[AppointmentDB]:
        return self.db.query(AppointmentDB).offset(skip).limit(limit).all()
