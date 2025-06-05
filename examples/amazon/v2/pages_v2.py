"""
Версия 2 страниц Amazon - расширенная реализация с новыми возможностями
"""
import time
from selenium.webdriver.common.by import By
from page_object_library import Button, Input, BaseElement, auto_log
from examples.amazon.v1.pages_v1 import (
    AmazonLoginPageV1,
    AmazonHomePageV1,
    AmazonSearchResultsPageV1,
    AmazonProductPageV1,
    AmazonCartPageV1,
    AmazonCheckoutPageV1
)
from examples.amazon.v2.components_v2 import (
    HeaderComponentV2,
    ProductDetailsComponentV2,
    TwoFactorComponentV2
)


class AmazonLoginPageV2(AmazonLoginPageV1):
    """Страница входа Amazon версии 2 с поддержкой 2FA и новым UI"""

    def _init_elements(self):
        """Инициализирует элементы страницы версии 2"""
        super()._init_elements()

        self.two_factor_component = TwoFactorComponentV2(self)
        self.remember_device_checkbox = Input(
            self,
            (By.ID, "remember-device"),
            "Чекбокс запомнить устройство"
        )
        self.alternative_login_button = Button(
            self,
            (By.CSS_SELECTOR, ".alternative-login-btn"),
            "Альтернативный способ входа"
        )

        self.email_input = Input(
            self,
            (By.ID, "ap_email_login"),
            "Поле ввода email"
        )

    @auto_log
    def login(self, email, password, use_2fa=False):
        """Выполняет вход в аккаунт с поддержкой 2FA (версия 2)"""
        self.email_input.type(email)
        self.continue_button.click()

        if self._is_captcha_present():
            self._handle_captcha()

        self.password_input.type(password)
        self.sign_in_button.click()
        if use_2fa or self.two_factor_component.is_visible():
            self._handle_two_factor_auth()

        return self.navigate_to(AmazonHomePageV2)

    @auto_log
    def _is_captcha_present(self):
        """Проверяет наличие капчи на странице"""
        try:
            captcha_element = self.find_element((By.ID, "auth-captcha-image"))
            return captcha_element.is_visible()
        except:
            return False

    @auto_log
    def _handle_captcha(self):
        """Обрабатывает капчу (заглушка для реальной реализации)"""
        raise NotImplementedError("Обработка капчи требует дополнительной реализации")

    @auto_log
    def _handle_two_factor_auth(self):
        """Обрабатывает двухфакторную аутентификацию"""
        time.sleep(2)

        if self.two_factor_component.is_sms_method_available():
            self.two_factor_component.select_sms_method()
            verification_code = "123456"
            self.two_factor_component.enter_verification_code(verification_code)
        elif self.two_factor_component.is_app_method_available():
            self.two_factor_component.select_app_method()
            verification_code = "654321"
            self.two_factor_component.enter_verification_code(verification_code)

    @auto_log
    def login_with_alternative_method(self):
        """Альтернативный способ входа (новая функция в v2)"""
        self.alternative_login_button.click()
        return self


class AmazonHomePageV2(AmazonHomePageV1):
    """Главная страница Amazon версии 2 с улучшенным поиском"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 2"""
        self.header = HeaderComponentV2(self)

        super()._init_elements()

        self.voice_search_button = Button(
            self,
            (By.CSS_SELECTOR, ".voice-search-btn"),
            "Кнопка голосового поиска"
        )
        self.quick_filters = BaseElement(
            self,
            (By.CSS_SELECTOR, ".quick-filters"),
            "Быстрые фильтры"
        )

    @auto_log
    def search_with_voice(self):
        """Голосовой поиск (новая функция в v2)"""
        self.voice_search_button.click()
        return self.navigate_to(AmazonSearchResultsPageV2)

    @auto_log
    def apply_quick_filter(self, filter_name):
        """Применяет быстрый фильтр (новая функция в v2)"""
        filter_element = self.find_element((By.CSS_SELECTOR, f"[data-filter='{filter_name}']"))
        filter_element.click()
        return self


