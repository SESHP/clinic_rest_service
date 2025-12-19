"""
REST-сервис "Поликлиника"
Курсовой проект по дисциплине "Технология программирования"
"""

from fastapi import FastAPI
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
from app.controllers import (
    patient_router,
    doctor_router,
    appointment_router,
    specialization_router,
    cabinet_router
)

log_file = os.getenv("LOG_FILE", "logs/app.log")
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_file=log_file, log_level=log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Запуск приложения...")
    init_db()
    logger.info("✅ Приложение запущено")
    yield
    logger.info("🛑 Приложение остановлено")


app = FastAPI(
    title="REST-сервис 'Поликлиника'",
    description="""
    ## Курсовой проект
    
    REST API для управления поликлиникой:
    - 👥 Пациенты
    - 👨‍⚕️ Врачи  
    - 📅 Приемы
    - 🏥 Специализации
    - 🚪 Кабинеты
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ClinicException, clinic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(specialization_router)
app.include_router(cabinet_router)
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(appointment_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "REST-сервис 'Поликлиника'",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
