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
    """
    Сервис для управления кабинетами
    
    Операции:
    - Создать кабинет
    - Получить по ID
    - Получить все
    - Получить по этажу
    - Обновить кабинет
    - Удалить кабинет
    - Получить врачей в кабинете
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_cabinet(self, data: CabinetCreate) -> CabinetDB:
        """Создание нового кабинета"""
        logger.info(f"Попытка создания кабинета: {data.number}")
        
        existing = self.db.query(CabinetDB).filter(CabinetDB.number == data.number).first()
        if existing:
            logger.warning(f"Кабинет '{data.number}' уже существует")
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
            logger.info(f"Кабинет создан с ID={db_cabinet.id}")
            return db_cabinet
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка при создании кабинета: {str(e)}")
            raise DatabaseException("Ошибка при создании кабинета")
    
    def get_by_id(self, cabinet_id: int) -> CabinetDB:
        """Получение кабинета по ID"""
        logger.info(f"Получение кабинета с ID={cabinet_id}")
        
        cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == cabinet_id).first()
        if not cabinet:
            logger.warning(f"Кабинет с ID={cabinet_id} не найден")
            raise NotFoundException("Кабинет", cabinet_id)
        return cabinet
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[CabinetDB]:
        """Получение всех кабинетов"""
        logger.info(f"Получение списка кабинетов (skip={skip}, limit={limit})")
        return self.db.query(CabinetDB).order_by(CabinetDB.number).offset(skip).limit(limit).all()
    
    def get_by_floor(self, floor: int) -> List[CabinetDB]:
        """Получение кабинетов по этажу"""
        logger.info(f"Получение кабинетов на этаже {floor}")
        return self.db.query(CabinetDB).filter(CabinetDB.floor == floor).order_by(CabinetDB.number).all()
    
    def update_cabinet(self, cabinet_id: int, data: CabinetUpdate) -> CabinetDB:
        """Обновление кабинета"""
        logger.info(f"Обновление кабинета ID={cabinet_id}")
        
        cabinet = self.get_by_id(cabinet_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'number' in update_data:
            existing = self.db.query(CabinetDB).filter(
                CabinetDB.number == update_data['number'],
                CabinetDB.id != cabinet_id
            ).first()
            if existing:
                logger.warning(f"Кабинет '{update_data['number']}' уже существует")
                raise AlreadyExistsException(f"Кабинет '{update_data['number']}' уже существует")
        
        for field, value in update_data.items():
            setattr(cabinet, field, value)
        
        self.db.commit()
        self.db.refresh(cabinet)
        logger.info(f"Кабинет ID={cabinet_id} успешно обновлен")
        return cabinet
    
    def delete_cabinet(self, cabinet_id: int) -> dict:
        """
        Удаление кабинета
        
        Ограничение: нельзя удалить кабинет, если в нем работают врачи
        """
        logger.info(f"Попытка удаления кабинета ID={cabinet_id}")
        
        cabinet = self.get_by_id(cabinet_id)
        if cabinet.doctors:
            logger.warning(f"В кабинете ID={cabinet_id} работают {len(cabinet.doctors)} врачей")
            raise DatabaseException(f"Невозможно удалить. {len(cabinet.doctors)} врачей работают в этом кабинете.")
        
        self.db.delete(cabinet)
        self.db.commit()
        logger.info(f"Кабинет ID={cabinet_id} успешно удален")
        return {"message": "Кабинет удален"}
    
    def get_cabinet_doctors(self, cabinet_id: int) -> List:
        """Получение списка врачей в кабинете"""
        logger.info(f"Получение врачей в кабинете ID={cabinet_id}")
        
        cabinet = self.get_by_id(cabinet_id)
        return cabinet.doctors
