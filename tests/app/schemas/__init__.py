"""
Модуль Pydantic схем для валидации данных
"""

from .schemas import (
    # Специализации
    SpecializationCreate,
    SpecializationResponse,
    # Кабинеты
    CabinetCreate,
    CabinetUpdate,
    CabinetResponse,
    # Пациенты
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    # Врачи
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    # Приемы
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentDetailResponse
)

__all__ = [
    "SpecializationCreate",
    "SpecializationResponse",
    "CabinetCreate",
    "CabinetUpdate",
    "CabinetResponse",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "DoctorCreate",
    "DoctorUpdate",
    "DoctorResponse",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentDetailResponse"
]
