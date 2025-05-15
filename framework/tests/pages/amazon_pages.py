from framework.src.core.base_page import BasePage
from framework.tests.locators.amazon_locators import (
    AmazonLoginPageLocators,
    AmazonHomePageLocators,
    AmazonSearchResultsLocators,
    AmazonProductPageLocators,
    AmazonCartPageLocators,
    AmazonCheckoutPageLocators
)
from framework.tests.components.amazon_components import (
    CartItemComponent,
    HeaderComponent,
    ProductDetailsComponent
)


class AmazonLoginPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fhomepage.html%3F_encoding%3DUTF8%26ref_%3Dnavm_em_signin%26action%3Dsign-out%26path%3D%252Fgp%252Fhomepage.html%253F_encoding%253DUTF8%2526ref_%253Dnavm_em_signin%26signIn%3D1%26useRedirectOnSuccess%3D1%26ref_%3Dnav_em_signout_0_1_1_40&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
        self.locators = AmazonLoginPageLocators()
        self._init_elements()

    def login(self, email, password):
        """Выполняет вход в аккаунт"""
        self.type(self.locators.EMAIL_INPUT, email)
        self.click(self.locators.CONTINUE_BUTTON)
        self.type(self.locators.PASSWORD_INPUT, password)
        self.click(self.locators.SIGN_IN_BUTTON)
        return self.navigate_to(AmazonHomePage)


class AmazonHomePage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = ""
        self.locators = AmazonHomePageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

    def search(self, search_text):
        """Выполняет поиск товара через компонент header"""
        return self.header.search(search_text)

    def go_to_cart(self):
        """Переходит в корзину через компонент header"""
        return self.header.go_to_cart()


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
        products = self.find_all(self.locators.PRODUCT_TITLES)
        if len(products) > index:
            self.click(products[index])
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

    def get_product_title(self):
        """Получает название товара через компонент product_details"""
        return self.product_details.get_title()

    def get_product_price(self):
        """Получает цену товара через компонент product_details"""
        return self.product_details.get_price()

    def add_to_cart(self):
        """Добавляет товар в корзину через компонент product_details"""
        return self.product_details.add_to_cart()


class AmazonCartPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = "gp/cart/view.html"
        self.locators = AmazonCartPageLocators()
        self._init_elements()

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

    def get_cart_items(self):
        """Получает список компонентов элементов корзины"""
        items = self.find_all(self.locators.CART_ITEMS)
        return [CartItemComponent(self, item) for item in items]

    def get_cart_items_count(self):
        """Получает количество товаров в корзине"""
        return len(self.get_cart_items())

    def increase_quantity(self, index=0, count=1):
        """Увеличивает количество товара на указанное число"""
        cart_items = self.get_cart_items()
        if len(cart_items) > index:
            for _ in range(count):
                cart_items[index].increase_quantity()
            return self
        raise ValueError(f"Товар с индексом {index} не найден в корзине")

    def get_subtotal(self):
        """Получает общую сумму заказа"""
        subtotal_element = self.find(self.locators.SUBTOTAL)
        return subtotal_element.text.strip()

    def proceed_to_checkout(self):
        """Переходит к оформлению заказа"""
        self.click(self.locators.PROCEED_TO_CHECKOUT)
        return self.navigate_to(AmazonCheckoutPage)

    def delete_item(self, index=0):
        """Удаляет товар из корзины"""
        cart_items = self.get_cart_items()
        if len(cart_items) > index:
            cart_items[index].delete()
            return self
        raise ValueError(f"Товар с индексом {index} не найден в корзине")


class AmazonCheckoutPage(BasePage):
    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = "gp/buy/spc/handlers/display.html"
        self.locators = AmazonCheckoutPageLocators()
        self._init_elements()

    def get_order_total(self):
        """Получает итоговую сумму заказа"""
        total_element = self.find(self.locators.ORDER_TOTAL)
        return total_element.text.strip()
