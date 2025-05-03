from tests.custom_testing.pages import GoogleHomePage, GoogleSearchResultsPage


class PageManager:
    def __init__(self, driver):
        self.driver = driver
        self.home_page = GoogleHomePage(driver)
        self.search_results_page = GoogleSearchResultsPage(driver)
        self.current_page = None

    def open_home_page(self):
        self.home_page.open()
        self.current_page = self.home_page
        return self.home_page

    def search(self, query):
        if not isinstance(self.current_page, GoogleHomePage):
            self.open_home_page()

        self.home_page.search_box.search(query)
        self.current_page = self.search_results_page
        return self.search_results_page