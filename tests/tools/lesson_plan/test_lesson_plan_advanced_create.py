from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 요소가 화면에 표시될 때까지 기다린 뒤 반환하는 헬퍼
def _find(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


# 요소가 클릭 가능할 때까지 기다린 뒤 클릭하는 헬퍼
def _click(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    ).click()


# 요소를 화면 중앙으로 스크롤한 뒤 클릭하는 헬퍼
def _scroll_and_click(driver, by, value, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
        element,
    )

    WebDriverWait(driver, timeout).until(EC.visibility_of(element))
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


# 입력 필드를 비운 뒤 새 텍스트를 입력하는 헬퍼
def _type_text(driver, by, value, text, timeout=10):
    element = _find(driver, by, value, timeout)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


# 드롭다운에서 원하는 옵션을 선택하고 반영 여부까지 확인하는 헬퍼
def _select_dropdown_option(driver, label_text, option_text):
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//label[contains(text(),'{label_text}')]/following::div[@role='combobox'][1]",
        ))
    )
    dropdown.click()

    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//ul[@role='listbox']//li[normalize-space()='{option_text}']",
        ))
    )
    option.click()

    WebDriverWait(driver, 10).until(
        lambda d: option_text in d.find_element(
            By.XPATH,
            f"//label[contains(text(),'{label_text}')]/following::div[@role='combobox'][1]",
        ).text
    )


# 생성 버튼이 활성화될 때까지 기다리는 헬퍼
def _wait_until_generate_button_enabled(driver, timeout=180):
    button_locator = (
        By.XPATH,
        "//button[normalize-space()='수업지도안 생성' or normalize-space()='다시 생성']",
    )

    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(*button_locator).is_enabled()
    )

    return driver.find_element(*button_locator)


# =========================
# 수업지도안에서 정교한 생성 선택 후 생성 버튼이 다시 활성화되는지 검증
# =========================
def test_lesson_plan_detail_create(logged_in_driver, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    testlog.arrange("open_lesson_plan_tool", mode="advanced")
    # 도구 메뉴에서 수업지도안 페이지로 진입
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='수업지도안']")

    # 수업지도안 페이지 진입 여부 확인
    _find(driver, By.XPATH, "//*[contains(text(),'수업지도안')]", timeout=10)

    # 학교급 선택
    _select_dropdown_option(driver, "학교급", "초등학교")

    # 학년 선택
    _select_dropdown_option(driver, "학년", "6학년")

    # 과목 선택
    _select_dropdown_option(driver, "과목", "국어")

    # 교육 내용 입력
    _type_text(
        driver,
        By.XPATH,
        "//label[contains(text(),'교육 내용')]/following::input[1]",
        "1단원: 문학작품감상",
    )

    # 수업 차시 선택
    _select_dropdown_option(driver, "수업 차시", "1")

    # 생성 방식에서 정교한 생성 선택
    _scroll_and_click(driver, By.XPATH, "//*[contains(text(),'정교한 생성')]")

    # ==========
    # Act
    # ==========
    # 수업지도안 생성 버튼 또는 다시 생성 버튼까지 스크롤 후 클릭
    testlog.act("generate_advanced_lesson_plan")
    button_locator = (
        By.XPATH,
        "//button[normalize-space()='수업지도안 생성' or normalize-space()='다시 생성']",
    )
    generate_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(button_locator)
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
        generate_button,
    )

    button_text = generate_button.text.strip()

    try:
        generate_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", generate_button)

    # 다시 생성 버튼인 경우 확인 모달에서 다시 생성 버튼을 한 번 더 클릭
    if button_text == "다시 생성":
        _find(driver, By.XPATH, "//*[normalize-space()='결과 다시 생성하기']")

        _click(
            driver,
            By.XPATH,
            "//div[@role='dialog']//button[normalize-space()='다시 생성']",
        )

    # ==========
    # Assert
    # ==========
    # 생성 요청 후 버튼이 비활성화되는지 확인
    WebDriverWait(driver, 10).until(
        lambda d: not d.find_element(*button_locator).is_enabled()
    )

    # 생성 완료 후 버튼이 다시 활성화되는지 확인
    re_enabled_button = _wait_until_generate_button_enabled(driver, timeout=180)

    testlog.assert_(
        "advanced_lesson_plan_generation_completed",
        expected=True,
        actual=re_enabled_button.is_enabled(),
    )
    assert re_enabled_button.is_enabled(), "정교한 생성 완료 후 버튼이 다시 활성화되지 않았습니다."

    print("수업지도안 정교한 생성 완료!")
