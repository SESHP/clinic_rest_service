"""
Модуль контроллеров (REST API endpoints)
"""

from .patient_controller import router as patient_router
from .doctor_controller import router as doctor_router
from .appointment_controller import router as appointment_router
from .specialization_controller import router as specialization_router
from .cabinet_controller import router as cabinet_router

__all__ = [
    "patient_router",
    "doctor_router",
    "appointment_router",
    "specialization_router",
    "cabinet_router"
]
