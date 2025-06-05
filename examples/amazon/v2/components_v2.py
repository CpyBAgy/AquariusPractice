"""
Компоненты Amazon версии 2 - расширенная реализация с новыми возможностями
"""
import time
from selenium.webdriver.common.by import By
from page_object_library import ElementGroup, auto_log, Input, Button, BaseElement, Link
from examples.amazon.v1.components_v1 import (
    HeaderComponentV1,
    CartItemComponentV1,
    ProductDetailsComponentV1
)


class TwoFactorComponentV2(ElementGroup):
    """Компонент двухфакторной аутентификации (новый в версии 2)"""

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента 2FA"""
        self.verification_code_input = Input(
            self.page,
            (By.ID, "auth-mfa-otpcode"),
            "Поле ввода кода подтверждения"
        )
        self.submit_code_button = Button(
            self.page,
            (By.ID, "auth-signin-button"),
            "Кнопка отправки кода"
        )
        self.sms_method_radio = Button(
            self.page,
            (By.CSS_SELECTOR, "input[value='sms']"),
            "SMS метод"
        )
        self.app_method_radio = Button(
            self.page,
            (By.CSS_SELECTOR, "input[value='app']"),
            "Приложение аутентификатор"
        )
        self.remember_device_checkbox = Input(
            self.page,
            (By.ID, "auth-mfa-remember-device"),
            "Запомнить устройство"
        )

    @auto_log
    def is_visible(self):
        """Проверяет видимость формы 2FA"""
        try:
            return self.verification_code_input.is_visible()
        except:
            return False

    @auto_log
    def is_sms_method_available(self):
        """Проверяет доступность SMS метода"""
        try:
            return self.sms_method_radio.is_visible()
        except:
            return False

    @auto_log
    def is_app_method_available(self):
        """Проверяет доступность метода через приложение"""
        try:
            return self.app_method_radio.is_visible()
        except:
            return False

    @auto_log
    def select_sms_method(self):
        """Выбирает SMS метод подтверждения"""
        self.sms_method_radio.click()
        return self

    @auto_log
    def select_app_method(self):
        """Выбирает метод через приложение аутентификатор"""
        self.app_method_radio.click()
        return self

    @auto_log
    def enter_verification_code(self, code):
        """Вводит код подтверждения и отправляет"""
        self.verification_code_input.type(code)
        self.submit_code_button.click()
        time.sleep(2)
        return self

    @auto_log
    def remember_device(self, remember=True):
        """Устанавливает чекбокс запоминания устройства"""
        if remember and not self.remember_device_checkbox.is_checked():
            self.remember_device_checkbox.click()
        elif not remember and self.remember_device_checkbox.is_checked():
            self.remember_device_checkbox.click()
        return self


class HeaderComponentV2(HeaderComponentV1):
    """Компонент верхнего меню Amazon версии 2 с расширенным функционалом"""

    def _init_elements(self):
        """Инициализирует элементы компонента версии 2"""
        super()._init_elements()

        self.voice_search_button = Button(
            self.page,
            (By.CSS_SELECTOR, ".voice-search-icon"),
            "Кнопка голосового поиска"
        )
        self.search_suggestions = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".search-suggestions"),
            "Подсказки поиска"
        )
        self.recently_viewed_dropdown = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".recently-viewed-dropdown"),
            "Выпадающий список недавно просмотренных"
        )
        self.wishlist_icon = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".wishlist-icon"),
            "Иконка списка желаний"
        )

    @auto_log
    def search_with_suggestions(self, search_text):
        """Выполняет поиск с использованием подсказок (новая функция в v2)"""
        self.search_input.type(search_text)

        time.sleep(1)

        if self.search_suggestions.is_visible():
            first_suggestion = self.search_suggestions.find_element(
                (By.CSS_SELECTOR, ".suggestion-item:first-child")
            )
            first_suggestion.click()
        else:
            self.search_button.click()

        from examples.amazon.v2.pages_v2 import AmazonSearchResultsPageV2
        return self.page.navigate_to(AmazonSearchResultsPageV2)

    @auto_log
    def use_voice_search(self):
        """Использует голосовой поиск (новая функция в v2)"""
        self.voice_search_button.click()
        return self

    @auto_log
    def go_to_wishlist(self):
        """Переходит к списку желаний (новая функция в v2)"""
        self.wishlist_icon.click()
        return self

    @auto_log
    def open_recently_viewed(self):
        """Открывает недавно просмотренные товары (новая функция в v2)"""
        self.recently_viewed_dropdown.click()
        return self


class CartItemComponentV2(CartItemComponentV1):
    """Компонент элемента корзины версии 2 с дополнительными возможностями"""

    def _init_elements(self):
        """Инициализирует элементы компонента версии 2"""
        self.increment_button = Button(
            self.page,
            (By.CSS_SELECTOR, ".quantity-plus"),
            "Кнопка увеличения количества",
            self.item_element
        )
        self.decrement_button = Button(
            self.page,
            (By.CSS_SELECTOR, ".quantity-minus"),
            "Кнопка уменьшения количества",
            self.item_element
        )
        self.delete_button = Button(
            self.page,
            (By.CSS_SELECTOR, ".delete-item-btn"),
            "Кнопка удаления",
            self.item_element
        )

  
        self.save_for_later_button = Button(
            self.page,
            (By.CSS_SELECTOR, ".save-for-later-btn"),
            "Кнопка сохранить на потом",
            self.item_element
        )
        self.quantity_dropdown = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".quantity-dropdown"),
            "Выпадающий список количества",
            self.item_element
        )
        self.gift_wrap_checkbox = Input(
            self.page,
            (By.CSS_SELECTOR, ".gift-wrap-checkbox"),
            "Чекбокс подарочной упаковки",
            self.item_element
        )

    @auto_log
    def save_for_later(self):
        """Сохраняет товар на потом (новая функция в v2)"""
        self.save_for_later_button.click()
        self.page.wait_for_page_loaded()
        return self.page

    @auto_log
    def set_quantity(self, quantity):
        """Устанавливает точное количество через выпадающий список (новая функция в v2)"""
        self.quantity_dropdown.click()

  
        if quantity > 10:
            quantity_input = self.page.find_element(
                (By.CSS_SELECTOR, ".quantity-input")
            )
            quantity_input.clear()
            quantity_input.send_keys(str(quantity))
        else:
            quantity_option = self.page.find_element(
                (By.CSS_SELECTOR, f"option[value='{quantity}']")
            )
            quantity_option.click()

        self.page.wait_for_page_loaded()
        return self

    @auto_log
    def add_gift_wrap(self):
        """Добавляет подарочную упаковку (новая функция в v2)"""
        if not self.gift_wrap_checkbox.is_checked():
            self.gift_wrap_checkbox.click()
        return self

    @auto_log
    def get_title(self):
        """Получает название товара (обновленный селектор для v2)"""
        title_element = self.page.find_element((By.CSS_SELECTOR, ".item-title"))
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара (обновленный селектор для v2)"""
        price_element = self.page.find_element((By.CSS_SELECTOR, ".item-price"))
        return price_element.get_text().strip()


