from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def test_spec_create(logged_in_driver):
    driver = logged_in_driver

    # =========================
    # Arrange (준비)
    # =========================

    # 도구 → 세부 특기사항 진입
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='세부 특기사항']")

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
    click(driver, By.XPATH, "//li[normalize-space()='중학교']")

    # 학년 선택
    click(driver, By.XPATH, "//label[text()='학년']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='3학년']")

    # 과목 입력 및 선택
    type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']",
        "국어"
    )
    click(driver, By.XPATH, "//li[normalize-space()='국어']")

    # 단원 입력
    type_text(
        driver,
        By.XPATH,
        "//input[@placeholder='수업 단원을 입력해주세요.']",
        "1단원 : 문학작품감상"
    )

    # =========================
    # Act (실행)
    # =========================

    # 다음으로 버튼 클릭 (type='submit' 포함하여 더 정확하게 선택)
    click(driver, By.XPATH, "//button[@type='submit' and contains(., '다음으로')]")

    # 결과 화면(학생 이름 입력 단계) 로딩 대기
    name_input_area = find(driver, By.XPATH, "//p[text()='이름을 입력해주세요.']")

    # 스크린샷 저장 (디버깅용)
    driver.save_screenshot("result.png")
    print("스크린샷 저장 완료 (result.png)")

    # =========================
    # Assert (검증)
    # =========================

    # 1. 학생 이름 입력 화면 진입 여부 확인
    assert name_input_area.is_displayed(), "학생 이름 입력 화면이 나타나지 않았습니다."

    # 2. 이전 단계 입력값 저장/노출 여부 확인
    assert find(driver, By.XPATH, "//h6[normalize-space()='초등학교']").is_displayed(), "학교급이 저장되지 않았습니다."
    assert find(driver, By.XPATH, "//h6[normalize-space()='6학년']").is_displayed(), "학년이 저장되지 않았습니다."
    assert find(driver, By.XPATH, "//h6[normalize-space()='국어']").is_displayed(), "과목이 저장되지 않았습니다."
    assert find(driver, By.XPATH, "//h6[normalize-space()='1단원 : 문학작품감상']").is_displayed(), "단원이 저장되지 않았습니다."
