import logging
from examples.amazon.pages import AmazonLoginPage


def test_two_users_parallel_shopping(multi_driver, multi_page_factory):
    """
    Тест параллельной работы двух пользователей:
    1. Оба пользователя входят в свои аккаунты
    2. Оба ищут один и тот же товар
    3. Оба добавляют товар в корзину
    4. Проверяем, что у каждого в корзине свой товар (изолированные сессии)
    """
    logging.info("=== Начало теста с двумя пользователями ===")

    # Создаем второй драйвер для второго пользователя
    multi_driver.create_driver("user2", "chrome", headless=False)

    # Пользователь 1: вход в аккаунт
    logging.info(">>> Пользователь 1: начинаем вход")
    login_page_user1 = multi_page_factory.create_page(AmazonLoginPage, "default")
    login_page_user1.open()
    home_page_user1 = login_page_user1.login("vancous220@gmail.com", "MyStrongPassword")

    # Пользователь 2: вход в аккаунт
    logging.info(">>> Пользователь 2: начинаем вход")
    login_page_user2 = multi_page_factory.create_page(AmazonLoginPage, "user2")
    login_page_user2.open()
    home_page_user2 = login_page_user2.login("test_user2@example.com", "Password123")

    # Оба пользователя ищут один и тот же товар
    search_query = "levoit air purifier"

    logging.info(f">>> Пользователь 1: ищет '{search_query}'")
    search_results_user1 = home_page_user1.header.search(search_query)

    logging.info(f">>> Пользователь 2: ищет '{search_query}'")
    search_results_user2 = home_page_user2.header.search(search_query)

    # Пользователь 1: выбирает первый товар
    logging.info(">>> Пользователь 1: выбирает первый товар")
    product_page_user1 = search_results_user1.select_product(0)
    product_title_user1 = product_page_user1.get_product_title()
    product_price_user1 = product_page_user1.get_product_price_as_float()

    # Пользователь 2: выбирает второй товар (для разнообразия)
    logging.info(">>> Пользователь 2: выбирает второй товар")
    product_page_user2 = search_results_user2.select_product(1)
    product_title_user2 = product_page_user2.get_product_title()
    product_price_user2 = product_page_user2.get_product_price_as_float()

    # Оба добавляют товары в корзину
    logging.info(">>> Пользователь 1: добавляет товар в корзину")
    product_page_user1.add_to_cart()

    logging.info(">>> Пользователь 2: добавляет товар в корзину")
    product_page_user2.add_to_cart()

    # Проверяем корзины
    logging.info(">>> Проверяем корзину пользователя 1")
    cart_page_user1 = home_page_user1.header.go_to_cart()
    cart_items_user1 = cart_page_user1.get_cart_items()
    assert len(cart_items_user1) == 1, f"Ожидался 1 товар в корзине пользователя 1, найдено {len(cart_items_user1)}"

    logging.info(">>> Проверяем корзину пользователя 2")
    cart_page_user2 = home_page_user2.header.go_to_cart()
    cart_items_user2 = cart_page_user2.get_cart_items()
    assert len(cart_items_user2) == 1, f"Ожидался 1 товар в корзине пользователя 2, найдено {len(cart_items_user2)}"

    # Проверяем, что товары соответствуют выбранным
    cart_item_title_user1 = cart_items_user1[0].get_title()
    cart_item_title_user2 = cart_items_user2[0].get_title()

    logging.info(f"Пользователь 1 выбрал: {product_title_user1[:50]}...")
    logging.info(f"Пользователь 2 выбрал: {product_title_user2[:50]}...")

    # Проверяем изоляцию сессий - у каждого пользователя свой товар
    assert cart_item_title_user1 in product_title_user1 or product_title_user1 in cart_item_title_user1, \
        "Товар в корзине пользователя 1 не соответствует выбранному"
    assert cart_item_title_user2 in product_title_user2 or product_title_user2 in cart_item_title_user2, \
        "Товар в корзине пользователя 2 не соответствует выбранному"

    logging.info("✅ Тест успешно завершен - сессии пользователей изолированы")
