"""
Сервис для работы со специализациями врачей
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.models.database import SpecializationDB
from app.schemas import SpecializationCreate
from app.exceptions import NotFoundException, AlreadyExistsException, DatabaseException

logger = logging.getLogger(__name__)


class SpecializationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_specialization(self, data: SpecializationCreate) -> SpecializationDB:
        """Создание новой специализации"""
        existing = self.db.query(SpecializationDB).filter(
            SpecializationDB.name == data.name
        ).first()
        
        if existing:
            raise AlreadyExistsException(f"Специализация '{data.name}' уже существует")
        
        try:
            db_spec = SpecializationDB(name=data.name)
            self.db.add(db_spec)
            self.db.commit()
            self.db.refresh(db_spec)
            return db_spec
        except IntegrityError:
            self.db.rollback()
            raise DatabaseException("Ошибка при создании специализации")
    
    def get_by_id(self, spec_id: int) -> SpecializationDB:
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        if not spec:
            raise NotFoundException("Специализация", spec_id)
        return spec
    
    def get_all(self) -> List[SpecializationDB]:
        return self.db.query(SpecializationDB).order_by(SpecializationDB.name).all()
    
    def delete(self, spec_id: int) -> dict:
        spec = self.get_by_id(spec_id)
        if spec.doctors:
            raise DatabaseException(f"Невозможно удалить. {len(spec.doctors)} врачей имеют эту специализацию.")
        
        self.db.delete(spec)
        self.db.commit()
        return {"message": "Специализация удалена"}
    
    def seed_default_specializations(self) -> List[SpecializationDB]:
        """Заполнение базы дефолтными специализациями"""
        default_specs = [
            'Терапевт', 'Хирург', 'Кардиолог', 'Невролог', 'Педиатр',
            'Офтальмолог', 'Отоларинголог', 'Дерматолог', 'Эндокринолог',
            'Гастроэнтеролог', 'Уролог', 'Гинеколог', 'Стоматолог'
        ]
        
        for name in default_specs:
            existing = self.db.query(SpecializationDB).filter(SpecializationDB.name == name).first()
            if not existing:
                self.db.add(SpecializationDB(name=name))
        
        self.db.commit()
        return self.get_all()
