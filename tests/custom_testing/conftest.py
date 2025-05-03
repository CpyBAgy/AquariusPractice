import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.custom_testing.page_manager import PageManager


class WebDriverFactory:
    @staticmethod
    def get_driver(browser_type="chrome", headless=False):
        if browser_type.lower() == "chrome":
            options = Options()
            if headless:
                options.add_argument("--headless")

            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            driver = webdriver.Chrome(options=options)
        elif browser_type.lower() == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")

        driver.maximize_window()
        driver.implicitly_wait(10)
        return driver


@pytest.fixture
def driver(request):
    driver = WebDriverFactory.get_driver(headless=True)
    yield driver
    driver.quit()


@pytest.fixture
def page_manager(driver):
    return PageManager(driver)