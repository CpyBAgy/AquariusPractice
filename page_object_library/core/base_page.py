from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import TypeVar, Type

from page_object_library.core.locator import LocatorMeta
from page_object_library.utils.decorators import auto_log
from page_object_library.core.component import BaseElement


T = TypeVar('T', bound='BasePage')
E = TypeVar('E', bound='BaseElement')


class BasePage(metaclass=LocatorMeta):
    """Базовый класс для всех страниц"""
    DEFAULT_URL = None  # Переопределяется в подклассах

    def __init__(self, driver, url=None, timeout=10, driver_name="default"):
        self.driver = driver  # Драйвер Selenium
        self.driver_name = driver_name  # Имя драйвера для логгирования
        self.url = url or self.DEFAULT_URL  # URL страницы (по умолчанию None)
        self.page_name = self.__class__.__name__  # Имя страницы (класса)
        self.wait = WebDriverWait(driver, timeout)  # Ожидание для поиска элементов
        self._init_elements()  # Инициализация элементов страницы

    def _init_elements(self):
        """Инициализирует элементы на странице.
        Переопределяется в подклассах."""
        pass

    @property
    def title(self):
        """Возвращает заголовок страницы"""
        return self.driver.title

    def _is_page_loaded(self):
        """Проверяет загружена ли страница (внутренний метод)"""
        return self.driver.execute_script("return document.readyState") == "complete"

    @auto_log
    def open(self):
        """Открывает страницу по URL"""
        if not self.url:
            raise ValueError(f"URL не задан для страницы {self.page_name}")

        self.driver.get(self.url)
        self.wait_for_page_loaded()
        return self

    @auto_log
    def wait_for_page_loaded(self):
        """Ожидание загрузки страницы с использованием лямбды"""
        try:
            self.wait.until(lambda d: self._is_page_loaded())
            return True
        except TimeoutException:
            raise TimeoutException(f"Страница {self.page_name} не загрузилась за 10 секунд")

    @auto_log
    def find_element(self, locator):
        """Находит элемент и возвращает базовый объект элемента"""
        try:
            self.wait.until(
                EC.presence_of_element_located(locator)
            )
            return BaseElement(self, locator)
        except TimeoutException:
            raise TimeoutException(f"Элемент {locator} не найден за 10 секунд")

    @auto_log
    def find_elements(self, locator):
        """Находит все элементы и возвращает список базовых объектов элементов"""
        try:
            self.wait.until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            return [BaseElement(self, locator, element=element) for element in elements]
        except TimeoutException:
            raise TimeoutException(f"Элементы {locator} не найдены за 10 секунд")

    @auto_log
    def navigate_to(self, page_class: Type[T]) -> T:
        """
        Переход на другую страницу.

        Автоматически открывает страницу, если у неё задан URL.
        Возвращает типизированный объект страницы.
        """
        new_page = page_class(self.driver, driver_name=self.driver_name)

        new_page.open()

        return new_page

    @auto_log
    def navigate_back(self):
        """Возвращается на предыдущую страницу"""
        self.driver.back()
        return self