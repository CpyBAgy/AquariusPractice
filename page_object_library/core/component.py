from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from page_object_library.core.locator import LocatorMeta
from page_object_library.utils.decorators import auto_log


class BaseElement:
    """Базовый класс для элементов страницы"""

    def __init__(self, page, locator, element=None):
        self.page = page
        self.driver = page.driver
        self.locator = locator
        self._element = element  # Можно передать уже найденный элемент
        self.wait = WebDriverWait(self.driver, 10)

    @property
    def element(self):
        """Получает элемент"""
        if self._element is None:
            try:
                self._element = self.wait.until(
                    EC.presence_of_element_located(self.locator)
                )
            except TimeoutException:
                raise TimeoutException(f"Элемент {self.locator} не найден за 10 секунд")
        return self._element

    @auto_log
    def is_visible(self):
        """Проверяет видимость элемента"""
        try:
            self.wait.until(
                EC.visibility_of_element_located(self.locator)
            )
            return True
        except TimeoutException:
            return False

    @auto_log
    def is_present(self):
        """Проверяет наличие элемента"""
        try:
            self.element()
            return True
        except TimeoutException:
            return False

    @auto_log
    def click(self):
        """Базовый метод клика для всех элементов"""
        try:
            clickable_element = self.wait.until(
                EC.element_to_be_clickable(self.locator)
            )
            clickable_element.click()
            return self.page
        except Exception as e:
            raise Exception(f"Ошибка при клике: {e}")

    @auto_log
    def get_text(self):
        """Получает текст элемента"""
        return self.element.text

    @auto_log
    def get_attribute(self, name):
        """Получает атрибут элемента"""
        return self.element.get_attribute(name)


class Button(BaseElement):
    """Кнопка"""

    @auto_log
    def is_enabled(self):
        """Проверяет, активна ли кнопка"""
        return self.element.is_enabled()


class Input(BaseElement):
    """Поле ввода"""

    @auto_log
    def type(self, text):
        """Вводит текст в поле"""
        try:
            self.element.clear()
            self.element.send_keys(text)
            return self.page
        except Exception as e:
            raise Exception(f"Ошибка при вводе текста: {e}")

    @auto_log
    def clear(self):
        """Очищает поле"""
        self.element.clear()
        return self.page

    @auto_log
    def get_value(self):
        """Получает значение поля"""
        return self.element.get_attribute("value")


class Checkbox(BaseElement):
    """Чекбокс"""

    @auto_log
    def check(self):
        """Отмечает чекбокс"""
        if not self.is_checked():
            self.click()
        return self.page

    @auto_log
    def uncheck(self):
        """Снимает отметку с чекбокса"""
        if self.is_checked():
            self.click()
        return self.page

    @auto_log
    def is_checked(self):
        """Проверяет, отмечен ли чекбокс"""
        return self.element.is_selected()


class Radio(BaseElement):
    """Радиокнопка"""

    @auto_log
    def select(self):
        """Выбирает радиокнопку"""
        if not self.is_selected():
            self.click()
        return self.page

    @auto_log
    def is_selected(self):
        """Проверяет, выбрана ли радиокнопка"""
        return self.element.is_selected()


class Dropdown(BaseElement):
    """Выпадающий список"""

    @auto_log
    def select_by_text(self, text):
        """Выбирает элемент по видимому тексту"""
        select = Select(self.element)
        select.select_by_visible_text(text)
        return self.page

    @auto_log
    def select_by_index(self, index):
        """Выбирает элемент по индексу"""
        select = Select(self.element)
        select.select_by_index(index)
        return self.page

    @auto_log
    def get_selected_option(self):
        """Получает выбранный элемент"""
        select = Select(self.element)
        return select.first_selected_option


class Link(BaseElement):
    """Ссылка"""

    @auto_log
    def get_url(self):
        """Получает URL ссылки"""
        return self.element.get_attribute("href")


class ElementGroup(metaclass=LocatorMeta):
    """Базовый класс для групп элементов на странице"""

    def __init__(self, page, timeout=10):
        """
        Инициализация группы элементов.

        Args:
            page: Страница, на которой находится группа элементов
        """
        self.page = page
        self.driver = page.driver
        self.wait = WebDriverWait(self.driver, timeout)
        self.group_name = self.__class__.__name__
        self._init_elements()

    def _init_elements(self):
        """
        Инициализирует элементы группы.
        Переопределяется в подклассах для создания элементов.
        """
        pass

    @auto_log
    def wait_for_page_loaded(self):
        """Ожидание загрузки страницы"""
        return self.page.wait_for_page_loaded()
