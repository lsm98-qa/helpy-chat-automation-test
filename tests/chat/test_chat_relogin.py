import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import LOGIN_BUTTON
from pages.account_menu import AccountMenu
from pages.chat_actions import click_new_chat, send_chat_message


def test_chat_persistence_after_relogin(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    click_new_chat(wait)

    #==========
    # Act
    #==========
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    first_chat = "안녕하세요"
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))
    send_chat_message(wait, first_chat)

    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count)

    # 로그아웃 직전 마지막 응답
    before_logout = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text

    # 로그아웃
    account_menu.logout()

    # 재로그인
    password = os.getenv("ACCOUNT_PASSWORD")
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    password_input.clear()
    password_input.send_keys(password)
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON)).click()

    #==========
    # Assert
    #==========
    wait.until(EC.presence_of_element_located((By.NAME, "input")))
    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0)
    after_relogin = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text
    assert after_relogin == before_logout
