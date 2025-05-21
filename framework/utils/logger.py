import logging
from pathlib import Path
import datetime
import sys


def setup_logger(log_level=logging.INFO, log_dir="logs", log_to_console=True, log_prefix="test"):
    """Настройка логгера для тестов"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"{log_prefix}_{timestamp}.log"

    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")
    except (PermissionError, IOError) as e:
        print(f"Ошибка при создании файла логов: {e}")
        log_file = Path(f"{log_prefix}_{timestamp}.log")

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = []

    try:
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    except Exception as e:
        print(f"Не удалось создать файловый обработчик: {e}")

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(console_handler)

    if hasattr(logging, 'basicConfig') and 'force' in logging.basicConfig.__code__.co_varnames:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format,
            handlers=handlers,
            force=True
        )
    else:

        root_logger.setLevel(log_level)
        for handler in handlers:
            root_logger.addHandler(handler)

    logging.info(f"Логирование настроено. Лог-файл: {log_file}")
    return log_file