"""
Главный файл FastAPI приложения

REST-сервис "Поликлиника"
Курсовой проект по дисциплине "Технология программирования"
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.database import init_db
from app.logger import setup_logging
from app.problem_details import (
    clinic_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.exceptions import ClinicException
from app.controllers import patient_router, doctor_router, appointment_router

# Настройка логирования
log_file = os.getenv("LOG_FILE", "logs/app.log")
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_file=log_file, log_level=log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    
    Выполняется при запуске и завершении приложения
    """
    # Startup
    logger.info("🚀 Запуск приложения...")
    logger.info("📊 Инициализация базы данных...")
    init_db()
    logger.info("✅ Приложение успешно запущено")
    
    yield
    
    # Shutdown
    logger.info("🛑 Завершение работы приложения...")
    logger.info("✅ Приложение остановлено")


# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="REST-сервис 'Поликлиника'",
    description="""
    ## Курсовой проект по дисциплине "Технология программирования"
    
    REST API для управления поликлиникой:
    - 👥 Управление пациентами
    - 👨‍⚕️ Управление врачами
    - 📅 Управление приемами (записи на прием)
    
    ### Реализованные требования:
    
    ✅ Полнофункциональная база данных PostgreSQL с 3 связанными таблицами  
    ✅ CRUD операции для всех сущностей  
    ✅ Валидация данных через Pydantic схемы  
    ✅ Обработка пользовательских исключений  
    ✅ Вывод ошибок в формате Problem Details (RFC 7807)  
    ✅ Логирование всех операций и ошибок  
    ✅ Бизнес-логика с проверками и ограничениями  
    
    ### Бизнес-правила:
    
    **Пациенты:**
    - Уникальный номер полиса ОМС (16 цифр)
    - Валидация ФИО, даты рождения, телефона
    - Каскадное удаление приемов при удалении пациента
    
    **Врачи:**
    - Специализация из предопределенного списка
    - Нельзя удалить врача с запланированными приемами
    - Ограничение: не более 30 активных пациентов
    
    **Приемы:**
    - Нет конфликтов по времени для врача и пациента
    - Максимум 20 приемов в день у врача
    - Минимум 20 минут между приемами
    - Один пациент - один прием к врачу в день
    - Нельзя отменить завершенный прием
    - Нельзя установить диагноз для отмененного приема
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
app.add_exception_handler(ClinicException, clinic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Подключение роутеров
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(appointment_router)


@app.get("/", tags=["Root"])
async def root():
    """Корневой endpoint"""
    return {
        "message": "REST-сервис 'Поликлиника'",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "operational"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
