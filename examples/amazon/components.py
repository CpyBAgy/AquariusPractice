from framework.core.component import ElementGroup
from framework import auto_log
from examples.amazon.component_locators import (
    SearchSuggestionLocators,
    HeaderComponentLocators,
    CartItemLocators,
    ProductDetailsLocators
)


class SearchSuggestionComponent(ElementGroup):
    """Компонент выпадающих подсказок при поиске"""

    def __init__(self, page):
        self.locators = SearchSuggestionLocators()
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        pass

    @auto_log
    def select_suggestion(self, index=0):
        """Выбирает подсказку поиска по индексу"""
        suggestions = self.page.find_elements(self.locators.SUGGESTION_ITEM)
        if len(suggestions) > index:
            suggestions[index].click()
            from tests.pages.amazon_pages import AmazonSearchResultsPage
            return self.page.navigate_to(AmazonSearchResultsPage)
        raise ValueError(f"Подсказка с индексом {index} не найдена")


class HeaderComponent(ElementGroup):
    """Компонент верхнего меню Amazon"""

    def __init__(self, page):
        self.locators = HeaderComponentLocators()
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        self.search_input = self.page.find_input(self.locators.SEARCH_INPUT)
        self.search_button = self.page.find_button(self.locators.SEARCH_BUTTON)
        self.account_menu = self.page.find_element(self.locators.ACCOUNT_MENU)
        self.cart_icon = self.page.find_element(self.locators.CART_ICON)
        self.orders_link = self.page.find_link(self.locators.ORDERS_LINK)

    @auto_log
    def search(self, search_text):
        """Выполняет поиск товара"""
        self.search_input.type(search_text)
        self.search_button.click()
        from tests.pages.amazon_pages import AmazonSearchResultsPage
        return self.page.navigate_to(AmazonSearchResultsPage)

    @auto_log
    def go_to_cart(self):
        """Переходит в корзину"""
        self.cart_icon.click()
        from tests.pages.amazon_pages import AmazonCartPage
        return self.page.navigate_to(AmazonCartPage)

    @auto_log
    def open_account_menu(self):
        """Открывает меню учетной записи"""
        self.account_menu.click()
        return self


class CartItemComponent(ElementGroup):
    """Компонент элемента корзины"""

    def __init__(self, page, item_element):
        self.item_element = item_element
        self.locators = CartItemLocators()
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        pass

    @auto_log
    def increment_button(self):
        """Возвращает кнопку увеличения количества"""
        return self.page.find_button(self.locators.INCREMENT_BUTTON)

    @auto_log
    def decrement_button(self):
        """Возвращает кнопку уменьшения количества"""
        return self.page.find_button(self.locators.DECREMENT_BUTTON)

    @auto_log
    def delete_button(self):
        """Возвращает кнопку удаления"""
        return self.page.find_button(self.locators.DELETE_BUTTON)

    @auto_log
    def increase_quantity(self):
        """Увеличивает количество товара на 1"""
        self.increment_button().click()
        self.page.wait_for_page_loaded()
        return self

    @auto_log
    def decrease_quantity(self):
        """Уменьшает количество товара на 1"""
        self.decrement_button().click()
        self.page.wait_for_page_loaded()
        return self

    @auto_log
    def delete(self):
        """Удаляет товар из корзины"""
        self.delete_button().click()
        self.page.wait_for_page_loaded()
        return self.page

    @auto_log
    def get_title(self):
        """Получает название товара"""
        title_element = self.page.find_element(self.locators.PRODUCT_TITLE)
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара"""
        price_element = self.page.find_element(self.locators.PRODUCT_PRICE)
        return price_element.get_text().strip()


class ProductDetailsComponent(ElementGroup):
    """Компонент деталей товара"""

    def __init__(self, page):
        self.locators = ProductDetailsLocators()
        super().__init__(page)

    def _init_elements(self):
        """Инициализирует элементы компонента"""
        pass

    @auto_log
    def get_title(self):
        """Получает название товара"""
        title_element = self.page.find_element(self.locators.PRODUCT_TITLE)
        return title_element.get_text()

    @auto_log
    def get_price(self):
        """Получает цену товара"""
        try:
            whole_element = self.page.find_element(self.locators.PRODUCT_PRICE_WHOLE)
            fraction_element = self.page.find_element(self.locators.PRODUCT_PRICE_FRACTION)
            whole = whole_element.get_text().strip()
            fraction = fraction_element.get_text().strip()
            return f"{whole}.{fraction}"
        except:
            try:
                price_element = self.page.find_element(self.locators.ALT_PRICE)
                price_text = price_element.get_attribute("innerText")
                return price_text.replace("$", "").strip()
            except:
                try:
                    price_element = self.page.find_element(self.locators.PRICE_BLOCK)
                    return price_element.get_text().replace("$", "").strip()
                except:
                    raise Exception("Не удалось найти цену товара на странице")

    @auto_log
    def add_to_cart(self):
        """Добавляет товар в корзину"""
        add_button = self.page.find_button(self.locators.ADD_TO_CART_BUTTON)
        add_button.click()
        self.page.wait_for_page_loaded()

        if "cart" in self.page.driver.current_url:
            from tests.pages.amazon_pages import AmazonCartPage
            return self.page.navigate_to(AmazonCartPage)
        return self.page