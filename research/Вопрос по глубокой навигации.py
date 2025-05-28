from selenium.webdriver.common.by import By
import functools
import logging
from page_object_library import BasePage, Button, Input, BaseElement, auto_log


# =============================================================================
# 1. БАЗОВЫЕ СТРАНИЦЫ С НАВИГАЦИЕЙ
# =============================================================================

class SmartBasePage(BasePage):
    """Расширенная базовая страница с умной навигацией"""

    # URL паттерны для определения текущей страницы
    URL_PATTERNS = {
        'LoginPage': ['login', 'signin', 'auth'],
        'HomePage': ['home', 'dashboard', 'main'],
        'SettingsPage': ['settings'],
        'NetworkSettingsPage': ['settings/network', 'network-settings'],
        'NicSettingsPage': ['settings/network/nic', 'nic-settings']
    }

    def get_current_page_type(self):
        """Определяет тип текущей страницы по URL"""
        current_url = self.driver.current_url.lower()

        for page_type, patterns in self.URL_PATTERNS.items():
            if any(pattern in current_url for pattern in patterns):
                return page_type
        return 'UnknownPage'

    def is_on_page_type(self, page_type):
        """Проверяет, находимся ли на странице определенного типа"""
        return self.get_current_page_type() == page_type

    @auto_log
    def smart_navigate_to(self, target_page_class):
        """Умная навигация с оптимизацией пути"""
        target_page_name = target_page_class.__name__
        current_page_type = self.get_current_page_type()

        logging.info(f"Навигация: {current_page_type} -> {target_page_name}")

        # Если уже на нужной странице
        if current_page_type == target_page_name:
            logging.info("Уже на нужной странице")
            return target_page_class(self.driver, driver_name=self.driver_name)

        # Определяем оптимальный путь
        navigation_path = self._find_optimal_path(current_page_type, target_page_name)

        if navigation_path:
            return self._execute_navigation_path(navigation_path, target_page_class)
        else:
            # Fallback к стандартной навигации
            return self.navigate_to(target_page_class)

    def _find_optimal_path(self, current, target):
        """Находит оптимальный путь навигации"""
        # Граф навигации (кто к кому может перейти напрямую)
        navigation_graph = {
            'LoginPage': ['HomePage'],
            'HomePage': ['SettingsPage'],
            'SettingsPage': ['NetworkSettingsPage', 'HomePage'],
            'NetworkSettingsPage': ['NicSettingsPage', 'SettingsPage'],
            'NicSettingsPage': ['NetworkSettingsPage']
        }

        # Простой поиск пути (можно улучшить алгоритмом поиска кратчайшего пути)
        if target in navigation_graph.get(current, []):
            return [target]  # Прямой переход

        # Поиск через промежуточные страницы
        for intermediate in navigation_graph.get(current, []):
            if target in navigation_graph.get(intermediate, []):
                return [intermediate, target]

        return None  # Путь не найден

    def _execute_navigation_path(self, path, final_page_class):
        """Выполняет навигацию по заданному пути"""
        current_page = self

        for page_name in path:
            method_name = f"go_to_{page_name.replace('Page', '').lower()}"

            if hasattr(current_page, method_name):
                current_page = getattr(current_page, method_name)()
            else:
                logging.warning(f"Метод {method_name} не найден, используем стандартную навигацию")
                page_class = globals().get(page_name, BasePage)
                current_page = current_page.navigate_to(page_class)

        return current_page


# =============================================================================
# 2. КОНКРЕТНЫЕ СТРАНИЦЫ
# =============================================================================

class LoginPage(SmartBasePage):
    def _init_elements(self):
        self.username_input = Input(self, (By.ID, "username"), "Поле имени пользователя")
        self.password_input = Input(self, (By.ID, "password"), "Поле пароля")
        self.login_button = Button(self, (By.ID, "login-btn"), "Кнопка входа")

    @auto_log
    def login(self, username, password):
        """Выполняет вход в систему"""
        self.username_input.type(username)
        self.password_input.type(password)
        self.login_button.click()
        return self.smart_navigate_to(HomePage)


class HomePage(SmartBasePage):
    def _init_elements(self):
        self.settings_button = Button(self, (By.ID, "settings-btn"), "Кнопка настроек")
        self.user_menu = BaseElement(self, (By.ID, "user-menu"), "Меню пользователя")

    @auto_log
    def go_to_settings(self):
        """Переход к настройкам"""
        self.settings_button.click()
        return self.smart_navigate_to(SettingsPage)

    @auto_log
    def go_to_nic_settings(self):
        """Прямой переход к настройкам сетевых карт"""
        # Сначала идем к настройкам, потом к сетевым, потом к NIC
        settings_page = self.go_to_settings()
        return settings_page.go_to_nic_settings()


