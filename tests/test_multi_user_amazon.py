import logging
from examples.amazon.v1.pages_v1 import AmazonLoginPageV1


def test_two_users_parallel_shopping(multi_page_factory):
    """
    Улучшенный тест параллельной работы двух пользователей:
    - Драйверы создаются автоматически при создании страниц
    - Не нужно вручную создавать драйверы
    - В логах отображаются понятные имена драйверов
    """
    logging.info("=== Начало улучшенного теста с двумя пользователями ===")

    logging.info(">>> Пользователь 1: создаем страницу логина")
    login_page_user1 = multi_page_factory.create_page(AmazonLoginPageV1, "default", version=None)
    login_page_user1.open()
    home_page_user1 = login_page_user1.login("vancous220@gmail.com", "MyStrongPassword")

    logging.info(">>> Пользователь 2: создаем страницу логина")
    login_page_user2 = multi_page_factory.create_page(AmazonLoginPageV1, "user2", version=None)
    login_page_user2.open()
    home_page_user2 = login_page_user2.login("test_user2@example.com", "Password123", version=None)

    logging.info(">>> Пользователь 3: создаем страницу логина в Firefox")
    login_page_user3 = multi_page_factory.create_page(
        AmazonLoginPageV1,
        driver_name="user3_firefox",
        browser_type="firefox",
        headless=True,
        version=None
    )
    login_page_user3.open()

    search_query = "levoit air purifier"

    logging.info(f">>> Пользователь 1: ищет '{search_query}'")
    search_results_user1 = home_page_user1.header.search(search_query)

    logging.info(f">>> Пользователь 2: ищет '{search_query}'")
    search_results_user2 = home_page_user2.header.search(search_query)

    logging.info(">>> Пользователь 1: выбирает первый товар")
    product_page_user1 = search_results_user1.select_product(0)
    product_title_user1 = product_page_user1.get_product_title()

    logging.info(">>> Пользователь 2: выбирает второй товар")
    product_page_user2 = search_results_user2.select_product(1)
    product_title_user2 = product_page_user2.get_product_title()

    logging.info(">>> Пользователь 1: добавляет товар в корзину")
    product_page_user1.add_to_cart()

    logging.info(">>> Пользователь 2: добавляет товар в корзину")
    product_page_user2.add_to_cart()

    logging.info(">>> Проверяем корзину пользователя 1")
    cart_page_user1 = home_page_user1.header.go_to_cart()
    cart_items_user1 = cart_page_user1.get_cart_items()
    assert len(cart_items_user1) == 1, f"Ожидался 1 товар в корзине пользователя 1, найдено {len(cart_items_user1)}"

    logging.info(">>> Проверяем корзину пользователя 2")
    cart_page_user2 = home_page_user2.header.go_to_cart()
    cart_items_user2 = cart_page_user2.get_cart_items()
    assert len(cart_items_user2) == 1, f"Ожидался 1 товар в корзине пользователя 2, найдено {len(cart_items_user2)}"

    cart_item_title_user1 = cart_items_user1[0].get_title()
    cart_item_title_user2 = cart_items_user2[0].get_title()

    logging.info(f"Пользователь 1 выбрал: {product_title_user1[:50]}...")
    logging.info(f"Пользователь 2 выбрал: {product_title_user2[:50]}...")

    assert cart_item_title_user1 in product_title_user1 or product_title_user1 in cart_item_title_user1, \
        "Товар в корзине пользователя 1 не соответствует выбранному"
    assert cart_item_title_user2 in product_title_user2 or product_title_user2 in cart_item_title_user2, \
        "Товар в корзине пользователя 2 не соответствует выбранному"

    logging.info("✅ Улучшенный тест успешно завершен - драйверы создавались автоматически!")