class AmazonSearchResultsPageV2(AmazonSearchResultsPageV1):
    """Страница результатов поиска Amazon версии 2 с расширенными фильтрами"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 2"""
        self.header = HeaderComponentV2(self)

        self.advanced_filters = BaseElement(
            self,
            (By.CSS_SELECTOR, ".advanced-filters-panel"),
            "Панель расширенных фильтров"
        )
        self.sort_dropdown = BaseElement(
            self,
            (By.CSS_SELECTOR, ".sort-dropdown"),
            "Выпадающий список сортировки"
        )

    @auto_log
    def select_product(self, index=0):
        """Выбирает товар из результатов поиска (улучшенная версия)"""
        products = self.find_elements((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))

        if len(products) > index:
            product_link = products[index].find_element(By.CSS_SELECTOR, "h2 a")
            product_link.click()
            return self.navigate_to(AmazonProductPageV2)
        raise ValueError(f"Товар с индексом {index} не найден в результатах поиска")

    @auto_log
    def apply_price_filter(self, min_price, max_price):
        """Применяет ценовой фильтр (новая функция в v2)"""
        price_filter = self.find_element((By.CSS_SELECTOR, ".price-filter"))

        min_input = price_filter.find_element(By.CSS_SELECTOR, "input[name='low-price']")
        max_input = price_filter.find_element(By.CSS_SELECTOR, "input[name='high-price']")

        min_input.clear()
        min_input.send_keys(str(min_price))

        max_input.clear()
        max_input.send_keys(str(max_price))

        apply_button = price_filter.find_element(By.CSS_SELECTOR, ".apply-filter-btn")
        apply_button.click()

        return self

    @auto_log
    def sort_by(self, sort_option):
        """Сортирует результаты (новая функция в v2)"""
        self.sort_dropdown.click()
        sort_option_element = self.find_element((By.CSS_SELECTOR, f"[data-sort='{sort_option}']"))
        sort_option_element.click()
        return self


class AmazonProductPageV2(AmazonProductPageV1):
    """Страница товара Amazon версии 2 с дополнительными возможностями"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 2"""
        self.header = HeaderComponentV2(self)
        self.product_details = ProductDetailsComponentV2(self)

        super()._init_elements()

        self.wishlist_button = Button(
            self,
            (By.CSS_SELECTOR, ".add-to-wishlist-btn"),
            "Кнопка добавить в список желаний"
        )
        self.compare_button = Button(
            self,
            (By.CSS_SELECTOR, ".add-to-compare-btn"),
            "Кнопка добавить к сравнению"
        )
        self.quantity_selector = BaseElement(
            self,
            (By.CSS_SELECTOR, ".quantity-selector"),
            "Селектор количества"
        )

    @auto_log
    def add_to_wishlist(self):
        """Добавляет товар в список желаний (новая функция в v2)"""
        self.wishlist_button.click()
        self.wait_for_page_loaded()
        return self

    @auto_log
    def add_to_compare(self):
        """Добавляет товар к сравнению (новая функция в v2)"""
        self.compare_button.click()
        self.wait_for_page_loaded()
        return self

    @auto_log
    def select_quantity(self, quantity):
        """Выбирает количество товара перед добавлением в корзину (новая функция в v2)"""
        self.quantity_selector.click()
        quantity_option = self.find_element((By.CSS_SELECTOR, f"option[value='{quantity}']"))
        quantity_option.click()
        return self

    @auto_log
    def add_to_cart(self, quantity=1):
        """Добавляет товар в корзину с указанным количеством (улучшенная версия)"""
        if quantity > 1:
            self.select_quantity(quantity)

        self.add_to_cart_button.click()
        self.wait_for_page_loaded()

        if self._is_confirmation_modal_visible():
            self._handle_confirmation_modal()

        if "cart" in self.driver.current_url:
            return self.navigate_to(AmazonCartPageV2)
        return self

    @auto_log
    def _is_confirmation_modal_visible(self):
        """Проверяет видимость модального окна подтверждения"""
        try:
            modal = self.find_element((By.CSS_SELECTOR, ".confirmation-modal"))
            return modal.is_visible()
        except:
            return False

    @auto_log
    def _handle_confirmation_modal(self):
        """Обрабатывает модальное окно подтверждения"""
        continue_button = self.find_element((By.CSS_SELECTOR, ".modal-continue-btn"))
        continue_button.click()


