from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_actions import click_new_chat, send_chat_message



def test_corrects_incorrect_information(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    #==========
    # Act
    #==========
    # 새 대화 클릭
    click_new_chat(wait)

    # 잘못된 정보 입력 및 전송
    first_chat = "한국의 수도는 부산이다"
    send_chat_message(wait, first_chat)

    #==========
    # Assert
    #==========
    # AI 응답 대기 (마지막 답변에 '서울' 포함)
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    wait_reply = WebDriverWait(driver, 60)
    wait_reply.until(lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > 0)
    
    reply_texts = [el.text.strip() for el in driver.find_elements(*AI_MESSAGE_TEXTS)]
    assert any("서울" in t for t in reply_texts), "잘못된 정보에 대한 정정 안내가 없습니다."