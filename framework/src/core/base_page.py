from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from framework.src.core.locator import Locator
from framework.src.utils.decorators import auto_log


class BasePage:
    """Базовый класс для всех страниц"""

    def __init__(self, driver, base_url=None):
        self.driver = driver  # Драйвер Selenium
        self.base_url = base_url  # Базовый URL для страниц
        self.url = None  # URL страницы
        self.page_name = self.__class__.__name__  # Имя страницы (класса)
        self.wait = WebDriverWait(driver, 10)  # Ожидание для поиска элементов
        self._init_elements()  # Инициализация элементов страницы

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
    def wait_for_page_loaded(self):
        """Ожидание загрузки страницы"""
        try:
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            raise TimeoutException(f"Страница {self.page_name} не загрузилась за 10 секунд")

    @auto_log
    def find(self, locator):
        """Находит элемент с ожиданием"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"Элемент {locator} не найден за 10 секунд")

    @auto_log
    def find_all(self, locator):
        """Находит все элементы с ожиданием хотя бы одного"""
        try:
            self.wait.until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            return elements
        except TimeoutException:
            raise TimeoutException(f"Элементы {locator} не найдены за 10 секунд")

    @auto_log
    def click(self, locator_or_element):
        """Клик по элементу с ожиданием кликабельности"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.wait.until(
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
    def is_visible(self, locator):
        """Проверяет видимость элемента"""
        try:
            self.wait.until(
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

    @auto_log
    def navigate_back(self):
        """Возвращается на предыдущую страницу"""
        self.driver.back()
        return self
