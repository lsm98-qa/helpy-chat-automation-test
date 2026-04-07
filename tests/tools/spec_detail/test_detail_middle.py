from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.tools.spec_detail.assert_messages import (
    GRADE_NOT_SAVED,
    NAME_INPUT_AREA_NOT_DISPLAYED,
    SCHOOL_LEVEL_NOT_SAVED,
    SUBJECT_NOT_SAVED,
    UNIT_NOT_SAVED,
)
from tests.tools.spec_detail.input_values import SUBJECT_INPUT, UNIT_INPUT


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
# 세부 특기사항 생성 후 학생 이름 입력 화면으로 정상 진입하는지 검증
# =========================
def test_spec_create(logged_in_driver, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    testlog.arrange("open_spec_detail_tool", school_level="중학교", grade="3학년", subject="국어")
    # 도구 메뉴에서 세부 특기사항 페이지로 진입
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='세부 특기사항']")

    # 기존 입력 내역이 있으면 초기화
    _reset_input_history_if_exists(driver)

    # 학교급 선택
    _click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='중학교']")

    # 학년 선택
    _click(driver, By.XPATH, "//label[text()='학년']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='3학년']")

    # 과목 입력 및 선택
    _type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']",
        SUBJECT_INPUT,
    )
    _click(driver, By.XPATH, "//li[normalize-space()='국어']")

    # 단원 입력
    _type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='수업 단원을 입력해주세요.']",
        UNIT_INPUT,
    )

    # ==========
    # Act
    # ==========
    # 다음으로 버튼을 클릭
    testlog.act("submit_spec_detail_form")
    _click(
        driver,
        By.XPATH,
        "//button[@type='submit' and contains(., '다음으로')]",
    )

    # 학생 이름 입력 화면이 나타날 때까지 대기
    name_input_area = _find(driver, By.XPATH, "//p[text()='이름을 입력해주세요.']")

    # 디버깅용 스크린샷 저장
    driver.save_screenshot("result.png")
    print("스크린샷 저장 완료 (result.png)")

    # ==========
    # Assert
    # ==========
    # 학생 이름 입력 화면이 정상적으로 표시되는지 확인
    testlog.assert_(
        "spec_detail_student_info_step_visible",
        expected=True,
        actual=name_input_area.is_displayed(),
    )
    assert name_input_area.is_displayed(), NAME_INPUT_AREA_NOT_DISPLAYED

    # 이전 단계에서 입력한 값이 정상적으로 유지되는지 확인
    assert _find(driver, By.XPATH, "//h6[normalize-space()='중학교']").is_displayed(), SCHOOL_LEVEL_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='3학년']").is_displayed(), GRADE_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='국어']").is_displayed(), SUBJECT_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='1단원 : 문학작품감상']").is_displayed(), UNIT_NOT_SAVED
