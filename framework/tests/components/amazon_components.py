from framework.src.core.component import Component
from framework.tests.locators.amazon_component_locators import (
    SearchSuggestionLocators,
    HeaderComponentLocators,
    CartItemLocators,
    ProductDetailsLocators
)


class SearchSuggestionComponent(Component):
    """Компонент выпадающих подсказок при поиске"""

    def __init__(self, page):
        self.locators = SearchSuggestionLocators()
        super().__init__(page, self.locators.SUGGESTION_ITEM)

    def select_suggestion(self, index=0):
        """Выбирает подсказку поиска по индексу"""
        suggestions = self.find_all(self.locators.SUGGESTION_ITEM)
        if len(suggestions) > index:
            self.click(suggestions[index])
            from framework.tests.pages.amazon_pages import AmazonSearchResultsPage
            return self.page.navigate_to(AmazonSearchResultsPage)
        raise ValueError(f"Подсказка с индексом {index} не найдена")


class HeaderComponent(Component):
    """Компонент верхнего меню Amazon"""

    def __init__(self, page):
        self.locators = HeaderComponentLocators()
        super().__init__(page, self.locators.NAVBAR)

    def search(self, search_text):
        """Выполняет поиск товара"""
        self.type(self.locators.SEARCH_INPUT, search_text)
        self.click(self.locators.SEARCH_BUTTON)
        from framework.tests.pages.amazon_pages import AmazonSearchResultsPage
        return self.page.navigate_to(AmazonSearchResultsPage)

    def go_to_cart(self):
        """Переходит в корзину"""
        self.click(self.locators.CART_ICON)
        from framework.tests.pages.amazon_pages import AmazonCartPage
        return self.page.navigate_to(AmazonCartPage)

    def open_account_menu(self):
        """Открывает меню учетной записи"""
        self.click(self.locators.ACCOUNT_MENU)
        return self


class CartItemComponent(Component):
    """Компонент элемента корзины"""

    def __init__(self, page, item_element):
        self.locators = CartItemLocators()
        super().__init__(page, root_element=item_element)

    def increase_quantity(self):
        """Увеличивает количество товара на 1"""
        self.click(self.locators.INCREMENT_BUTTON)
        self.page.wait_for_page_loaded()
        return self

    def decrease_quantity(self):
        """Уменьшает количество товара на 1"""
        self.click(self.locators.DECREMENT_BUTTON)
        self.page.wait_for_page_loaded()
        return self

    def delete(self):
        """Удаляет товар из корзины"""
        self.click(self.locators.DELETE_BUTTON)
        self.page.wait_for_page_loaded()
        return self.page

    def get_title(self):
        """Получает название товара"""
        title_element = self.find(self.locators.PRODUCT_TITLE)
        return title_element.text

    def get_price(self):
        """Получает цену товара"""
        price_element = self.find(self.locators.PRODUCT_PRICE)
        return price_element.text.strip()


class ProductDetailsComponent(Component):
    """Компонент деталей товара"""

    def __init__(self, page):
        self.locators = ProductDetailsLocators()
        super().__init__(page, self.locators.PRODUCT_CONTAINER)

    def get_title(self):
        """Получает название товара"""
        return self.page.find(self.locators.PRODUCT_TITLE).text

    def get_price(self):
        """Получает цену товара"""
        try:
            whole = self.page.find(self.locators.PRODUCT_PRICE_WHOLE).text.strip()
            fraction = self.page.find(self.locators.PRODUCT_PRICE_FRACTION).text.strip()
            return f"{whole}.{fraction}"
        except:
            try:
                price_element = self.page.find(self.locators.ALT_PRICE)
                price_text = price_element.get_attribute("innerText")
                return price_text.replace("$", "").strip()
            except:
                try:
                    price_element = self.page.find(self.locators.PRICE_BLOCK)
                    return price_element.text.replace("$", "").strip()
                except:
                    raise Exception("Не удалось найти цену товара на странице")

    def add_to_cart(self):
        """Добавляет товар в корзину"""
        self.page.click(self.locators.ADD_TO_CART_BUTTON)
        self.page.wait_for_page_loaded()
        if "cart" in self.page.driver.current_url:
            from framework.tests.pages.amazon_pages import AmazonCartPage
            return self.page.navigate_to(AmazonCartPage)
        return self.page