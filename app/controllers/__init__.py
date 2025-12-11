"""
Модуль контроллеров (REST API endpoints)
"""

from .patient_controller import router as patient_router
from .doctor_controller import router as doctor_router
from .appointment_controller import router as appointment_router

__all__ = [
    "patient_router",
    "doctor_router",
    "appointment_router"
]
