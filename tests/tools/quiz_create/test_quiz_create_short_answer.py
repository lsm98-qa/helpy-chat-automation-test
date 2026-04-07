from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
            f"//label[text()='{label_text}']/following::div[@role='combobox'][1]",
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
            f"//label[text()='{label_text}']/following::div[@role='combobox'][1]",
        ).text
    )


# 요소가 보이는지 여부만 확인하는 헬퍼
def _is_element_present(driver, by, value, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return True
    except TimeoutException:
        return False


# 이전 결과가 있으면 새 생성 이후 결과가 갱신될 때까지 기다리는 헬퍼
def _wait_for_result_refresh(driver, timeout=30):
    option_b_locator = (
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='B']",
    )

    # 이전 객관식 결과가 남아 있으면, 새 생성 시작 후 사라질 때까지 대기
    if _is_element_present(driver, *option_b_locator, timeout=2):
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(option_b_locator)
        )


# 이전 생성 결과가 있으면 다시 생성 플로우로 새 결과를 만들고,
# 없으면 자동 생성으로 새 결과를 시작하는 헬퍼
def _generate_quiz_result(driver):
    generate_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[@type='submit' and (normalize-space()='자동 생성' or normalize-space()='다시 생성')]",
        ))
    )

    button_text = generate_button.text.strip()
    generate_button.click()

    if button_text == "다시 생성":
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//h2[normalize-space()='결과 다시 생성하기']",
            ))
        )

        _click(
            driver,
            By.XPATH,
            "//div[@role='dialog']//button[normalize-space()='다시 생성']",
        )


# =========================
# 퀴즈 생성에서 주관식 유형을 선택했을 때 단일 답안 형태로 생성되는지 검증
# =========================
def test_quiz_create_short_answer(logged_in_driver, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    testlog.arrange("open_quiz_create_tool", quiz_type="주관식", difficulty="상")
    # 도구 메뉴에서 퀴즈 생성 페이지로 진입
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='퀴즈 생성']")

    # 유형 선택
    _select_dropdown_option(driver, "유형", "주관식")

    # 난이도 선택
    _select_dropdown_option(driver, "난이도", "상")

    # 주제 입력
    quiz_topic = "다음 중 프로그래밍의 기본 개념에 대한 설명으로 가장 적절한 것을 고르시오"
    _type_text(
        driver,
        By.XPATH,
        "//label[text()='주제']/following::textarea[1]",
        quiz_topic,
    )

    # ==========
    # Act
    # ==========
    testlog.act("generate_short_answer_quiz")
    _generate_quiz_result(driver)
    _wait_for_result_refresh(driver)

    # ==========
    # Assert
    # ==========
    # 주관식 결과의 A 항목이 표시되는지 확인
    option_a = _find(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='A']",
        timeout=180,
    )

    assert option_a.is_displayed(), "주관식 퀴즈 생성 실패: A 선택지가 표시되지 않았습니다."

    # 주관식에서는 B 항목이 표시되지 않아야 하는지 확인
    option_b_exists = _is_element_present(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='B']",
        timeout=5,
    )

    testlog.assert_(
        "short_answer_quiz_option_shape_valid",
        expected=True,
        actual=(option_a.is_displayed() and not option_b_exists),
        option_b_exists=option_b_exists,
    )
    assert not option_b_exists, "주관식 퀴즈 생성 실패: B 선택지가 표시되었습니다."

    print("주관식 퀴즈 생성 완료!")
