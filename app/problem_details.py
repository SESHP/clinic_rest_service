"""
Problem Details для стандартизированного вывода ошибок

Согласно RFC 7807 и требованиям курсовой работы:
"Вывод на экран в случае ошибки должен быть оформлен в виде Problem Details"
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Dict, Any
import logging

from app.exceptions import ClinicException

logger = logging.getLogger(__name__)


def create_problem_details(
    title: str,
    status_code: int,
    detail: str,
    instance: str = None,
    type_uri: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Создание Problem Details согласно RFC 7807
    
    Args:
        title: Краткое описание проблемы
        status_code: HTTP статус код
        detail: Подробное описание проблемы
        instance: URI экземпляра проблемы
        type_uri: URI типа проблемы
        **kwargs: Дополнительные поля
    
    Returns:
        Словарь с Problem Details
    """
    problem = {
        "type": type_uri or f"https://api.clinic.ru/problems/{status_code}",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    
    if instance:
        problem["instance"] = instance
    
    # Добавляем дополнительные поля
    problem.update(kwargs)
    
    return problem


async def clinic_exception_handler(request: Request, exc: ClinicException):
    """
    Обработчик пользовательских исключений ClinicException
    
    Формирует ответ в формате Problem Details
    """
    logger.error(f"ClinicException: {exc.message}")
    
    problem = create_problem_details(
        title=type(exc).__name__.replace("Exception", " Error"),
        status_code=exc.status_code,
        detail=exc.message,
        instance=str(request.url)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=problem
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации Pydantic
    
    Преобразует ошибки валидации в Problem Details
    """
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Форматируем ошибки валидации
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        message = error["msg"]
        
        if field in errors:
            errors[field].append(message)
        else:
            errors[field] = [message]
    
    problem = create_problem_details(
        title="Ошибка валидации данных",
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Переданные данные не прошли валидацию. Проверьте правильность заполнения полей.",
        instance=str(request.url),
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=problem
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Обработчик всех остальных исключений
    
    Логирует ошибку и возвращает стандартный Problem Details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    problem = create_problem_details(
        title="Внутренняя ошибка сервера",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.",
        instance=str(request.url)
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem
    )
