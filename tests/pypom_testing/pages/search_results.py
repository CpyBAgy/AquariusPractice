from pypom import Page, Region
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class SearchResultRegion(Region):
    """Представляет отдельный результат поиска Google"""

    _title_locator = (By.CSS_SELECTOR, "h3")
    _link_locator = (By.CSS_SELECTOR, "a")

    @property
    def title(self):
        return self.find_element(*self._title_locator).text

    @property
    def link(self):
        return self.find_element(*self._link_locator).get_attribute("href")

    def contains_text(self, text):
        return text.lower() in self.title.lower()

    def click(self):
        self.find_element(*self._title_locator).click()


class GoogleSearchResultsPage(Page):
    """Страница с результатами поиска Google"""

    _result_items_locator = (By.CSS_SELECTOR, "div.g")
    _result_titles_locator = (By.CSS_SELECTOR, "h3")
    _stats_locator = (By.ID, "result-stats")

    @property
    def loaded(self):
        return (self.is_element_displayed(*self._result_titles_locator) or
                self.is_element_displayed(*self._stats_locator))

    @property
    def search_results(self):
        results = self.find_elements(*self._result_items_locator)
        return [SearchResultRegion(self, item) for item in results]

    def get_results_count(self):
        return len(self.find_elements(*self._result_titles_locator))

    def get_first_result_title(self):
        try:
            return self.find_element(*self._result_titles_locator).text
        except NoSuchElementException:
            return None

    def has_result_containing(self, text):
        titles = self.find_elements(*self._result_titles_locator)
        for title in titles:
            if text.lower() in title.text.lower():
                return True
        return False