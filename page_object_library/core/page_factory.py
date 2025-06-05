# page_object_library/core/page_factory.py
from typing import TypeVar, Type, Dict, Any
import logging
import importlib

T = TypeVar('T', bound='BasePage')


class PageFactory:
    """Фабрика для создания объектов страниц без явной передачи драйвера"""

    def __init__(self, driver, base_url=None, driver_name="default", target_version=None):
        """
        Инициализация фабрики страниц

        Args:
            driver: WebDriver instance
            base_url: Базовый URL для всех страниц (опционально)
            driver_name: Имя драйвера для логгирования
            target_version: Целевая версия страниц (например, "v1", "v2")
        """
        self.driver = driver
        self.base_url = base_url
        self.driver_name = driver_name
        self.target_version = target_version
        self._page_cache: Dict[str, Any] = {}
        logging.info(
            f"Инициализирована фабрика страниц для драйвера '{driver_name}' с base_url: {base_url}, target_version: {target_version}")

    def create_page(self, page_class: Type[T], use_cache=True, base_url=None, version=None) -> T:
        """
        Создает экземпляр страницы

        Args:
            page_class: Класс страницы для создания
            use_cache: Использовать ли кеширование страниц
            base_url: Базовый URL для этой конкретной страницы (переопределяет фабричный)
            version: Версия страницы (переопределяет target_version фабрики)

        Returns:
            Экземпляр запрошенной страницы
        """
        effective_version = version or self.target_version

        versioned_page_class = self._get_versioned_class(page_class, effective_version)

        page_name = versioned_page_class.__name__
        effective_base_url = base_url or self.base_url

        cache_key = f"{page_name}_{effective_base_url}_{effective_version}" if effective_base_url or effective_version else page_name

        if use_cache and cache_key in self._page_cache:
            logging.info(f"Возвращаем страницу {page_name} из кеша")
            return self._page_cache[cache_key]

        logging.info(
            f"Создаем новый экземпляр страницы {page_name} с base_url: {effective_base_url}, version: {effective_version}")

        if effective_base_url:
            page = versioned_page_class(self.driver, base_url=effective_base_url, driver_name=self.driver_name)
        else:
            page = versioned_page_class(self.driver, driver_name=self.driver_name)

        if use_cache:
            self._page_cache[cache_key] = page

        return page

    def _get_versioned_class(self, page_class: Type[T], version: str) -> Type[T]:
        """
        Получает версионный класс страницы

        Args:
            page_class: Базовый класс страницы
            version: Требуемая версия (например, "v1", "v2")

        Returns:
            Версионный класс страницы
        """
        if not version:
            return page_class

        original_class_name = page_class.__name__

        if self._is_already_target_version(original_class_name, version):
            return page_class

        base_class_name = self._extract_base_class_name(original_class_name)

        versioned_class = self._try_find_versioned_class(page_class, base_class_name, version)

        if versioned_class:
            return versioned_class

        logging.warning(
            f"Версионный класс для {original_class_name} версии {version} не найден, используем оригинальный класс")
        return page_class

    def _is_already_target_version(self, class_name: str, version: str) -> bool:
        """Проверяет, является ли класс уже нужной версии"""
        return class_name.endswith(f"V{version.upper()}")

    def _extract_base_class_name(self, class_name: str) -> str:
        """Извлекает базовое имя класса без версии"""
        for v in ["V1", "V2", "V3"]:
            if class_name.endswith(v):
                return class_name[:-2]
        return class_name

    def _try_find_versioned_class(self, page_class: Type[T], base_class_name: str, version: str) -> Type[T]:
        """Пытается найти версионный класс в соответствующем модуле"""
        original_module = page_class.__module__

        versioned_module_name = self._build_versioned_module_path(original_module, version)

        if versioned_module_name:
            versioned_class = self._import_versioned_class(versioned_module_name, base_class_name, version)
            if versioned_class:
                return versioned_class

        return self._try_find_in_current_module(original_module, base_class_name, version)

    def _build_versioned_module_path(self, original_module: str, version: str) -> str:
        """Строит путь к версионному модулю"""
        module_parts = original_module.split('.')

        if len(module_parts) < 3:
            return None

        if self._has_version_in_path(module_parts):
            return self._replace_existing_version(module_parts, version)
        else:
            return self._add_version_to_path(module_parts, version)

    def _has_version_in_path(self, module_parts: list) -> bool:
        """Проверяет, есть ли версия в пути модуля"""
        return any(part.startswith('v') and part[1:].isdigit() for part in module_parts)

    def _replace_existing_version(self, module_parts: list, version: str) -> str:
        """Заменяет существующую версию в пути модуля"""
        new_module_parts = []
        for part in module_parts:
            if part.startswith('v') and part[1:].isdigit():
                new_module_parts.append(version)
            elif part.startswith('pages_v') or part.startswith('components_v'):
                base_name = part.split('_v')[0]
                new_module_parts.append(f"{base_name}_{version}")
            else:
                new_module_parts.append(part)
        return '.'.join(new_module_parts)

    def _add_version_to_path(self, module_parts: list, version: str) -> str:
        """Добавляет версию в путь модуля"""
        if module_parts[-1] in ['pages', 'components']:
            versioned_parts = module_parts[:-1] + [version] + [f"{module_parts[-1]}_{version}"]
        else:
            versioned_parts = module_parts[:-1] + [version] + [module_parts[-1]]
        return '.'.join(versioned_parts)

    def _import_versioned_class(self, module_name: str, base_class_name: str, version: str) -> Type[T]:
        """Импортирует версионный класс из модуля"""
        try:
            versioned_module = importlib.import_module(module_name)
            versioned_class_name = f"{base_class_name}V{version.upper()}"

            if hasattr(versioned_module, versioned_class_name):
                versioned_class = getattr(versioned_module, versioned_class_name)
                logging.info(f"Найден версионный класс {versioned_class_name} в модуле {module_name}")
                return versioned_class
            else:
                logging.warning(f"Класс {versioned_class_name} не найден в модуле {module_name}")
        except ImportError as e:
            logging.warning(f"Не удалось импортировать модуль {module_name}: {e}")
        return None

    def _try_find_in_current_module(self, original_module: str, base_class_name: str, version: str) -> Type[T]:
        """Пытается найти версионный класс в текущем модуле"""
        try:
            current_module = importlib.import_module(original_module)
            versioned_class_name = f"{base_class_name}V{version.upper()}"

            if hasattr(current_module, versioned_class_name):
                versioned_class = getattr(current_module, versioned_class_name)
                logging.info(f"Найден версионный класс {versioned_class_name} в текущем модуле")
                return versioned_class
        except ImportError:
            pass
        return None

    def clear_cache(self):
        """Очищает кеш страниц"""
        self._page_cache.clear()
        logging.info("Кеш страниц очищен")

    def get_cached_page(self, page_class: Type[T], base_url=None, version=None) -> T:
        """
        Получает страницу из кеша или создает новую

        Args:
            page_class: Класс страницы
            base_url: Базовый URL для страницы
            version: Версия страницы

        Returns:
            Экземпляр страницы
        """
        return self.create_page(page_class, use_cache=True, base_url=base_url, version=version)

    def create_new_page(self, page_class: Type[T], base_url=None, version=None) -> T:
        """
        Создает новый экземпляр страницы без использования кеша

        Args:
            page_class: Класс страницы
            base_url: Базовый URL для страницы
            version: Версия страницы

        Returns:
            Новый экземпляр страницы
        """
        return self.create_page(page_class, use_cache=False, base_url=base_url, version=version)


