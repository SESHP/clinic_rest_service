"""
Pydantic схемы для валидации данных
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, time
from typing import Optional, List
import re


# ==================== СПЕЦИАЛИЗАЦИИ ====================

class SpecializationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        valid = ['Терапевт', 'Хирург', 'Кардиолог', 'Невролог', 'Педиатр',
                 'Офтальмолог', 'Отоларинголог', 'Дерматолог', 'Эндокринолог',
                 'Гастроэнтеролог', 'Уролог', 'Гинеколог', 'Стоматолог']
        if v not in valid:
            raise ValueError(f'Специализация должна быть одной из: {", ".join(valid)}')
        return v


class SpecializationResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# ==================== КАБИНЕТЫ ====================

class CabinetCreate(BaseModel):
    number: str = Field(..., min_length=1, max_length=10)
    floor: Optional[int] = Field(None, ge=1, le=20)
    description: Optional[str] = Field(None, max_length=200)


class CabinetUpdate(BaseModel):
    number: Optional[str] = Field(None, min_length=1, max_length=10)
    floor: Optional[int] = Field(None, ge=1, le=20)
    description: Optional[str] = Field(None, max_length=200)


class CabinetResponse(BaseModel):
    id: int
    number: str
    floor: Optional[int]
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


# ==================== ПАЦИЕНТЫ ====================

class PatientCreate(BaseModel):
    fio: str = Field(..., min_length=5, max_length=100)
    birth_date: date
    phone: str
    address: str = Field(..., min_length=10, max_length=200)
    insurance_number: str
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: str) -> str:
        if len(v.strip().split()) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Дата рождения не может быть в будущем')
        if v.year < 1900:
            raise ValueError('Дата рождения не может быть раньше 1900 года')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v
    
    @field_validator('insurance_number')
    @classmethod
    def validate_insurance_number(cls, v: str) -> str:
        if not re.match(r'^\d{16}$', v):
            raise ValueError('Номер полиса ОМС должен содержать 16 цифр')
        return v


class PatientUpdate(BaseModel):
    fio: Optional[str] = Field(None, min_length=5, max_length=100)
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10, max_length=200)
    insurance_number: Optional[str] = None
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v):
        if v and len(v.strip().split()) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v
    
    @field_validator('insurance_number')
    @classmethod
    def validate_insurance_number(cls, v):
        if v and not re.match(r'^\d{16}$', v):
            raise ValueError('Номер полиса ОМС должен содержать 16 цифр')
        return v


class PatientResponse(BaseModel):
    id: int
    fio: str
    birth_date: date
    phone: str
    address: str
    insurance_number: str
    model_config = ConfigDict(from_attributes=True)


# ==================== ВРАЧИ ====================

class DoctorCreate(BaseModel):
    fio: str = Field(..., min_length=5, max_length=100)
    specialization_ids: List[int] = Field(..., min_length=1)
    cabinet_id: Optional[int] = None
    phone: str
    experience_years: int = Field(..., ge=0, le=60)
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v: str) -> str:
        if len(v.strip().split()) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v


class DoctorUpdate(BaseModel):
    fio: Optional[str] = Field(None, min_length=5, max_length=100)
    specialization_ids: Optional[List[int]] = Field(None, min_length=1)
    cabinet_id: Optional[int] = None
    phone: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    
    @field_validator('fio')
    @classmethod
    def validate_fio(cls, v):
        if v and len(v.strip().split()) < 3:
            raise ValueError('ФИО должно содержать минимум 3 слова')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^\+7\d{10}$', v):
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return v


class DoctorResponse(BaseModel):
    id: int
    fio: str
    specializations: List[SpecializationResponse]
    cabinet: Optional[CabinetResponse]
    phone: str
    experience_years: int
    model_config = ConfigDict(from_attributes=True)


# ==================== ПРИЕМЫ ====================

class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    appointment_date: date
    appointment_time: time
    status: str = Field(default="scheduled")
    
    @field_validator('appointment_date')
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Дата приема не может быть в прошлом')
        return v
    
    @field_validator('appointment_time')
    @classmethod
    def validate_time(cls, v: time) -> time:
        if v < time(8, 0) or v >= time(20, 0):
            raise ValueError('Время приема должно быть с 8:00 до 20:00')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = ['scheduled', 'completed', 'cancelled']
        if v not in valid:
            raise ValueError(f'Статус должен быть: {", ".join(valid)}')
        return v


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    diagnosis: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v:
            valid = ['scheduled', 'completed', 'cancelled']
            if v not in valid:
                raise ValueError(f'Статус должен быть: {", ".join(valid)}')
        return v


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
    model_config = ConfigDict(from_attributes=True)


class AppointmentDetailResponse(BaseModel):
    id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
    patient: PatientResponse
    doctor: DoctorResponse
    model_config = ConfigDict(from_attributes=True)
