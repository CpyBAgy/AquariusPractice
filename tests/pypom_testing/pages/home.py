from pypom import Page, Region
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.pypom_testing.pages.search_results import GoogleSearchResultsPage


class SearchBoxRegion(Region):
    """Регион, представляющий поисковую строку Google"""

    _search_input_locator = (By.NAME, "q")
    _search_button_locator = (By.CSS_SELECTOR, "input[name='btnK']")

    @property
    def search_input(self):
        return self.find_element(*self._search_input_locator)

    @property
    def search_button(self):
        try:
            return self.find_element(*self._search_button_locator)
        except:
            raise Exception("Не удалось найти кнопку поиска Google")

    def search(self, query):
        self.search_input.clear()
        self.search_input.send_keys(query)
        try:
            self.search_button.click()
        except:
            self.search_input.send_keys(Keys.RETURN)
        return GoogleSearchResultsPage(self.driver, self.page.base_url)

    def search_with_enter(self, query):
        self.search_input.clear()
        self.search_input.send_keys(query)
        self.search_input.send_keys(Keys.RETURN)
        return GoogleSearchResultsPage(self.driver, self.page.base_url)


class GoogleHomePage(Page):
    """Главная страница Google"""

    URL_TEMPLATE = 'https://www.google.com/'

    _search_form_locator = (By.TAG_NAME, "form")

    @property
    def loaded(self):
        return self.is_element_displayed(*self._search_form_locator)

    @property
    def search_box(self):
        return SearchBoxRegion(self, self.find_element(*self._search_form_locator))
