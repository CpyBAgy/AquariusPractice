from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Element:
    def __init__(self, driver, locator, timeout=10):
        self.driver = driver
        self.locator = locator
        self.timeout = timeout

    def find(self):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(self.locator)
        )

    def find_all(self):
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(self.locator)
        )
        return self.driver.find_elements(*self.locator)

    def click(self):
        WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(self.locator)
        ).click()
        return self

    def type(self, text):
        element = self.find()
        element.clear()
        element.send_keys(text)
        return self

    def is_visible(self):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(self.locator)
            )
            return True
        except TimeoutException:
            return False

    def get_text(self):
        return self.find().text

    def get_attribute(self, attribute_name):
        return self.find().get_attribute(attribute_name)