from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from chat_actions import click_new_chat, send_chat_message


def test_login(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    #==========
    # Act
    #==========

    # 새 대화 생성
    click_new_chat(wait)

    first_chat = "안녕하세요"
    send_chat_message(wait, first_chat)

    #==========
    # Assert
    #==========
    # 입력 값 제외 안녕/반갑/도와 문구 포함 여부로 응답 검증
    assert wait.until(
        lambda d: any(
            len(t) > 4 and t != first_chat and ("안녕" in t or "반갑" in t or "도와" in t)
            for t in (p.text.strip() for p in d.find_element(By.TAG_NAME, "body").find_elements(By.TAG_NAME, "p"))
        )
    )