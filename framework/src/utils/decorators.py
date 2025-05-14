import functools
import inspect
import logging
import time
from ..core.locator import Locator

# Глобальная переменная для отслеживания вложенности вызовов
call_depth = 0


def auto_log(func):
    """Декоратор для автоматического логирования с поддержкой табуляции для отображения вложенности."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global call_depth
        indent = "  " * call_depth

        class_name = args[0].__class__.__name__ if args else "Unknown"
        method_name = func.__name__

        # Собираем аргументы для лога
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        params = []
        for name, value in list(bound_args.arguments.items())[1:]:  # Пропускаем self
            if hasattr(value, 'description') and isinstance(value, Locator):
                params.append(f"{value.description}")
            elif isinstance(value, str) and len(value) > 20:
                params.append(f"{name}='{value[:20]}...'")
            else:
                params.append(f"{name}={value}")

        action = f"{class_name}.{method_name}"
        if params:
            action += f" с {', '.join(params)}"

        logging.info(f"{indent}➡️  {action}")

        call_depth += 1
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time

            if duration > 1.0:
                duration_str = f" (за {duration:.2f}с)"
            else:
                duration_str = ""

            logging.info(f"{indent}✅ {action} - успешно{duration_str}")
            return result
        except Exception as e:
            logging.error(f"{indent}❌ {action} - ошибка: {str(e)}")
            raise
        finally:
            call_depth -= 1

    return wrapper
