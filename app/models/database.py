"""
SQLAlchemy модели для работы с PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class PatientDB(Base):
    """
    Таблица «Пациент»
    
    Согласно описанию из курсовой работы:
    - ID (PK) - INTEGER - Уникальный идентификатор пациента
    - FIO - TEXT - ФИО пациента
    - BIRTH_DATE - DATE - Дата рождения пациента
    - PHONE - TEXT - Номер телефона пациента
    - ADDRESS - TEXT - Адрес проживания пациента
    - INSURANCE_NUMBER - TEXT - Номер полиса ОМС
    """
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Уникальный идентификатор пациента. Первичный ключ.")
    fio = Column(Text, nullable=False, comment="ФИО пациента")
    birth_date = Column(Date, nullable=False, comment="Дата рождения пациента")
    phone = Column(Text, nullable=False, comment="Номер телефона пациента")
    address = Column(Text, nullable=False, comment="Адрес проживания пациента")
    insurance_number = Column(String(16), unique=True, nullable=False, index=True, comment="Номер полиса ОМС")
    
    # Связь с приемами (один-ко-многим)
    appointments = relationship("AppointmentDB", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, fio='{self.fio}')>"


class DoctorDB(Base):
    """
    Таблица «Врач»
    
    Согласно описанию из курсовой работы:
    - ID (PK) - INTEGER - Уникальный идентификатор врача
    - FIO - TEXT - ФИО врача
    - SPECIALIZATION - TEXT - Специализация врача
    - CABINET_NUMBER - TEXT - Номер кабинета
    - PHONE - TEXT - Номер телефона врача
    - EXPERIENCE_YEARS - INTEGER - Стаж работы в годах
    """
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Уникальный идентификатор врача. Первичный ключ.")
    fio = Column(Text, nullable=False, comment="ФИО врача")
    specialization = Column(Text, nullable=False, comment="Специализация врача (терапевт, хирург и т.д.)")
    cabinet_number = Column(Text, nullable=False, comment="Номер кабинета")
    phone = Column(Text, nullable=False, comment="Номер телефона врача")
    experience_years = Column(Integer, nullable=False, comment="Стаж работы в годах")
    
    # Связь с приемами (один-ко-многим)
    appointments = relationship("AppointmentDB", back_populates="doctor")
    
    # Индекс для быстрого поиска по специализации
    __table_args__ = (
        Index('idx_doctor_specialization', 'specialization'),
    )
    
    def __repr__(self):
        return f"<Doctor(id={self.id}, fio='{self.fio}', specialization='{self.specialization}')>"


class AppointmentDB(Base):
    """
    Таблица «Прием» (Связь пациентов и врачей)
    
    Согласно описанию из курсовой работы:
    - ID (PK) - INTEGER - Уникальный идентификатор записи
    - PATIENT_ID (FK) - INTEGER - Код пациента. Внешний ключ.
    - DOCTOR_ID (FK) - INTEGER - Код врача. Внешний ключ.
    - APPOINTMENT_DATE - DATE - Дата приема
    - APPOINTMENT_TIME - TIME - Время приема
    - DIAGNOSIS - TEXT - Диагноз (может быть NULL)
    - STATUS - TEXT - Статус приема (scheduled, completed, cancelled)
    """
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Уникальный идентификатор записи. Первичный ключ.")
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, comment="Код пациента. Внешний ключ.")
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, comment="Код врача. Внешний ключ.")
    appointment_date = Column(Date, nullable=False, comment="Дата приема")
    appointment_time = Column(Time, nullable=False, comment="Время приема")
    diagnosis = Column(Text, nullable=True, comment="Диагноз")
    status = Column(String(20), nullable=False, default="scheduled", comment="Статус приема")
    
    # Связи
    patient = relationship("PatientDB", back_populates="appointments")
    doctor = relationship("DoctorDB", back_populates="appointments")
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_appointment_patient', 'patient_id'),
        Index('idx_appointment_doctor', 'doctor_id'),
        Index('idx_appointment_date', 'appointment_date'),
        Index('idx_appointment_doctor_date_time', 'doctor_id', 'appointment_date', 'appointment_time'),
    )
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, date={self.appointment_date})>"
