import logging
import pytest
from examples.amazon.pages import AmazonLoginPage


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

    home_page = amazon_login

    search_results = home_page.header.search("levoit air purifier")

    product_page = search_results.select_product(0)

    product_price_text = product_page.get_product_price()
    product_price = float(product_price_text.replace("$", "").replace(",", ""))  # $12,123,132 -> 12123132.0

    product_page.add_to_cart()

    cart_page = home_page.header.go_to_cart()

    cart_items = cart_page.get_cart_items()
    assert len(cart_items) > 0, "Корзина пуста"

    cart_items[0].increase_quantity()  # Увеличиваем количество товара на 1

    cart_subtotal_text = cart_page.get_subtotal()
    cart_subtotal = float(cart_subtotal_text.replace("$", "").replace(",", ""))  # $12,123,132 -> 12123132.0

    expected_subtotal = product_price * 2
    assert abs(cart_subtotal - expected_subtotal) < 0.01, \
        f"Подытог {cart_subtotal} не соответствует ожидаемому {expected_subtotal}"
