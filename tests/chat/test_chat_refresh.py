from selenium.webdriver.common.by import By
from pages.chat_actions import click_new_chat, send_chat_message


def test_chat_message_persists_after_refresh(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    #==========
    # Act
    #==========
    click_new_chat(wait)

    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))

    first_chat = "안녕하세요"
    send_chat_message(wait, first_chat)

    # AI 응답 대기(전송 전과 동일한 선택자로 개수 비교) — 응답 지연 대비 60초
    wait.until(
        lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count
    )

    # 새로고침 전 저장
    messages = driver.find_elements(*AI_MESSAGE_TEXTS)
    before_refresh = messages[-1].text

    # 새로고침
    driver.refresh()

    #==========
    # Assert
    #==========
    # 다시 메시지 로딩 대기 후 마지막 메시지 내용 검증
    wait.until(
        lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0
        and d.find_elements(*AI_MESSAGE_TEXTS)[-1].text == before_refresh
    )

    after_refresh = driver.find_elements(*AI_MESSAGE_TEXTS)[-1].text
    assert before_refresh == after_refresh