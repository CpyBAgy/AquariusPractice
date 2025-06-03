"""
Страницы Amazon с умной навигацией - автоматический поиск оптимального пути.
Система автоматически определяет кратчайший путь между страницами.
"""

from selenium.webdriver.common.by import By
import logging
from page_object_library import BasePage, Button, Input, BaseElement, auto_log


class SmartBasePage(BasePage):
    """Базовая страница с умной навигацией"""

    # URL паттерны для определения текущей страницы
    URL_PATTERNS = {
        'SmartAmazonLoginPage': ['signin', 'ap/signin'],
        'SmartAmazonHomePage': ['amazon.com/?', 'amazon.com/ref', 'amazon.com$', '/?'],
        'SmartAmazonAccountPage': ['gp/css/homepage.html', 'css/homepage'],
        'SmartAmazonDigitalServicesPage': ['nodeId=200127470'],
        'SmartAmazonFireTabletsPage': ['nodeId=GJDXXK9NZ6FMB8PJ'],
        'SmartAmazonWifiHelpPage': ['nodeId=GZFJ72443RVDHEFQ']
    }

    def get_current_page_type(self):
        """Определяет тип текущей страницы по URL"""
        current_url = self.driver.current_url.lower()

        for page_type, patterns in self.URL_PATTERNS.items():
            if any(pattern.lower() in current_url for pattern in patterns):
                return page_type
        return 'UnknownPage'

    def is_on_page_type(self, page_type):
        """Проверяет, находимся ли на странице определенного типа"""
        return self.get_current_page_type() == page_type

    @auto_log
    def smart_navigate_to(self, target_page_class):
        """Умная навигация с автоматическим поиском оптимального пути"""
        target_page_name = target_page_class.__name__
        current_page_type = self.get_current_page_type()

        logging.info(f"Умная навигация: {current_page_type} → {target_page_name}")

        if current_page_type == target_page_name:
            logging.info("Уже на целевой странице")
            return target_page_class(self.driver, base_url=self.base_url, driver_name=self.driver_name)

        navigation_path = self._find_optimal_path(current_page_type, target_page_name)

        if navigation_path:
            logging.info(f"Найден оптимальный путь: {' → '.join(navigation_path)}")
            return self._execute_navigation_path(navigation_path, target_page_class)
        else:
            logging.info("Оптимальный путь не найден, используем стандартную навигацию")
            return self.navigate_to(target_page_class)

    def _find_optimal_path(self, current, target):
        """Находит оптимальный путь навигации"""
        navigation_graph = {
            'SmartAmazonLoginPage': ['SmartAmazonHomePage'],
            'SmartAmazonHomePage': ['SmartAmazonAccountPage'],
            'SmartAmazonAccountPage': ['SmartAmazonDigitalServicesPage', 'SmartAmazonHomePage'],
            'SmartAmazonDigitalServicesPage': ['SmartAmazonFireTabletsPage', 'SmartAmazonAccountPage'],
            'SmartAmazonFireTabletsPage': ['SmartAmazonWifiHelpPage', 'SmartAmazonDigitalServicesPage'],
            'SmartAmazonWifiHelpPage': ['SmartAmazonFireTabletsPage']
        }

        from collections import deque

        queue = deque([(current, [])])
        visited = {current}

        while queue:
            current_node, path = queue.popleft()

            if current_node == target:
                return path

            for neighbor in navigation_graph.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def _execute_navigation_path(self, path, final_page_class):
        """Выполняет навигацию по найденному пути"""
        current_page = self

        for page_name in path:
            method_name = f"go_to_{page_name.replace('SmartAmazon', '').replace('Page', '').lower()}"

            if hasattr(current_page, method_name):
                logging.info(f"Выполняю переход: {method_name}")
                current_page = getattr(current_page, method_name)()
            else:
                logging.warning(f"Метод {method_name} не найден, используем прямую навигацию")
                page_class = globals().get(page_name, BasePage)
                current_page = current_page.navigate_to(page_class)

        return current_page