class MultiPageFactory:
    """Фабрика для работы с несколькими драйверами и их страницами"""

    def __init__(self, multi_driver_manager, default_browser_type="chrome", default_headless=False,
                 default_base_url=None, default_target_version=None):
        """
        Инициализация фабрики для нескольких драйверов

        Args:
            multi_driver_manager: Экземпляр MultiDriverManager
            default_browser_type: Тип браузера по умолчанию для автоматического создания
            default_headless: Режим headless по умолчанию для автоматического создания
            default_base_url: Базовый URL по умолчанию для всех драйверов
            default_target_version: Целевая версия страниц по умолчанию
        """
        self.multi_driver = multi_driver_manager
        self.default_browser_type = default_browser_type
        self.default_headless = default_headless
        self.default_base_url = default_base_url
        self.default_target_version = default_target_version
        self._factories: Dict[str, PageFactory] = {}

    def get_factory(self, driver_name="default", browser_type=None, headless=None, base_url=None,
                    target_version=None) -> PageFactory:
        """
        Получает фабрику страниц для конкретного драйвера, создавая его при необходимости

        Args:
            driver_name: Имя драйвера
            browser_type: Тип браузера (если нужно создать новый драйвер)
            headless: Режим headless (если нужно создать новый драйвер)
            base_url: Базовый URL для этой фабрики
            target_version: Целевая версия страниц для этой фабрики

        Returns:
            PageFactory для указанного драйвера
        """
        effective_base_url = base_url or self.default_base_url
        effective_target_version = target_version or self.default_target_version
        factory_key = f"{driver_name}_{effective_base_url}_{effective_target_version}"

        if factory_key not in self._factories:
            browser_type = browser_type or self.default_browser_type
            headless = headless if headless is not None else self.default_headless

            driver = self.multi_driver.get_or_create_driver(driver_name, browser_type, headless)
            self._factories[factory_key] = PageFactory(
                driver,
                base_url=effective_base_url,
                driver_name=driver_name,
                target_version=effective_target_version
            )

        return self._factories[factory_key]

    def create_page(self, page_class: Type[T], driver_name="default", browser_type=None, headless=None, base_url=None,
                    target_version=None, version=None) -> T:
        """
        Создает страницу для указанного драйвера, автоматически создавая драйвер при необходимости

        Args:
            page_class: Класс страницы
            driver_name: Имя драйвера
            browser_type: Тип браузера (если нужно создать новый драйвер)
            headless: Режим headless (если нужно создать новый драйвер)
            base_url: Базовый URL для страницы
            target_version: Целевая версия страниц для фабрики
            version: Версия конкретной страницы (переопределяет target_version)

        Returns:
            Экземпляр страницы
        """
        factory = self.get_factory(driver_name, browser_type, headless, base_url, target_version)
        return factory.create_page(page_class, version=version)

    def clear_all_caches(self):
        """Очищает кеш всех фабрик"""
        for factory in self._factories.values():
            factory.clear_cache()
        logging.info("Очищен кеш всех фабрик страниц")