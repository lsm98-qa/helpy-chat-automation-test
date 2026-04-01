from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_actions import click_new_chat, send_chat_message


# =========================
# 틀린 정보를 전송했을 때 올바른 정보로 정정해주는 지 검증
# =========================
def test_corrects_user_incorrect_claim(logged_in_driver, wait):
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

    # 잘못된 내용의 대화 전송
    first_chat = "한국의 수도는 부산이다"
    send_chat_message(wait, first_chat)

    #==========
    # Assert
    #==========
    # AI 응답 대기
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    wait_reply = WebDriverWait(driver, 60)
    wait_reply.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0)

    # 응답에 올바른 정보가 포함되어 있는지 확인
    reply_texts = [el.text.strip() for el in driver.find_elements(*AI_MESSAGE_TEXTS)]
    assert any("서울" in t for t in reply_texts), "잘못된 정보에 대한 정정 안내가 없습니다."