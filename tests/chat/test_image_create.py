from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.chat_actions import click_new_chat


# =========================
# 대화의 이미지 생성 기능을 사용했을 때 이미지 정상 출력 여부 검증
# =========================
def test_chat_generates_and_displays_image(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver
    testlog.arrange("logged_in_driver_ready", prompt="강아지 이미지 생성해줘")


    #==========
    # Act
    #==========
    testlog.act("request_image_generation")

    # 새 대화 시작
    click_new_chat(wait)

    # 입력창 확인
    chat_input = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "input")
        )
    )

    # 플러스 버튼 클릭
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

    # 이미지 생성 요청 전송
    chat_input.click()
    chat_input.send_keys("강아지 이미지 생성해줘")
    chat_input.send_keys(Keys.ENTER)

    #==========
    # Assert
    #==========
    # 생성된 이미지가 표시되는지 확인
    wait_image = WebDriverWait(driver, 60)
    has_generated_image = wait_image.until(
        lambda d: len(
            d.execute_script(
                """
                return Array.from(document.querySelectorAll('main img'))
                  .filter(img => img.src && img.complete && img.naturalWidth >= 200 && img.offsetParent !== null);
                """
            )
        )
        > 0
    )
    testlog.assert_(
        "generated_image_is_visible",
        expected=True,
        actual=has_generated_image,
    )
    assert has_generated_image, "이미지 파일이 생성되지 않았습니다."
