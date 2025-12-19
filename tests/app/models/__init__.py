"""
Модуль моделей данных
"""

from .entities import Patient, Doctor, Appointment, Specialization, Cabinet
from .database import PatientDB, DoctorDB, AppointmentDB, SpecializationDB, CabinetDB, Base, doctor_specialization

__all__ = [
    "Patient",
    "Doctor", 
    "Appointment",
    "Specialization",
    "Cabinet",
    "PatientDB",
    "DoctorDB",
    "AppointmentDB",
    "SpecializationDB",
    "CabinetDB",
    "Base",
    "doctor_specialization"
]
