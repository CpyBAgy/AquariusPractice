from selenium.webdriver.common.by import By
from framework import PageLocators


class AmazonLoginPageLocators(PageLocators):
    EMAIL_INPUT = (By.ID, "ap_email")
    CONTINUE_BUTTON = (By.ID, "continue")
    PASSWORD_INPUT = (By.ID, "ap_password")
    SIGN_IN_BUTTON = (By.ID, "signInSubmit")
    CHANGE_LINK = (By.ID, "ap_change_login_claim")
    FORGOT_PASSWORD_LINK = (By.ID, "auth-fpp-link-bottom")


class AmazonHomePageLocators(PageLocators):
    SEARCH_INPUT = (By.ID, "twotabsearchtextbox")
    SEARCH_BUTTON = (By.ID, "nav-search-submit-button")
    ACCOUNT_MENU = (By.ID, "nav-link-accountList")
    CART_ICON = (By.ID, "nav-cart")
    SEARCH_DROPDOWN = (By.ID, "searchDropdownBox")
    SEARCH_SUGGESTIONS = (By.CSS_SELECTOR, "div.s-suggestion")


class AmazonSearchResultsLocators(PageLocators):
    SEARCH_RESULTS = (By.CSS_SELECTOR, "div.s-result-item")
    PRODUCT_TITLES = (By.CSS_SELECTOR, "span.a-size-medium")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "span.a-dropdown-label")
    BEST_SELLER_BADGE = (By.CSS_SELECTOR, "span.a-badge-text")


class AmazonProductPageLocators(PageLocators):
    PRODUCT_TITLE = (By.ID, "productTitle")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "span.a-price-whole")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart-button")
    BUY_NOW_BUTTON = (By.ID, "buy-now-button")
    PRODUCT_DESCRIPTION = (By.ID, "productDescription")
    COLOR_OPTIONS = (By.CSS_SELECTOR, "li.swatch-list")


class AmazonCartPageLocators(PageLocators):
    CART_ITEMS = (By.CSS_SELECTOR, ".sc-list-item")
    QUANTITY_DROPDOWN = (By.CSS_SELECTOR, "select.a-native-dropdown")
    QUANTITY_INCREMENT = (By.CSS_SELECTOR, "input.a-button-input[data-action='increase-quantity']")
    QUANTITY_DECREMENT = (By.CSS_SELECTOR, "input.a-button-input[data-action='decrease-quantity']")
    QUANTITY_TEXTBOX = (By.CSS_SELECTOR, "input.sc-quantity-textfield")
    DELETE_BUTTON = (By.CSS_SELECTOR, "input[value='Delete']")
    PROCEED_TO_CHECKOUT = (By.CSS_SELECTOR, "input[name='proceedToRetailCheckout']")
    SUBTOTAL = (By.CSS_SELECTOR, "#sc-subtotal-amount-activecart > span")
    SAVE_FOR_LATER = (By.CSS_SELECTOR, "input[value='Save for later']")


class AmazonCheckoutPageLocators(PageLocators):
    DELIVERY_ADDRESS = (By.CSS_SELECTOR, ".ship-to-this-address a")
    ADD_NEW_ADDRESS = (By.CSS_SELECTOR, "a#add-new-address-popover-link")
    PAYMENT_METHOD = (By.CSS_SELECTOR, "#payment-method")
    ORDER_TOTAL = (By.CSS_SELECTOR, ".grand-total-price")
    PLACE_ORDER_BUTTON = (By.CSS_SELECTOR, "#placeYourOrder")