"""
Контроллер для работы с пациентами
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, AppointmentResponse
from app.services import PatientService, AppointmentService
from app.exceptions import ClinicException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Создать нового пациента
    
    Валидация:
    - ФИО должно содержать минимум 3 слова
    - Дата рождения не может быть в будущем
    - Номер телефона в формате +7XXXXXXXXXX
    - Номер полиса ОМС уникален и содержит 16 цифр
    """
    try:
        service = PatientService(db)
        db_patient = service.create_patient(patient)
        logger.info(f"[API] Создан пациент ID={db_patient.id}")
        return db_patient
    except ClinicException as e:
        logger.error(f"[API] Ошибка создания пациента: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Получить данные пациента по ID"""
    try:
        service = PatientService(db)
        return service.get_patient_by_id(patient_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[PatientResponse])
def get_all_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех пациентов"""
    service = PatientService(db)
    return service.get_all_patients(skip=skip, limit=limit)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    """Обновить данные пациента"""
    try:
        service = PatientService(db)
        updated = service.update_patient(patient_id, patient)
        logger.info(f"[API] Обновлен пациент ID={patient_id}")
        return updated
    except ClinicException as e:
        logger.error(f"[API] Ошибка обновления пациента: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Удалить пациента (каскадно удаляются все его приемы)"""
    try:
        service = PatientService(db)
        result = service.delete_patient(patient_id)
        logger.info(f"[API] Удален пациент ID={patient_id}")
        return result
    except ClinicException as e:
        logger.error(f"[API] Ошибка удаления пациента: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}/appointments", response_model=List[AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    """Получить историю приёмов пациента"""
    try:
        PatientService(db).get_patient_by_id(patient_id)
        appointments = AppointmentService(db).get_patient_appointments(patient_id)
        logger.info(f"[API] Получена история пациента ID={patient_id}: {len(appointments)} записей")
        return appointments
    except ClinicException as e:
        logger.error(f"[API] Ошибка получения истории пациента: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
