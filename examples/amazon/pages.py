from selenium.webdriver.common.by import By

from page_object_library import BasePage, Button, Input, Link, BaseElement
from examples.amazon.components import (
    HeaderComponent,
    ProductDetailsComponent
)


class AmazonLoginPage(BasePage):
    EMAIL_INPUT = (By.ID, "ap_email")
    CONTINUE_BUTTON = (By.ID, "continue")
    PASSWORD_INPUT = (By.ID, "ap_password")
    SIGN_IN_BUTTON = (By.ID, "signInSubmit")
    CHANGE_LINK = (By.ID, "ap_change_login_claim")
    FORGOT_PASSWORD_LINK = (By.ID, "auth-fpp-link-bottom")


    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

    def _init_elements(self):
        """Инициализирует элементы страницы, используя новый подход"""
        self.email_input = Input(self, self.EMAIL_INPUT)
        self.continue_button = Button(self, self.CONTINUE_BUTTON)
        self.password_input = Input(self, self.PASSWORD_INPUT)
        self.sign_in_button = Button(self, self.SIGN_IN_BUTTON)
        self.forgot_password_link = Link(self, self.FORGOT_PASSWORD_LINK)

    def login(self, email, password):
        """Выполняет вход в аккаунт используя объектно-ориентированный подход"""
        self.email_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()
        return self.navigate_to(AmazonHomePage)


class AmazonHomePage(BasePage):
    SEARCH_INPUT = (By.ID, "twotabsearchtextbox")
    SEARCH_BUTTON = (By.ID, "nav-search-submit-button")
    ACCOUNT_MENU = (By.ID, "nav-link-accountList")
    CART_ICON = (By.ID, "nav-cart")
    SEARCH_DROPDOWN = (By.ID, "searchDropdownBox")
    SEARCH_SUGGESTIONS = (By.CSS_SELECTOR, "div.s-suggestion")

    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = base_url

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

        self.search_input = Input(self, self.SEARCH_INPUT)
        self.search_button = Button(self, self.SEARCH_BUTTON)
        self.cart_icon = BaseElement(self, self.CART_ICON)

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
    SEARCH_RESULTS = (By.CSS_SELECTOR, "div.s-result-item")
    PRODUCT_TITLES = (By.CSS_SELECTOR, "span.a-size-medium")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "span.a-dropdown-label")
    BEST_SELLER_BADGE = (By.CSS_SELECTOR, "span.a-badge-text")

    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

    def select_product(self, index=0):
        """Выбирает товар из результатов поиска по индексу"""
        products = self.find_elements(self.PRODUCT_TITLES)

        if len(products) > index:
            products[index].click()
            return self.navigate_to(AmazonProductPage)
        raise ValueError(f"Товар с индексом {index} не найден в результатах поиска")


class AmazonProductPage(BasePage):
    PRODUCT_TITLE = (By.ID, "productTitle")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "span.a-price-whole")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart-button")
    BUY_NOW_BUTTON = (By.ID, "buy-now-button")
    PRODUCT_DESCRIPTION = (By.ID, "productDescription")
    COLOR_OPTIONS = (By.CSS_SELECTOR, "li.swatch-list")

    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)
        self.product_details = ProductDetailsComponent(self)

        self.add_to_cart_button = Button(self, self.ADD_TO_CART_BUTTON)

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
        return self


class AmazonCartPage(BasePage):
    CART_ITEMS = (By.CSS_SELECTOR, ".sc-list-item")
    QUANTITY_DROPDOWN = (By.CSS_SELECTOR, "select.a-native-dropdown")
    QUANTITY_INCREMENT = (By.CSS_SELECTOR, "input.a-button-input[data-action='increase-quantity']")
    QUANTITY_DECREMENT = (By.CSS_SELECTOR, "input.a-button-input[data-action='decrease-quantity']")
    QUANTITY_TEXTBOX = (By.CSS_SELECTOR, "input.sc-quantity-textfield")
    DELETE_BUTTON = (By.CSS_SELECTOR, "input[value='Delete']")
    PROCEED_TO_CHECKOUT = (By.CSS_SELECTOR, "input[name='proceedToRetailCheckout']")
    SUBTOTAL = (By.CSS_SELECTOR, "#sc-subtotal-amount-activecart > span")
    SAVE_FOR_LATER = (By.CSS_SELECTOR, "input[value='Save for later']")

    def __init__(self, driver, base_url="https://www.amazon.com"):
        super().__init__(driver, base_url)
        self.url = f"{base_url}/gp/cart/view.html"

    def _init_elements(self):
        """Инициализирует компоненты страницы"""
        self.header = HeaderComponent(self)

        self.proceed_to_checkout = Button(self, self.PROCEED_TO_CHECKOUT)
        self.subtotal = BaseElement(self, self.SUBTOTAL)

    def get_cart_items(self):
        """Получает список компонентов элементов корзины"""
        items = self.find_elements(self.CART_ITEMS)

        from examples.amazon.components import CartItemComponent
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
        return self.navigate_to(AmazonCheckoutPage)

class AmazonCheckoutPage(BasePage):
    DELIVERY_ADDRESS = (By.CSS_SELECTOR, ".ship-to-this-address a")
    ADD_NEW_ADDRESS = (By.CSS_SELECTOR, "a#add-new-address-popover-link")
    PAYMENT_METHOD = (By.CSS_SELECTOR, "#payment-method")
    ORDER_TOTAL = (By.CSS_SELECTOR, ".grand-total-price")
    PLACE_ORDER_BUTTON = (By.CSS_SELECTOR, "#placeYourOrder")
