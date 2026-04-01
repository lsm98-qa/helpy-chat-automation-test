from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_actions import click_new_chat

def test_chat_generates_and_displays_image(logged_in_driver, wait):
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

    # 생성할 이미지 내용 전송
    chat_input.click()
    chat_input.send_keys("강아지 이미지 생성해줘")
    chat_input.send_keys(Keys.ENTER)

    #==========
    # Assert
    #==========
    # 채팅 본문에 로드 완료된 이미지가 보일 때까지 대기
    wait_image = WebDriverWait(driver, 60)
    assert wait_image.until(
        lambda d: len(
            d.execute_script(
                """
                return Array.from(document.querySelectorAll('main img'))
                  .filter(img => img.src && img.complete && img.naturalWidth >= 200 && img.offsetParent !== null);
                """
            )
        )
        > 0
    ), "이미지 파일이 생성되지 않았습니다."
