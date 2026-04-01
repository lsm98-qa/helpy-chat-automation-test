from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.tools.spec_detail.assert_messages import (
    NAME_INPUT_AREA_NOT_DISPLAYED,
    SCHOOL_LEVEL_NOT_SAVED,
)


# 요소가 화면에 표시될 때까지 기다린 뒤 반환하는 헬퍼
def _find(driver, by, value):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, value))
    )


# 요소가 클릭 가능할 때까지 기다린 뒤 클릭하는 헬퍼
def _click(driver, by, value):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    ).click()


# 입력 필드를 비운 뒤 새 텍스트를 입력하는 헬퍼
def _type_text(driver, by, value, text):
    element = _find(driver, by, value)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


# 입력 내역 초기화 버튼이 있으면 초기화하는 헬퍼
def _reset_input_history_if_exists(driver):
    try:
        reset_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., '입력 내역 초기화')]")
            )
        )
        reset_btn.click()

        confirm_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., '초기화 하기')]")
            )
        )
        confirm_btn.click()

        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//button[contains(., '초기화 하기')]")
            )
        )
    except Exception:
        # 초기화 버튼이 없는 경우 그대로 진행
        pass


# =========================
# 행동특성 및 종합의견에서 학교급 선택 후 학생 정보 입력 화면으로 정상 진입하는지 검증
# =========================
def test_behavior_create(logged_in_driver):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    # 도구 메뉴에서 행동특성 및 종합의견 페이지로 진입
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='행동특성 및 종합의견']")

    # 기존 입력 내역이 있으면 초기화
    _reset_input_history_if_exists(driver)

    # 학교급 선택
    _click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='초등학교']")

    # ==========
    # Act
    # ==========
    # 다음으로 버튼을 클릭
    _click(driver, By.XPATH, "//button[@type='submit' and contains(., '다음으로')]")

    # 학생 정보 입력 화면이 나타날 때까지 대기
    name_input_area = _find(
        driver,
        By.XPATH,
        "//input[@placeholder='학생 이름 검색']",
    )

    # 학교급 정보가 저장되어 표시되는지 확인하기 위한 요소 대기
    school_level_area = _find(
        driver,
        By.XPATH,
        "//p[normalize-space()='학교급']/following::h6[normalize-space()='초등학교'][1]",
    )

    # ==========
    # Assert
    # ==========
    # 학생 정보 입력 화면이 정상적으로 표시되는지 확인
    assert name_input_area.is_displayed(), NAME_INPUT_AREA_NOT_DISPLAYED

    # 이전 단계에서 선택한 학교급이 정상적으로 유지되는지 확인
    assert school_level_area.is_displayed(), SCHOOL_LEVEL_NOT_SAVED

    print("PASS: 행동특성 및 종합의견 - 학교급 저장 확인 완료")
