from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.tools.spec_detail.assert_messages import (
    NAME_INPUT_AREA_NOT_DISPLAYED,
    SCHOOL_LEVEL_NOT_SAVED,
)


def find(driver, by, value):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, value))
    )


def click(driver, by, value):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    ).click()


def type_text(driver, by, value, text):
    element = find(driver, by, value)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def test_behavior_create(logged_in_driver):
    driver = logged_in_driver

    # =========================
    # Arrange (준비)
    # =========================

    # 도구 → 행동특성 및 종합의견 진입
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='행동특성 및 종합의견']")

    # 입력 내역 초기화 버튼 있으면 초기화
    try:
        reset_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., '입력 내역 초기화')]"))
        )
        reset_btn.click()

        confirm_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., '초기화 하기')]"))
        )
        confirm_btn.click()

        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, "//button[contains(., '초기화 하기')]"))
        )

    except:
        pass

    # 학교급 선택
    click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='초등학교']")

    # =========================
    # Act (실행)
    # =========================

    # 다음으로 버튼 클릭
    click(driver, By.XPATH, "//button[@type='submit' and contains(., '다음으로')]")

    # 학생 정보 입력 화면 로딩 대기
    name_input_area = find(driver, By.XPATH, "//input[@placeholder='학생 이름 검색']")

    # 학교급 표시 영역 찾기
    school_level_area = find(
        driver,
        By.XPATH,
        "//p[normalize-space()='학교급']/following::h6[normalize-space()='초등학교'][1]"
    )

    # =========================
    # Assert (검증)
    # =========================

    try:
        # 1. 학생 정보 입력 화면 진입 여부 확인
        assert name_input_area.is_displayed(), NAME_INPUT_AREA_NOT_DISPLAYED

        # 2. 학교급 저장/노출 여부 확인
        assert school_level_area.is_displayed(), SCHOOL_LEVEL_NOT_SAVED

        print("PASS: 행동특성 및 종합의견 - 학교급 저장 확인 완료")

    except AssertionError as e:
        print(f"FAIL: 행동특성 및 종합의견 테스트 실패 - {e}")
        raise