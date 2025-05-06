import logging
from selenium.webdriver.common.by import By
from dataclasses import dataclass
import sys
import os

# Настройка логирования
LOG_FILE = "locator_comparison.log"
try:
    with open(LOG_FILE, 'w') as f:
        f.write("Файл лога создан\n")
except Exception as e:
    print(f"Ошибка при создании файла лога: {e}")
    LOG_FILE = os.path.join(os.path.expanduser("~"), "locator_comparison.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("=== НАЧАЛО СРАВНЕНИЯ ПОДХОДОВ К ЛОКАТОРАМ ===")

# ============ 1. ОБЫЧНЫЕ ЛОКАТОРЫ ============
# Определение обычных локаторов
std_login_form = (By.ID, "login-form")
std_username_field = (By.NAME, "username")
std_password_field = (By.NAME, "password")
std_submit_button = (By.CSS_SELECTOR, "button[type='submit']")
std_remember_me_checkbox = (By.ID, "remember-me")
std_forgot_password_link = (By.LINK_TEXT, "Forgot password?")
std_error_message = (By.CLASS_NAME, "error-message")
std_login_heading = (By.TAG_NAME, "h1")
std_non_existent = (By.ID, "non-existent-id")


# ============ 2. ЛОКАТОРЫ С РУЧНЫМ ОПИСАНИЕМ ============
@dataclass
class Locator:
    by: str
    value: str
    description: str

    def __iter__(self):
        return iter((self.by, self.value))

    def __str__(self):
        return self.description


# Создаем локаторы с ручным описанием
desc_login_form = Locator(By.ID, "login-form", "форма авторизации")
desc_username_field = Locator(By.NAME, "username", "поле ввода логина")
desc_password_field = Locator(By.NAME, "password", "поле ввода пароля")
desc_submit_button = Locator(By.CSS_SELECTOR, "button[type='submit']", "кнопка входа")
desc_remember_me_checkbox = Locator(By.ID, "remember-me", "чекбокс 'Запомнить меня'")
desc_forgot_password_link = Locator(By.LINK_TEXT, "Forgot password?", "ссылка 'Забыли пароль?'")
desc_error_message = Locator(By.CLASS_NAME, "error-message", "сообщение об ошибке авторизации")
desc_login_heading = Locator(By.TAG_NAME, "h1", "заголовок страницы входа")
desc_non_existent = Locator(By.ID, "non-existent-id", "несуществующий элемент формы")


# ============ 3. ЛОКАТОРЫ С АВТОМАТИЧЕСКИМ ОПИСАНИЕМ ============
class LocatorWithDescription:
    def __init__(self, locator, description):
        self.locator = locator
        self.description = description

    def __iter__(self):
        return iter(self.locator)

    def __str__(self):
        return self.description

    @property
    def by(self):
        return self.locator[0]

    @property
    def value(self):
        return self.locator[1]


class AutoDescribeLocators:
    def __init__(self):
        self._locators = {}

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            description = self._generate_description(name, value)
            self._locators[name] = LocatorWithDescription(value, description)

    def __getattr__(self, name):
        if name in self._locators:
            return self._locators[name]
        raise AttributeError(f"'{self.__class__.__name__}' не имеет атрибута '{name}'")

    def _generate_description(self, name, value):
        # Разбиваем имя на части для лучшего анализа
        name_parts = name.lower().split('_')

        # Определяем тип элемента
        element_type = ""

        # Определение типа элемента из имени
        if any(part in ['btn', 'button'] for part in name_parts):
            element_type = "кнопка"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['btn', 'button']]
        elif any(part in ['field', 'input', 'username', 'password', 'email', 'text'] for part in name_parts):
            element_type = "поле ввода"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['field', 'input']]
        elif any(part in ['link', 'href', 'url'] for part in name_parts):
            element_type = "ссылка"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['link', 'href', 'url']]
        elif any(part in ['checkbox', 'check', 'toggle'] for part in name_parts):
            element_type = "чекбокс"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['checkbox', 'check', 'toggle']]
        elif any(part in ['form', 'container'] for part in name_parts):
            element_type = "форма"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['form', 'container']]
        elif any(part in ['message', 'notification', 'alert', 'error'] for part in name_parts):
            element_type = "сообщение"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['message', 'notification']]
        elif any(part in ['heading', 'header', 'title', 'h1', 'h2', 'h3'] for part in name_parts):
            element_type = "заголовок"
            # Удаляем служебные слова из описания
            name_parts = [part for part in name_parts if part not in ['heading', 'header', 'title', 'h1', 'h2', 'h3']]
        else:
            element_type = "элемент"

        # Создаем описание на основе имени
        description_text = " ".join(name_parts)

        # Добавляем слово "страницы" или "формы" для некоторых элементов
        if any(word in name_parts for word in ['login', 'auth', 'signin']):
            if element_type in ["заголовок", "ссылка"]:
                description_text += " страницы входа"

        if element_type == "поле ввода" and "username" in name_parts:
            description_text = "логина"
        elif element_type == "поле ввода" and "password" in name_parts:
            description_text = "пароля"
        elif "submit" in name_parts and element_type == "кнопка":
            description_text = "входа"
        elif "forgot" in name_parts and "password" in name_parts:
            description_text = "'Забыли пароль?'"
        elif "remember" in name_parts and "me" in name_parts:
            description_text = "'Запомнить меня'"
        elif "error" in name_parts:
            description_text = "об ошибке авторизации"

        # Формируем итоговое описание
        description = f"{element_type} {description_text}".strip()

        # Добавляем технические детали локатора
        locator_type = value[0]
        locator_value = value[1]

        # Добавляем технические детали в зависимости от типа локатора
        if locator_type == By.ID:
            description += f" (ID: {locator_value})"
        elif locator_type == By.NAME:
            description += f" (name: {locator_value})"
        elif locator_type == By.CLASS_NAME:
            description += f" (класс: {locator_value})"
        elif locator_type == By.CSS_SELECTOR:
            description += f" (CSS: {locator_value})"
        elif locator_type == By.XPATH:
            description += f" (XPath: {locator_value})"
        elif locator_type == By.LINK_TEXT:
            description += f" (text: {locator_value})"
        elif locator_type == By.TAG_NAME:
            description += f" (тег: {locator_value})"

        return description


