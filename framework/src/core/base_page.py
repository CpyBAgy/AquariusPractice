from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from framework.src.core.locator import Locator
from framework.src.utils.decorators import auto_log


class BasePage:
    """Базовый класс для всех страниц"""

    def __init__(self, driver, base_url=None):
        self.driver = driver
        self.base_url = base_url
        self.url = None
        self.page_name = self.__class__.__name__
        self.wait = WebDriverWait(driver, 10)
        self._init_elements()

    def _init_elements(self):
        """Инициализирует элементы на странице.
        Переопределяется в подклассах."""
        pass

    @property
    def title(self):
        """Возвращает заголовок страницы"""
        return self.driver.title

    @auto_log
    def open(self):
        """Открывает страницу по URL"""
        if self.url:
            full_url = self.url
            if self.base_url and not self.url.startswith(('http://', 'https://')):
                full_url = f"{self.base_url.rstrip('/')}/{self.url.lstrip('/')}"

            self.driver.get(full_url)
            self.wait_for_page_loaded()
            return self
        else:
            raise ValueError(f"URL не задан для страницы {self.page_name}")

    @auto_log
    def wait_for_page_loaded(self, timeout=30):
        """Ожидание загрузки страницы"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            raise TimeoutException(f"Страница {self.page_name} не загрузилась за {timeout} секунд")

    @auto_log
    def find(self, locator, timeout=10):
        """Находит элемент с ожиданием"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"Элемент {locator} не найден за {timeout} секунд")

    @auto_log
    def find_all(self, locator, timeout=10):
        """Находит все элементы с ожиданием хотя бы одного"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            return elements
        except TimeoutException:
            raise TimeoutException(f"Элементы {locator} не найдены за {timeout} секунд")

    @auto_log
    def click(self, locator_or_element, timeout=10):
        """Клик по элементу с ожиданием кликабельности"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(locator_or_element)
                )
            else:
                element = locator_or_element

            element.click()
            return True
        except Exception as e:
            raise Exception(f"Ошибка при клике: {e}")

    @auto_log
    def type(self, locator_or_element, text, timeout=10):
        """Ввод текста в элемент"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.find(locator_or_element, timeout)
            else:
                element = locator_or_element

            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            raise Exception(f"Ошибка при вводе текста: {e}")

    @auto_log
    def is_visible(self, locator, timeout=10):
        """Проверяет видимость элемента"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    @auto_log
    def is_element_present(self, locator, timeout=1):
        """Проверяет наличие элемента на странице"""
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    @auto_log
    def navigate_to(self, page_class, *args, **kwargs):
        """Переход на другую страницу"""
        new_page = page_class(self.driver, *args, **kwargs)
        return new_page
