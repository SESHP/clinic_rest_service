"""
Пользовательские исключения для REST-сервиса "Поликлиника"

Все операции должны иметь защиту в виде обработки пользовательских исключений.
"""


class ClinicException(Exception):
    """Базовое исключение для всех ошибок поликлиники"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(ClinicException):
    """Исключение валидации данных"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, status_code=400)


class NotFoundException(ClinicException):
    """Исключение - объект не найден"""
    def __init__(self, entity: str, entity_id: int):
        message = f"{entity} с ID={entity_id} не найден"
        super().__init__(message, status_code=404)


class AlreadyExistsException(ClinicException):
    """Исключение - объект уже существует"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class TimeConflictException(ClinicException):
    """Исключение - конфликт времени приема"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class MaxAppointmentsExceededException(ClinicException):
    """Исключение - превышено максимальное количество приемов"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class BusinessLogicException(ClinicException):
    """Исключение бизнес-логики"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class DatabaseException(ClinicException):
    """Исключение работы с базой данных"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
