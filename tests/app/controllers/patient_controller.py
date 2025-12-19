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
    try:
        service = PatientService(db)
        return service.create_patient(patient)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        service = PatientService(db)
        return service.get_patient_by_id(patient_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[PatientResponse])
def get_all_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = PatientService(db)
    return service.get_all_patients(skip=skip, limit=limit)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    try:
        service = PatientService(db)
        return service.update_patient(patient_id, patient)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        service = PatientService(db)
        return service.delete_patient(patient_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{patient_id}/appointments", response_model=List[AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    try:
        PatientService(db).get_patient_by_id(patient_id)
        return AppointmentService(db).get_patient_appointments(patient_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