# Создаем экземпляр класса с автоматическим описанием
auto_locators = AutoDescribeLocators()

# Определяем локаторы, которые автоматически получат описания
auto_locators.LOGIN_FORM = (By.ID, "login-form")
auto_locators.USERNAME_FIELD = (By.NAME, "username")
auto_locators.PASSWORD_FIELD = (By.NAME, "password")
auto_locators.SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
auto_locators.REMEMBER_ME_CHECKBOX = (By.ID, "remember-me")
auto_locators.FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot password?")
auto_locators.ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
auto_locators.LOGIN_HEADING = (By.TAG_NAME, "h1")
auto_locators.NON_EXISTENT_ELEMENT = (By.ID, "non-existent-id")


# ============ СОЗДАНИЕ СРАВНИТЕЛЬНЫХ ТАБЛИЦ ============

# Функция для имитации поиска элемента
def find_element(locator, successful=True):
    if successful:
        return {"success": True, "element": "WebElement"}
    else:
        return {"success": False, "error": f"Не удалось найти элемент: {locator}"}


# Выводим заголовок сравнения
logging.info("\n=== СРАВНЕНИЕ ЛОГОВ ДЛЯ РАЗНЫХ ТИПОВ ЛОКАТОРОВ ===\n")

# 1. Сравнение логов при успешных операциях
logging.info("Таблица 1: Сравнение логов при успешных операциях")
logging.info("-" * 200)
logging.info(
    "| {:<20} | {:<45} | {:<45} | {:<45} |".format("Элемент", "Обычные локаторы", "Ручное описание", "Автоописание"))
logging.info("-" * 200)

# Форма логина
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Форма логина",
                                                            f"{std_login_form}",
                                                            f"{desc_login_form}",
                                                            f"{auto_locators.LOGIN_FORM}"))

# Поле логина
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Поле логина",
                                                            f"{std_username_field}",
                                                            f"{desc_username_field}",
                                                            f"{auto_locators.USERNAME_FIELD}"))

# Поле пароля
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Поле пароля",
                                                            f"{std_password_field}",
                                                            f"{desc_password_field}",
                                                            f"{auto_locators.PASSWORD_FIELD}"))

# Кнопка входа
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Кнопка входа",
                                                            f"{std_submit_button}",
                                                            f"{desc_submit_button}",
                                                            f"{auto_locators.SUBMIT_BUTTON}"))

