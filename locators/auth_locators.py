from selenium.webdriver.common.by import By

EMAIL_INPUT = (By.NAME, "loginId")
PASSWORD_INPUT = (By.NAME, "password")
LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

PROFILE_AVATAR = (By.CSS_SELECTOR, "[data-testid='PersonIcon']")
LOGOUT_BUTTON = (
    By.XPATH,
    "//div[@role='button' and .//*[@data-testid='arrow-right-from-bracketIcon']]",
)
