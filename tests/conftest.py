import pytest
import logging
from datetime import datetime
from pathlib import Path

from page_object_library import DriverFactory, MultiDriverManager, PageFactory, MultiPageFactory
from page_object_library import setup_logger


def pytest_addoption(parser):
    """Добавляем опции командной строки"""
    parser.addoption(
        "--browser-type", action="store", default="chrome",
        help="Тип браузера: chrome или firefox"
    )
    parser.addoption(
        "--headless-mode", action="store_true", default=False,
        help="Запускать браузер в headless режиме"
    )
    parser.addoption(
        "--base-url", action="store", default="https://www.amazon.com",
        help="Базовый URL для тестирования"
    )


@pytest.fixture(scope="session")
def setup_logging():
    """Настройка логирования на уровне сессии"""
    return setup_logger()


@pytest.fixture(scope="session")
def base_url(request):
    """Фикстура для получения базового URL из командной строки"""
    return request.config.getoption("--base-url")


@pytest.fixture
def driver(setup_logging, request):
    """Фикстура для создания одиночного драйвера"""
    browser_type = request.config.getoption("--browser-type", default="chrome")
    headless = request.config.getoption("--headless-mode", default=False)

    driver = DriverFactory.create_driver(browser_type, headless)

    request.node.driver = driver

    yield driver

    driver.quit()


@pytest.fixture
def page_factory(driver, base_url):
    """Фикстура для фабрики страниц с одним драйвером и базовым URL"""
    return PageFactory(driver, base_url=base_url, driver_name="default")


@pytest.fixture
def multi_driver(setup_logging, request):
    """Фикстура для создания менеджера нескольких драйверов"""
    manager = MultiDriverManager()

    browser_type = request.config.getoption("--browser-type", default="chrome")
    headless = request.config.getoption("--headless-mode", default=False)

    # Создаем драйвер по умолчанию
    manager.create_driver("default", browser_type, headless)

    request.node.multi_driver = manager

    yield manager

    manager.close_all_drivers()


@pytest.fixture
def multi_page_factory(multi_driver, base_url, request):
    """Фикстура для фабрики страниц с несколькими драйверами и базовым URL"""
    browser_type = request.config.getoption("--browser-type", default="chrome")
    headless = request.config.getoption("--headless-mode", default=False)
    return MultiPageFactory(
        multi_driver,
        default_browser_type=browser_type,
        default_headless=headless,
        default_base_url=base_url
    )


SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для создания скриншота при падении теста"""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver", None)
        if driver is not None:
            take_screenshot(driver, item.name)

        multi_driver = item.funcargs.get("multi_driver", None)
        if multi_driver is not None:
            for name, driver in multi_driver.drivers.items():
                take_screenshot(driver, f"{item.name}_{name}")


def take_screenshot(driver, test_name):
    """Создает скриншот текущего состояния браузера"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.png"
    filepath = SCREENSHOTS_DIR / filename

    try:
        driver.save_screenshot(str(filepath))
        logging.info(f"Скриншот сохранен: {filepath}")
    except Exception as e:
        logging.error(f"Не удалось сохранить скриншот: {e}")
