"""
Конфигурация подключения к базе данных PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clinic_db")

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Включить для отладки SQL-запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=10,
    max_overflow=20
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency для получения сессии базы данных
    
    Используется в FastAPI endpoints через Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных
    
    Создает все таблицы согласно моделям
    """
    from app.models.database import Base
    
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована успешно")


def drop_all_tables():
    """
    Удаление всех таблиц (использовать только для тестирования!)
    """
    from app.models.database import Base
    
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Все таблицы удалены")
