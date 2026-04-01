from pathlib import Path

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


# 모달 내부 버튼을 클릭하는 헬퍼
def _click_modal_button(driver, button_text, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@role='presentation' or @role='dialog']//button[normalize-space()='{button_text}']",
        ))
    ).click()


# 입력 내역 초기화 버튼이 있으면 초기화하는 헬퍼
def _reset_input_history_if_exists(driver):
    try:
        _click(driver, By.XPATH, "//button[contains(., '입력 내역 초기화')]", timeout=3)
        _click(driver, By.XPATH, "//button[contains(., '초기화 하기')]", timeout=5)

        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//button[contains(., '초기화 하기')]")
            )
        )
    except Exception:
        pass


# 세부 특기사항의 학생 정보 입력 단계까지 이동하는 헬퍼
def _go_to_student_info_step(driver):
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='세부 특기사항']")

    _reset_input_history_if_exists(driver)

    _click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='초등학교']")

    _click(driver, By.XPATH, "//label[text()='학년']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='6학년']")

    _type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']",
        SUBJECT_INPUT,
    )
    _click(driver, By.XPATH, "//li[normalize-space()='국어']")

    _type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='수업 단원을 입력해주세요.']",
        UNIT_INPUT,
    )

    _click(
        driver,
        By.XPATH,
        "//button[@type='submit' and contains(., '다음으로')]",
    )

    name_input_area = _find(driver, By.XPATH, "//p[text()='이름을 입력해주세요.']")

    assert name_input_area.is_displayed(), NAME_INPUT_AREA_NOT_DISPLAYED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='초등학교']").is_displayed(), SCHOOL_LEVEL_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='6학년']").is_displayed(), GRADE_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='국어']").is_displayed(), SUBJECT_NOT_SAVED
    assert _find(driver, By.XPATH, "//h6[normalize-space()='1단원 : 문학작품감상']").is_displayed(), UNIT_NOT_SAVED


# 학생 이름과 활동 키워드를 입력 및 저장하는 헬퍼
def _save_student_keyword(driver, student_name):
    _click(driver, By.XPATH, "//*[normalize-space()='이름을 입력해주세요.']")
    active_element = driver.switch_to.active_element
    active_element.send_keys(Keys.CONTROL, "a")
    active_element.send_keys(Keys.BACKSPACE)
    active_element.send_keys(student_name)

    _click(driver, By.XPATH, "//*[normalize-space()='키워드를 선택해주세요.']")
    _find(driver, By.XPATH, "//div[@role='presentation' or @role='dialog']")
    _click(driver, By.XPATH, "//*[normalize-space()='학습 태도']")
    _click(driver, By.XPATH, "//*[normalize-space()='수업 집중도 높음']")
    _click_modal_button(driver, "저장")

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located(
            (By.XPATH, "//div[@role='presentation' or @role='dialog']")
        )
    )


# 학생 이름 행의 AI 생성 결과가 완료될 때까지 기다리는 헬퍼
def _wait_for_completed_ai_result(driver, student_name, timeout=180):
    loading_message = "입력한 내용을 바탕으로 세부 특기사항을 생성하고 있습니다."

    def _result_is_ready(d):
        cell = d.find_element(
            By.XPATH,
            f"//*[normalize-space()='{student_name}']/ancestor::tr/td[last()]",
        )
        text = cell.text.strip()

        if not text or text == "-" or loading_message in text:
            return False

        return text

    return WebDriverWait(driver, timeout).until(_result_is_ready)


# AI 생성 결과 텍스트를 txt 파일로 저장하는 헬퍼
def _save_text_file(file_path, text):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


# =========================
# 세부 특기사항에서 학생 정보와 활동 키워드를 저장한 뒤 AI 생성 결과를 txt 파일로 저장하는지 검증
# =========================
def test_spec_ai_result_save_to_txt(logged_in_driver):
    driver = logged_in_driver
    student_name = "홍길동"
    result_file_path = Path("tests/tools/spec_detail/downloads/spec_ai_result_honggildong.txt")

    # ==========
    # Arrange
    # ==========
    _go_to_student_info_step(driver)

    # ==========
    # Act
    # ==========
    _save_student_keyword(driver, student_name)
    ai_result_text = _wait_for_completed_ai_result(driver, student_name)
    _save_text_file(result_file_path, ai_result_text)

    # ==========
    # Assert
    # ==========
    assert ai_result_text, "AI 생성 결과가 비어 있습니다."
    assert result_file_path.exists(), "AI 생성 결과 txt 파일이 생성되지 않았습니다."
    assert result_file_path.read_text(encoding="utf-8").strip(), "생성된 txt 파일 내용이 비어 있습니다."

    print(f"PASS: AI 생성 결과 txt 저장 완료 - {result_file_path}")
