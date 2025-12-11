"""
Скрипт для наполнения базы данных тестовыми данными

Создает полно-заполненную базу данных согласно требованиям курсовой работы
"""

from datetime import date, time, timedelta
from sqlalchemy.orm import Session
import random
import logging

from app.database import SessionLocal, init_db
from app.models.database import PatientDB, DoctorDB, AppointmentDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Тестовые данные
PATIENT_NAMES = [
    "Иванов Иван Иванович",
    "Петрова Мария Сергеевна",
    "Сидоров Алексей Петрович",
    "Кузнецова Анна Владимировна",
    "Смирнов Дмитрий Александрович",
    "Волкова Елена Игоревна",
    "Соколов Михаил Николаевич",
    "Новикова Ольга Викторовна",
    "Лебедев Сергей Андреевич",
    "Козлова Наталья Дмитриевна",
    "Морозов Владимир Юрьевич",
    "Андреева Татьяна Павловна",
    "Федоров Николай Михайлович",
    "Романова Екатерина Сергеевна",
    "Зайцев Артем Владимирович"
]

DOCTOR_DATA = [
    ("Смирнов Алексей Викторович", "Терапевт", "201", 15),
    ("Кузнецова Ирина Петровна", "Кардиолог", "305", 20),
    ("Попов Дмитрий Сергеевич", "Хирург", "410", 12),
    ("Васильева Елена Александровна", "Невролог", "203", 18),
    ("Михайлов Андрей Владимирович", "Педиатр", "102", 10),
    ("Соколова Мария Николаевна", "Офтальмолог", "215", 14),
    ("Новиков Игорь Юрьевич", "Эндокринолог", "308", 16),
    ("Федорова Анна Дмитриевна", "Гастроэнтеролог", "407", 11)
]

ADDRESSES = [
    "г. Москва, ул. Ленина, д. 10, кв. 25",
    "г. Москва, ул. Пушкина, д. 5, кв. 12",
    "г. Москва, пр. Мира, д. 88, кв. 45",
    "г. Москва, ул. Гагарина, д. 15, кв. 7",
    "г. Москва, ул. Чехова, д. 22, кв. 33",
    "г. Москва, пр. Победы, д. 50, кв. 18",
    "г. Москва, ул. Советская, д. 3, кв. 9",
    "г. Москва, ул. Московская, д. 77, кв. 55"
]


def generate_phone():
    """Генерация случайного номера телефона"""
    return f"+7916{random.randint(1000000, 9999999)}"


def generate_insurance_number():
    """Генерация случайного номера полиса ОМС"""
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])


def create_patients(db: Session, count: int = 15):
    """Создание тестовых пациентов"""
    logger.info(f"Создание {count} тестовых пациентов...")
    
    patients = []
    for i, name in enumerate(PATIENT_NAMES[:count], 1):
        birth_year = random.randint(1950, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        patient = PatientDB(
            fio=name,
            birth_date=date(birth_year, birth_month, birth_day),
            phone=generate_phone(),
            address=random.choice(ADDRESSES),
            insurance_number=generate_insurance_number()
        )
        patients.append(patient)
        db.add(patient)
    
    db.commit()
    logger.info(f"✅ Создано {len(patients)} пациентов")
    return patients


def create_doctors(db: Session):
    """Создание тестовых врачей"""
    logger.info(f"Создание {len(DOCTOR_DATA)} тестовых врачей...")
    
    doctors = []
    for fio, spec, cabinet, exp in DOCTOR_DATA:
        doctor = DoctorDB(
            fio=fio,
            specialization=spec,
            cabinet_number=cabinet,
            phone=generate_phone(),
            experience_years=exp
        )
        doctors.append(doctor)
        db.add(doctor)
    
    db.commit()
    logger.info(f"✅ Создано {len(doctors)} врачей")
    return doctors


def create_appointments(db: Session, patients: list, doctors: list, count: int = 30):
    """Создание тестовых приемов"""
    logger.info(f"Создание ~{count} тестовых приемов...")
    
    appointments = []
    statuses = ["scheduled", "completed", "cancelled"]
    diagnoses = [
        "ОРВИ", "Грипп", "Гастрит", "Гипертония", 
        "Остеохондроз", "Аллергия", "Здоров",
        "Бронхит", "Анемия", "Мигрень"
    ]
    
    # Создаем приемы за последние 30 дней и на будущее
    start_date = date.today() - timedelta(days=30)
    
    created = 0
    attempts = 0
    max_attempts = count * 3
    
    while created < count and attempts < max_attempts:
        attempts += 1
        
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        
        # Случайная дата в диапазоне [-30, +30] дней от сегодня
        days_offset = random.randint(-30, 30)
        appt_date = date.today() + timedelta(days=days_offset)
        
        # Время приема
        hour = random.randint(8, 19)
        minute = random.choice([0, 20, 40])
        appt_time = time(hour, minute)
        
        # Проверяем, нет ли конфликта
        existing = db.query(AppointmentDB).filter(
            AppointmentDB.doctor_id == doctor.id,
            AppointmentDB.appointment_date == appt_date,
            AppointmentDB.appointment_time == appt_time
        ).first()
        
        if existing:
            continue
        
        # Определяем статус
        if appt_date < date.today():
            status = random.choice(["completed", "cancelled"])
            diagnosis = random.choice(diagnoses) if status == "completed" else None
        else:
            status = "scheduled"
            diagnosis = None
        
        appointment = AppointmentDB(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appt_date,
            appointment_time=appt_time,
            status=status,
            diagnosis=diagnosis
        )
        
        appointments.append(appointment)
        db.add(appointment)
        created += 1
    
    db.commit()
    logger.info(f"✅ Создано {len(appointments)} приемов")
    return appointments


def populate_database():
    """Наполнение базы данных всеми тестовыми данными"""
    logger.info("=" * 80)
    logger.info("НАПОЛНЕНИЕ БАЗЫ ДАННЫХ ТЕСТОВЫМИ ДАННЫМИ")
    logger.info("=" * 80)
    
    # Инициализация БД
    init_db()
    
    # Создание сессии
    db = SessionLocal()
    
    try:
        # Создание данных
        patients = create_patients(db, count=15)
        doctors = create_doctors(db)
        appointments = create_appointments(db, patients, doctors, count=40)
        
        logger.info("=" * 80)
        logger.info("✅ БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
        logger.info(f"   📊 Пациентов: {len(patients)}")
        logger.info(f"   👨‍⚕️ Врачей: {len(doctors)}")
        logger.info(f"   📅 Приемов: {len(appointments)}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при наполнении БД: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
