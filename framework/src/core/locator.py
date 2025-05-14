from dataclasses import dataclass
from selenium.webdriver.common.by import By


@dataclass
class Locator:
    by: str
    value: str
    description: str = None

    def __post_init__(self):
        if self.description is None:
            self.description = "элемент"

    def __iter__(self):
        """Позволяет использовать локатор как кортеж (by, value)"""
        return iter((self.by, self.value))

    def __str__(self):
        """Возвращает описание для логов"""
        return self.description


class LocatorMeta(type):
    """Метакласс для автоматической генерации описаний локаторов"""

    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in list(attrs.items()):
            if attr_name.isupper() and isinstance(attr_value, tuple) and len(attr_value) == 2:
                by, value = attr_value
                description = mcs._generate_description(attr_name, by, value)
                attrs[attr_name] = Locator(by, value, description)

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _generate_description(attr_name, by, value):
        """Генерирует описание на основе имени атрибута, типа локатора и его значения"""
        parts = attr_name.split('_')
        words = [word.lower() for word in parts]

        element_type = "элемент"

        element_type_mapping = {
            'button': "кнопка",
            'btn': "кнопка",
            'input': "поле ввода",
            'field': "поле ввода",
            'text': "поле ввода",
            'email': "поле ввода email",
            'password': "поле ввода пароля",
            'link': "ссылка",
            'href': "ссылка",
            'checkbox': "чекбокс",
            'check': "чекбокс",
            'radio': "радиокнопка",
            'dropdown': "выпадающий список",
            'select': "выпадающий список",
            'form': "форма",
            'message': "сообщение",
            'error': "сообщение об ошибке",
            'success': "сообщение об успехе",
            'alert': "уведомление",
            'header': "заголовок",
            'heading': "заголовок",
            'title': "заголовок",
            'h1': "заголовок",
            'h2': "заголовок",
            'h3': "заголовок",
            'image': "изображение",
            'img': "изображение",
            'icon': "иконка",
            'table': "таблица",
            'menu': "меню",
            'nav': "навигация",
            'navigation': "навигация",
            'tab': "вкладка",
            'modal': "модальное окно",
            'dialog': "диалоговое окно",
            'popup': "всплывающее окно",
            'search': "поле поиска",
            'label': "метка",
            'container': "контейнер",
            'wrapper': "обертка",
            'block': "блок",
        }

        for type_word, type_name in element_type_mapping.items():
            if type_word in words:
                element_type = type_name
                words = [w for w in words if w != type_word]
                break

        if "submit" in words:
            if element_type == "кнопка":
                words = [w for w in words if w != "submit"]
                words.append("отправки")

        if "login" in words and element_type == "кнопка":
            words = [w for w in words if w != "login"]
            words.append("входа")

        description_part = " ".join(words).strip()
        if description_part:
            description = f"{element_type} {description_part}"
        else:
            description = element_type

        if by == By.ID:
            description += f" (ID: {value})"
        elif by == By.NAME:
            description += f" (name: {value})"
        elif by == By.CLASS_NAME:
            description += f" (класс: {value})"
        elif by == By.CSS_SELECTOR:
            description += f" (CSS: {value})"
        elif by == By.XPATH:
            description += f" (XPath: {value})"
        elif by == By.LINK_TEXT:
            description += f" (текст: {value})"
        elif by == By.TAG_NAME:
            description += f" (тег: {value})"

        return description


class PageLocators(metaclass=LocatorMeta):
    """Базовый класс для локаторов страницы с автоматическим описанием"""
    pass