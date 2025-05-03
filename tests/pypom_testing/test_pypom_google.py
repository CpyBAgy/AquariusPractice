from tests.pypom_testing.pages.home import GoogleHomePage


def test_google_search_direct(driver):
    """Тест прямого поиска с использованием Page Objects"""
    home_page = GoogleHomePage(driver).open()

    results_page = home_page.search_box.search("Python selenium testing")

    # Проверки
    assert results_page.get_results_count() > 0
    assert results_page.has_result_containing("Selenium")
    assert results_page.has_result_containing("Python")


def test_google_search_with_enter(driver):
    """Тест поиска с использованием клавиши Enter"""
    home_page = GoogleHomePage(driver).open()
    results_page = home_page.search_box.search_with_enter("PyTest framework")

    # Проверки
    assert results_page.get_results_count() > 0
    assert results_page.has_result_containing("PyTest")
    assert results_page.has_result_containing("framework")
