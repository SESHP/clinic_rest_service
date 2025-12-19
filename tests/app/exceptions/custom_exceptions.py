"""
Пользовательские исключения для REST-сервиса "Поликлиника"
"""


class ClinicException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(ClinicException):
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, status_code=400)


class NotFoundException(ClinicException):
    def __init__(self, entity: str, entity_id):
        message = f"{entity} с ID={entity_id} не найден"
        super().__init__(message, status_code=404)


class AlreadyExistsException(ClinicException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class TimeConflictException(ClinicException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class MaxAppointmentsExceededException(ClinicException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class BusinessLogicException(ClinicException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class DatabaseException(ClinicException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
