from selenium.webdriver.common.by import By
from pages.chat_actions import click_new_chat, send_chat_message


def test_chat_message_persists_after_refresh(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver

    #==========
    # Act
    #==========
    # 새 대화 시작
    click_new_chat(wait)

    # 현재 응답 메시지 개수 확인
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))

    first_chat = "안녕하세요"

    # 대화 전송
    send_chat_message(wait, first_chat)

    # AI 응답 대기
    wait.until(
        lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count
    )

    # 마지막 응답 저장 후 새로고침
    messages = driver.find_elements(*AI_MESSAGE_TEXTS)
    before_refresh = messages[-1].text
    driver.refresh()

    #==========
    # Assert
    #==========
    # 새로고침 후 메시지가 유지되는지 확인
    wait.until(
        lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0
        and d.find_elements(*AI_MESSAGE_TEXTS)[-1].text == before_refresh
    )

    after_refresh = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text
    assert before_refresh == after_refresh, "새로고침 전과 채팅이 동일하지 않습니다."
