"""
Скрипт инициализации базы данных

Заполняет специализации, кабинеты и обновляет врачей
"""

from app.database import SessionLocal, init_db
from app.models.database import SpecializationDB, CabinetDB, DoctorDB
from datetime import date, time, timedelta
from app.models.database import AppointmentDB
from app.models.database import SpecializationDB, CabinetDB, DoctorDB, PatientDB, AppointmentDB

import logging

logger = logging.getLogger(__name__)

def seed_specializations(db):
    """Заполнение специализаций"""
    specializations = [
        'Терапевт', 'Хирург', 'Кардиолог', 'Невролог', 'Педиатр',
        'Офтальмолог', 'Отоларинголог', 'Дерматолог', 'Эндокринолог',
        'Гастроэнтеролог', 'Уролог', 'Гинеколог', 'Стоматолог'
    ]
    
    created = 0
    for name in specializations:
        existing = db.query(SpecializationDB).filter(SpecializationDB.name == name).first()
        if not existing:
            db.add(SpecializationDB(name=name))
            created += 1
    
    db.commit()
    print(f"✅ Специализации: добавлено {created}, всего {len(specializations)}")
    return db.query(SpecializationDB).all()


def seed_cabinets(db):
    """Заполнение кабинетов"""
    cabinets_data = [
        {"number": "101", "floor": 1, "description": "Терапевтический кабинет"},
        {"number": "102", "floor": 1, "description": "Кабинет педиатра"},
        {"number": "103", "floor": 1, "description": "Процедурный кабинет"},
        {"number": "201", "floor": 2, "description": "Хирургический кабинет"},
        {"number": "202", "floor": 2, "description": "Кабинет кардиолога"},
        {"number": "203", "floor": 2, "description": "Кабинет невролога"},
        {"number": "301", "floor": 3, "description": "Кабинет офтальмолога"},
        {"number": "302", "floor": 3, "description": "Кабинет ЛОР"},
        {"number": "303", "floor": 3, "description": "Кабинет дерматолога"},
        {"number": "401", "floor": 4, "description": "Стоматологический кабинет"},
    ]
    
    created = 0
    for data in cabinets_data:
        existing = db.query(CabinetDB).filter(CabinetDB.number == data["number"]).first()
        if not existing:
            db.add(CabinetDB(**data))
            created += 1
    
    db.commit()
    print(f"✅ Кабинеты: добавлено {created}, всего {len(cabinets_data)}")
    return db.query(CabinetDB).all()


def update_doctors(db, specializations, cabinets):
    """Обновление существующих врачей - привязка к специализациям и кабинетам"""
    
    # Словари для быстрого поиска
    spec_by_name = {s.name: s for s in specializations}
    cab_by_number = {c.number: c for c in cabinets}
    
    # Получаем всех врачей без специализаций
    doctors = db.query(DoctorDB).all()
    updated = 0
    
    for doctor in doctors:
        changed = False
        
        # Если у врача нет специализаций - назначаем Терапевта по умолчанию
        if not doctor.specializations:
            if 'Терапевт' in spec_by_name:
                doctor.specializations.append(spec_by_name['Терапевт'])
                changed = True
        
        # Если у врача нет кабинета - назначаем 101
        if doctor.cabinet_id is None:
            if '101' in cab_by_number:
                doctor.cabinet_id = cab_by_number['101'].id
                changed = True
        
        if changed:
            updated += 1
    
    db.commit()
    print(f"✅ Врачи: обновлено {updated} из {len(doctors)}")


def seed_sample_doctors(db, specializations, cabinets):
    """Создание тестовых врачей если их нет"""
    
    if db.query(DoctorDB).count() > 0:
        print("ℹ️  Врачи уже есть в базе, пропускаем создание тестовых")
        return
    
    spec_by_name = {s.name: s for s in specializations}
    cab_by_number = {c.number: c for c in cabinets}
    
    doctors_data = [
        {
            "fio": "Иванов Иван Иванович",
            "phone": "+79001234567",
            "experience_years": 15,
            "specializations": ["Терапевт"],
            "cabinet": "101"
        },
        {
            "fio": "Петрова Анна Сергеевна",
            "phone": "+79001234568",
            "experience_years": 10,
            "specializations": ["Кардиолог"],
            "cabinet": "202"
        },
        {
            "fio": "Сидоров Петр Михайлович",
            "phone": "+79001234569",
            "experience_years": 20,
            "specializations": ["Хирург"],
            "cabinet": "201"
        },
        {
            "fio": "Козлова Мария Александровна",
            "phone": "+79001234570",
            "experience_years": 8,
            "specializations": ["Педиатр"],
            "cabinet": "102"
        },
        {
            "fio": "Новиков Александр Викторович",
            "phone": "+79001234571",
            "experience_years": 12,
            "specializations": ["Невролог", "Терапевт"],
            "cabinet": "203"
        },
    ]
    
    for data in doctors_data:
        doctor = DoctorDB(
            fio=data["fio"],
            phone=data["phone"],
            experience_years=data["experience_years"],
            cabinet_id=cab_by_number[data["cabinet"]].id
        )
        
        for spec_name in data["specializations"]:
            if spec_name in spec_by_name:
                doctor.specializations.append(spec_by_name[spec_name])
        
        db.add(doctor)
    
    db.commit()
    print(f"✅ Создано {len(doctors_data)} тестовых врачей")

