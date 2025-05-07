import logging
import os
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = str(LOGS_DIR / "basic_test.log")

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
    LOG_FILE_PATH = os.path.join(home_dir, "basic_test.log")
    print(f"Пробуем создать файл в домашней директории: {LOG_FILE_PATH}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logging.info("*** Инициализация логирования для basic_approach.py ***")
logging.info(f"Лог-файл будет создан по пути: {LOG_FILE_PATH}")
logging.root.handlers[0].flush()


class SearchPage:
    """Класс, представляющий страницу поиска DuckDuckGo"""

    def __init__(self, driver):
        self.driver = driver
        self.search_box = (By.ID, "searchbox_input")
        self.search_button = (By.CSS_SELECTOR, "button[aria-label='Search']")
        self.results = (By.CSS_SELECTOR, ".react-results--main")
        self.result_titles = (By.CSS_SELECTOR, "h2")
        self.non_existent = (By.ID, "this-element-does-not-exist")

    def open(self, url="https://duckduckgo.com/"):
        logging.info(f"Открываю страницу {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info(f"Страница {url} загружена")
        logging.root.handlers[0].flush()
        return self

    def search(self, query):
        logging.info(f"Выполняю поиск: {query}")

        logging.info(f"Ищу элемент: {self.search_box}")
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.search_box)
        )
        search_input.clear()
        search_input.send_keys(query)

        logging.info(f"Ищу кнопку поиска: {self.search_button}")
        try:
            search_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.search_button)
            )
            search_button.click()
        except TimeoutException:
            logging.info("Кнопка поиска не найдена, использую Enter")
            search_input.send_keys(Keys.RETURN)

        logging.info("Жду загрузки результатов")
        time.sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.result_titles)
        )
        logging.info("Результаты поиска загружены")
        logging.root.handlers[0].flush()
        return self

    def get_results_count(self):
        logging.info(f"Ищу результаты поиска: {self.result_titles}")
        time.sleep(1)
        titles = self.driver.find_elements(*self.result_titles)
        count = len(titles)
        logging.info(f"Найдено результатов: {count}")
        return count

    def has_result_containing(self, text):
        logging.info(f"Проверяю наличие результата с текстом: {text}")
        titles = self.driver.find_elements(*self.result_titles)
        for title in titles:
            if text.lower() in title.text.lower():
                logging.info(f"Найден результат с текстом: {text}")
                return True
        logging.info(f"Не найден результат с текстом: {text}")
        return False

    def find_non_existent_element(self):
        """Метод, который будет вызывать ошибку для демонстрации логов"""
        logging.info(f"Пытаюсь найти несуществующий элемент: {self.non_existent}")
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.non_existent)
            )
            return element
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
    logging.info("Запуск тестов базового подхода")
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