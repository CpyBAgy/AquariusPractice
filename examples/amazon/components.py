from selenium.webdriver.common.by import By

from page_object_library import ElementGroup, auto_log, Input, Button, BaseElement, Link


class SearchSuggestionComponent(ElementGroup):
    """Компонент выпадающих подсказок при поиске"""
    SUGGESTION_ITEM = (By.CSS_SELECTOR, "div.s-suggestion")

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.suggestion_list = self.page.find_elements(self.SUGGESTION_ITEM)
        pass

    @auto_log
    def select_suggestion(self, index=0):
        """Выбирает подсказку поиска по индексу"""
        if len(self.suggestion_list) > index:
            self.suggestion_list[index].click()
            from examples.amazon.pages import AmazonSearchResultsPage
            return self.page.navigate_to(AmazonSearchResultsPage)
        raise ValueError(f"Подсказка с индексом {index} не найдена")


class HeaderComponent(ElementGroup):
    """Компонент верхнего меню Amazon"""
    NAVBAR = (By.ID, "navbar")
    SEARCH_INPUT = (By.ID, "twotabsearchtextbox")
    SEARCH_BUTTON = (By.ID, "nav-search-submit-button")
    ACCOUNT_MENU = (By.ID, "nav-link-accountList")
    CART_ICON = (By.ID, "nav-cart")
    ORDERS_LINK = (By.ID, "nav-orders")

    def __init__(self, page):
        self.page = page
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.search_input = Input(self.page, self.SEARCH_INPUT)
        self.search_button = Button(self.page, self.SEARCH_BUTTON)
        self.account_menu = BaseElement(self.page, self.ACCOUNT_MENU)
        self.cart_icon = BaseElement(self.page, self.CART_ICON)
        self.orders_link = Link(self.page, self.ORDERS_LINK)

    @auto_log
    def search(self, search_text):
        """Выполняет поиск товара"""
        self.search_input.type(search_text)
        self.search_button.click()
        from examples.amazon.pages import AmazonSearchResultsPage
        return self.page.navigate_to(AmazonSearchResultsPage)

    @auto_log
    def go_to_cart(self):
        """Переходит в корзину"""
        self.cart_icon.click()
        from examples.amazon.pages import AmazonCartPage
        return self.page.navigate_to(AmazonCartPage)

    @auto_log
    def open_account_menu(self):
        """Открывает меню учетной записи"""
        self.account_menu.click()
        return self


class CartItemComponent(ElementGroup):
    """Компонент элемента корзины"""
    INCREMENT_BUTTON = (By.CSS_SELECTOR, "input[data-action='increase-quantity']")
    DECREMENT_BUTTON = (By.CSS_SELECTOR, "input[data-action='decrease-quantity']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "input[value='Delete']")
    QUANTITY_FIELD = (By.CSS_SELECTOR, "input.sc-quantity-textfield")
    PRODUCT_TITLE = (By.CSS_SELECTOR, "span.a-truncate-cut")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "span.sc-price")

    def __init__(self, page, item_element):
        self.item_element = item_element
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.increment_button = Button(self.page, self.INCREMENT_BUTTON, self.item_element)
        self.decrement_button = Button(self.page, self.DECREMENT_BUTTON, self.item_element)
        self.delete_button = Button(self.page, self.DELETE_BUTTON, self.item_element)
        pass

    @auto_log
    def increment_button(self):
        """Возвращает кнопку увеличения количества"""
        return self.increment_button

    @auto_log
    def decrement_button(self):
        """Возвращает кнопку уменьшения количества"""
        return self.decrement_button

    @auto_log
    def delete_button(self):
        """Возвращает кнопку удаления"""
        return self.delete_button

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
        title_element = self.page.find_element(self.PRODUCT_TITLE)
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара"""
        price_element = self.page.find_element(self.PRODUCT_PRICE)
        return price_element.get_text().strip()


class ProductDetailsComponent(ElementGroup):
    """Компонент деталей товара"""
    PRODUCT_CONTAINER = (By.ID, "ppd")
    PRODUCT_TITLE = (By.ID, "productTitle")
    PRODUCT_PRICE_WHOLE = (By.CSS_SELECTOR, "span.a-price .a-price-whole")
    PRODUCT_PRICE_FRACTION = (By.CSS_SELECTOR, "span.a-price .a-price-fraction")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart-button")
    BUY_NOW_BUTTON = (By.ID, "buy-now-button")
    ALT_PRICE = (By.CSS_SELECTOR, ".a-price .a-offscreen")
    PRICE_BLOCK = (By.CSS_SELECTOR, "#priceblock_ourprice, #price_inside_buybox")

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.price_whole = BaseElement(self.page, self.PRODUCT_PRICE_WHOLE)
        self.price_fraction = BaseElement(self.page, self.PRODUCT_PRICE_FRACTION)
        self.alt_price = BaseElement(self.page, self.ALT_PRICE)
        self.price_block = BaseElement(self.page, self.PRICE_BLOCK)
        self.add_to_cart_button = Button(self.page, self.ADD_TO_CART_BUTTON)

    @auto_log
    def get_title(self):
        """Получает название товара"""
        title_element = self.page.find_element(self.PRODUCT_TITLE)
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
    def add_to_cart(self):
        """Добавляет товар в корзину"""
        self.add_to_cart_button.click()
        self.page.wait_for_page_loaded()

        if "cart" in self.page.driver.current_url:
            from examples.amazon.pages import AmazonCartPage
            return self.page.navigate_to(AmazonCartPage)
        return self.page