"""
Конфигурация подключения к базе данных SQLite
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "clinic.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.database import Base
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")


def drop_all_tables():
    from app.models.database import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Все таблицы удалены")
