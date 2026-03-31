from locators.auth_locators import EMAIL_INPUT, LOGIN_BUTTON, PASSWORD_INPUT


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def enter_email(self, email):
        self.driver.find_element(*EMAIL_INPUT).send_keys(email)

    def enter_password(self, password):
        self.driver.find_element(*PASSWORD_INPUT).send_keys(password)

    def click_login(self):
        self.driver.find_element(*LOGIN_BUTTON).click()

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()
