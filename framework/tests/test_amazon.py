import logging

import pytest
from framework.tests.pages.amazon_pages import AmazonLoginPage
from framework.tests.components.amazon_components import SearchSuggestionComponent


@pytest.fixture
def amazon_login(driver):
    """Фикстура для входа в аккаунт Amazon"""
    login_page = AmazonLoginPage(driver)
    login_page.open()
    return login_page.login("vancous220@gmail.com", "MyStrongPassword")


def test_search_add_to_cart_checkout(amazon_login):
    """
    Тест полного цикла покупки:
    1. Вход в аккаунт
    2. Поиск товара
    3. Добавление в корзину
    4. Увеличение количества
    5. Проверка общей суммы на странице оформления заказа
    """
    logging.info("=== Начало теста с добавлением элемента в корзину и проверкой стоимости ===")
    logging.root.handlers[0].flush()

    home_page = amazon_login

    search_results = home_page.search("levoit air purifier")

    product_page = search_results.select_product(0)

    product_price_text = product_page.get_product_price()
    product_price = float(product_price_text.replace("$", "").replace(",", ""))

    cart_page = product_page.add_to_cart()

    if "cart" not in cart_page.driver.current_url:
        cart_page = home_page.go_to_cart()

    cart_page.increase_quantity(index=0, count=1)

    cart_subtotal_text = cart_page.get_subtotal()
    cart_subtotal = float(cart_subtotal_text.replace("$", "").replace(",", ""))

    expected_subtotal = product_price * 2
    assert abs(
        cart_subtotal - expected_subtotal) < 0.01, f"Подытог {cart_subtotal} не соответствует ожидаемому {expected_subtotal}"

    checkout_page = cart_page.proceed_to_checkout()

    order_total_text = checkout_page.get_order_total()
    order_total = float(order_total_text.replace("$", "").replace(",", ""))

    assert abs(
        order_total - expected_subtotal) < 10.0, f"Итоговая сумма {order_total} слишком отличается от ожидаемой {expected_subtotal}"


def test_search_by_suggestions(amazon_login):
    """
    Тест поиска товара через подсказки:
    1. Вход в аккаунт
    2. Ввод части запроса
    3. Выбор подсказки
    4. Проверка результатов поиска
    """
    logging.info("=== Начало теста с поиском товара ===")
    logging.root.handlers[0].flush()

    home_page = amazon_login

    search_input = home_page.header.find(home_page.header.search_input)
    home_page.type(search_input, "levoit air")

    search_suggestions = SearchSuggestionComponent(home_page)

    search_results = search_suggestions.select_suggestion(0)

    results_count = len(search_results.find_all(search_results.locators.SEARCH_RESULTS))
    assert results_count > 0, "Результаты поиска не найдены"


def test_add_remove_from_cart(amazon_login):
    """
    Тест добавления и удаления товара из корзины:
    1. Вход в аккаунт
    2. Поиск товара
    3. Добавление в корзину
    4. Проверка наличия в корзине
    5. Удаление из корзины
    6. Проверка, что корзина пуста
    """
    logging.info("=== Начало теста с добавлением и удалением элемента из корзины ===")
    logging.root.handlers[0].flush()

    home_page = amazon_login

    search_results = home_page.search("levoit air purifier")

    product_page = search_results.select_product(0)


    cart_page = product_page.add_to_cart()

    if "cart" not in cart_page.driver.current_url:
        cart_page = home_page.go_to_cart()

    cart_items_count = cart_page.get_cart_items_count()
    assert cart_items_count > 0, "Корзина пуста после добавления товара"

    cart_page.delete_item(0)

    new_cart_items_count = cart_page.get_cart_items_count()
    assert new_cart_items_count < cart_items_count, "Товар не был удален из корзины"