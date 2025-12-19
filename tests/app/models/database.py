"""
SQLAlchemy модели для работы с SQLite
"""

from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text, Index, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

doctor_specialization = Table(
    'doctor_specialization',
    Base.metadata,
    Column('doctor_id', Integer, ForeignKey('doctors.id', ondelete='CASCADE'), primary_key=True),
    Column('specialization_id', Integer, ForeignKey('specializations.id', ondelete='CASCADE'), primary_key=True)
)


class SpecializationDB(Base):
    __tablename__ = "specializations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    
    doctors = relationship("DoctorDB", secondary=doctor_specialization, back_populates="specializations")


class CabinetDB(Base):
    __tablename__ = "cabinets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Text, unique=True, nullable=False)
    floor = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    
    doctors = relationship("DoctorDB", back_populates="cabinet")


class PatientDB(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fio = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    insurance_number = Column(String(16), unique=True, nullable=False, index=True)
    
    appointments = relationship("AppointmentDB", back_populates="patient", cascade="all, delete-orphan")


class DoctorDB(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fio = Column(Text, nullable=False)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id", ondelete="SET NULL"), nullable=True)
    phone = Column(Text, nullable=False)
    experience_years = Column(Integer, nullable=False)
    
    cabinet = relationship("CabinetDB", back_populates="doctors")
    specializations = relationship("SpecializationDB", secondary=doctor_specialization, back_populates="doctors")
    appointments = relationship("AppointmentDB", back_populates="doctor")


class AppointmentDB(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    diagnosis = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="scheduled")
    
    patient = relationship("PatientDB", back_populates="appointments")
    doctor = relationship("DoctorDB", back_populates="appointments")
