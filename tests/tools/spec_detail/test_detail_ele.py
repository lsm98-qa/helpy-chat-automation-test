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
    click(driver, By.ID, "//label[text()='학교급']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='초등학교']")

    # 학년 선택
    click(driver, By.XPATH, "//label[text()='학년']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='6학년']")

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

    # 다음으로 버튼 클릭
    click(driver, By.XPATH, "//button[contains(text(),'다음으로')]")

    # 결과 화면(학생 이름 입력 단계) 로딩 대기
    name_input_area = find(driver, By.XPATH, "//p[text()='이름을 입력해주세요.']")

    # 스크린샷 저장
    driver.save_screenshot("result.png")
    print("스크린샷 저장 완료 (result.png)")

    # =========================
    # Assert (검증)
    # =========================

    # 이름 입력 영역이 실제로 화면에 보이는지 확인
    assert name_input_area.is_displayed(), "학생 이름 입력 화면이 나타나지 않았습니다."

    # URL 또는 특정 화면 요소로 다음 단계 진입 여부 확인하고 싶으면 추가 가능