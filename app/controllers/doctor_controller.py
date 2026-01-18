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
    """
    Создать нового врача
    
    Валидация:
    - ФИО должно содержать минимум 3 слова
    - Специализации должны существовать в базе
    - Кабинет должен существовать (если указан)
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
        return service.get_doctor_by_id(doctor_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None, description="Фильтр по названию специализации"),
    specialization_id: Optional[int] = Query(None, description="Фильтр по ID специализации"),
    cabinet_id: Optional[int] = Query(None, description="Фильтр по ID кабинета"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех врачей
    
    Фильтры:
    - specialization: название специализации
    - specialization_id: ID специализации
    - cabinet_id: ID кабинета
    """
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
    """Обновить данные врача"""
    try:
        service = DoctorService(db)
        updated = service.update_doctor(doctor_id, doctor)
        logger.info(f"[API] Обновлен врач ID={doctor_id}")
        return updated
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
    """Получить расписание врача на определенную дату"""
    try:
        DoctorService(db).get_doctor_by_id(doctor_id)
        appointments = AppointmentService(db).get_doctor_schedule(doctor_id, date)
        logger.info(f"[API] Получено расписание врача ID={doctor_id} на {date}: {len(appointments)} записей")
        return appointments
    except ClinicException as e:
        logger.error(f"[API] Ошибка получения расписания: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{doctor_id}/specializations/{specialization_id}", response_model=DoctorResponse)
def add_doctor_specialization(doctor_id: int, specialization_id: int, db: Session = Depends(get_db)):
    """Добавить специализацию врачу"""
    try:
        doctor = DoctorService(db).add_specialization(doctor_id, specialization_id)
        logger.info(f"[API] Добавлена специализация ID={specialization_id} врачу ID={doctor_id}")
        return doctor
    except ClinicException as e:
        logger.error(f"[API] Ошибка добавления специализации: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{doctor_id}/specializations/{specialization_id}", response_model=DoctorResponse)
def remove_doctor_specialization(doctor_id: int, specialization_id: int, db: Session = Depends(get_db)):
    """
    Удалить специализацию у врача
    
    Ограничение: врач должен иметь хотя бы одну специализацию
    """
    try:
        doctor = DoctorService(db).remove_specialization(doctor_id, specialization_id)
        logger.info(f"[API] Удалена специализация ID={specialization_id} у врача ID={doctor_id}")
        return doctor
    except ClinicException as e:
        logger.error(f"[API] Ошибка удаления специализации: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
