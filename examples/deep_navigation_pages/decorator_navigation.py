"""
Страницы Amazon с декораторной навигацией - автоматический переход к нужной странице
перед выполнением метода с помощью декоратора @requires_page.
"""

from selenium.webdriver.common.by import By
import functools
import logging
from page_object_library import BasePage, Button, Input, BaseElement, auto_log


def requires_page(target_page_class):
    """
    Декоратор, который автоматически навигирует к нужной странице
    перед выполнением метода.

    Использование:
    @requires_page(TargetPage)
    def some_method(self):
        # Метод автоматически выполнится на TargetPage
    """

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            target_page_name = target_page_class.__name__

            current_page_type = self.get_current_page_type() if hasattr(self, 'get_current_page_type') else None

            if current_page_type != target_page_name:
                logging.info(f"🔄 Декоратор: автоматическая навигация {current_page_type} → {target_page_name}")

                if hasattr(self, 'navigate_to_page_with_path'):
                    target_page = self.navigate_to_page_with_path(target_page_class)
                elif hasattr(self, 'navigate_to'):
                    target_page = self.navigate_to(target_page_class)
                else:
                    raise Exception("Нет доступных методов навигации")

                return getattr(target_page, method.__name__)(*args, **kwargs)

            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class DecoratorBasePage(BasePage):
    """Базовая страница с поддержкой декораторной навигации"""

    # URL паттерны для определения типа страницы
    URL_PATTERNS = {
        'DecoratorAmazonLoginPage': ['signin', 'ap/signin'],
        'DecoratorAmazonHomePage': ['amazon.com/?', 'amazon.com/ref', 'amazon.com$', '/?'],
        'DecoratorAmazonAccountPage': ['gp/css/homepage.html', 'css/homepage'],
        'DecoratorAmazonDigitalServicesPage': ['nodeId=200127470'],
        'DecoratorAmazonFireTabletsPage': ['nodeId=GJDXXK9NZ6FMB8PJ'],
        'DecoratorAmazonWifiHelpPage': ['nodeId=GZFJ72443RVDHEFQ']
    }

    def get_current_page_type(self):
        """Определяет тип текущей страницы по URL"""
        current_url = self.driver.current_url.lower()

        for page_type, patterns in self.URL_PATTERNS.items():
            if any(pattern.lower() in current_url for pattern in patterns):
                return page_type
        return 'UnknownPage'

    @auto_log
    def navigate_to_page_with_path(self, target_page_class):
        """Навигация с определением пути"""
        target_page_name = target_page_class.__name__
        current_page_type = self.get_current_page_type()

        navigation_sequence = self._get_navigation_sequence(current_page_type, target_page_name)

        if navigation_sequence:
            return self._execute_navigation_sequence(navigation_sequence, target_page_class)
        else:
            return self.navigate_to(target_page_class)

    def _get_navigation_sequence(self, current, target):
        """Определяет последовательность методов для навигации"""
        # Карта переходов: откуда → [(куда, метод), ...]
        transition_map = {
            'DecoratorAmazonLoginPage': [
                ('DecoratorAmazonHomePage', 'go_to_home')
            ],
            'DecoratorAmazonHomePage': [
                ('DecoratorAmazonAccountPage', 'go_to_account')
            ],
            'DecoratorAmazonAccountPage': [
                ('DecoratorAmazonHomePage', 'go_to_home'),
                ('DecoratorAmazonDigitalServicesPage', 'go_to_digital_services')
            ],
            'DecoratorAmazonDigitalServicesPage': [
                ('DecoratorAmazonAccountPage', 'go_to_account'),
                ('DecoratorAmazonFireTabletsPage', 'go_to_fire_tablets')
            ],
            'DecoratorAmazonFireTabletsPage': [
                ('DecoratorAmazonDigitalServicesPage', 'go_to_digital_services'),
                ('DecoratorAmazonWifiHelpPage', 'go_to_wifi_help')
            ],
            'DecoratorAmazonWifiHelpPage': [
                ('DecoratorAmazonFireTabletsPage', 'go_to_fire_tablets')
            ]
        }

        from collections import deque

        queue = deque([(current, [])])
        visited = {current}

        while queue:
            current_node, path = queue.popleft()

            if current_node == target:
                return path

            for next_page, method in transition_map.get(current_node, []):
                if next_page not in visited:
                    visited.add(next_page)
                    queue.append((next_page, path + [method]))

        return None

    def _execute_navigation_sequence(self, sequence, target_page_class):
        """Выполняет последовательность методов навигации"""
        current_page = self

        for method_name in sequence:
            if hasattr(current_page, method_name):
                logging.info(f"🔗 Выполняю навигационный метод: {method_name}")
                current_page = getattr(current_page, method_name)()
            else:
                logging.warning(f"⚠️ Метод {method_name} не найден")
                return self.navigate_to(target_page_class)

        return current_page


