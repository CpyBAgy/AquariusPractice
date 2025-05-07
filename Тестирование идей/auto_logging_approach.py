import logging
import os
import sys
import time
import functools
import inspect
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = str(LOGS_DIR / "auto_logging_test.log")

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

try:
    with open(LOG_FILE_PATH, 'a') as f:
        f.write("# Проверка доступа к файлу логов - OK\n")
except Exception as e:
    print(f"ОШИБКА: Не удается записать в файл логов: {e}")
    home_dir = str(Path.home())
    LOG_FILE_PATH = os.path.join(home_dir, "auto_logging_test.log")
    print(f"Пробуем создать файл в домашней директории: {LOG_FILE_PATH}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logging.info("*** Инициализация логирования для auto_logging_approach.py ***")
logging.info(f"Лог-файл будет создан по пути: {LOG_FILE_PATH}")
logging.root.handlers[0].flush()


@dataclass
class Locator:
    by: str
    value: str
    description: str

    def __iter__(self):
        return iter((self.by, self.value))

    def __str__(self):
        return self.description


def auto_log(func):
    """Декоратор для автоматического логирования действий"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__ if args else "Unknown"
        method_name = func.__name__

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        params = []
        for name, value in list(bound_args.arguments.items())[1:]:
            if hasattr(value, 'description'):
                params.append(f"{value.description}")
            elif isinstance(value, str) and len(value) > 20:
                params.append(f"{name}='{value[:20]}...'")
            else:
                params.append(f"{name}={value}")

        action = f"{class_name}.{method_name}"
        if params:
            action += f" с {', '.join(params)}"

        logging.info(f"➡️  {action}")
        logging.root.handlers[0].flush()

        try:
            result = func(*args, **kwargs)
            logging.info(f"✅ {action} - успешно")
            logging.root.handlers[0].flush()
            return result
        except Exception as e:
            logging.error(f"❌ {action} - ошибка: {str(e)}")
            logging.root.handlers[0].flush()
            raise

    return wrapper


class SearchPage:
    """Класс, представляющий страницу поиска DuckDuckGo с автоматическим логированием методов"""

    def __init__(self, driver):
        self.driver = driver
        self.url = "https://duckduckgo.com"
        self.search_box = Locator(By.ID, "searchbox_input", "поле ввода поискового запроса")
        self.search_button = Locator(By.CSS_SELECTOR, "button[aria-label='Search']", "кнопка поиска")
        self.results = Locator(By.CSS_SELECTOR, ".react-results--main", "контейнер результата поиска")
        self.result_titles = Locator(By.CSS_SELECTOR, "h2", "заголовок результата поиска")
        self.non_existent = Locator(By.ID, "this-element-does-not-exist", "несуществующий элемент")

    @auto_log
    def open(self):
        """Открывает страницу поиска"""
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return self

    @auto_log
    def find(self, locator, timeout=10):
        """Находит элемент с ожиданием"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"Не удалось найти {locator} за {timeout} секунд")

    @auto_log
    def click(self, locator, timeout=10):
        """Клик по элементу с ожиданием кликабельности"""
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    @auto_log
    def type(self, locator, text, timeout=10):
        """Ввод текста в элемент"""
        element = self.find(locator, timeout)
        element.clear()
        element.send_keys(text)

    @auto_log
    def search(self, query):
        """Выполняет поиск по запросу"""
        self.type(self.search_box, query)

        try:
            self.click(self.search_button)
        except TimeoutException:
            self.find(self.search_box).send_keys(Keys.RETURN)

        time.sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.result_titles)
        )
        return self

    @auto_log
    def get_results_count(self):
        """Получает количество результатов поиска"""
        time.sleep(1)
        elements = self.driver.find_elements(*self.result_titles)
        return len(elements)

    @auto_log
    def has_result_containing(self, text):
        """Проверяет наличие результата, содержащего заданный текст"""
        elements = self.driver.find_elements(*self.result_titles)
        for element in elements:
            if text.lower() in element.text.lower():
                return True
        return False

    @auto_log
    def find_non_existent_element(self):
        """Метод, который будет вызывать ошибку для демонстрации логов"""
        return self.find(self.non_existent, 3)


# Тесты
def test_search_success():
    """Тест успешного поиска"""
    logging.info("=== Начало теста успешного поиска ===")
    logging.root.handlers[0].flush()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        search_page = SearchPage(driver)
        search_page.open().search("Python selenium testing")

        time.sleep(2)

        assert search_page.get_results_count() > 0, "Ожидались результаты поиска"
        assert search_page.has_result_containing("Python"), "Ожидался результат с 'Python'"

        logging.info("✓ Тест успешного поиска прошел")
        logging.root.handlers[0].flush()
    except Exception as e:
        logging.error(f"✗ Тест провалился: {e}")
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = f"error_screenshot_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
            logging.info(f"Скриншот сохранен: {screenshot_path}")
        except Exception as screenshot_error:
            logging.error(f"Не удалось сохранить скриншот: {screenshot_error}")
        logging.root.handlers[0].flush()
        raise
    finally:
        driver.quit()
        logging.info("=== Конец теста успешного поиска ===")
        logging.root.handlers[0].flush()


def test_search_failure():
    """Тест с ошибкой при поиске элемента"""
    logging.info("=== Начало теста с ошибкой при поиске элемента ===")
    logging.root.handlers[0].flush()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        search_page = SearchPage(driver)
        search_page.open()

        search_page.find_non_existent_element()

        logging.info("✓ Тест прошел (не должен дойти до этой точки)")
    except TimeoutException as e:
        logging.info(f"✓ Тест ожидаемо провалился: {e}")
        logging.root.handlers[0].flush()
    except Exception as e:
        logging.error(f"✗ Тест неожиданно провалился: {e}")
        logging.root.handlers[0].flush()
        raise
    finally:
        driver.quit()
        logging.info("=== Конец теста с ошибкой при поиске элемента ===")
        logging.root.handlers[0].flush()


if __name__ == "__main__":
    logging.info("Запуск тестов подхода с автоматическим логированием")
    logging.root.handlers[0].flush()

    try:
        test_search_success()
        test_search_failure()
        logging.info("Все тесты завершены")
        logging.root.handlers[0].flush()

        if os.path.exists(LOG_FILE_PATH):
            file_size = os.path.getsize(LOG_FILE_PATH)
            logging.info(f"Файл логов создан. Размер: {file_size} байт")
            if file_size == 0:
                logging.warning("ВНИМАНИЕ: Файл логов создан, но его размер равен 0!")
        else:
            logging.error(f"ОШИБКА: Файл логов не существует: {LOG_FILE_PATH}")

        logging.root.handlers[0].flush()
    except Exception as e:
        logging.error(f"Ошибка при выполнении тестов: {e}")
        logging.root.handlers[0].flush()