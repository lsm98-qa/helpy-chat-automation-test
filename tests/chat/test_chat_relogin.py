import os

from locators.login_locators import LOGIN_BUTTON
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_new_chat, send_chat_message




def test_chat_relogin(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver
    click_new_chat(wait)
    #==========
    # Act
    #==========
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    first_chat = "안녕하세요"
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))
    send_chat_message(wait, first_chat)

    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count)

    # 로그아웃 전 마지막 응답
    before_logout = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text

    # 로그아웃
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//*[@data-testid='PersonIcon']]")
        )
    ).click()

    logout_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//p[normalize-space()='로그아웃']"))
    )
    logout_btn.click()

    # 재 로그인
    password = os.getenv("ACCOUNT_PASSWORD")
    wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(password)
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON)).click()

    #==========
    # Assert
    #==========
    wait.until(EC.presence_of_element_located((By.NAME, "input")))
    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0)
    after_relogin = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text
    assert after_relogin == before_logout