class DecoratorAmazonLoginPage(DecoratorBasePage):
    """Страница входа с декораторной навигацией"""
    DEFAULT_URL = "/ap/signin"

    def _init_elements(self):
        self.username_input = Input(self, (By.ID, "ap_email"), "Поле ввода email")
        self.continue_button = Button(self, (By.ID, "continue"), "Кнопка продолжить")
        self.password_input = Input(self, (By.ID, "ap_password"), "Поле ввода пароля")
        self.sign_in_button = Button(self, (By.ID, "signInSubmit"), "Кнопка входа")

    @auto_log
    def login(self, email, password):
        """Выполняет вход в систему"""
        self.username_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()
        return self.navigate_to(DecoratorAmazonHomePage)

    @auto_log
    def go_to_home(self):
        """Переход на главную страницу"""
        return self.navigate_to(DecoratorAmazonHomePage)


class DecoratorAmazonWifiHelpPage:
    pass


class DecoratorAmazonAccountPage:
    pass


class DecoratorAmazonFireTabletsPage:
    pass


class DecoratorAmazonHomePage(DecoratorBasePage):
    """Главная страница с декораторными методами"""
    DEFAULT_URL = "/"

    def _init_elements(self):
        self.account_menu = BaseElement(self, (By.ID, "nav-link-accountList"), "Меню аккаунта")
        self.search_input = Input(self, (By.ID, "twotabsearchtextbox"), "Поле поиска")

    @auto_log
    def go_to_account(self):
        """Обычный переход к аккаунту"""
        self.account_menu.click()
        return self.navigate_to(DecoratorAmazonAccountPage)

    @requires_page(DecoratorAmazonWifiHelpPage)
    def get_wifi_instructions_from_home(self):
        """Получает инструкции WiFi прямо с главной страницы (автоматически навигирует)"""
        return self.get_wifi_instructions()

    @requires_page(DecoratorAmazonAccountPage)
    def access_account_settings_from_home(self):
        """Доступ к настройкам аккаунта (автоматически навигирует)"""
        logging.info("✅ Находимся в настройках аккаунта")
        return "Account settings accessed"

    @requires_page(DecoratorAmazonFireTabletsPage)
    def get_fire_tablet_help_from_home(self):
        """Получает помощь по Fire Tablets прямо с главной (автоматически навигирует)"""
        logging.info("✅ Находимся на странице помощи Fire Tablets")
        return "Fire Tablet help accessed"


class DecoratorAmazonAccountPage(DecoratorBasePage):
    """Страница аккаунта с декораторными методами"""
    DEFAULT_URL = "/gp/css/homepage.html"

    def _init_elements(self):
        self.digital_services_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Ссылка на цифровые сервисы"
        )
        self.back_to_home = BaseElement(self, (By.ID, "nav-logo"), "Возврат на главную")

    @auto_log
    def go_to_digital_services(self):
        """Обычный переход к цифровым сервисам"""
        self.digital_services_link.click()
        return self.navigate_to(DecoratorAmazonDigitalServicesPage)

    @auto_log
    def go_to_home(self):
        """Возврат на главную"""
        self.back_to_home.click()
        return self.navigate_to(DecoratorAmazonHomePage)

    # Декораторные методы
    @requires_page(DecoratorAmazonWifiHelpPage)
    def configure_wifi_from_account(self):
        """Настройка WiFi прямо из аккаунта (автоматически навигирует)"""
        instructions = self.get_wifi_instructions()
        logging.info("✅ WiFi настройка доступна из аккаунта")
        return instructions

    @requires_page(DecoratorAmazonFireTabletsPage)
    def manage_fire_tablets_from_account(self):
        """Управление Fire Tablets из аккаунта (автоматически навигирует)"""
        logging.info("✅ Управление Fire Tablets доступно из аккаунта")
        return "Fire Tablets management accessed"