def seed_sample_patients(db):
    """Создание тестовых пациентов"""
    logger.info("Проверка наличия пациентов...")
    
    count = db.query(PatientDB).count()
    if count > 0:
        logger.info(f"В базе уже есть {count} пациентов, пропускаем")
        return
    
    patients = [
        PatientDB(
            fio="Смирнов Алексей Петрович",
            birth_date=date(1985, 3, 15),
            phone="+79001234567",
            address="г. Москва, ул. Ленина, д. 10, кв. 5",
            insurance_number="1234567890123456"
        ),
        PatientDB(
            fio="Кузнецова Мария Ивановна",
            birth_date=date(1990, 7, 22),
            phone="+79001234568",
            address="г. Москва, ул. Пушкина, д. 25, кв. 12",
            insurance_number="2345678901234567"
        ),
        PatientDB(
            fio="Попов Дмитрий Сергеевич",
            birth_date=date(1978, 11, 8),
            phone="+79001234569",
            address="г. Москва, ул. Гагарина, д. 5, кв. 45",
            insurance_number="3456789012345678"
        ),
        PatientDB(
            fio="Волкова Анна Александровна",
            birth_date=date(2015, 5, 30),
            phone="+79001234570",
            address="г. Москва, ул. Мира, д. 18, кв. 7",
            insurance_number="4567890123456789"
        ),
        PatientDB(
            fio="Соколов Игорь Владимирович",
            birth_date=date(1965, 9, 12),
            phone="+79001234571",
            address="г. Москва, ул. Советская, д. 33, кв. 21",
            insurance_number="5678901234567890"
        ),
    ]
    
    for patient in patients:
        db.add(patient)
    
    db.commit()
    logger.info(f"Создано {len(patients)} тестовых пациентов")


def seed_sample_appointments(db):
    """Создание тестовых приемов"""
    logger.info("Проверка наличия приемов...")
    
    count = db.query(AppointmentDB).count()
    if count > 0:
        logger.info(f"В базе уже есть {count} приемов, пропускаем")
        return
    
    doctors = db.query(DoctorDB).all()
    patients = db.query(PatientDB).all()
    
    if not doctors or not patients:
        logger.warning("Нет врачей или пациентов для создания приемов")
        return
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    yesterday = today - timedelta(days=1)
    
    appointments = [
        # Прошедшие приемы (завершенные)
        AppointmentDB(
            patient_id=patients[0].id,
            doctor_id=doctors[0].id,
            appointment_date=yesterday,
            appointment_time=time(9, 0),
            status="completed",
            diagnosis="ОРВИ, легкое течение. Рекомендован постельный режим."
        ),
        AppointmentDB(
            patient_id=patients[1].id,
            doctor_id=doctors[1].id,
            appointment_date=yesterday,
            appointment_time=time(10, 30),
            status="completed",
            diagnosis="Гипертоническая болезнь II стадии. Назначена терапия."
        ),
        # Сегодняшние приемы
        AppointmentDB(
            patient_id=patients[2].id,
            doctor_id=doctors[0].id,
            appointment_date=today,
            appointment_time=time(11, 0),
            status="scheduled"
        ),
        AppointmentDB(
            patient_id=patients[3].id,
            doctor_id=doctors[3].id,
            appointment_date=today,
            appointment_time=time(14, 0),
            status="scheduled"
        ),
        # Завтрашние приемы
        AppointmentDB(
            patient_id=patients[0].id,
            doctor_id=doctors[1].id,
            appointment_date=tomorrow,
            appointment_time=time(9, 30),
            status="scheduled"
        ),
        AppointmentDB(
            patient_id=patients[4].id,
            doctor_id=doctors[2].id,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status="scheduled"
        ),
        AppointmentDB(
            patient_id=patients[1].id,
            doctor_id=doctors[4].id,
            appointment_date=tomorrow,
            appointment_time=time(15, 0),
            status="scheduled"
        ),
        # Послезавтра
        AppointmentDB(
            patient_id=patients[2].id,
            doctor_id=doctors[1].id,
            appointment_date=day_after,
            appointment_time=time(11, 30),
            status="scheduled"
        ),
        # Отмененный прием
        AppointmentDB(
            patient_id=patients[3].id,
            doctor_id=doctors[0].id,
            appointment_date=yesterday,
            appointment_time=time(16, 0),
            status="cancelled"
        ),
    ]
    
    for appointment in appointments:
        db.add(appointment)
    
    db.commit()
    logger.info(f"Создано {len(appointments)} тестовых приемов")

def main():
    print("=" * 50)
    print("Инициализация базы данных")
    print("=" * 50)
    
    # Создаем таблицы
    init_db()
    
    # Открываем сессию
    db = SessionLocal()
    
    try:
        # Заполняем справочники
        specializations = seed_specializations(db)
        cabinets = seed_cabinets(db)
        
        # Обновляем существующих врачей
        update_doctors(db, specializations, cabinets)
        
        # Создаем тестовых врачей если база пустая
        seed_sample_doctors(db, specializations, cabinets)

        seed_sample_patients(db)      # <-- добавь
        seed_sample_appointments(db)
        
        print("=" * 50)
        print("✅ Инициализация завершена успешно!")
        print("=" * 50)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