class SmartAmazonLoginPage(SmartBasePage):
    """Умная страница входа в аккаунт"""
    DEFAULT_URL = "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

    def _init_elements(self):
        self.username_input = Input(self, (By.ID, "ap_email"), "Поле ввода email")
        self.continue_button = Button(self, (By.ID, "continue"), "Кнопка продолжить")
        self.password_input = Input(self, (By.ID, "ap_password"), "Поле ввода пароля")
        self.sign_in_button = Button(self, (By.ID, "signInSubmit"), "Кнопка входа")

    @auto_log
    def login(self, email, password):
        """Выполняет вход в систему с умной навигацией"""
        self.username_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()
        return self.smart_navigate_to(SmartAmazonHomePage)

    @auto_log
    def go_to_homepage(self):
        """Переход на главную страницу"""
        return self.smart_navigate_to(SmartAmazonHomePage)


class SmartAmazonHomePage(SmartBasePage):
    """Умная главная страница"""
    DEFAULT_URL = "/"

    def _init_elements(self):
        self.account_menu = BaseElement(self, (By.ID, "nav-link-accountList"), "Меню аккаунта")
        self.search_input = Input(self, (By.ID, "twotabsearchtextbox"), "Поле поиска")

    @auto_log
    def go_to_account(self):
        """Переход к настройкам аккаунта"""
        self.account_menu.click()
        return self.smart_navigate_to(SmartAmazonAccountPage)

    @auto_log
    def quick_access_wifi_help(self):
        """Быстрый доступ к помощи WiFi через умную навигацию"""
        return self.smart_navigate_to(SmartAmazonWifiHelpPage)


class SmartAmazonAccountPage(SmartBasePage):
    """Умная страница настроек аккаунта"""
    DEFAULT_URL = "/gp/css/homepage.html"

    def _init_elements(self):
        self.digital_services_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Ссылка на цифровые сервисы"
        )
        self.back_to_home = BaseElement(self, (By.ID, "nav-logo"), "Возврат на главную")

    @auto_log
    def go_to_digitalservices(self):
        """Переход к цифровым сервисам"""
        self.digital_services_link.click()
        return self.smart_navigate_to(SmartAmazonDigitalServicesPage)

    @auto_log
    def go_to_homepage(self):
        """Возврат на главную"""
        self.back_to_home.click()
        return self.smart_navigate_to(SmartAmazonHomePage)

    @auto_log
    def quick_access_fire_tablets(self):
        """Быстрый доступ к Fire Tablets через умную навигацию"""
        return self.smart_navigate_to(SmartAmazonFireTabletsPage)


class SmartAmazonDigitalServicesPage(SmartBasePage):
    """Умная страница цифровых сервисов"""
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
    def go_to_firetablets(self):
        """Переход к Fire Tablets"""
        self.fire_tablets_link.click()
        return self.smart_navigate_to(SmartAmazonFireTabletsPage)

    @auto_log
    def go_to_account(self):
        """Возврат к аккаунту"""
        self.back_to_account.click()
        return self.smart_navigate_to(SmartAmazonAccountPage)


class SmartAmazonFireTabletsPage(SmartBasePage):
    """Умная страница Fire Tablets"""
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
    def go_to_wifihelp(self):
        """Переход к помощи WiFi"""
        self.wifi_help_link.click()
        return self.smart_navigate_to(SmartAmazonWifiHelpPage)

    @auto_log
    def go_to_digitalservices(self):
        """Возврат к цифровым сервисам"""
        self.back_to_digital_services.click()
        return self.smart_navigate_to(SmartAmazonDigitalServicesPage)


class SmartAmazonWifiHelpPage(SmartBasePage):
    """Умная страница помощи WiFi"""
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
    def go_to_firetablets(self):
        """Возврат к Fire Tablets"""
        self.back_to_fire_tablets.click()
        return self.smart_navigate_to(SmartAmazonFireTabletsPage)

    @auto_log
    def quick_return_to_home(self):
        """Быстрый возврат на главную через умную навигацию"""
        return self.smart_navigate_to(SmartAmazonHomePage)