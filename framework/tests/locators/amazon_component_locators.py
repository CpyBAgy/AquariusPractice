from selenium.webdriver.common.by import By
from framework.src.core.locator import PageLocators


class SearchSuggestionLocators(PageLocators):
    SUGGESTION_ITEM = (By.CSS_SELECTOR, "div.s-suggestion")


class HeaderComponentLocators(PageLocators):
    NAVBAR = (By.ID, "navbar")
    SEARCH_INPUT = (By.ID, "twotabsearchtextbox")
    SEARCH_BUTTON = (By.ID, "nav-search-submit-button")
    ACCOUNT_MENU = (By.ID, "nav-link-accountList")
    CART_ICON = (By.ID, "nav-cart")
    ORDERS_LINK = (By.ID, "nav-orders")


class CartItemLocators(PageLocators):
    INCREMENT_BUTTON = (By.CSS_SELECTOR, "input[data-action='increase-quantity']")
    DECREMENT_BUTTON = (By.CSS_SELECTOR, "input[data-action='decrease-quantity']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "input[value='Delete']")
    QUANTITY_FIELD = (By.CSS_SELECTOR, "input.sc-quantity-textfield")
    PRODUCT_TITLE = (By.CSS_SELECTOR, "span.a-truncate-cut")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "span.sc-price")


class ProductDetailsLocators(PageLocators):
    PRODUCT_CONTAINER = (By.ID, "ppd")
    PRODUCT_TITLE = (By.ID, "productTitle")
    PRODUCT_PRICE_WHOLE = (By.CSS_SELECTOR, "span.a-price .a-price-whole")
    PRODUCT_PRICE_FRACTION = (By.CSS_SELECTOR, "span.a-price .a-price-fraction")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart-button")
    BUY_NOW_BUTTON = (By.ID, "buy-now-button")
    ALT_PRICE = (By.CSS_SELECTOR, ".a-price .a-offscreen")
    PRICE_BLOCK = (By.CSS_SELECTOR, "#priceblock_ourprice, #price_inside_buybox")
