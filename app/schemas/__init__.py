"""
Модуль Pydantic схем для валидации данных
"""

from .schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentDetailResponse
)

__all__ = [
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
