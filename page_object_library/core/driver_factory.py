from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import logging


class DriverFactory:
    @staticmethod
    def create_driver(browser_type="chrome", headless=False, options=None):
        """Создает WebDriver с указанными настройками"""
        logging.info(f"Создание драйвера {browser_type}. Headless: {headless}")

        if browser_type.lower() == "chrome":
            chrome_options = ChromeOptions() if options is None else options
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)

        elif browser_type.lower() == "firefox":
            firefox_options = FirefoxOptions() if options is None else options
            if headless:
                firefox_options.add_argument("--headless")

            driver = webdriver.Firefox(options=firefox_options)

        else:
            raise ValueError(f"Неподдерживаемый тип браузера: {browser_type}")

        driver.maximize_window()
        return driver


class MultiDriverManager:
    """Менеджер для работы с несколькими драйверами"""

    def __init__(self):
        self.drivers = {}
        self.current_driver_name = None

    def create_driver(self, name="default", browser_type="chrome", headless=False, options=None):
        """Создает новый драйвер с указанным именем"""
        logging.info(f"Создание драйвера с именем '{name}'")

        if name in self.drivers:
            logging.info(f"Драйвер '{name}' уже существует. Закрываем его.")
            self.close_driver(name)

        driver = DriverFactory.create_driver(browser_type, headless, options)
        self.drivers[name] = driver

        if self.current_driver_name is None:
            self.current_driver_name = name

        return driver

    def get_driver(self, name="default"):
        """Получает драйвер по имени"""
        if name not in self.drivers:
            raise ValueError(f"Драйвер с именем '{name}' не существует")
        return self.drivers[name]

    def get_or_create_driver(self, name="default", browser_type="chrome", headless=False, options=None):
        """Получает существующий драйвер или создает новый"""
        if name in self.drivers:
            logging.info(f"Используем существующий драйвер '{name}'")
            return self.drivers[name]
        else:
            logging.info(f"Создаем новый драйвер '{name}'")
            return self.create_driver(name, browser_type, headless, options)

    def switch_to_driver(self, name):
        """Переключается на другой драйвер"""
        if name not in self.drivers:
            raise ValueError(f"Драйвер с именем '{name}' не существует")

        logging.info(f"Переключение на драйвер '{name}'")
        self.current_driver_name = name
        return self.drivers[name]

    def get_current_driver(self):
        """Получает текущий активный драйвер"""
        if self.current_driver_name is None:
            raise ValueError("Нет активного драйвера")
        return self.drivers[self.current_driver_name]

    def close_driver(self, name=None):
        """Закрывает указанный драйвер"""
        if name is None:
            name = self.current_driver_name

        if name not in self.drivers:
            return

        logging.info(f"Закрытие драйвера '{name}'")
        self.drivers[name].quit()
        del self.drivers[name]

        if name == self.current_driver_name:
            self.current_driver_name = next(iter(self.drivers)) if self.drivers else None

    def close_all_drivers(self):
        """Закрывает все драйверы"""
        logging.info("Закрытие всех драйверов")
        for name in list(self.drivers.keys()):
            self.drivers[name].quit()

        self.drivers.clear()
        self.current_driver_name = None