# Чекбокс "Запомнить меня"
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Чекбокс",
                                                            f"{std_remember_me_checkbox}",
                                                            f"{desc_remember_me_checkbox}",
                                                            f"{auto_locators.REMEMBER_ME_CHECKBOX}"))

# Ссылка "Забыли пароль"
logging.info("| {:<20} | {:<45} | {:<45} | {:<45} |".format("Ссылка",
                                                            f"{std_forgot_password_link}",
                                                            f"{desc_forgot_password_link}",
                                                            f"{auto_locators.FORGOT_PASSWORD_LINK}"))

logging.info("-" * 200)

# 2. Сравнение логов при ошибке
logging.info("Таблица 2: Сравнение логов при ошибке поиска элемента")
logging.info("-" * 120)
logging.info("| {:<20} | {:<80} |".format("Тип локаторов", "Сообщение об ошибке"))
logging.info("-" * 120)

# Ошибка с обычным локатором
error_std = find_element(std_non_existent, False)
logging.info("| {:<20} | {:<80} |".format("Обычные", f"Не удалось найти элемент: {std_non_existent}"))

# Ошибка с локатором с ручным описанием
error_desc = find_element(desc_non_existent, False)
logging.info("| {:<20} | {:<80} |".format("С описанием", f"Не удалось найти элемент: {desc_non_existent}"))

# Ошибка с локатором с автоматическим описанием
error_auto = find_element(auto_locators.NON_EXISTENT_ELEMENT, False)
logging.info(
    "| {:<20} | {:<80} |".format("С автоописанием", f"Не удалось найти элемент: {auto_locators.NON_EXISTENT_ELEMENT}"))

logging.info("-" * 120)

# Имитация процесса поиска и вызова исключений для демонстрации
logging.info("\n=== ДЕМОНСТРАЦИЯ ЛОГОВ ПРИ ПОИСКЕ ЭЛЕМЕНТОВ ===\n")

# 1. Обычные локаторы
logging.info("--- Обычные локаторы ---")
logging.info(f"Ищу элемент формы: {std_login_form}")
logging.info(f"Ищу поле логина: {std_username_field}")
logging.info(f"Ищу поле пароля: {std_password_field}")
logging.info(f"Ищу кнопку входа: {std_submit_button}")
logging.info(f"Ищу чекбокс: {std_remember_me_checkbox}")
logging.info(f"Ищу ссылку: {std_forgot_password_link}")
logging.info(f"Ищу несуществующий элемент: {std_non_existent}")
logging.error(f"Ошибка при поиске элемента: Не удалось найти элемент: {std_non_existent}")

# 2. Локаторы с ручным описанием
logging.info("\n--- Локаторы с ручным описанием ---")
logging.info(f"Ищу {desc_login_form}")
logging.info(f"Ищу {desc_username_field}")
logging.info(f"Ищу {desc_password_field}")
logging.info(f"Ищу {desc_submit_button}")
logging.info(f"Ищу {desc_remember_me_checkbox}")
logging.info(f"Ищу {desc_forgot_password_link}")
logging.info(f"Ищу {desc_non_existent}")
logging.error(f"Ошибка при поиске элемента: Не удалось найти элемент: {desc_non_existent}")

# 3. Локаторы с автоматическим описанием
logging.info("\n--- Локаторы с автоматическим описанием ---")
logging.info(f"Ищу {auto_locators.LOGIN_FORM}")
logging.info(f"Ищу {auto_locators.USERNAME_FIELD}")
logging.info(f"Ищу {auto_locators.PASSWORD_FIELD}")
logging.info(f"Ищу {auto_locators.SUBMIT_BUTTON}")
logging.info(f"Ищу {auto_locators.REMEMBER_ME_CHECKBOX}")
logging.info(f"Ищу {auto_locators.FORGOT_PASSWORD_LINK}")
logging.info(f"Ищу {auto_locators.NON_EXISTENT_ELEMENT}")
logging.error(f"Ошибка при поиске элемента: Не удалось найти элемент: {auto_locators.NON_EXISTENT_ELEMENT}")

logging.info("\n=== ЗАВЕРШЕНИЕ СРАВНЕНИЯ ПОДХОДОВ К ЛОКАТОРАМ ===")

print(f"\nСравнение завершено. Лог сохранен в файле: {os.path.abspath(LOG_FILE)}")