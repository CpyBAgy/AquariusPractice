import functools
import inspect
import logging
import threading
import time
from typing import Any, Callable

from page_object_library.core.locator import Locator

# Хранилище для глубины вызовов
call_depth_store = threading.local()

# Словарь с описаниями действий для методов
METHOD_DESCRIPTIONS = {
    # BasePage методы
    "open": "Открытие страницы",
    "wait_for_page_loaded": "Ожидание загрузки страницы",
    "find": "Поиск элемента",
    "navigate_to": "Переход на страницу",
    "navigate_back": "Возврат на предыдущую страницу",

    # BaseElement методы
    "click": "Клик по элементу",
    "type": "Ввод текста в элемент",
    "clear": "Очистка текста в элементе",
    "get_text": "Получение текста элемента",
    "get_attribute": "Получение атрибута элемента",
    "is_visible": "Проверка видимости элемента",
    "is_present": "Проверка наличия элемента",
    "find_child": "Поиск дочернего элемента",
    "find_children": "Поиск дочерних элементов",

    # Button методы
    "is_enabled": "Проверка активности кнопки",

    # Checkbox методы
    "check": "Отметка чекбокса",
    "uncheck": "Снятие отметки с чекбокса",
    "is_checked": "Проверка отметки чекбокса",

    # Radio методы
    "select": "Выбор радиокнопки",
    "is_selected": "Проверка выбора радиокнопки",

    # Dropdown методы
    "select_by_text": "Выбор элемента по тексту",
    "select_by_index": "Выбор элемента по индексу",
    "get_selected_option": "Получение выбранного элемента",

    # Link методы
    "get_url": "Получение URL ссылки",

    # Компонентные методы
    "login": "Выполнение входа",
    "search": "Поиск",
    "select_product": "Выбор продукта",
    "add_to_cart": "Добавление в корзину",
    "increase_quantity": "Увеличение количества",
    "decrease_quantity": "Уменьшение количества",
    "delete": "Удаление элемента",
    "get_title": "Получение заголовка",
    "get_price": "Получение цены",
    "get_subtotal": "Получение промежуточной суммы",
    "proceed_to_checkout": "Переход к оформлению заказа",
}


def get_method_description(method_name: str) -> str:
    """Получает описание метода из словаря или возвращает имя метода, если описание не найдено"""
    return METHOD_DESCRIPTIONS.get(method_name, f"Вызов метода {method_name}")


def format_param_value(name: str, value: Any) -> str:
    """Форматирует значение параметра для логирования"""
    # Если это локатор из Locator dataclass
    if hasattr(value, 'description') and isinstance(value, Locator):
        return f"{value.description}"

    # Если это кортеж локатора
    if isinstance(value, tuple) and len(value) == 2:
        # Пытаемся определить тип элемента по локатору
        locator_type, locator_value = value
        if isinstance(locator_value, str):
            if 'button' in locator_value.lower() or 'btn' in locator_value.lower():
                return f"кнопка ({locator_type}: {locator_value})"
            elif 'input' in locator_value.lower() or 'field' in locator_value.lower():
                return f"поле ввода ({locator_type}: {locator_value})"
            else:
                return f"элемент ({locator_type}: {locator_value})"
        return f"элемент {value}"

    if isinstance(value, str):
        if name == "text" or name == "search_text":
            return f'"{value[:20]}{"..." if len(value) > 20 else ""}"'
        elif name == "description":
            return None  # Не выводим description как параметр
        elif len(value) > 40:
            return f'"{value[:37]}..."'
        else:
            return f'"{value}"'

    if hasattr(value, '__class__') and hasattr(value, 'locator') and hasattr(value, 'page'):
        # Это объект элемента
        if hasattr(value, 'description') and value.description:
            return f"{value.description}"
        elif hasattr(value.locator, 'description'):
            return f"{value.locator.description}"
        else:
            return f"элемент {value.__class__.__name__}"

    if inspect.isclass(value) and 'Page' in value.__name__:
        return f"{value.__name__}"

    return f"{value}"


def auto_log(func: Callable) -> Callable:
    """Декоратор для автоматического логирования с человеко-читаемыми сообщениями"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(call_depth_store, 'depth'):
            call_depth_store.depth = 0

        indent = "  " * call_depth_store.depth

        method_name = func.__name__

        obj = args[0]

        # Получаем имя драйвера вместо ID
        if hasattr(obj, 'driver_name'):
            driver_identifier = obj.driver_name
        else:
            driver_identifier = f"#{id(obj.driver)}" if hasattr(obj, 'driver') else 'unknown'

        if hasattr(obj, 'page_name'):
            object_name = obj.page_name
        elif hasattr(obj, 'group_name'):
            object_name = obj.group_name
        else:
            object_name = obj.__class__.__name__

        action_description = get_method_description(method_name)

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        params = []
        element_description = None

        # Проверяем, есть ли у самого объекта описание (для BaseElement и его наследников)
        if hasattr(obj, 'description') and obj.description:
            element_description = obj.description

        for name, value in list(bound_args.arguments.items())[1:]:
            if name == "description":
                continue  # Пропускаем параметр description
            formatted_value = format_param_value(name, value)
            if formatted_value is None:
                continue
            if name == "locator" or name == "element_type" or name == "multiple":
                if name == "locator" and formatted_value:
                    params.append(f"{formatted_value}")
                elif name == "element_type" and value is not None:
                    params.append(f"как {value.__name__}")
                elif name == "multiple" and value:
                    params.append("множественный")
            else:
                params.append(f"{name}={formatted_value}")

        prefix = f"[Driver {driver_identifier}] {object_name}"

        # Используем описание элемента, если оно есть
        if element_description and method_name in ["click", "type", "get_text", "is_visible", "is_present"]:
            action = f"{action_description} - {element_description}"
        else:
            action = f"{action_description}"

        if params:
            log_message = f"{prefix}: {action} ({', '.join(params)})"
        else:
            log_message = f"{prefix}: {action}"

        logging.info(f"{indent}➡️  {log_message}")

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

            logging.info(f"{indent}✅ {log_message} - успешно{duration_str}")

            return result
        except Exception as e:
            logging.error(f"{indent}❌ {log_message} - ошибка: {str(e)}")
            raise
        finally:
            call_depth_store.depth -= 1

    return wrapper