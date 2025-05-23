import logging
import pytest
from examples.amazon.pages import AmazonLoginPage, AmazonHomePage


@pytest.fixture
def amazon_home(driver):
    """Фикстура для входа в аккаунт Amazon и возврата домашней страницы"""
    login_page = AmazonLoginPage(driver)
    login_page.open()
    home_page = login_page.login("vancous220@gmail.com", "MyStrongPassword")
    return home_page


def test_search_add_to_cart_checkout(amazon_home):
    """
    Тест полного цикла покупки:
    1. Вход в аккаунт
    2. Поиск товара
    3. Добавление в корзину
    4. Увеличение количества
    5. Проверка общей суммы на странице оформления заказа
    """
    logging.info("=== Начало теста с добавлением элемента в корзину и проверкой стоимости ===")

    home_page = amazon_home

    search_results = home_page.header.search("levoit air purifier")

    product_page = search_results.select_product(0)

    # Используем новый метод для получения цены как float
    product_price = product_page.get_product_price_as_float()

    product_page.add_to_cart()

    cart_page = home_page.header.go_to_cart()

    cart_items = cart_page.get_cart_items()
    assert len(cart_items) > 0, "Корзина пуста"

    cart_items[0].increase_quantity()  # Увеличиваем количество товара на 1

    # Используем новый метод для получения суммы как float
    cart_subtotal = cart_page.get_subtotal_as_float()

    expected_subtotal = product_price * 2
    assert abs(cart_subtotal - expected_subtotal) < 0.01, \
        f"Подытог {cart_subtotal} не соответствует ожидаемому {expected_subtotal}"