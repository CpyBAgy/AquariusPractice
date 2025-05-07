import logging
import os
import sys
import time
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

LOG_FILE_PATH = str(LOGS_DIR / "base_page_test.log")

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
    LOG_FILE_PATH = os.path.join(home_dir, "base_page_test.log")
    print(f"Пробуем создать файл в домашней директории: {LOG_FILE_PATH}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logging.info("*** Инициализация логирования для base_page_approach.py ***")
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


class BasePage:
    """Базовый класс для всех страниц"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, url):
        """Открывает указанный URL"""
        logging.info(f"Открываю страницу {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info(f"Страница {url} загружена")
        logging.root.handlers[0].flush()
        return self

    def find(self, locator, timeout=10):
        """Находит элемент с ожиданием"""
        try:
            logging.info(f"Ищу {locator}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            error_msg = f"Не удалось найти {locator} за {timeout} секунд"
            logging.error(error_msg)
            logging.root.handlers[0].flush()
            raise TimeoutException(error_msg)

    def find_all(self, locator, timeout=10):
        """Находит все элементы с ожиданием хотя бы одного"""
        try:
            logging.info(f"Ищу все {locator}")
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            logging.info(f"Найдено {len(elements)} элементов {locator}")
            return elements
        except TimeoutException:
            error_msg = f"Не удалось найти {locator} за {timeout} секунд"
            logging.error(error_msg)
            logging.root.handlers[0].flush()
            raise TimeoutException(error_msg)

    def click(self, locator, timeout=10):
        """Клик по элементу с ожиданием кликабельности"""
        try:
            logging.info(f"Кликаю на {locator}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
        except TimeoutException:
            error_msg = f"Элемент {locator} не кликабелен в течение {timeout} секунд"
            logging.error(error_msg)
            logging.root.handlers[0].flush()
            raise TimeoutException(error_msg)

    def type(self, locator, text, timeout=10):
        """Ввод текста в элемент"""
        try:
            logging.info(f"Ввожу текст '{text}' в {locator}")
            element = self.find(locator, timeout)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            error_msg = f"Не удалось ввести текст в {locator}: {e}"
            logging.error(error_msg)
            logging.root.handlers[0].flush()
            raise

    def is_visible(self, locator, timeout=10):
        """Проверяет видимость элемента"""
        try:
            logging.info(f"Проверяю видимость {locator}")
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            logging.info(f"Элемент {locator} не видим")
            return False

    def wait_for_page_loaded(self, timeout=30):
        """Ожидание полной загрузки страницы"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                logging.info("Страница полностью загружена")
                return True
            time.sleep(0.5)

        error_msg = f"Страница не загрузилась за {timeout} секунд"
        logging.error(error_msg)
        logging.root.handlers[0].flush()
        raise TimeoutException(error_msg)


class SearchPage(BasePage):
    """Класс, представляющий страницу поиска DuckDuckGo"""

    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://duckduckgo.com"
        self.search_box = Locator(By.ID, "searchbox_input", "поле ввода поискового запроса")
        self.search_button = Locator(By.CSS_SELECTOR, "button[aria-label='Search']", "кнопка поиска")
        self.results = Locator(By.CSS_SELECTOR, ".react-results--main", "контейнер результата поиска")
        self.result_titles = Locator(By.CSS_SELECTOR, "h2", "заголовок результата поиска")
        self.non_existent = Locator(By.ID, "this-element-does-not-exist", "несуществующий элемент")

    def open(self):
        """Открывает страницу поиска DuckDuckGo"""
        return super().open(self.url)

    def search(self, query):
        """Выполняет поиск по запросу"""
        logging.info(f"Выполняю поиск: {query}")

        self.type(self.search_box, query)

        try:
            self.click(self.search_button)
        except TimeoutException:
            logging.info("Кнопка поиска не найдена, использую Enter")
            self.find(self.search_box).send_keys(Keys.RETURN)

        time.sleep(2)
        self.wait_for_page_loaded()
        self.find(self.result_titles)
        logging.info("Результаты поиска загружены")
        logging.root.handlers[0].flush()
        return self

    def get_results_count(self):
        """Получает количество результатов поиска"""
        titles = self.find_all(self.result_titles)
        return len(titles)

    def has_result_containing(self, text):
        """Проверяет наличие результата, содержащего заданный текст"""
        logging.info(f"Проверяю наличие результата с текстом: {text}")
        titles = self.find_all(self.result_titles)
        for title in titles:
            if text.lower() in title.text.lower():
                logging.info(f"Найден результат с текстом: {text}")
                return True
        logging.info(f"Не найден результат с текстом: {text}")
        return False

    def find_non_existent_element(self):
        """Метод, который будет вызывать ошибку для демонстрации логов"""
        try:
            return self.find(self.non_existent, 3)
        except TimeoutException as e:
            logging.error(f"Ошибка при поиске элемента: {e}")
            logging.root.handlers[0].flush()
            raise


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
    logging.info("Запуск тестов подхода с базовой страницей")
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