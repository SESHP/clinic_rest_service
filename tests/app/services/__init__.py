"""
Модуль сервисов (бизнес-логика)
"""

from .patient_service import PatientService
from .doctor_service import DoctorService
from .appointment_service import AppointmentService
from .specialization_service import SpecializationService
from .cabinet_service import CabinetService

__all__ = [
    "PatientService",
    "DoctorService",
    "AppointmentService",
    "SpecializationService",
    "CabinetService"
]
