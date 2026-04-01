from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import LOGOUT_BUTTON, PROFILE_AVATAR


class AccountMenu:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def click_profile_avatar(self):
        self.wait.until(EC.element_to_be_clickable(PROFILE_AVATAR)).click()

    def click_logout_button(self):
        self.wait.until(EC.element_to_be_clickable(LOGOUT_BUTTON)).click()

    def logout(self):
        self.click_profile_avatar()
        self.click_logout_button()
