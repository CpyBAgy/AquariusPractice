import logging
from pathlib import Path
import datetime


def setup_logger(log_level=logging.INFO, log_dir="logs", log_to_console=True, log_prefix="test"):
    """Настройка логгера для тестов"""
    # Создаем директорию для логов, если она не существует
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Формируем имя лог-файла с датой и временем
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"{log_prefix}_{timestamp}.log"

    # Настройка формата логов
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Создаем список обработчиков логов
    handlers = []

    # Файловый обработчик
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(file_handler)

    # Консольный обработчик, если включено логирование в консоль
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(console_handler)

    # Настройка корневого логгера
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )

    logging.info(f"Логирование настроено. Лог-файл: {log_file}")
    return log_file