"""
Pydantic схемы для валидации входных/выходных данных

Реализуют функциональные требования из курсовой работы:
- Валидация вводимых значений
- Проверка форматов данных
- Преобразование типов
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, time
from typing import Optional, List
import re
from datetime import datetime


# ==================== СХЕМЫ ДЛЯ ПАЦИЕНТОВ ====================

class PatientCreate(BaseModel):
    """Схема для создания пациента"""
    fio: str = Field(..., min_length=5, max_length=100, description="ФИО пациента (минимум 3 слова)")
    birth_date: date = Field(..., description="Дата рождения")
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    address: str = Field(..., min_length=10, max_length=200, description="Адрес проживания")
    insurance_number: str = Field(..., description="Номер полиса ОМС (16 цифр)")
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: str) -> str:
        """ФИО должно содержать минимум 3 слова (фамилия, имя, отчество)"""
        words = v.strip().split()
        if len(words) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова (Фамилия Имя Отчество)')
        return v
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        """Дата рождения не может быть в будущем и не раньше 1900 года"""
        today = date.today()
        if v > today:
            raise ValueError('Дата рождения не может быть в будущем')
        if v.year < 1900:
            raise ValueError('Дата рождения не может быть раньше 1900 года')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Номер телефона должен соответствовать формату +7XXXXXXXXXX"""
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v
    
    @field_validator('insurance_number')
    @classmethod
    def validate_insurance_number(cls, v: str) -> str:
        """Номер полиса ОМС должен содержать 16 цифр"""
        if not re.match(r'^\d{16}$', v):
            raise ValueError('Номер полиса ОМС должен содержать ровно 16 цифр')
        return v


class PatientUpdate(BaseModel):
    """Схема для обновления пациента"""
    fio: Optional[str] = Field(None, min_length=5, max_length=100)
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10, max_length=200)
    insurance_number: Optional[str] = None
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            words = v.strip().split()
            if len(words) < 3:
                raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            today = date.today()
            if v > today:
                raise ValueError('Дата рождения не может быть в будущем')
            if v.year < 1900:
                raise ValueError('Дата рождения не может быть раньше 1900 года')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v
    
    @field_validator('insurance_number')
    @classmethod
    def validate_insurance_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^\d{16}$', v):
            raise ValueError('Номер полиса ОМС должен содержать ровно 16 цифр')
        return v


class PatientResponse(BaseModel):
    """Схема ответа с данными пациента"""
    id: int
    fio: str
    birth_date: date
    phone: str
    address: str
    insurance_number: str
    
    model_config = ConfigDict(from_attributes=True)


# ==================== СХЕМЫ ДЛЯ ВРАЧЕЙ ====================

class DoctorCreate(BaseModel):
    """Схема для создания врача"""
    fio: str = Field(..., min_length=5, max_length=100, description="ФИО врача")
    specialization: str = Field(..., description="Специализация врача")
    cabinet_number: str = Field(..., min_length=1, max_length=10, description="Номер кабинета")
    phone: str = Field(..., description="Номер телефона")
    experience_years: int = Field(..., ge=0, le=60, description="Стаж работы в годах")
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: str) -> str:
        """ФИО должно содержать минимум 3 слова"""
        words = v.strip().split()
        if len(words) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова (Фамилия Имя Отчество)')
        return v
    
    @field_validator('specialization')
    @classmethod
    def validate_specialization(cls, v: str) -> str:
        """Специализация должна быть из предопределенного списка"""
        valid_specializations = [
            'Терапевт', 'Хирург', 'Кардиолог', 'Невролог', 'Педиатр',
            'Офтальмолог', 'Отоларинголог', 'Дерматолог', 'Эндокринолог',
            'Гастроэнтеролог', 'Уролог', 'Гинеколог', 'Стоматолог'
        ]
        if v not in valid_specializations:
            raise ValueError(f'Специализация должна быть одной из: {", ".join(valid_specializations)}')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валидация номера телефона"""
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v


class DoctorUpdate(BaseModel):
    """Схема для обновления врача"""
    fio: Optional[str] = Field(None, min_length=5, max_length=100)
    specialization: Optional[str] = None
    cabinet_number: Optional[str] = Field(None, min_length=1, max_length=10)
    phone: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            words = v.strip().split()
            if len(words) < 3:
                raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v


class DoctorResponse(BaseModel):
    """Схема ответа с данными врача"""
    id: int
    fio: str
    specialization: str
    cabinet_number: str
    phone: str
    experience_years: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== СХЕМЫ ДЛЯ ПРИЕМОВ ====================

class AppointmentCreate(BaseModel):
    """Схема для создания приема"""
    patient_id: int = Field(..., gt=0, description="ID пациента")
    doctor_id: int = Field(..., gt=0, description="ID врача")
    appointment_date: date = Field(..., description="Дата приема")
    appointment_time: time = Field(..., description="Время приема")
    status: str = Field(default="scheduled", description="Статус приема")
    
    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v: date) -> date:
        """Дата приема не может быть в прошлом"""
        today = date.today()
        if v < today:
            raise ValueError('Дата приема не может быть в прошлом')
        return v
    
    @field_validator('appointment_time')
    @classmethod
    def validate_appointment_time(cls, v: time) -> time:
        """Время приема должно быть в рабочие часы (8:00 - 20:00)"""
        if v < time(8, 0) or v >= time(20, 0):
            raise ValueError('Время приема должно быть в рабочие часы (с 8:00 до 20:00)')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Статус должен быть одним из разрешенных"""
        valid_statuses = ['scheduled', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Статус должен быть одним из: {", ".join(valid_statuses)}')
        return v


class AppointmentUpdate(BaseModel):
    """Схема для обновления приема"""
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    diagnosis: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_statuses = ['scheduled', 'completed', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f'Статус должен быть одним из: {", ".join(valid_statuses)}')
        return v


class AppointmentResponse(BaseModel):
    """Схема ответа с данными приема"""
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentDetailResponse(BaseModel):
    """Подробная информация о приеме с данными пациента и врача"""
    id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
    patient: PatientResponse
    doctor: DoctorResponse
    
    model_config = ConfigDict(from_attributes=True)
