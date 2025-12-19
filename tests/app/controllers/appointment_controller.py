"""
Контроллер для работы с приемами
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging

from app.database import get_db
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentDetailResponse
from app.services import AppointmentService
from app.exceptions import ClinicException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        return service.create_appointment(appointment)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{appointment_id}", response_model=AppointmentDetailResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        return service.get_appointment_by_id(appointment_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/patient/{patient_id}", response_model=List[AppointmentDetailResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        return service.get_patient_appointments(patient_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/doctor/{doctor_id}", response_model=List[AppointmentDetailResponse])
def get_doctor_appointments(
    doctor_id: int,
    appointment_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        service = AppointmentService(db)
        return service.get_doctor_appointments(doctor_id, appointment_date)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[AppointmentResponse])
def get_all_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = AppointmentService(db)
    return service.get_all_appointments(skip=skip, limit=limit)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, appointment: AppointmentUpdate, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        return service.update_appointment(appointment_id, appointment)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        appointment = service.cancel_appointment(appointment_id)
        return {"message": "Прием отменен", "appointment": appointment}
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    diagnosis: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        service = AppointmentService(db)
        appointment = service.complete_appointment(appointment_id, diagnosis)
        return {"message": "Прием завершен", "appointment": appointment}
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        service = AppointmentService(db)
        return service.delete_appointment(appointment_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
