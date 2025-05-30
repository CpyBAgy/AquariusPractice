from typing import TypeVar, Type, Dict, Any
import logging

T = TypeVar('T', bound='BasePage')


class PageFactory:
    """Фабрика для создания объектов страниц без явной передачи драйвера"""

    def __init__(self, driver, base_url=None, driver_name="default"):
        """
        Инициализация фабрики страниц

        Args:
            driver: WebDriver instance
            base_url: Базовый URL для всех страниц (опционально)
            driver_name: Имя драйвера для логгирования
        """
        self.driver = driver
        self.base_url = base_url
        self.driver_name = driver_name
        self._page_cache: Dict[str, Any] = {}
        logging.info(f"Инициализирована фабрика страниц для драйвера '{driver_name}' с base_url: {base_url}")

    def create_page(self, page_class: Type[T], use_cache=True, base_url=None) -> T:
        """
        Создает экземпляр страницы

        Args:
            page_class: Класс страницы для создания
            use_cache: Использовать ли кеширование страниц
            base_url: Базовый URL для этой конкретной страницы (переопределяет фабричный)

        Returns:
            Экземпляр запрошенной страницы
        """
        page_name = page_class.__name__
        effective_base_url = base_url or self.base_url

        # Ключ кеша должен учитывать base_url
        cache_key = f"{page_name}_{effective_base_url}" if effective_base_url else page_name

        # Проверяем кеш, если включено кеширование
        if use_cache and cache_key in self._page_cache:
            logging.info(f"Возвращаем страницу {page_name} из кеша")
            return self._page_cache[cache_key]

        # Создаем новый экземпляр страницы
        logging.info(f"Создаем новый экземпляр страницы {page_name} с base_url: {effective_base_url}")

        if effective_base_url:
            page = page_class(self.driver, base_url=effective_base_url, driver_name=self.driver_name)
        else:
            page = page_class(self.driver, driver_name=self.driver_name)

        # Сохраняем в кеш, если включено кеширование
        if use_cache:
            self._page_cache[cache_key] = page

        return page

    def clear_cache(self):
        """Очищает кеш страниц"""
        self._page_cache.clear()
        logging.info("Кеш страниц очищен")

    def get_cached_page(self, page_class: Type[T], base_url=None) -> T:
        """
        Получает страницу из кеша или создает новую

        Args:
            page_class: Класс страницы
            base_url: Базовый URL для страницы

        Returns:
            Экземпляр страницы
        """
        return self.create_page(page_class, use_cache=True, base_url=base_url)

    def create_new_page(self, page_class: Type[T], base_url=None) -> T:
        """
        Создает новый экземпляр страницы без использования кеша

        Args:
            page_class: Класс страницы
            base_url: Базовый URL для страницы

        Returns:
            Новый экземпляр страницы
        """
        return self.create_page(page_class, use_cache=False, base_url=base_url)


class MultiPageFactory:
    """Фабрика для работы с несколькими драйверами и их страницами"""

    def __init__(self, multi_driver_manager, default_browser_type="chrome", default_headless=False, default_base_url=None):
        """
        Инициализация фабрики для нескольких драйверов

        Args:
            multi_driver_manager: Экземпляр MultiDriverManager
            default_browser_type: Тип браузера по умолчанию для автоматического создания
            default_headless: Режим headless по умолчанию для автоматического создания
            default_base_url: Базовый URL по умолчанию для всех драйверов
        """
        self.multi_driver = multi_driver_manager
        self.default_browser_type = default_browser_type
        self.default_headless = default_headless
        self.default_base_url = default_base_url
        self._factories: Dict[str, PageFactory] = {}

    def get_factory(self, driver_name="default", browser_type=None, headless=None, base_url=None) -> PageFactory:
        """
        Получает фабрику страниц для конкретного драйвера, создавая его при необходимости

        Args:
            driver_name: Имя драйвера
            browser_type: Тип браузера (если нужно создать новый драйвер)
            headless: Режим headless (если нужно создать новый драйвер)
            base_url: Базовый URL для этой фабрики

        Returns:
            PageFactory для указанного драйвера
        """
        effective_base_url = base_url or self.default_base_url
        factory_key = f"{driver_name}_{effective_base_url}" if effective_base_url else driver_name

        if factory_key not in self._factories:
            browser_type = browser_type or self.default_browser_type
            headless = headless if headless is not None else self.default_headless

            driver = self.multi_driver.get_or_create_driver(driver_name, browser_type, headless)
            self._factories[factory_key] = PageFactory(driver, base_url=effective_base_url, driver_name=driver_name)

        return self._factories[factory_key]

    def create_page(self, page_class: Type[T], driver_name="default", browser_type=None, headless=None, base_url=None) -> T:
        """
        Создает страницу для указанного драйвера, автоматически создавая драйвер при необходимости

        Args:
            page_class: Класс страницы
            driver_name: Имя драйвера
            browser_type: Тип браузера (если нужно создать новый драйвер)
            headless: Режим headless (если нужно создать новый драйвер)
            base_url: Базовый URL для страницы

        Returns:
            Экземпляр страницы
        """
        factory = self.get_factory(driver_name, browser_type, headless, base_url)
        return factory.create_page(page_class)

    def clear_all_caches(self):
        """Очищает кеш всех фабрик"""
        for factory in self._factories.values():
            factory.clear_cache()
        logging.info("Очищен кеш всех фабрик страниц")