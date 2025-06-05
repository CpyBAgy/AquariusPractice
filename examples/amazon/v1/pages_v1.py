"""
Версия 1 страниц Amazon - базовая реализация
"""
from selenium.webdriver.common.by import By
from page_object_library import BasePage, Button, Input, Link, BaseElement
from examples.amazon.v1.components_v1 import HeaderComponentV1, ProductDetailsComponentV1


class AmazonLoginPageV1(BasePage):
    """Страница входа Amazon версии 1"""
    DEFAULT_URL = "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

    def _init_elements(self):
        """Инициализирует элементы страницы версии 1"""
        self.email_input = Input(self, (By.ID, "ap_email"), "Поле ввода email")
        self.continue_button = Button(self, (By.ID, "continue"), "Кнопка продолжить")
        self.password_input = Input(self, (By.ID, "ap_password"), "Поле ввода пароля")
        self.sign_in_button = Button(self, (By.ID, "signInSubmit"), "Кнопка входа")
        self.forgot_password_link = Link(self, (By.ID, "auth-fpp-link-bottom"), "Ссылка забыли пароль")

    def login(self, email, password):
        """Выполняет вход в аккаунт (версия 1)"""
        self.email_input.type(email)
        self.continue_button.click()
        self.password_input.type(password)
        self.sign_in_button.click()
        return self.navigate_to(AmazonHomePageV1)


class AmazonHomePageV1(BasePage):
    """Главная страница Amazon версии 1"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 1"""
        self.header = HeaderComponentV1(self)
        self.search_input = Input(self, (By.ID, "twotabsearchtextbox"), "Поле поиска")
        self.search_button = Button(self, (By.ID, "nav-search-submit-button"), "Кнопка поиска")
        self.cart_icon = BaseElement(self, (By.ID, "nav-cart"), "Иконка корзины")

    def search(self, search_text):
        """Выполняет поиск товара через поле поиска"""
        self.search_input.type(search_text)
        self.search_button.click()
        return self.navigate_to(AmazonSearchResultsPageV1)

    def go_to_cart(self):
        """Переходит в корзину"""
        self.cart_icon.click()
        return self.navigate_to(AmazonCartPageV1)


class AmazonSearchResultsPageV1(BasePage):
    """Страница результатов поиска Amazon версии 1"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 1"""
        self.header = HeaderComponentV1(self)

    def select_product(self, index=0):
        """Выбирает товар из результатов поиска по индексу"""
        products = self.find_elements((By.CSS_SELECTOR, "span.a-size-medium"))

        if len(products) > index:
            products[index].click()
            return self.navigate_to(AmazonProductPageV1)
        raise ValueError(f"Товар с индексом {index} не найден в результатах поиска")


class AmazonProductPageV1(BasePage):
    """Страница товара Amazon версии 1"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 1"""
        self.header = HeaderComponentV1(self)
        self.product_details = ProductDetailsComponentV1(self)
        self.add_to_cart_button = Button(self, (By.ID, "add-to-cart-button"), "Кнопка добавить в корзину")

    def get_product_title(self):
        """Получает название товара"""
        return self.product_details.get_title()

    def get_product_price(self):
        """Получает цену товара"""
        return self.product_details.get_price()

    def get_product_price_as_float(self):
        """Получает цену товара как float"""
        return self.product_details.get_price_as_float()

    def add_to_cart(self):
        """Добавляет товар в корзину"""
        self.add_to_cart_button.click()
        self.wait_for_page_loaded()
        return self


class AmazonCartPageV1(BasePage):
    """Страница корзины Amazon версии 1"""
    DEFAULT_URL = "/gp/cart/view.html"

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 1"""
        self.header = HeaderComponentV1(self)
        self.proceed_to_checkout = Button(
            self,
            (By.CSS_SELECTOR, "input[name='proceedToRetailCheckout']"),
            "Кнопка перейти к оформлению"
        )
        self.subtotal = BaseElement(
            self,
            (By.CSS_SELECTOR, "#sc-subtotal-amount-activecart > span"),
            "Промежуточная сумма"
        )

    def get_cart_items(self):
        """Получает список компонентов элементов корзины"""
        items = self.find_elements((By.CSS_SELECTOR, ".sc-list-item"))
        from examples.amazon.components_v1 import CartItemComponentV1
        return [CartItemComponentV1(self, item.element) for item in items]

    def get_cart_items_count(self):
        """Получает количество товаров в корзине"""
        return len(self.get_cart_items())

    def get_subtotal(self):
        """Получает общую сумму заказа"""
        return self.subtotal.get_text()

    def get_subtotal_as_float(self):
        """Получает общую сумму заказа как float"""
        subtotal_text = self.get_subtotal()
        from examples.amazon.components_v1 import ProductDetailsComponentV1
        return ProductDetailsComponentV1.parse_price_to_float(subtotal_text)

    def go_to_checkout(self):
        """Переходит к оформлению заказа"""
        self.proceed_to_checkout.click()
        return self.navigate_to(AmazonCheckoutPageV1)


class AmazonCheckoutPageV1(BasePage):
    """Страница оформления заказа Amazon версии 1"""

    def _init_elements(self):
        """Инициализирует элементы страницы версии 1"""
        self.delivery_address = BaseElement(
            self,
            (By.CSS_SELECTOR, ".ship-to-this-address a"),
            "Адрес доставки"
        )
        self.add_new_address = BaseElement(
            self,
            (By.CSS_SELECTOR, "a#add-new-address-popover-link"),
            "Добавить новый адрес"
        )
        self.payment_method = BaseElement(
            self,
            (By.CSS_SELECTOR, "#payment-method"),
            "Способ оплаты"
        )
        self.order_total = BaseElement(
            self,
            (By.CSS_SELECTOR, ".grand-total-price"),
            "Общая сумма заказа"
        )
        self.place_order_button = Button(
            self,
            (By.CSS_SELECTOR, "#placeYourOrder"),
            "Кнопка разместить заказ"
        )
