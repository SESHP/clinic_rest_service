"""
Скрипт инициализации базы данных

Заполняет специализации, кабинеты и обновляет врачей
"""

from app.database import SessionLocal, init_db
from app.models.database import SpecializationDB, CabinetDB, DoctorDB


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
        
        print("=" * 50)
        print("✅ Инициализация завершена успешно!")
        print("=" * 50)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
