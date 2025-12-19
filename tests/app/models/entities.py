"""
Модели данных для REST-сервиса "Поликлиника"
"""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional, List


@dataclass
class Specialization:
    id: int
    name: str


@dataclass
class Cabinet:
    id: int
    number: str
    floor: Optional[int] = None
    description: Optional[str] = None


@dataclass
class Patient:
    id: int
    fio: str
    birth_date: date
    phone: str
    address: str
    insurance_number: str


@dataclass
class Doctor:
    id: int
    fio: str
    cabinet_id: Optional[int]
    phone: str
    experience_years: int
    specializations: Optional[List[Specialization]] = None


@dataclass
class Appointment:
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
