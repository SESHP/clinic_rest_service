"""
Контроллер для работы с врачами
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging

from app.database import get_db
from app.schemas import DoctorCreate, DoctorUpdate, DoctorResponse, AppointmentResponse
from app.services import DoctorService, AppointmentService
from app.exceptions import ClinicException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    try:
        service = DoctorService(db)
        return service.create_doctor(doctor)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        service = DoctorService(db)
        return service.get_doctor_by_id(doctor_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None),
    specialization_id: Optional[int] = Query(None),
    cabinet_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = DoctorService(db)
    if specialization:
        return service.get_doctors_by_specialization(specialization)
    elif specialization_id:
        return service.get_doctors_by_specialization_id(specialization_id)
    elif cabinet_id:
        return service.get_doctors_by_cabinet(cabinet_id)
    return service.get_all_doctors(skip=skip, limit=limit)


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doctor: DoctorUpdate, db: Session = Depends(get_db)):
    try:
        service = DoctorService(db)
        return service.update_doctor(doctor_id, doctor)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        service = DoctorService(db)
        return service.delete_doctor(doctor_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{doctor_id}/schedule", response_model=List[AppointmentResponse])
def get_doctor_schedule(
    doctor_id: int,
    date: date = Query(...),
    db: Session = Depends(get_db)
):
    try:
        DoctorService(db).get_doctor_by_id(doctor_id)
        return AppointmentService(db).get_doctor_schedule(doctor_id, date)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{doctor_id}/specializations/{specialization_id}", response_model=DoctorResponse)
def add_doctor_specialization(doctor_id: int, specialization_id: int, db: Session = Depends(get_db)):
    try:
        return DoctorService(db).add_specialization(doctor_id, specialization_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{doctor_id}/specializations/{specialization_id}", response_model=DoctorResponse)
def remove_doctor_specialization(doctor_id: int, specialization_id: int, db: Session = Depends(get_db)):
    try:
        return DoctorService(db).remove_specialization(doctor_id, specialization_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
