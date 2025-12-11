"""
Контроллер для работы с приемами

Реализует REST API endpoints
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
    """
    Записать пациента на прием к врачу
    
    Бизнес-правила:
    - Проверка существования пациента и врача
    - У врача не может быть двух приемов в одно время
    - Пациент не может быть записан к двум врачам в одно время
    - Врач не может иметь более 20 приемов в день
    - Между приемами должен быть интервал минимум 20 минут
    - Пациент может быть записан к одному врачу только один раз в день
    """
    try:
        service = AppointmentService(db)
        db_appointment = service.create_appointment(appointment)
        logger.info(f"[API] Создан прием ID={db_appointment.id}")
        return db_appointment
    except ClinicException as e:
        logger.error(f"[API] Ошибка создания приема: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{appointment_id}", response_model=AppointmentDetailResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Получить подробную информацию о приеме"""
    try:
        service = AppointmentService(db)
        appointment = service.get_appointment_by_id(appointment_id)
        return appointment
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/patient/{patient_id}", response_model=List[AppointmentDetailResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    """Получить все приемы пациента (история приемов)"""
    try:
        service = AppointmentService(db)
        appointments = service.get_patient_appointments(patient_id)
        return appointments
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/doctor/{doctor_id}", response_model=List[AppointmentDetailResponse])
def get_doctor_appointments(
    doctor_id: int,
    appointment_date: Optional[date] = Query(None, description="Фильтр по дате"),
    db: Session = Depends(get_db)
):
    """
    Получить все приемы врача
    
    Опционально можно указать конкретную дату для получения расписания на день
    """
    try:
        service = AppointmentService(db)
        appointments = service.get_doctor_appointments(doctor_id, appointment_date)
        return appointments
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[AppointmentResponse])
def get_all_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех приемов"""
    service = AppointmentService(db)
    appointments = service.get_all_appointments(skip=skip, limit=limit)
    return appointments


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить прием
    
    Ограничения:
    - Нельзя установить диагноз для отмененного приема
    - Нельзя отменить завершенный прием
    - Прием можно завершить только в день проведения или позже
    """
    try:
        service = AppointmentService(db)
        updated_appointment = service.update_appointment(appointment_id, appointment)
        logger.info(f"[API] Обновлен прием ID={appointment_id}")
        return updated_appointment
    except ClinicException as e:
        logger.error(f"[API] Ошибка обновления приема: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Отменить прием"""
    try:
        service = AppointmentService(db)
        appointment = service.cancel_appointment(appointment_id)
        logger.info(f"[API] Отменен прием ID={appointment_id}")
        return {"message": "Прием успешно отменен", "appointment": appointment}
    except ClinicException as e:
        logger.error(f"[API] Ошибка отмены приема: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    diagnosis: str = Query(..., description="Диагноз"),
    db: Session = Depends(get_db)
):
    """Завершить прием (установить диагноз и статус 'completed')"""
    try:
        service = AppointmentService(db)
        appointment = service.complete_appointment(appointment_id, diagnosis)
        logger.info(f"[API] Завершен прием ID={appointment_id}")
        return {"message": "Прием успешно завершен", "appointment": appointment}
    except ClinicException as e:
        logger.error(f"[API] Ошибка завершения приема: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Удалить запись о приеме"""
    try:
        service = AppointmentService(db)
        result = service.delete_appointment(appointment_id)
        logger.info(f"[API] Удален прием ID={appointment_id}")
        return result
    except ClinicException as e:
        logger.error(f"[API] Ошибка удаления приема: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


