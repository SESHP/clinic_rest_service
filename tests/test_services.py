"""
Unit-тесты для REST-сервиса "Поликлиника"

Демонстрация тестирования методов согласно требованиям курсовой работы
"""

import unittest
from datetime import date, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, PatientDB, DoctorDB, AppointmentDB
from app.schemas import PatientCreate, DoctorCreate, AppointmentCreate, AppointmentUpdate
from app.services import PatientService, DoctorService, AppointmentService
from app.exceptions import (
    NotFoundException,
    AlreadyExistsException,
    TimeConflictException,
    MaxAppointmentsExceededException,
    BusinessLogicException
)


class TestClinicServices(unittest.TestCase):
    """Тестирование сервисов поликлиники"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка тестовой базы данных (выполняется один раз)"""
        # Используем in-memory SQLite для тестов
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db = self.SessionLocal()
        
        # Создаем тестовые данные
        self._create_test_data()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()
        # Очищаем все таблицы
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
    
    def _create_test_data(self):
        """Создание тестовых данных"""
        # Создаем тестового пациента
        patient = PatientDB(
            id=1,
            fio="Иванов Иван Иванович",
            birth_date=date(1985, 5, 15),
            phone="+79161234567",
            address="г. Москва, ул. Ленина, д. 10",
            insurance_number="1234567890123456"
        )
        self.db.add(patient)
        
        # Создаем тестового врача
        doctor = DoctorDB(
            id=1,
            fio="Смирнов Алексей Викторович",
            specialization="Терапевт",
            cabinet_number="201",
            phone="+79161112233",
            experience_years=15
        )
        self.db.add(doctor)
        
        self.db.commit()
    
    # ==================== ТЕСТЫ ДЛЯ ПАЦИЕНТОВ ====================
    
    def test_create_patient_valid(self):
        """Тест создания валидного пациента"""
        patient_data = PatientCreate(
            fio="Петров Петр Петрович",
            birth_date=date(1990, 1, 1),
            phone="+79267654321",
            address="г. Москва, ул. Пушкина, д. 20",
            insurance_number="6543210987654321"
        )
        
        service = PatientService(self.db)
        patient = service.create_patient(patient_data)
        
        self.assertIsNotNone(patient.id)
        self.assertEqual(patient.fio, "Петров Петр Петрович")
        self.assertEqual(patient.insurance_number, "6543210987654321")
    
    def test_create_patient_duplicate_insurance(self):
        """Тест создания пациента с дублирующимся номером полиса"""
        patient_data = PatientCreate(
            fio="Сидоров Сидор Сидорович",
            birth_date=date(1980, 3, 10),
            phone="+79161111111",
            address="г. Москва, ул. Ленина, д. 1",
            insurance_number="1234567890123456"  # Дубликат!
        )
        
        service = PatientService(self.db)
        
        with self.assertRaises(AlreadyExistsException):
            service.create_patient(patient_data)
    
    def test_get_patient_by_id_exists(self):
        """Тест получения существующего пациента"""
        service = PatientService(self.db)
        patient = service.get_patient_by_id(1)
        
        self.assertEqual(patient.id, 1)
        self.assertEqual(patient.fio, "Иванов Иван Иванович")
    
    def test_get_patient_by_id_not_exists(self):
        """Тест получения несуществующего пациента"""
        service = PatientService(self.db)
        
        with self.assertRaises(NotFoundException):
            service.get_patient_by_id(999)
    
    def test_update_patient(self):
        """Тест обновления данных пациента"""
        from app.schemas import PatientUpdate
        
        update_data = PatientUpdate(phone="+79999999999")
        
        service = PatientService(self.db)
        patient = service.update_patient(1, update_data)
        
        self.assertEqual(patient.phone, "+79999999999")
        self.assertEqual(patient.fio, "Иванов Иван Иванович")  # Не изменилось
    
    def test_delete_patient(self):
        """Тест удаления пациента"""
        service = PatientService(self.db)
        result = service.delete_patient(1)
        
        self.assertIn("message", result)
        
        # Проверяем, что пациент действительно удален
        with self.assertRaises(NotFoundException):
            service.get_patient_by_id(1)
    
    # ==================== ТЕСТЫ ДЛЯ ВРАЧЕЙ ====================
    
    def test_create_doctor_valid(self):
        """Тест создания валидного врача"""
        doctor_data = DoctorCreate(
            fio="Кузнецов Иван Петрович",
            specialization="Хирург",
            cabinet_number="305",
            phone="+79162223344",
            experience_years=10
        )
        
        service = DoctorService(self.db)
        doctor = service.create_doctor(doctor_data)
        
        self.assertIsNotNone(doctor.id)
        self.assertEqual(doctor.specialization, "Хирург")
    
    def test_get_doctors_by_specialization(self):
        """Тест поиска врачей по специализации"""
        service = DoctorService(self.db)
        doctors = service.get_doctors_by_specialization("Терапевт")
        
        self.assertEqual(len(doctors), 1)
        self.assertEqual(doctors[0].fio, "Смирнов Алексей Викторович")
    
    def test_delete_doctor_with_scheduled_appointments(self):
        """Тест удаления врача с запланированными приемами"""
        # Создаем прием
        appointment = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            status="scheduled"
        )
        self.db.add(appointment)
        self.db.commit()
        
        service = DoctorService(self.db)
        
        with self.assertRaises(BusinessLogicException):
            service.delete_doctor(1)
    
    # ==================== ТЕСТЫ ДЛЯ ПРИЕМОВ ====================
    
    def test_create_appointment_valid(self):
        """Тест создания валидной записи на прием"""
        tomorrow = date.today() + timedelta(days=1)
        appointment_data = AppointmentCreate(
            patient_id=1,
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status="scheduled"
        )
        
        service = AppointmentService(self.db)
        appointment = service.create_appointment(appointment_data)
        
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.status, "scheduled")
    
    def test_create_appointment_time_conflict_doctor(self):
        """Тест обнаружения конфликта времени у врача"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Создаем первую запись
        appointment1 = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status="scheduled"
        )
        self.db.add(appointment1)
        self.db.commit()
        
        # Пытаемся создать вторую на то же время
        appointment_data = AppointmentCreate(
            patient_id=1,  # Тот же или другой пациент
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status="scheduled"
        )
        
        service = AppointmentService(self.db)
        
        with self.assertRaises(TimeConflictException):
            service.create_appointment(appointment_data)
    
    def test_create_appointment_minimum_interval(self):
        """Тест проверки минимального интервала между приемами"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Создаем первую запись
        appointment1 = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status="scheduled"
        )
        self.db.add(appointment1)
        self.db.commit()
        
        # Пытаемся создать вторую через 10 минут (меньше минимума 20 минут)
        appointment_data = AppointmentCreate(
            patient_id=1,
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(10, 10),
            status="scheduled"
        )
        
        service = AppointmentService(self.db)
        
        with self.assertRaises(BusinessLogicException):
            service.create_appointment(appointment_data)
    
    def test_create_appointment_max_per_day(self):
        """Тест ограничения на количество приемов в день"""
        tomorrow = date.today() + timedelta(days=1)
        service = AppointmentService(self.db)
        
        # Создаем 20 приемов (максимум)
        for i in range(20):
            appointment = AppointmentDB(
                patient_id=1,
                doctor_id=1,
                appointment_date=tomorrow,
                appointment_time=time(8 + i // 3, (i % 3) * 20),
                status="scheduled"
            )
            self.db.add(appointment)
        self.db.commit()
        
        # 21-я запись должна вызвать исключение
        appointment_data = AppointmentCreate(
            patient_id=1,
            doctor_id=1,
            appointment_date=tomorrow,
            appointment_time=time(19, 0),
            status="scheduled"
        )
        
        with self.assertRaises(MaxAppointmentsExceededException):
            service.create_appointment(appointment_data)
    
    def test_complete_appointment(self):
        """Тест завершения приема"""
        # Создаем прием на сегодня
        appointment = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status="scheduled"
        )
        self.db.add(appointment)
        self.db.commit()
        
        service = AppointmentService(self.db)
        completed = service.complete_appointment(appointment.id, "ОРВИ")
        
        self.assertEqual(completed.status, "completed")
        self.assertEqual(completed.diagnosis, "ОРВИ")
    
    def test_cancel_completed_appointment(self):
        """Тест отмены завершенного приема (должна быть ошибка)"""
        # Создаем завершенный прием
        appointment = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status="completed",
            diagnosis="Здоров"
        )
        self.db.add(appointment)
        self.db.commit()
        
        service = AppointmentService(self.db)
        
        with self.assertRaises(BusinessLogicException):
            service.cancel_appointment(appointment.id)
    
    def test_set_diagnosis_for_cancelled_appointment(self):
        """Тест установки диагноза для отмененного приема (должна быть ошибка)"""
        # Создаем отмененный прием
        appointment = AppointmentDB(
            patient_id=1,
            doctor_id=1,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status="cancelled"
        )
        self.db.add(appointment)
        self.db.commit()
        
        service = AppointmentService(self.db)
        update_data = AppointmentUpdate(diagnosis="Тест")
        
        with self.assertRaises(BusinessLogicException):
            service.update_appointment(appointment.id, update_data)


def run_tests():
    """Запуск всех тестов"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
