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


# =========================
# 퀴즈 생성에서 객관식 단일 선택 유형을 선택했을 때 선택지가 정상 생성되는지 검증
# =========================
def test_quiz_create_single_choice(logged_in_driver):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    # 도구 메뉴에서 퀴즈 생성 페이지로 진입
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='퀴즈 생성']")

    # 유형 선택
    _select_dropdown_option(driver, "유형", "객관식 (단일 선택)")

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
    # 생성 버튼을 클릭하고 필요 시 다시 생성 확인 모달을 처리
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

    # ==========
    # Assert
    # ==========
    # 객관식 선택지 A가 생성되어 표시되는지 확인
    option_a = _find(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='A']",
        timeout=180,
    )

    # 객관식 선택지 B가 생성되어 표시되는지 확인
    option_b = _find(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='B']",
        timeout=30,
    )

    assert option_a.is_displayed(), "객관식 퀴즈 생성 실패: A 선택지가 표시되지 않았습니다."
    assert option_b.is_displayed(), "객관식 퀴즈 생성 실패: B 선택지가 표시되지 않았습니다."

    print("객관식 퀴즈 생성 완료!")
