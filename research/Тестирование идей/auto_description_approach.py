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

LOG_FILE_PATH = str(LOGS_DIR / "auto_description_test.log")

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
    LOG_FILE_PATH = os.path.join(home_dir, "auto_description_test.log")
    print(f"Пробуем создать файл в домашней директории: {LOG_FILE_PATH}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logging.info("*** Инициализация логирования для auto_description_approach.py ***")
logging.info(f"Лог-файл будет создан по пути: {LOG_FILE_PATH}")

logging.root.handlers[0].flush()


class LocatorWithDescription:
    def __init__(self, locator):
        self.locator = locator
        self._description = self._generate_description()

    def __iter__(self):
        return iter(self.locator)

    def __str__(self):
        return self._description

    @property
    def by(self):
        return self.locator[0]

    @property
    def value(self):
        return self.locator[1]

    def _generate_description(self):
        """Автоматически генерирует описание на основе типа локатора и значения"""
        locator_type = self.by
        locator_value = self.value

        element_type = ""
        description = ""

        if isinstance(locator_value, str):
            if 'button' in locator_value.lower() or 'btn' in locator_value.lower():
                element_type = "кнопка"
            elif 'input' in locator_value.lower() or 'username' in locator_value.lower() or 'password' in locator_value.lower() or 'email' in locator_value.lower():
                element_type = "поле ввода"
            elif 'link' in locator_value.lower() or locator_type == By.LINK_TEXT:
                element_type = "ссылка"
            elif 'checkbox' in locator_value.lower() or 'remember' in locator_value.lower():
                element_type = "чекбокс"
            elif 'form' in locator_value.lower():
                element_type = "форма"
            elif locator_type == By.TAG_NAME and locator_value in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                element_type = "заголовок"
            else:
                element_type = "элемент"
        else:
            element_type = "элемент"

        if locator_type == By.ID:
            description = f"{element_type} (ID: {locator_value})"
        elif locator_type == By.NAME:
            description = f"{element_type} (name: {locator_value})"
        elif locator_type == By.CLASS_NAME:
            description = f"{element_type} (класс: {locator_value})"
        elif locator_type == By.CSS_SELECTOR:
            description = f"{element_type} (CSS: {locator_value})"
        elif locator_type == By.XPATH:
            description = f"{element_type} (XPath: {locator_value})"
        elif locator_type == By.LINK_TEXT:
            description = f"{element_type} (text: {locator_value})"
        elif locator_type == By.TAG_NAME:
            description = f"{element_type} (тег: {locator_value})"

        if locator_value == 'q' and locator_type == By.NAME:
            description = f"поле ввода поискового запроса (name: {locator_value})"
        elif isinstance(locator_value, str) and 'search' in locator_value.lower():
            description = f"поле поиска ({locator_type}: {locator_value})"

        return description


class SearchPage:
    """Класс, представляющий страницу поиска DuckDuckGo"""

    def __init__(self, driver):
        self.driver = driver

        self.search_box = LocatorWithDescription((By.ID, "searchbox_input"))
        self.search_button = LocatorWithDescription((By.CSS_SELECTOR, "button[aria-label='Search']"))
        self.result_titles = LocatorWithDescription((By.CSS_SELECTOR, "h2"))
        self.non_existent = LocatorWithDescription((By.ID, "this-element-does-not-exist"))

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

        logging.info(f"Ищу {self.search_box}")
        try:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.search_box)
            )
            search_input.clear()
            search_input.send_keys(query)
            logging.info(f"Ввел поисковый запрос: {query}")

            logging.info(f"Ищу {self.search_button}")
            try:
                search_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.search_button)
                )
                search_button.click()
                logging.info("Нажал кнопку поиска")
            except TimeoutException:
                logging.info("Кнопка поиска не найдена, использую Enter")
                search_input.send_keys(Keys.RETURN)
                logging.info("Отправил Enter")

            logging.info("Жду загрузки результатов")
            time.sleep(2)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.result_titles)
            )
            logging.info("Результаты поиска загружены")
            logging.root.handlers[0].flush()
            return self
        except Exception as e:
            logging.error(f"Ошибка при поиске: {e}")
            logging.root.handlers[0].flush()
            raise

    def get_results_count(self):
        logging.info(f"Ищу {self.result_titles}")
        try:
            time.sleep(1)
            titles = self.driver.find_elements(*self.result_titles)
            count = len(titles)
            logging.info(f"Найдено результатов: {count}")
            return count
        except Exception as e:
            logging.error(f"Ошибка при подсчете результатов: {e}")
            logging.root.handlers[0].flush()
            return 0

    def has_result_containing(self, text):
        logging.info(f"Проверяю наличие результата с текстом: {text}")
        try:
            titles = self.driver.find_elements(*self.result_titles)
            for title in titles:
                title_text = title.text.lower()
                if text.lower() in title_text:
                    logging.info(f"Найден результат с текстом: {text}")
                    return True
            logging.info(f"Не найден результат с текстом: {text}")
            return False
        except Exception as e:
            logging.error(f"Ошибка при проверке результатов: {e}")
            logging.root.handlers[0].flush()
            return False

    def find_non_existent_element(self):
        """Метод, который будет вызывать ошибку для демонстрации логов"""
        logging.info(f"Пытаюсь найти {self.non_existent}")
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.non_existent)
            )
            return element
        except TimeoutException as e:
            logging.error(f"Ошибка при поиске элемента: Не удалось найти {self.non_existent}")
            logging.root.handlers[0].flush()
            raise


# Тесты
def test_search_success():
    """Тест успешного поиска"""
    logging.info("=== Начало теста успешного поиска ===")

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

        results_count = search_page.get_results_count()
        logging.info(f"Количество результатов: {results_count}")

        assert results_count > 0, "Ожидались результаты поиска"

        has_result = search_page.has_result_containing("Python")
        logging.info(f"Наличие результата с 'Python': {has_result}")

        assert has_result, "Ожидался результат с 'Python'"

        logging.info("✓ Тест успешного поиска прошел")
        logging.root.handlers[0].flush()
    except Exception as e:
        logging.error(f"✗ Тест провалился: {e}")
        logging.root.handlers[0].flush()
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = f"error_screenshot_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
            logging.info(f"Скриншот сохранен: {screenshot_path}")
        except Exception as screenshot_error:
            logging.error(f"Не удалось сохранить скриншот: {screenshot_error}")
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
    logging.info("Запуск тестов автоматического описания локаторов")
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