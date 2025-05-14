from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from framework.src.core.locator import Locator
from framework.src.utils.decorators import auto_log


class Component:
    """Базовый класс для компонентов страницы (регионов)"""

    def __init__(self, page, root_locator=None, root_element=None):
        """
        Инициализация компонента.

        :param page: Страница, на которой находится компонент
        :param root_locator: Локатор корневого элемента компонента
        :param root_element: Корневой элемент компонента (если уже найден)
        """
        self.page = page
        self.driver = page.driver
        self.root_locator = root_locator
        self._root_element = root_element
        self.component_name = self.__class__.__name__
        self._init_elements()

    def _init_elements(self):
        """Инициализирует элементы компонента.
        Переопределяется в подклассах."""
        pass

    @property
    def root(self):
        """Получает корневой элемент компонента"""
        if self._root_element is None and self.root_locator is not None:
            self._root_element = self.page.find(self.root_locator)
        return self._root_element

    @auto_log
    def find(self, locator, timeout=10):
        """Находит элемент внутри компонента"""
        try:
            if self.root is not None:
                # Поиск относительно корневого элемента
                element = WebDriverWait(self.driver, timeout).until(
                    lambda d: self.root.find_element(*locator)
                )
            else:
                # Поиск относительно всей страницы
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
            return element
        except TimeoutException:
            raise TimeoutException(f"Элемент {locator} не найден в компоненте {self.component_name}")

    @auto_log
    def find_all(self, locator, timeout=10):
        """Находит все элементы внутри компонента"""
        try:
            if self.root is not None:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(self.root.find_elements(*locator)) > 0
                )
                elements = self.root.find_elements(*locator)
            else:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                elements = self.driver.find_elements(*locator)

            return elements
        except TimeoutException:
            raise TimeoutException(f"Элементы {locator} не найдены в компоненте {self.component_name}")

    @auto_log
    def click(self, locator_or_element, timeout=10):
        """Клик по элементу компонента"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.find(locator_or_element, timeout)
            else:
                element = locator_or_element

            element.click()
            return True
        except Exception as e:
            raise Exception(f"Ошибка при клике в компоненте {self.component_name}: {e}")

    @auto_log
    def type(self, locator_or_element, text, timeout=10):
        """Ввод текста в элемент компонента"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.find(locator_or_element, timeout)
            else:
                element = locator_or_element

            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            raise Exception(f"Ошибка при вводе текста в компоненте {self.component_name}: {e}")

    @auto_log
    def is_visible(self, locator, timeout=10):
        """Проверяет видимость элемента в компоненте"""
        try:
            if self.root is not None:
                element = WebDriverWait(self.driver, timeout).until(
                    lambda d: self.root.find_element(*locator)
                )
                return element.is_displayed()
            else:
                return WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(locator)
                )
        except TimeoutException:
            return False