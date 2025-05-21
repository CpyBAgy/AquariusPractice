from framework.core import BasePage
from framework.core.component import Input
from tests.locators.amazon_locators import (
    AmazonLoginPageLocators,
    AmazonHomePageLocators,
    AmazonSearchResultsLocators,
    AmazonProductPageLocators,
    AmazonCartPageLocators
)
from tests.components.amazon_components import (
    HeaderComponent,
    ProductDetailsComponent
)


class AmazonLoginPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = "https://www.amazon.com/ap/signin"
        self.locators = AmazonLoginPageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует элементы страницы, используя новый подход"""
        self.email_input = Input(self.locators.EMAIL_INPUT),
        self.continue_button = self.find_button(self.locators.CONTINUE_BUTTON),
        self.password_input = self.find_input(self.locators.PASSWORD_INPUT),
        self.sign_in_button = self.find_button(self.locators.SIGN_IN_BUTTON),
        self.forgot_password_link = self.find_link(self.locators.FORGOT_PASSWORD_LINK)

    def login(self, email, password):
        """Выполняет вход в аккаунт используя объектно-ориентированный подход"""
        self.email_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()
        return self.navigate_to(AmazonHomePage)


class AmazonHomePage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = base_url
        self.locators = AmazonHomePageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

        self.search_input = self.find_input(self.locators.SEARCH_INPUT),
        self.search_button = self.find_button(self.locators.SEARCH_BUTTON),
        self.cart_icon = self.find_element(self.locators.CART_ICON)

    def search(self, search_text):
        """Выполняет поиск товара через компонент header"""
        self.search_input.type(search_text)
        self.search_button.click()
        return self.navigate_to(AmazonSearchResultsPage)

    def go_to_cart(self):
        """Переходит в корзину через элемент cart_icon"""
        self.cart_icon.click()
        return self.navigate_to(AmazonCartPage)


class AmazonSearchResultsPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.locators = AmazonSearchResultsLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

    def select_product(self, index=0):
        """Выбирает товар из результатов поиска по индексу"""
        products = self.find_elements(self.locators.PRODUCT_TITLES)

        if len(products) > index:
            products[index].click()
            return self.navigate_to(AmazonProductPage)
        raise ValueError(f"Товар с индексом {index} не найден в результатах поиска")


class AmazonProductPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.locators = AmazonProductPageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)
        self.product_details = ProductDetailsComponent(self)

        self.add_to_cart_button = self.find_button(self.locators.ADD_TO_CART_BUTTON)

    def get_product_title(self):
        """Получает название товара через компонент product_details"""
        return self.product_details.get_title()

    def get_product_price(self):
        """Получает цену товара через компонент product_details"""
        return self.product_details.get_price()

    def add_to_cart(self):
        """Добавляет товар в корзину через кнопку"""
        self.add_to_cart_button.click()
        self.wait_for_page_loaded()

        if "cart" in self.driver.current_url:
            return self.navigate_to(AmazonCartPage)
        return self


class AmazonCartPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = f"{base_url}/gp/cart/view.html"
        self.locators = AmazonCartPageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

        self.proceed_to_checkout = self.find_button(self.locators.PROCEED_TO_CHECKOUT),
        self.subtotal = self.find_element(self.locators.SUBTOTAL)

    def get_cart_items(self):
        """Получает список компонентов элементов корзины"""
        items = self.find_elements(self.locators.CART_ITEMS)

        from tests.components.amazon_components import CartItemComponent
        return [CartItemComponent(self, item.element) for item in items]

    def get_cart_items_count(self):
        """Получает количество товаров в корзине"""
        return len(self.get_cart_items())

    def get_subtotal(self):
        """Получает общую сумму заказа"""
        return self.subtotal.get_text()

    def proceed_to_checkout(self):
        """Переходит к оформлению заказа"""
        self.proceed_to_checkout.click()
        from tests.pages.amazon_pages import AmazonCheckoutPage
        return self.navigate_to(AmazonCheckoutPage)