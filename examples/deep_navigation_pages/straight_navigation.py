"""
Обычные страницы Amazon для тестирования глубокой навигации.
Путь навигации: Login -> Home -> Account -> Digital Services -> Fire Tablets -> WiFi Help
"""

from selenium.webdriver.common.by import By
from page_object_library import BasePage, Button, Input, BaseElement, auto_log


class AmazonLoginPage(BasePage):
    """Страница входа в аккаунт Amazon"""
    DEFAULT_URL = "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

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
        return self.navigate_to(AmazonHomePage)


class AmazonHomePage(BasePage):
    """Главная страница Amazon"""
    DEFAULT_URL = "/"

    def _init_elements(self):
        self.account_menu = BaseElement(self, (By.ID, "nav-link-accountList"), "Меню аккаунта")
        self.search_input = Input(self, (By.ID, "twotabsearchtextbox"), "Поле поиска")
        self.logo = BaseElement(self, (By.ID, "nav-logo"), "Логотип Amazon")

    @auto_log
    def go_to_account(self):
        """Переход к настройкам аккаунта"""
        self.account_menu.click()
        return self.navigate_to(AmazonAccountPage)


class AmazonAccountPage(BasePage):
    """Страница настроек аккаунта"""
    DEFAULT_URL = "/gp/css/homepage.html"

    def _init_elements(self):
        self.digital_services_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'help') and contains(text(), 'Digital')]"),
            "Ссылка на цифровые сервисы и поддержку устройств"
        )
        self.back_to_home = BaseElement(self, (By.ID, "nav-logo"), "Возврат на главную")

    @auto_log
    def go_to_digital_services(self):
        """Переход к цифровым сервисам и поддержке устройств"""
        self.digital_services_link.click()
        return self.navigate_to(AmazonDigitalServicesPage)

    @auto_log
    def go_to_home(self):
        """Возврат на главную страницу"""
        self.back_to_home.click()
        return self.navigate_to(AmazonHomePage)


class AmazonDigitalServicesPage(BasePage):
    """Страница поддержки цифровых сервисов и устройств"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=200127470"

    def _init_elements(self):
        self.fire_tablets_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ') or contains(text(), 'Fire Tablet')]"),
            "Ссылка на Fire Tablets"
        )
        self.account_breadcrumb = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'css/homepage')]"),
            "Возврат к аккаунту"
        )

    @auto_log
    def go_to_fire_tablets(self):
        """Переход к разделу Fire Tablets"""
        self.fire_tablets_link.click()
        return self.navigate_to(AmazonFireTabletsPage)

    @auto_log
    def go_to_account(self):
        """Возврат к настройкам аккаунта"""
        self.account_breadcrumb.click()
        return self.navigate_to(AmazonAccountPage)


class AmazonFireTabletsPage(BasePage):
    """Страница помощи по Fire Tablets"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GJDXXK9NZ6FMB8PJ"

    def _init_elements(self):
        # Ищем ссылку на WiFi помощь
        self.wifi_help_link = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GZFJ72443RVDHEFQ') or contains(text(), 'Wi-Fi') or contains(text(), 'WiFi')]"),
            "Ссылка на помощь с WiFi"
        )
        self.back_to_digital_services = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=200127470')]"),
            "Возврат к цифровым сервисам"
        )

    @auto_log
    def go_to_wifi_help(self):
        """Переход к помощи с WiFi"""
        self.wifi_help_link.click()
        return self.navigate_to(AmazonWifiHelpPage)

    @auto_log
    def go_to_digital_services(self):
        """Возврат к цифровым сервисам"""
        self.back_to_digital_services.click()
        return self.navigate_to(AmazonDigitalServicesPage)


class AmazonWifiHelpPage(BasePage):
    """Страница помощи с WiFi для Fire Tablets"""
    DEFAULT_URL = "/gp/help/customer/display.html?nodeId=GZFJ72443RVDHEFQ"

    def _init_elements(self):
        self.wifi_instructions = BaseElement(
            self,
            (By.XPATH, "//span[contains(text(), 'Access internet by following these steps') or contains(text(), 'Connect your Fire tablet')]"),
            "Инструкции по подключению к WiFi"
        )
        self.back_to_fire_tablets = BaseElement(
            self,
            (By.XPATH, "//a[contains(@href, 'nodeId=GJDXXK9NZ6FMB8PJ')]"),
            "Возврат к Fire Tablets"
        )

    @auto_log
    def get_wifi_instructions(self):
        """Получает текст инструкций по подключению к WiFi"""
        return self.wifi_instructions.get_text()

    @auto_log
    def verify_wifi_instructions_present(self):
        """Проверяет наличие инструкций по WiFi на странице"""
        instructions = self.get_wifi_instructions()
        return len(instructions) > 0 and ("internet" in instructions.lower() or "wi-fi" in instructions.lower() or "connect" in instructions.lower())

    @auto_log
    def go_to_fire_tablets(self):
        """Возврат к Fire Tablets"""
        self.back_to_fire_tablets.click()
        return self.navigate_to(AmazonFireTabletsPage)
