"""
Сервис для работы с кабинетами
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.models.database import CabinetDB
from app.schemas import CabinetCreate, CabinetUpdate
from app.exceptions import NotFoundException, AlreadyExistsException, DatabaseException

logger = logging.getLogger(__name__)


class CabinetService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_cabinet(self, data: CabinetCreate) -> CabinetDB:
        existing = self.db.query(CabinetDB).filter(CabinetDB.number == data.number).first()
        if existing:
            raise AlreadyExistsException(f"Кабинет '{data.number}' уже существует")
        
        try:
            db_cabinet = CabinetDB(
                number=data.number,
                floor=data.floor,
                description=data.description
            )
            self.db.add(db_cabinet)
            self.db.commit()
            self.db.refresh(db_cabinet)
            return db_cabinet
        except IntegrityError:
            self.db.rollback()
            raise DatabaseException("Ошибка при создании кабинета")
    
    def get_by_id(self, cabinet_id: int) -> CabinetDB:
        cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == cabinet_id).first()
        if not cabinet:
            raise NotFoundException("Кабинет", cabinet_id)
        return cabinet
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[CabinetDB]:
        return self.db.query(CabinetDB).order_by(CabinetDB.number).offset(skip).limit(limit).all()
    
    def get_by_floor(self, floor: int) -> List[CabinetDB]:
        return self.db.query(CabinetDB).filter(CabinetDB.floor == floor).order_by(CabinetDB.number).all()
    
    def update_cabinet(self, cabinet_id: int, data: CabinetUpdate) -> CabinetDB:
        cabinet = self.get_by_id(cabinet_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'number' in update_data:
            existing = self.db.query(CabinetDB).filter(
                CabinetDB.number == update_data['number'],
                CabinetDB.id != cabinet_id
            ).first()
            if existing:
                raise AlreadyExistsException(f"Кабинет '{update_data['number']}' уже существует")
        
        for field, value in update_data.items():
            setattr(cabinet, field, value)
        
        self.db.commit()
        self.db.refresh(cabinet)
        return cabinet
    
    def delete_cabinet(self, cabinet_id: int) -> dict:
        cabinet = self.get_by_id(cabinet_id)
        if cabinet.doctors:
            raise DatabaseException(f"Невозможно удалить. {len(cabinet.doctors)} врачей работают в этом кабинете.")
        
        self.db.delete(cabinet)
        self.db.commit()
        return {"message": "Кабинет удален"}
    
    def get_cabinet_doctors(self, cabinet_id: int) -> List:
        cabinet = self.get_by_id(cabinet_id)
        return cabinet.doctors
