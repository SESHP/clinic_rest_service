"""
Модели базы данных для REST-сервиса "Поликлиника"

Согласно ER-диаграмме из курсовой работы:
- Пациенты (Patient)
- Врачи (Doctor) 
- Приемы (Appointment) - связь многие-ко-многим между пациентами и врачами
"""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class Patient:
    """
    Объект Пациент
    
    Характеристики:
    - id: код пациента (уникальный идентификатор)
    - fio: ФИО пациента
    - birth_date: дата рождения
    - phone: номер телефона
    - address: адрес проживания
    - insurance_number: номер полиса ОМС
    """
    id: int
    fio: str
    birth_date: date
    phone: str
    address: str
    insurance_number: str


@dataclass
class Doctor:
    """
    Объект Врач
    
    Характеристики:
    - id: код врача (уникальный идентификатор)
    - fio: ФИО врача
    - specialization: специализация (терапевт, хирург, кардиолог и т.д.)
    - cabinet_number: номер кабинета
    - phone: номер телефона
    - experience_years: стаж работы в годах
    """
    id: int
    fio: str
    specialization: str   # удалить
    cabinet_number: str   # удалить
    phone: str
    experience_years: int


@dataclass
class Appointment:
    """
    Объект Прием (Связь пациента и врача)
    
    Характеристики:
    - id: код записи (уникальный идентификатор)
    - patient_id: ссылка на пациента
    - doctor_id: ссылка на врача
    - appointment_date: дата приема
    - appointment_time: время приема
    - diagnosis: диагноз (может быть пустым)
    - status: статус приема (scheduled, completed, cancelled)
    """
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    diagnosis: Optional[str]
    status: str
