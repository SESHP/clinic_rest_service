"""
Модуль сервисов (бизнес-логика)
"""

from .patient_service import PatientService
from .doctor_service import DoctorService
from .appointment_service import AppointmentService

__all__ = [
    "PatientService",
    "DoctorService",
    "AppointmentService"
]