class SettingsPage(SmartBasePage):
    def _init_elements(self):
        self.network_settings_link = Button(self, (By.ID, "network-settings"), "Ссылка сетевых настроек")
        self.back_to_home_button = Button(self, (By.ID, "back-home"), "Кнопка возврата на главную")

    @auto_log
    def go_to_network_settings(self):
        """Переход к сетевым настройкам"""
        self.network_settings_link.click()
        return self.smart_navigate_to(NetworkSettingsPage)

    @auto_log
    def go_to_home(self):
        """Возврат на главную страницу"""
        self.back_to_home_button.click()
        return self.smart_navigate_to(HomePage)

    @auto_log
    def go_to_nic_settings(self):
        """Переход к NIC настройкам через сетевые настройки"""
        network_page = self.go_to_network_settings()
        return network_page.go_to_nic_settings()


class NetworkSettingsPage(SmartBasePage):
    def _init_elements(self):
        self.nic_settings_link = Button(self, (By.ID, "nic-settings"), "Ссылка настроек сетевых карт")
        self.back_to_settings_button = Button(self, (By.ID, "back-settings"), "Возврат к настройкам")

    @auto_log
    def go_to_nic_settings(self):
        """Переход к настройкам сетевых карт"""
        self.nic_settings_link.click()
        return self.smart_navigate_to(NicSettingsPage)

    @auto_log
    def go_to_settings(self):
        """Возврат к общим настройкам"""
        self.back_to_settings_button.click()
        return self.smart_navigate_to(SettingsPage)


class NicSettingsPage(SmartBasePage):
    def _init_elements(self):
        self.nic_list = BaseElement(self, (By.ID, "nic-list"), "Список сетевых карт")
        self.add_nic_button = Button(self, (By.ID, "add-nic"), "Кнопка добавления NIC")
        self.back_to_network_button = Button(self, (By.ID, "back-network"), "Возврат к сетевым настройкам")

    @auto_log
    def configure_nic(self, nic_name, ip_address):
        """Настройка сетевой карты"""
        # Логика настройки NIC
        logging.info(f"Настройка NIC {nic_name} с IP {ip_address}")
        return self

    @auto_log
    def go_to_network_settings(self):
        """Возврат к сетевым настройкам"""
        self.back_to_network_button.click()
        return self.smart_navigate_to(NetworkSettingsPage)

# =============================================================================
# 3. ДЕКОРАТОРЫ ДЛЯ АВТОМАТИЧЕСКОЙ НАВИГАЦИИ
# =============================================================================

def requires_page(target_page_class):
    """
    Декоратор, который автоматически навигирует к нужной странице перед выполнением метода

    Использование:
    @requires_page(NicSettingsPage)
    def configure_network(self):
        # Этот метод автоматически перейдет к NIC settings, если нужно
        pass
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # Получаем текущую страницу
            current_page_type = self.get_current_page_type() if hasattr(self, 'get_current_page_type') else None
            target_page_name = target_page_class.__name__

            # Если мы не на нужной странице
            if current_page_type != target_page_name:
                logging.info(f"Автоматическая навигация: {current_page_type} -> {target_page_name}")

                # Используем умную навигацию
                if hasattr(self, 'smart_navigate_to'):
                    target_page = self.smart_navigate_to(target_page_class)
                    # Вызываем метод на правильной странице
                    return getattr(target_page, method.__name__)(*args, **kwargs)
                else:
                    # Fallback к обычной навигации
                    target_page = self.navigate_to(target_page_class)
                    return getattr(target_page, method.__name__)(*args, **kwargs)

            # Если уже на правильной странице, выполняем метод
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


class SmartHomePage(SmartBasePage):
    """Главная страница с автоматической навигацией"""

    @requires_page(NicSettingsPage)
    def configure_primary_nic(self, ip_address):
        """Настройка основной сетевой карты (автоматически перейдет к NIC settings)"""
        return self.configure_nic("eth0", ip_address)

    @requires_page(SettingsPage)
    def change_user_settings(self, settings_dict):
        """Изменение пользовательских настроек (автоматически перейдет к Settings)"""
        # Логика изменения настроек
        logging.info(f"Изменение настроек: {settings_dict}")
        return self
