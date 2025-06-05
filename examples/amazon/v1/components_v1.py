"""
Компоненты Amazon версии 1 - базовая реализация
"""
from selenium.webdriver.common.by import By

from page_object_library import ElementGroup, auto_log, Input, Button, BaseElement, Link


class SearchSuggestionComponentV1(ElementGroup):
    """Компонент выпадающих подсказок при поиске"""

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.suggestion_list = self.page.find_elements((By.CSS_SELECTOR, "div.s-suggestion"))

    @auto_log
    def select_suggestion(self, index=0):
        """Выбирает подсказку поиска по индексу"""
        if len(self.suggestion_list) > index:
            self.suggestion_list[index].click()
            from examples.amazon.v1.pages_v1 import AmazonSearchResultsPage
            return self.page.navigate_to(AmazonSearchResultsPage)
        raise ValueError(f"Подсказка с индексом {index} не найдена")


class HeaderComponentV1(ElementGroup):
    """Компонент верхнего меню Amazon"""

    def __init__(self, page):
        self.page = page
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.search_input = Input(self.page, (By.ID, "twotabsearchtextbox"), "Поле поиска")
        self.search_button = Button(self.page, (By.ID, "nav-search-submit-button"), "Кнопка поиска")
        self.account_menu = BaseElement(self.page, (By.ID, "nav-link-accountList"), "Меню аккаунта")
        self.cart_icon = BaseElement(self.page, (By.ID, "nav-cart"), "Иконка корзины")
        self.orders_link = Link(self.page, (By.ID, "nav-orders"), "Ссылка на заказы")

    @auto_log
    def search(self, search_text):
        """Выполняет поиск товара"""
        self.search_input.type(search_text)
        self.search_button.click()
        from examples.amazon.v1.pages_v1 import AmazonSearchResultsPage
        return self.page.navigate_to(AmazonSearchResultsPage)

    @auto_log
    def go_to_cart(self):
        """Переходит в корзину"""
        self.cart_icon.click()
        from examples.amazon.v1.pages_v1 import AmazonCartPage
        return self.page.navigate_to(AmazonCartPage)

    @auto_log
    def open_account_menu(self):
        """Открывает меню учетной записи"""
        self.account_menu.click()
        return self


class CartItemComponentV1(ElementGroup):
    """Компонент элемента корзины"""

    def __init__(self, page, item_element):
        self.item_element = item_element
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.increment_button = Button(
            self.page,
            (By.CSS_SELECTOR, "input[data-action='increase-quantity']"),
            "Кнопка увеличения количества",
            self.item_element
        )
        self.decrement_button = Button(
            self.page,
            (By.CSS_SELECTOR, "input[data-action='decrease-quantity']"),
            "Кнопка уменьшения количества",
            self.item_element
        )
        self.delete_button = Button(
            self.page,
            (By.CSS_SELECTOR, "input[value='Delete']"),
            "Кнопка удаления",
            self.item_element
        )

    @auto_log
    def increase_quantity(self):
        """Увеличивает количество товара на 1"""
        self.increment_button.click()
        self.page.wait_for_page_loaded()
        return self

    @auto_log
    def decrease_quantity(self):
        """Уменьшает количество товара на 1"""
        self.decrement_button.click()
        self.page.wait_for_page_loaded()
        return self

    @auto_log
    def delete(self):
        """Удаляет товар из корзины"""
        self.delete_button.click()
        self.page.wait_for_page_loaded()
        return self.page

    @auto_log
    def get_title(self):
        """Получает название товара"""
        title_element = self.page.find_element((By.CSS_SELECTOR, "span.a-truncate-cut"))
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара"""
        price_element = self.page.find_element((By.CSS_SELECTOR, "span.sc-price"))
        return price_element.get_text().strip()


class ProductDetailsComponentV1(ElementGroup):
    """Компонент деталей товара"""

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.price_whole = BaseElement(
            self.page,
            (By.CSS_SELECTOR, "span.a-price .a-price-whole"),
            "Целая часть цены"
        )
        self.price_fraction = BaseElement(
            self.page,
            (By.CSS_SELECTOR, "span.a-price .a-price-fraction"),
            "Дробная часть цены"
        )
        self.alt_price = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".a-price .a-offscreen"),
            "Альтернативная цена"
        )
        self.price_block = BaseElement(
            self.page,
            (By.CSS_SELECTOR, "#priceblock_ourprice, #price_inside_buybox"),
            "Блок цены"
        )
        self.add_to_cart_button = Button(
            self.page,
            (By.ID, "add-to-cart-button"),
            "Кнопка добавления в корзину"
        )

    @auto_log
    def get_title(self):
        """Получает название товара"""
        title_element = self.page.find_element((By.ID, "productTitle"))
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара"""
        try:
            whole = self.price_whole.get_text().strip()
            fraction = self.price_fraction.get_text().strip()
            return f"{whole}.{fraction}"
        except:
            try:
                price_text = self.alt_price.get_attribute("innerText")
                return price_text.replace("$", "").strip()
            except:
                try:
                    return self.price_block.get_text().replace("$", "").strip()
                except:
                    raise Exception("Не удалось найти цену товара на странице")

    @auto_log
    def get_price_as_float(self):
        """Получает цену товара как число с плавающей точкой"""
        price_text = self.get_price()
        return self.parse_price_to_float(price_text)

    @staticmethod
    def parse_price_to_float(price_text):
        """Преобразует текстовое представление цены в float

        Args:
            price_text: Строка с ценой, например "$12,123.45" или "12,123.45"

        Returns:
            float: Числовое значение цены
        """
        clean_price = price_text.replace("$", "").replace(",", "").strip()
        return float(clean_price)

    @auto_log
    def add_to_cart(self):
        """Добавляет товар в корзину"""
        self.add_to_cart_button.click()
        self.page.wait_for_page_loaded()

        if "cart" in self.page.driver.current_url:
            from examples.amazon.v1.pages_v1 import AmazonCartPage
            return self.page.navigate_to(AmazonCartPage)
        return self.page