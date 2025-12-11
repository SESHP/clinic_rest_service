"""
Конфигурация логирования

В случае возникновения исключительного события должен формироваться лог
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(log_file: str = "logs/app.log", log_level: str = "INFO"):
    """
    Настройка логирования для приложения
    
    Логи записываются как в файл, так и в консоль
    """
    # Создаем директорию для логов если её нет
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Настройка формата логов
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для записи в файл (с ротацией)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Уменьшаем verbose логов от сторонних библиотек
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info("=" * 80)
    logging.info(f"Логирование настроено. Файл: {log_file}, Уровень: {log_level}")
    logging.info("=" * 80)


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Логирование исключения с контекстом
    
    Args:
        logger: Объект логгера
        exception: Исключение для логирования
        context: Дополнительный контекст ошибки
    """
    error_msg = f"{context} | {type(exception).__name__}: {str(exception)}" if context else f"{type(exception).__name__}: {str(exception)}"
    logger.error(error_msg, exc_info=True)
