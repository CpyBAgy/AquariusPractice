from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

from framework.src.utils.decorators import auto_log


class BaseElement:
    """Базовый класс для элементов страницы"""

    def __init__(self, page, locator):
        self.page = page
        self.driver = page.driver
        self.locator = locator
        self.wait = WebDriverWait(self.driver, 10)

    @property
    def element(self):
        """Получает элемент"""
        return self.page.find(self.locator)

    def is_visible(self):
        """Проверяет видимость элемента"""
        return self.page.is_element_visible(self.locator)

    def is_present(self):
        """Проверяет наличие элемента"""
        return self.page.is_element_present(self.locator)


class Button(BaseElement):
    """Кнопка"""

    def click(self):
        """Кликает по кнопке"""
        self.page.click(self.locator)
        return self.page

    def is_enabled(self):
        """Проверяет, активна ли кнопка"""
        return self.element.is_enabled()

    def get_text(self):
        """Получает текст кнопки"""
        return self.element.text


class Input(BaseElement):
    """Поле ввода"""

    def type(self, text):
        """Вводит текст в поле"""
        self.page.type(self.locator, text)
        return self.page

    def clear(self):
        """Очищает поле"""
        self.element.clear()
        return self.page

    def get_value(self):
        """Получает значение поля"""
        return self.element.get_attribute("value")


class Checkbox(BaseElement):
    """Чекбокс"""

    def check(self):
        """Отмечает чекбокс"""
        if not self.is_checked():
            self.page.click(self.locator)
        return self.page

    def uncheck(self):
        """Снимает отметку с чекбокса"""
        if self.is_checked():
            self.page.click(self.locator)
        return self.page

    def is_checked(self):
        """Проверяет, отмечен ли чекбокс"""
        return self.element.is_selected()


class Radio(BaseElement):
    """Радиокнопка"""

    def select(self):
        """Выбирает радиокнопку"""
        if not self.is_selected():
            self.page.click(self.locator)
        return self.page

    def is_selected(self):
        """Проверяет, выбрана ли радиокнопка"""
        return self.element.is_selected()


class Dropdown(BaseElement):
    """Выпадающий список"""

    def select_by_text(self, text):
        """Выбирает элемент по видимому тексту"""
        select = Select(self.element)
        select.select_by_visible_text(text)
        return self.page

    def select_by_index(self, index):
        """Выбирает элемент по индексу"""
        select = Select(self.element)
        select.select_by_index(index)
        return self.page

    def get_selected_option(self):
        """Получает выбранный элемент"""
        select = Select(self.element)
        return select.first_selected_option


class Link(BaseElement):
    """Ссылка"""

    def click(self):
        """Кликает по ссылке"""
        self.page.click(self.locator)
        return self.page

    def get_url(self):
        """Получает URL ссылки"""
        return self.element.get_attribute("href")

    def get_text(self):
        """Получает текст ссылки"""
        return self.element.text


class ElementGroup:
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