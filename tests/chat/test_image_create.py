from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_actions import click_new_chat

def test_image_generation(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    
    # 새 대화 클릭
    click_new_chat(wait)
    
    #==========
    # Act
    #==========
    # 입력창 확인
    chat_input = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "input")
        )
    )

    # 좌측 + 버튼 클릭
    plus_btn = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='plusIcon']")
        )
    )

    plus_btn.click()

    # 이미지 생성 메뉴 클릭
    image_menu = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(normalize-space(), '이미지 생성')]")
        )
    )
    image_menu.click()

    # 프롬프트 입력 및 전송
    chat_input = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "input")
        )
    )
    chat_input.click()
    chat_input.send_keys("강아지 이미지 생성해줘")
    chat_input.send_keys(Keys.ENTER)