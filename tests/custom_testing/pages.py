from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.custom_testing.elements import Element


class BasePage:
    def __init__(self, driver, base_url="https://google.com"):
        self.driver = driver
        self.base_url = base_url

    def open(self, url=""):
        self.driver.get(f"{self.base_url}{url}")
        return self

    def get_title(self):
        return self.driver.title

    def wait_for_page_load(self):
        return self


class SearchBox:
    """Компонент поисковой строки Google"""

    def __init__(self, driver):
        self.driver = driver
        self.search_input = Element(driver, (By.NAME, "q"))
        self.search_buttons = [
            Element(driver, (By.CSS_SELECTOR, "input[name='btnK']")),
            Element(driver, (By.XPATH, "//input[@value='Google Search']")),
            Element(driver, (By.XPATH, "//button[@aria-label='Google Search']")),
            Element(driver, (By.CSS_SELECTOR, ".gNO89b"))
        ]

    def search(self, query):
        self.search_input.type(query)
        for button in self.search_buttons:
            try:
                button.click()
                return GoogleSearchResultsPage(self.driver)
            except:
                continue

        self.search_input.type(Keys.RETURN)
        return GoogleSearchResultsPage(self.driver)

    def search_with_enter(self, query):
        self.search_input.type(query + Keys.RETURN)
        return GoogleSearchResultsPage(self.driver)


class GoogleHomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.search_box = SearchBox(driver)
        self.form = Element(driver, (By.TAG_NAME, "form"))

    def is_loaded(self):
        return self.form.is_visible()


class GoogleSearchResultsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.search_results = Element(driver, (By.CSS_SELECTOR, "div.g"))
        self.result_titles = Element(driver, (By.CSS_SELECTOR, "h3"))
        self.stats = Element(driver, (By.ID, "result-stats"))

    def is_loaded(self):
        return self.result_titles.is_visible() or self.stats.is_visible()

    def get_results_count(self):
        return len(self.result_titles.find_all())

    def get_first_result_title(self):
        try:
            return self.result_titles.get_text()
        except:
            return None

    def has_result_containing(self, text):
        all_titles = self.result_titles.find_all()
        for title in all_titles:
            if text.lower() in title.text.lower():
                return True
        return False

    def click_result_with_text(self, text):
        all_titles = self.result_titles.find_all()
        for title in all_titles:
            if text.lower() in title.text.lower():
                title.click()
                return True
        return False