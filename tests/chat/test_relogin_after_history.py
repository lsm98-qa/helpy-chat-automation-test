import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import LOGIN_BUTTON
from pages.account_menu import AccountMenu
from pages.chat_actions import click_new_chat, send_chat_message


# =========================
# 대화 생성 후 재로그인 시 메시지가 유지되는 지 검증
# =========================
def test_chat_persistence_after_relogin(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    first_chat = "안녕하세요"
    testlog.arrange("logged_in_driver_ready", message=first_chat)

    # 새 대화 시작
    click_new_chat(wait)

    #==========
    # Act
    #==========
    testlog.act("send_message_logout_and_relogin")
    # 현재 응답 메시지 개수 확인
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))

    # 대화 전송
    send_chat_message(wait, first_chat)

    # AI 응답 대기
    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count)

    # 마지막 응답 저장 후 로그아웃
    before_logout = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text

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
    # 재로그인 후 마지막 메시지가 유지되는지 확인
    wait.until(EC.presence_of_element_located((By.NAME, "input")))
    wait.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0)
    after_relogin = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text
    is_persisted = after_relogin == before_logout
    testlog.assert_(
        "chat_message_persisted_after_relogin",
        expected=True,
        actual=is_persisted,
    )
    assert is_persisted, "로그아웃 전과 채팅이 동일하지 않습니다."
