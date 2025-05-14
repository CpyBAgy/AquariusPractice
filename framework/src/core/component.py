from selenium.webdriver.support.ui import WebDriverWait
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
        self.page = page  # Страница, на которой находится компонент
        self.driver = page.driver  # Драйвер Selenium
        self.root_locator = root_locator  # Локатор корневого элемента компонента
        self._root_element = root_element  # Корневой элемент компонента (если уже найден)
        self.component_name = self.__class__.__name__  # Имя компонента (класса)
        self.wait = WebDriverWait(self.driver, 10)  # Ожидание для поиска элементов
        self._init_elements()  # Инициализация элементов компонента

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
    def find(self, locator):
        """Находит элемент внутри компонента"""
        try:
            element = self.wait.until(
                lambda d: self.root.find_element(*locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"Элемент {locator} не найден в компоненте {self.component_name}")

    @auto_log
    def find_all(self, locator):
        """Находит все элементы внутри компонента"""
        try:
            self.wait.until(
                lambda d: len(self.root.find_elements(*locator)) > 0
            )
            elements = self.root.find_elements(*locator)

            return elements
        except TimeoutException:
            raise TimeoutException(f"Элементы {locator} не найдены в компоненте {self.component_name}")

    @auto_log
    def click(self, locator_or_element):
        """Клик по элементу компонента"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.find(locator_or_element)
            else:
                element = locator_or_element

            element.click()
            return True
        except Exception as e:
            raise Exception(f"Ошибка при клике в компоненте {self.component_name}: {e}")

    @auto_log
    def type(self, locator_or_element, text):
        """Ввод текста в элемент компонента"""
        try:
            if isinstance(locator_or_element, tuple) or isinstance(locator_or_element, Locator):
                element = self.find(locator_or_element)
            else:
                element = locator_or_element

            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            raise Exception(f"Ошибка при вводе текста в компоненте {self.component_name}: {e}")

    @auto_log
    def is_visible(self, locator):
        """Проверяет видимость элемента в компоненте"""
        try:
            element = self.wait.until(
                lambda d: self.root.find_element(*locator)
            )
            return element.is_displayed()
        except TimeoutException:
            return False