"""
Контроллер для работы с кабинетами
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.schemas import CabinetCreate, CabinetUpdate, CabinetResponse, DoctorResponse
from app.services import CabinetService
from app.exceptions import ClinicException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cabinets", tags=["Cabinets"])


@router.post("/", response_model=CabinetResponse, status_code=status.HTTP_201_CREATED)
def create_cabinet(cabinet: CabinetCreate, db: Session = Depends(get_db)):
    """Создать новый кабинет"""
    try:
        service = CabinetService(db)
        db_cabinet = service.create_cabinet(cabinet)
        return db_cabinet
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[CabinetResponse])
def get_all_cabinets(
    floor: Optional[int] = Query(None, description="Фильтр по этажу"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех кабинетов"""
    service = CabinetService(db)
    if floor is not None:
        return service.get_by_floor(floor)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{cabinet_id}", response_model=CabinetResponse)
def get_cabinet(cabinet_id: int, db: Session = Depends(get_db)):
    """Получить кабинет по ID"""
    try:
        service = CabinetService(db)
        return service.get_by_id(cabinet_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{cabinet_id}", response_model=CabinetResponse)
def update_cabinet(cabinet_id: int, cabinet: CabinetUpdate, db: Session = Depends(get_db)):
    """Обновить данные кабинета"""
    try:
        service = CabinetService(db)
        return service.update_cabinet(cabinet_id, cabinet)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{cabinet_id}")
def delete_cabinet(cabinet_id: int, db: Session = Depends(get_db)):
    """Удалить кабинет"""
    try:
        service = CabinetService(db)
        return service.delete_cabinet(cabinet_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{cabinet_id}/doctors", response_model=List[DoctorResponse])
def get_cabinet_doctors(cabinet_id: int, db: Session = Depends(get_db)):
    """Получить список врачей в кабинете"""
    try:
        service = CabinetService(db)
        return service.get_cabinet_doctors(cabinet_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