class ProductDetailsComponentV2(ProductDetailsComponentV1):
    """Компонент деталей товара версии 2 с расширенной информацией"""

    def _init_elements(self):
        """Инициализирует элементы компонента версии 2"""
  
        super()._init_elements()

  
        self.product_rating = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".product-rating"),
            "Рейтинг товара"
        )
        self.reviews_count = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".reviews-count"),
            "Количество отзывов"
        )
        self.availability_info = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".availability-info"),
            "Информация о наличии"
        )
        self.delivery_info = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".delivery-info"),
            "Информация о доставке"
        )
        self.product_images = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".product-images"),
            "Изображения товара"
        )
        self.variant_selector = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".variant-selector"),
            "Селектор вариантов"
        )

    @auto_log
    def get_rating(self):
        """Получает рейтинг товара (новая функция в v2)"""
        try:
            rating_text = self.product_rating.get_text()
      
            import re
            match = re.search(r'(\d+\.?\d*)', rating_text)
            return float(match.group(1)) if match else 0.0
        except:
            return 0.0

    @auto_log
    def get_reviews_count(self):
        """Получает количество отзывов (новая функция в v2)"""
        try:
            reviews_text = self.reviews_count.get_text()
      
            import re
            match = re.search(r'([\d,]+)', reviews_text)
            if match:
                return int(match.group(1).replace(',', ''))
            return 0
        except:
            return 0

    @auto_log
    def is_in_stock(self):
        """Проверяет наличие товара в stock (новая функция в v2)"""
        try:
            availability_text = self.availability_info.get_text().lower()
            return "в наличии" in availability_text or "available" in availability_text
        except:
            return False

    @auto_log
    def get_delivery_date(self):
        """Получает дату доставки (новая функция в v2)"""
        try:
            return self.delivery_info.get_text()
        except:
            return "Информация о доставке недоступна"

    @auto_log
    def select_variant(self, variant_name):
        """Выбирает вариант товара (размер, цвет и т.д.) (новая функция в v2)"""
        try:
            variant_option = self.variant_selector.find_element(
                (By.CSS_SELECTOR, f"[data-variant='{variant_name}']")
            )
            variant_option.click()
            self.page.wait_for_page_loaded()
            return self
        except:
            raise ValueError(f"Вариант '{variant_name}' не найден")

    @auto_log
    def view_larger_image(self, image_index=0):
        """Открывает увеличенное изображение (новая функция в v2)"""
        try:
            images = self.product_images.find_elements((By.CSS_SELECTOR, ".product-image"))
            if len(images) > image_index:
                images[image_index].click()
                return self
            raise ValueError(f"Изображение с индексом {image_index} не найдено")
        except:
            raise ValueError("Не удалось открыть изображение")

    @auto_log
    def get_product_specifications(self):
        """Получает технические характеристики товара (новая функция в v2)"""
        try:
            specs_section = self.page.find_element((By.CSS_SELECTOR, ".product-specifications"))
            specs = {}

            spec_rows = specs_section.find_elements((By.CSS_SELECTOR, ".spec-row"))
            for row in spec_rows:
                key_element = row.find_element((By.CSS_SELECTOR, ".spec-key"))
                value_element = row.find_element((By.CSS_SELECTOR, ".spec-value"))
                specs[key_element.get_text()] = value_element.get_text()

            return specs
        except:
            return {}


