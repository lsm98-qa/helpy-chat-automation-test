from selenium.webdriver.common.by import By
from pages.chat_actions import click_new_chat, send_chat_message


def test_chat_refresh(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    #==========
    # Act
    #==========
    click_new_chat(wait)

    before_count = len(driver.find_elements(By.XPATH, "//main//p"))

    first_chat = "안녕하세요"
    send_chat_message(wait, first_chat)
        
    # AI 응답 대기
    wait.until(lambda d: len(d.find_elements(By.XPATH, "//main//p")) > before_count)

    # 새로고침 전 저장
    messages = driver.find_elements(By.XPATH, "//main//p")
    before_refresh = messages[-1].text

    # 새로고침
    driver.refresh()

    #==========
    # Assert
    #==========
    # 다시 메시지 로딩 대기 후 마지막 메시지 내용 검증
    wait.until(
        lambda d: len(d.find_elements(By.XPATH, "//main//p")) > 0
        and d.find_elements(By.XPATH, "//main//p")[-1].text == before_refresh
    )

    after_refresh = driver.find_elements(By.XPATH, "//main//p")[-1].text
    assert before_refresh == after_refresh