class AmazonCartPageV2(AmazonCartPageV1):
    """Страница корзины Amazon версии 2 с улучшенным управлением"""

    def _init_elements(self):
        """Инициализирует компоненты страницы версии 2"""
        self.header = HeaderComponentV2(self)

        super()._init_elements()

        self.save_for_later_section = BaseElement(
            self,
            (By.CSS_SELECTOR, ".save-for-later-section"),
            "Секция отложенных товаров"
        )
        self.estimated_delivery = BaseElement(
            self,
            (By.CSS_SELECTOR, ".estimated-delivery"),
            "Информация о доставке"
        )
        self.promo_code_input = Input(
            self,
            (By.CSS_SELECTOR, "input[name='promo-code']"),
            "Поле ввода промокода"
        )
        self.apply_promo_button = Button(
            self,
            (By.CSS_SELECTOR, ".apply-promo-btn"),
            "Кнопка применения промокода"
        )

    def get_cart_items(self):
        """Получает список компонентов элементов корзины версии 2"""
        items = self.find_elements((By.CSS_SELECTOR, ".cart-item"))
        from examples.amazon.v2.components_v2 import CartItemComponentV2
        return [CartItemComponentV2(self, item.element) for item in items]

    @auto_log
    def apply_promo_code(self, promo_code):
        """Применяет промокод (новая функция в v2)"""
        self.promo_code_input.type(promo_code)
        self.apply_promo_button.click()
        self.wait_for_page_loaded()
        return self

    @auto_log
    def get_estimated_delivery_date(self):
        """Получает примерную дату доставки (новая функция в v2)"""
        return self.estimated_delivery.get_text()

    @auto_log
    def move_to_save_for_later(self, item_index=0):
        """Перемещает товар в 'Сохранить на потом' (новая функция в v2)"""
        cart_items = self.get_cart_items()
        if len(cart_items) > item_index:
            cart_items[item_index].save_for_later()
        return self


class AmazonCheckoutPageV2(AmazonCheckoutPageV1):
    """Страница оформления заказа Amazon версии 2 с расширенными опциями"""

    def _init_elements(self):
        """Инициализирует элементы страницы версии 2"""
        super()._init_elements()

        self.express_checkout_button = Button(
            self,
            (By.CSS_SELECTOR, ".express-checkout-btn"),
            "Кнопка экспресс оформления"
        )
        self.gift_options = BaseElement(
            self,
            (By.CSS_SELECTOR, ".gift-options"),
            "Опции подарка"
        )
        self.delivery_instructions = Input(
            self,
            (By.CSS_SELECTOR, "textarea[name='delivery-instructions']"),
            "Инструкции по доставке"
        )
        self.scheduled_delivery = BaseElement(
            self,
            (By.CSS_SELECTOR, ".scheduled-delivery-options"),
            "Опции запланированной доставки"
        )

    @auto_log
    def use_express_checkout(self):
        """Использует экспресс оформление заказа (новая функция в v2)"""
        self.express_checkout_button.click()
        return self

    @auto_log
    def add_gift_wrapping(self):
        """Добавляет подарочную упаковку (новая функция в v2)"""
        gift_wrap_checkbox = self.gift_options.find_element(
            (By.CSS_SELECTOR, "input[name='gift-wrap']")
        )
        gift_wrap_checkbox.click()
        return self

    @auto_log
    def add_delivery_instructions(self, instructions):
        """Добавляет инструкции по доставке (новая функция в v2)"""
        self.delivery_instructions.type(instructions)
        return self

    @auto_log
    def schedule_delivery(self, date, time_slot):
        """Планирует доставку на определенное время (новая функция в v2)"""
        date_picker = self.scheduled_delivery.find_element(
            (By.CSS_SELECTOR, ".date-picker")
        )
        date_picker.click()

        date_option = self.find_element(
            (By.CSS_SELECTOR, f"[data-date='{date}']")
        )
        date_option.click()

        time_slot_option = self.find_element(
            (By.CSS_SELECTOR, f"[data-time-slot='{time_slot}']")
        )
        time_slot_option.click()

        return self