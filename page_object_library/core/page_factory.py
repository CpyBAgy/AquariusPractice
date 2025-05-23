from typing import TypeVar, Type, Dict, Any
import logging

T = TypeVar('T', bound='BasePage')


class PageFactory:
    """Фабрика для создания объектов страниц без явной передачи драйвера"""

    def __init__(self, driver, base_url=None):
        """
        Инициализация фабрики страниц

        Args:
            driver: WebDriver instance
            base_url: Базовый URL для всех страниц (опционально)
        """
        self.driver = driver
        self.base_url = base_url
        self._page_cache: Dict[str, Any] = {}
        logging.info(f"Инициализирована фабрика страниц для драйвера {id(driver)}")

    def create_page(self, page_class: Type[T], use_cache=True) -> T:
        """
        Создает экземпляр страницы

        Args:
            page_class: Класс страницы для создания
            use_cache: Использовать ли кеширование страниц

        Returns:
            Экземпляр запрошенной страницы
        """
        page_name = page_class.__name__

        # Проверяем кеш, если включено кеширование
        if use_cache and page_name in self._page_cache:
            logging.info(f"Возвращаем страницу {page_name} из кеша")
            return self._page_cache[page_name]

        # Создаем новый экземпляр страницы
        logging.info(f"Создаем новый экземпляр страницы {page_name}")

        if self.base_url:
            page = page_class(self.driver, self.base_url)
        else:
            page = page_class(self.driver)

        # Сохраняем в кеш, если включено кеширование
        if use_cache:
            self._page_cache[page_name] = page

        return page

    def clear_cache(self):
        """Очищает кеш страниц"""
        self._page_cache.clear()
        logging.info("Кеш страниц очищен")

    def get_cached_page(self, page_class: Type[T]) -> T:
        """
        Получает страницу из кеша или создает новую

        Args:
            page_class: Класс страницы

        Returns:
            Экземпляр страницы
        """
        return self.create_page(page_class, use_cache=True)

    def create_new_page(self, page_class: Type[T]) -> T:
        """
        Создает новый экземпляр страницы без использования кеша

        Args:
            page_class: Класс страницы

        Returns:
            Новый экземпляр страницы
        """
        return self.create_page(page_class, use_cache=False)


class MultiPageFactory:
    """Фабрика для работы с несколькими драйверами и их страницами"""

    def __init__(self, multi_driver_manager):
        """
        Инициализация фабрики для нескольких драйверов

        Args:
            multi_driver_manager: Экземпляр MultiDriverManager
        """
        self.multi_driver = multi_driver_manager
        self._factories: Dict[str, PageFactory] = {}

    def get_factory(self, driver_name="default") -> PageFactory:
        """
        Получает фабрику страниц для конкретного драйвера

        Args:
            driver_name: Имя драйвера

        Returns:
            PageFactory для указанного драйвера
        """
        if driver_name not in self._factories:
            driver = self.multi_driver.get_driver(driver_name)
            self._factories[driver_name] = PageFactory(driver)

        return self._factories[driver_name]

    def create_page(self, page_class: Type[T], driver_name="default") -> T:
        """
        Создает страницу для указанного драйвера

        Args:
            page_class: Класс страницы
            driver_name: Имя драйвера

        Returns:
            Экземпляр страницы
        """
        factory = self.get_factory(driver_name)
        return factory.create_page(page_class)

    def clear_all_caches(self):
        """Очищает кеш всех фабрик"""
        for factory in self._factories.values():
            factory.clear_cache()
        logging.info("Очищен кеш всех фабрик страниц")