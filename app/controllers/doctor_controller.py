"""
Контроллер для работы с врачами

Реализует REST API endpoints
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
    """
    Создать нового врача
    
    Валидация:
    - ФИО должно содержать минимум 3 слова
    - Специализация из предопределенного списка
    - Стаж работы от 0 до 60 лет
    - Номер телефона в формате +7XXXXXXXXXX
    """
    try:
        service = DoctorService(db)
        db_doctor = service.create_doctor(doctor)
        logger.info(f"[API] Создан врач ID={db_doctor.id}")
        return db_doctor
    except ClinicException as e:
        logger.error(f"[API] Ошибка создания врача: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Получить данные врача по ID"""
    try:
        service = DoctorService(db)
        doctor = service.get_doctor_by_id(doctor_id)
        return doctor
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None, description="Фильтр по специализации"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех врачей
    
    Опционально можно фильтровать по специализации
    """
    service = DoctorService(db)
    
    if specialization:
        doctors = service.get_doctors_by_specialization(specialization)
    else:
        doctors = service.get_all_doctors(skip=skip, limit=limit)
    
    return doctors


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doctor: DoctorUpdate, db: Session = Depends(get_db)):
    """Обновить данные врача"""
    try:
        service = DoctorService(db)
        updated_doctor = service.update_doctor(doctor_id, doctor)
        logger.info(f"[API] Обновлен врач ID={doctor_id}")
        return updated_doctor
    except ClinicException as e:
        logger.error(f"[API] Ошибка обновления врача: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Удалить врача
    
    Ограничение: нельзя удалить врача, если у него есть запланированные приемы
    """
    try:
        service = DoctorService(db)
        result = service.delete_doctor(doctor_id)
        logger.info(f"[API] Удален врач ID={doctor_id}")
        return result
    except ClinicException as e:
        logger.error(f"[API] Ошибка удаления врача: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{doctor_id}/schedule", response_model=List[AppointmentResponse])
def get_doctor_schedule(
    doctor_id: int,
    date: date = Query(..., description="Дата для расписания (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Получить расписание врача на определенную дату
    
    Возвращает список всех записей на прием к данному врачу в указанную дату
    
    Args:
        doctor_id: ID врача
        date: Дата в формате YYYY-MM-DD (например, 2025-12-15)
    
    Returns:
        Список записей на прием с информацией о пациентах, времени и статусе
    """
    try:
        # Проверяем существование врача
        doctor_service = DoctorService(db)
        doctor_service.get_doctor_by_id(doctor_id)
        
        # Получаем расписание
        appointment_service = AppointmentService(db)
        appointments = appointment_service.get_doctor_schedule(doctor_id, date)
        
        logger.info(f"[API] Получено расписание врача ID={doctor_id} на {date}: {len(appointments)} записей")
        return appointments
    except ClinicException as e:
        logger.error(f"[API] Ошибка получения расписания: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)