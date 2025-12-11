"""
Модуль моделей данных
"""

from .entities import Patient, Doctor, Appointment
from .database import PatientDB, DoctorDB, AppointmentDB, Base

__all__ = [
    "Patient",
    "Doctor", 
    "Appointment",
    "PatientDB",
    "DoctorDB",
    "AppointmentDB",
    "Base"
]
