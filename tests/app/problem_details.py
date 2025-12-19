"""
Problem Details (RFC 7807)
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.exceptions import ClinicException

logger = logging.getLogger(__name__)


def create_problem_details(title: str, status_code: int, detail: str, instance: str = None, **kwargs):
    problem = {
        "type": f"https://api.clinic.ru/problems/{status_code}",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if instance:
        problem["instance"] = instance
    problem.update(kwargs)
    return problem


async def clinic_exception_handler(request: Request, exc: ClinicException):
    logger.error(f"ClinicException: {exc.message}")
    problem = create_problem_details(
        title=type(exc).__name__.replace("Exception", " Error"),
        status_code=exc.status_code,
        detail=exc.message,
        instance=str(request.url)
    )
    return JSONResponse(status_code=exc.status_code, content=problem)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.setdefault(field, []).append(error["msg"])
    
    problem = create_problem_details(
        title="Ошибка валидации",
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Проверьте правильность заполнения полей",
        instance=str(request.url),
        errors=errors
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem)


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    problem = create_problem_details(
        title="Внутренняя ошибка сервера",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Произошла непредвиденная ошибка",
        instance=str(request.url)
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=problem)