class SearchSuggestionComponentV2(ElementGroup):
    """Компонент выпадающих подсказок при поиске версии 2 с улучшенной функциональностью"""

    def __init__(self, page):
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента версии 2"""
        self.suggestion_list = self.page.find_elements((By.CSS_SELECTOR, ".search-suggestion"))
        self.trending_searches = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".trending-searches"),
            "Популярные запросы"
        )
        self.recent_searches = BaseElement(
            self.page,
            (By.CSS_SELECTOR, ".recent-searches"),
            "Недавние запросы"
        )

    @auto_log
    def select_suggestion(self, index=0):
        """Выбирает подсказку поиска по индексу (улучшенная версия)"""
        if len(self.suggestion_list) > index:
            self.suggestion_list[index].click()
            from examples.amazon.v1.pages_v2 import AmazonSearchResultsPageV2
            return self.page.navigate_to(AmazonSearchResultsPageV2)
        raise ValueError(f"Подсказка с индексом {index} не найдена")

    @auto_log
    def select_trending_search(self, index=0):
        """Выбирает популярный запрос (новая функция в v2)"""
        trending_items = self.trending_searches.find_elements((By.CSS_SELECTOR, ".trending-item"))
        if len(trending_items) > index:
            trending_items[index].click()
            from examples.amazon.v1.pages_v2 import AmazonSearchResultsPageV2
            return self.page.navigate_to(AmazonSearchResultsPageV2)
        raise ValueError(f"Популярный запрос с индексом {index} не найден")

    @auto_log
    def select_recent_search(self, index=0):
        """Выбирает недавний запрос (новая функция в v2)"""
        recent_items = self.recent_searches.find_elements((By.CSS_SELECTOR, ".recent-item"))
        if len(recent_items) > index:
            recent_items[index].click()
            from examples.amazon.v1.pages_v2 import AmazonSearchResultsPageV2
            return self.page.navigate_to(AmazonSearchResultsPageV2)
        raise ValueError(f"Недавний запрос с индексом {index} не найден")