import functools
import inspect
import logging
import threading
import time

from framework.src.core.locator import Locator

call_depth_store = threading.local()


def auto_log(func):
    """Декоратор для автоматического логирования с поддержкой табуляции для отображения вложенности."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(call_depth_store, 'depth'):
            call_depth_store.depth = 0

        indent = "  " * call_depth_store.depth

        method_name = func.__name__
        driver_id = id(args[0].driver) if hasattr(args[0], 'driver') else 'unknown'
        page_name = args[0].page_name if hasattr(args[0], 'page_name') else args[0].__class__.__name__
        action = f"[Driver {driver_id}] {page_name}.{method_name}"

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        params = []
        for name, value in list(bound_args.arguments.items())[1:]:
            if hasattr(value, 'description') and isinstance(value, Locator):
                params.append(f"{value.description}")
            elif isinstance(value, str) and len(value) > 20:
                params.append(f"{name}='{value[:20]}...'")
            else:
                params.append(f"{name}={value}")

        if params:
            action += f" с {', '.join(params)}"

        logging.info(f"{indent}➡️  {action}")

        call_depth_store.depth += 1

        try:
            start_time = time.time()
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
            call_depth_store.depth -= 1

    return wrapper
