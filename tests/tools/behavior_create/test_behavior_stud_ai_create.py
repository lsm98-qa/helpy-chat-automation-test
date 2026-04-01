import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.tools.spec_detail.assert_messages import (
    NAME_INPUT_AREA_NOT_DISPLAYED,
    SCHOOL_LEVEL_NOT_SAVED,
)


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


# 모달 내부 버튼을 클릭하는 헬퍼
def _click_modal_button(driver, button_text, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@role='presentation' or @role='dialog']//button[normalize-space()='{button_text}']",
        ))
    ).click()


# 행동특성 및 종합의견의 학생 정보 입력 단계까지 이동하는 헬퍼
def _go_to_behavior_student_info_step(driver):
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='행동특성 및 종합의견']")

    _reset_input_history_if_exists(driver)

    _click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    _click(driver, By.XPATH, "//li[normalize-space()='초등학교']")

    _click(driver, By.XPATH, "//button[@type='submit' and contains(., '다음으로')]")

    name_input_area = _find(
        driver,
        By.XPATH,
        "//input[@placeholder='학생 이름 검색']",
    )
    school_level_area = _find(
        driver,
        By.XPATH,
        "//p[normalize-space()='학교급']/following::h6[normalize-space()='초등학교'][1]",
    )

    assert name_input_area.is_displayed(), NAME_INPUT_AREA_NOT_DISPLAYED
    assert school_level_area.is_displayed(), SCHOOL_LEVEL_NOT_SAVED


# 학생 이름과 활동 키워드 및 직접 입력을 저장하는 헬퍼
def _save_behavior_keywords(driver, student_name, custom_keyword):
    _click(driver, By.XPATH, "//*[normalize-space()='이름을 입력해주세요.']")
    active_element = driver.switch_to.active_element
    active_element.send_keys(Keys.CONTROL, "a")
    active_element.send_keys(Keys.BACKSPACE)
    active_element.send_keys(student_name)

    _click(driver, By.XPATH, "//*[normalize-space()='키워드를 선택해주세요.']")
    _find(driver, By.XPATH, "//div[@role='presentation' or @role='dialog']")

    _click(driver, By.XPATH, "//*[normalize-space()='인성·태도(품성·책임감)']")
    _click(driver, By.XPATH, "//*[normalize-space()='예의 바르고 배려심 있음']")

    _type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='원하는 키워드를 직접 입력해주세요']",
        custom_keyword,
    )

    _click(driver, By.XPATH, "//button[normalize-space()='추가']")
    _click_modal_button(driver, "저장")

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located(
            (By.XPATH, "//div[@role='presentation' or @role='dialog']")
        )
    )


# 생성 결과 받기 버튼이 활성화될 때까지 기다리는 헬퍼
def _wait_for_result_download_button(driver, timeout=180):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[normalize-space()='생성 결과 받기']",
        ))
    )


# 새로 다운로드된 엑셀 파일을 기다리는 헬퍼
def _wait_for_new_excel_file(download_dir, before_files, timeout=60):
    end_time = time.time() + timeout

    while time.time() < end_time:
        current_files = {
            file for file in download_dir.glob("*.xlsx")
            if file.is_file() and not file.name.endswith(".crdownload")
        }

        new_files = current_files - before_files
        if new_files:
            latest_file = max(new_files, key=lambda file: file.stat().st_mtime)
            if latest_file.exists() and latest_file.stat().st_size > 0:
                return latest_file

        time.sleep(1)

    raise AssertionError("엑셀 파일이 제한 시간 내 다운로드되지 않았습니다.")


# =========================
# 행동특성 및 종합의견에서 AI 생성 결과 엑셀 파일을 다운로드할 수 있는지 검증
# =========================
def test_behavior_result_excel_download(logged_in_driver):
    driver = logged_in_driver
    download_dir = Path.home() / "Downloads"

    # ==========
    # Arrange
    # ==========
    _go_to_behavior_student_info_step(driver)

    # ==========
    # Act
    # ==========
    _save_behavior_keywords(driver, "홍길동", "차분하고 침착함")

    download_button = _wait_for_result_download_button(driver, timeout=180)

    before_files = {
        file for file in download_dir.glob("*.xlsx")
        if file.is_file()
    }

    download_button.click()

    downloaded_file = _wait_for_new_excel_file(
        download_dir,
        before_files,
        timeout=60,
    )

    # ==========
    # Assert
    # ==========
    assert downloaded_file.exists(), "생성 결과 엑셀 파일이 다운로드되지 않았습니다."
    assert downloaded_file.stat().st_size > 0, "다운로드된 엑셀 파일이 비어 있습니다."

    print(f"PASS: 생성 결과 엑셀 다운로드 완료 - {downloaded_file}")
