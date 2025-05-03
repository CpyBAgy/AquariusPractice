from tests.custom_testing.pages import GoogleHomePage


def test_google_search_direct(driver):
    """Тест поиска с использованием Page Objects напрямую"""
    home_page = GoogleHomePage(driver)
    home_page.open()

    results_page = home_page.search_box.search("Python selenium testing")

    # Проверки
    assert results_page.get_results_count() > 0
    assert results_page.has_result_containing("Selenium")


def test_google_search_with_enter(driver):
    """Тест поиска с использованием клавиши Enter"""
    home_page = GoogleHomePage(driver)
    home_page.open()

    results_page = home_page.search_box.search_with_enter("PyTest framework")

    # Проверки
    assert results_page.get_results_count() > 0
    assert results_page.has_result_containing("PyTest")
    assert results_page.has_result_containing("framework")


def test_google_search_with_page_manager(page_manager):
    """Тест поиска с использованием Page Manager"""
    page_manager.open_home_page()
    results_page = page_manager.search("Page Object Model selenium")

    # Проверки
    assert results_page.get_results_count() > 0
    assert results_page.has_result_containing("Page Object")