class DecoratorAmazonDigitalServicesPage(DecoratorBasePage):
    """Страница цифровых сервисов"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=200127470"

    def _init_elements(self):
        self.fire_tablets_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ')]"),
            "Ссылка на Fire Tablets"
        )
        self.back_to_account = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'css/homepage')]"),
            "Возврат к аккаунту"
        )

    @auto_log
    def go_to_fire_tablets(self):
        """Переход к Fire Tablets"""
        self.fire_tablets_link.click()
        return self.navigate_to(DecoratorAmazonFireTabletsPage)

    @auto_log
    def go_to_account(self):
        """Возврат к аккаунту"""
        self.back_to_account.click()
        return self.navigate_to(DecoratorAmazonAccountPage)


class DecoratorAmazonFireTabletsPage(DecoratorBasePage):
    """Страница Fire Tablets"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GJDXXK9NZ6FMB8PJ"

    def _init_elements(self):
        self.wifi_help_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GZFJ72443RVDHEFQ')]"),
            "Ссылка на помощь WiFi"
        )
        self.back_to_digital_services = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Возврат к цифровым сервисам"
        )

    @auto_log
    def go_to_wifi_help(self):
        """Переход к помощи WiFi"""
        self.wifi_help_link.click()
        return self.navigate_to(DecoratorAmazonWifiHelpPage)

    @auto_log
    def go_to_digital_services(self):
        """Возврат к цифровым сервисам"""
        self.back_to_digital_services.click()
        return self.navigate_to(DecoratorAmazonDigitalServicesPage)

    @requires_page(DecoratorAmazonWifiHelpPage)
    def troubleshoot_wifi_connection(self):
        """Диагностика проблем WiFi (автоматически навигирует к WiFi Help)"""
        instructions = self.get_wifi_instructions()
        logging.info("✅ Диагностика WiFi выполнена")
        return f"WiFi troubleshooting: {instructions[:50]}..."

    @requires_page(DecoratorAmazonHomePage)
    def return_to_main_from_tablets(self):
        """Быстрый возврат на главную с Fire Tablets (автоматически навигирует)"""
        logging.info("✅ Возврат на главную выполнен")
        return "Returned to home page"


class DecoratorAmazonWifiHelpPage(DecoratorBasePage):
    """Страница помощи WiFi с декораторными возможностями"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GZFJ72443RVDHEFQ"

    def _init_elements(self):
        self.wifi_instructions = BaseElement(
            self,
            (By.XPATH, "//span[contains(text(), 'Access internet by following these steps')]"),
            "Инструкции WiFi"
        )
        self.back_to_fire_tablets = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ')]"),
            "Возврат к Fire Tablets"
        )

    @auto_log
    def get_wifi_instructions(self):
        """Получает инструкции WiFi"""
        return self.wifi_instructions.get_text()

    @auto_log
    def verify_wifi_instructions_present(self):
        """Проверяет наличие инструкций WiFi"""
        instructions = self.get_wifi_instructions()
        return "internet" in instructions.lower() or "connect" in instructions.lower()

    @auto_log
    def go_to_fire_tablets(self):
        """Возврат к Fire Tablets"""
        self.back_to_fire_tablets.click()
        return self.navigate_to(DecoratorAmazonFireTabletsPage)

    @requires_page(DecoratorAmazonAccountPage)
    def save_wifi_settings_to_account(self):
        """Сохранение настроек WiFi в аккаунт (автоматически навигирует)"""
        logging.info("✅ Настройки WiFi сохранены в аккаунт")
        return "WiFi settings saved to account"

    @requires_page(DecoratorAmazonHomePage)
    def complete_wifi_setup_and_return_home(self):
        """Завершение настройки WiFi и возврат домой (автоматически навигирует)"""
        logging.info("✅ Настройка WiFi завершена, возвращаемся домой")
        return "WiFi setup completed, returned home"


class DecoratorAmazonUniversalPage(DecoratorBasePage):
    """Универсальная страница с доступом ко всем функциям через декораторы"""

    @requires_page(DecoratorAmazonWifiHelpPage)
    def get_wifi_help(self):
        """Получить помощь WiFi откуда угодно"""
        return self.get_wifi_instructions()

    @requires_page(DecoratorAmazonAccountPage)
    def access_account(self):
        """Доступ к аккаунту откуда угодно"""
        return "Account accessed"

    @requires_page(DecoratorAmazonFireTabletsPage)
    def access_tablet_help(self):
        """Доступ к помощи планшетов откуда угодно"""
        return "Tablet help accessed"

    @requires_page(DecoratorAmazonHomePage)
    def go_home(self):
        """Вернуться домой откуда угодно"""
        return "Home page reached"