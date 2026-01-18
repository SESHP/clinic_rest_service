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
    """
    Сервис для управления специализациями врачей
    
    Операции:
    - Создать специализацию
    - Получить по ID
    - Получить все
    - Удалить специализацию
    - Заполнить дефолтными специализациями
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_specialization(self, data: SpecializationCreate) -> SpecializationDB:
        """Создание новой специализации"""
        logger.info(f"Попытка создания специализации: {data.name}")
        
        existing = self.db.query(SpecializationDB).filter(
            SpecializationDB.name == data.name
        ).first()
        
        if existing:
            logger.warning(f"Специализация '{data.name}' уже существует")
            raise AlreadyExistsException(f"Специализация '{data.name}' уже существует")
        
        try:
            db_spec = SpecializationDB(name=data.name)
            self.db.add(db_spec)
            self.db.commit()
            self.db.refresh(db_spec)
            logger.info(f"Специализация создана с ID={db_spec.id}")
            return db_spec
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка при создании специализации: {str(e)}")
            raise DatabaseException("Ошибка при создании специализации")
    
    def get_by_id(self, spec_id: int) -> SpecializationDB:
        """Получение специализации по ID"""
        logger.info(f"Получение специализации с ID={spec_id}")
        
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        if not spec:
            logger.warning(f"Специализация с ID={spec_id} не найдена")
            raise NotFoundException("Специализация", spec_id)
        return spec
    
    def get_all(self) -> List[SpecializationDB]:
        """Получение всех специализаций"""
        logger.info("Получение списка всех специализаций")
        return self.db.query(SpecializationDB).order_by(SpecializationDB.name).all()
    
    def delete(self, spec_id: int) -> dict:
        """
        Удаление специализации
        
        Ограничение: нельзя удалить специализацию, если есть врачи с ней
        """
        logger.info(f"Попытка удаления специализации ID={spec_id}")
        
        spec = self.get_by_id(spec_id)
        if spec.doctors:
            logger.warning(f"Специализация ID={spec_id} имеет {len(spec.doctors)} врачей")
            raise DatabaseException(f"Невозможно удалить. {len(spec.doctors)} врачей имеют эту специализацию.")
        
        self.db.delete(spec)
        self.db.commit()
        logger.info(f"Специализация ID={spec_id} успешно удалена")
        return {"message": "Специализация удалена"}
    
    def seed_default_specializations(self) -> List[SpecializationDB]:
        """Заполнение базы дефолтными специализациями"""
        logger.info("Заполнение базы дефолтными специализациями")
        
        default_specs = [
            'Терапевт', 'Хирург', 'Кардиолог', 'Невролог', 'Педиатр',
            'Офтальмолог', 'Отоларинголог', 'Дерматолог', 'Эндокринолог',
            'Гастроэнтеролог', 'Уролог', 'Гинеколог', 'Стоматолог'
        ]
        
        created = 0
        for name in default_specs:
            existing = self.db.query(SpecializationDB).filter(SpecializationDB.name == name).first()
            if not existing:
                self.db.add(SpecializationDB(name=name))
                created += 1
        
        self.db.commit()
        logger.info(f"Создано {created} новых специализаций")
        return self.get_all()
