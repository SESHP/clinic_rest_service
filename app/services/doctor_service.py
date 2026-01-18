"""
Сервис для работы с врачами
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.models.database import DoctorDB, AppointmentDB, SpecializationDB, CabinetDB
from app.schemas import DoctorCreate, DoctorUpdate
from app.exceptions import NotFoundException, BusinessLogicException, DatabaseException

logger = logging.getLogger(__name__)


class DoctorService:
    """
    Сервис для управления врачами
    
    Операции:
    - Добавить нового врача
    - Получить данные врача по ID
    - Получить список всех врачей
    - Получить врачей по специализации
    - Редактировать данные врача
    - Удалить врача
    """
    
    MAX_ACTIVE_PATIENTS = 30
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_doctor(self, data: DoctorCreate) -> DoctorDB:
        """
        Создание нового врача
        
        Валидация:
        - Все обязательные поля заполнены
        - Специализации существуют в базе
        - Кабинет существует (если указан)
        """
        logger.info(f"Попытка создания нового врача: {data.fio}")
        
        # Проверка специализаций
        specializations = self.db.query(SpecializationDB).filter(
            SpecializationDB.id.in_(data.specialization_ids)
        ).all()
        
        if len(specializations) != len(data.specialization_ids):
            found_ids = {s.id for s in specializations}
            missing = set(data.specialization_ids) - found_ids
            logger.warning(f"Специализация с ID={list(missing)[0]} не найдена")
            raise NotFoundException("Специализация", list(missing)[0])
        
        # Проверка кабинета
        if data.cabinet_id:
            cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == data.cabinet_id).first()
            if not cabinet:
                logger.warning(f"Кабинет с ID={data.cabinet_id} не найден")
                raise NotFoundException("Кабинет", data.cabinet_id)
        
        try:
            doctor = DoctorDB(
                fio=data.fio,
                cabinet_id=data.cabinet_id,
                phone=data.phone,
                experience_years=data.experience_years
            )
            doctor.specializations = specializations
            
            self.db.add(doctor)
            self.db.commit()
            self.db.refresh(doctor)
            logger.info(f"Врач успешно создан с ID={doctor.id}")
            return doctor
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании врача: {str(e)}")
            raise DatabaseException("Ошибка при создании врача")
    
    def get_doctor_by_id(self, doctor_id: int) -> DoctorDB:
        """Получение врача по ID"""
        logger.info(f"Получение врача с ID={doctor_id}")
        
        doctor = self.db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
        if not doctor:
            logger.warning(f"Врач с ID={doctor_id} не найден")
            raise NotFoundException("Врач", doctor_id)
        return doctor
    
    def get_all_doctors(self, skip: int = 0, limit: int = 100) -> List[DoctorDB]:
        """Получение списка всех врачей с пагинацией"""
        logger.info(f"Получение списка врачей (skip={skip}, limit={limit})")
        return self.db.query(DoctorDB).offset(skip).limit(limit).all()
    
    def get_doctors_by_specialization(self, name: str) -> List[DoctorDB]:
        """Получение врачей по названию специализации"""
        logger.info(f"Поиск врачей по специализации: {name}")
        return self.db.query(DoctorDB).join(DoctorDB.specializations).filter(
            SpecializationDB.name == name
        ).all()
    
    def get_doctors_by_specialization_id(self, spec_id: int) -> List[DoctorDB]:
        """Получение врачей по ID специализации"""
        logger.info(f"Поиск врачей по ID специализации: {spec_id}")
        return self.db.query(DoctorDB).join(DoctorDB.specializations).filter(
            SpecializationDB.id == spec_id
        ).all()
    
    def get_doctors_by_cabinet(self, cabinet_id: int) -> List[DoctorDB]:
        """Получение врачей по кабинету"""
        logger.info(f"Поиск врачей в кабинете ID={cabinet_id}")
        return self.db.query(DoctorDB).filter(DoctorDB.cabinet_id == cabinet_id).all()
    
    def update_doctor(self, doctor_id: int, data: DoctorUpdate) -> DoctorDB:
        """
        Обновление данных врача
        
        Валидация:
        - Врач должен существовать
        - Новые специализации и кабинет должны существовать
        """
        logger.info(f"Обновление врача с ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'specialization_ids' in update_data:
            spec_ids = update_data.pop('specialization_ids')
            specializations = self.db.query(SpecializationDB).filter(
                SpecializationDB.id.in_(spec_ids)
            ).all()
            if len(specializations) != len(spec_ids):
                logger.warning(f"Одна из специализаций не найдена")
                raise NotFoundException("Специализация", "one of ids")
            doctor.specializations = specializations
        
        if 'cabinet_id' in update_data and update_data['cabinet_id']:
            cabinet = self.db.query(CabinetDB).filter(CabinetDB.id == update_data['cabinet_id']).first()
            if not cabinet:
                logger.warning(f"Кабинет с ID={update_data['cabinet_id']} не найден")
                raise NotFoundException("Кабинет", update_data['cabinet_id'])
        
        for field, value in update_data.items():
            setattr(doctor, field, value)
        
        self.db.commit()
        self.db.refresh(doctor)
        logger.info(f"Врач с ID={doctor_id} успешно обновлен")
        return doctor
    
    def delete_doctor(self, doctor_id: int) -> dict:
        """
        Удаление врача
        
        Бизнес-правила:
        - Врач не может быть удален, если у него есть запланированные приемы
        """
        logger.info(f"Попытка удаления врача с ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        
        scheduled = self.db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.status == "scheduled"
        ).count()
        
        if scheduled > 0:
            logger.warning(f"У врача ID={doctor_id} есть {scheduled} запланированных приемов")
            raise BusinessLogicException(f"У врача {scheduled} запланированных приемов. Сначала отмените или перенесите их.")
        
        self.db.delete(doctor)
        self.db.commit()
        logger.info(f"Врач с ID={doctor_id} успешно удален")
        return {"message": "Врач удален"}
    
    def add_specialization(self, doctor_id: int, spec_id: int) -> DoctorDB:
        """Добавление специализации врачу"""
        logger.info(f"Добавление специализации ID={spec_id} врачу ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        
        if not spec:
            logger.warning(f"Специализация с ID={spec_id} не найдена")
            raise NotFoundException("Специализация", spec_id)
        if spec in doctor.specializations:
            logger.warning(f"Врач ID={doctor_id} уже имеет специализацию ID={spec_id}")
            raise BusinessLogicException("Врач уже имеет эту специализацию")
        
        doctor.specializations.append(spec)
        self.db.commit()
        self.db.refresh(doctor)
        logger.info(f"Специализация ID={spec_id} добавлена врачу ID={doctor_id}")
        return doctor
    
    def remove_specialization(self, doctor_id: int, spec_id: int) -> DoctorDB:
        """
        Удаление специализации у врача
        
        Ограничение: врач должен иметь хотя бы одну специализацию
        """
        logger.info(f"Удаление специализации ID={spec_id} у врача ID={doctor_id}")
        
        doctor = self.get_doctor_by_id(doctor_id)
        spec = self.db.query(SpecializationDB).filter(SpecializationDB.id == spec_id).first()
        
        if not spec:
            logger.warning(f"Специализация с ID={spec_id} не найдена")
            raise NotFoundException("Специализация", spec_id)
        if spec not in doctor.specializations:
            logger.warning(f"Врач ID={doctor_id} не имеет специализации ID={spec_id}")
            raise BusinessLogicException("Врач не имеет этой специализации")
        if len(doctor.specializations) <= 1:
            logger.warning(f"Попытка удалить последнюю специализацию у врача ID={doctor_id}")
            raise BusinessLogicException("Врач должен иметь хотя бы одну специализацию")
        
        doctor.specializations.remove(spec)
        self.db.commit()
        self.db.refresh(doctor)
        logger.info(f"Специализация ID={spec_id} удалена у врача ID={doctor_id}")
        return doctor
