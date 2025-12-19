"""
Контроллер для работы со специализациями
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.schemas import SpecializationCreate, SpecializationResponse
from app.services import SpecializationService
from app.exceptions import ClinicException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/specializations", tags=["Specializations"])


@router.post("/", response_model=SpecializationResponse, status_code=status.HTTP_201_CREATED)
def create_specialization(spec: SpecializationCreate, db: Session = Depends(get_db)):
    """Создать новую специализацию"""
    try:
        service = SpecializationService(db)
        db_spec = service.create_specialization(spec)
        logger.info(f"[API] Создана специализация ID={db_spec.id}")
        return db_spec
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[SpecializationResponse])
def get_all_specializations(db: Session = Depends(get_db)):
    """Получить список всех специализаций"""
    service = SpecializationService(db)
    return service.get_all()


@router.get("/{spec_id}", response_model=SpecializationResponse)
def get_specialization(spec_id: int, db: Session = Depends(get_db)):
    """Получить специализацию по ID"""
    try:
        service = SpecializationService(db)
        return service.get_by_id(spec_id)
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{spec_id}")
def delete_specialization(spec_id: int, db: Session = Depends(get_db)):
    """Удалить специализацию"""
    try:
        service = SpecializationService(db)
        result = service.delete(spec_id)
        return result
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/seed", response_model=List[SpecializationResponse])
def seed_specializations(db: Session = Depends(get_db)):
    """Заполнить базу дефолтными специализациями"""
    try:
        service = SpecializationService(db)
        specs = service.seed_default_specializations()
        return specs
    except ClinicException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
