from selenium.webdriver.common.by import By
from chat_actions import click_new_chat, send_chat_message


def test_login(logged_in_driver, wait):
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