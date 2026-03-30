from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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

def test_deep_research_generation(logged_in_driver):
    driver = logged_in_driver

    # =========================
    # Arrange (준비)
    # =========================
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='심층 조사']")

    type_text(driver, By.NAME, "topic", "AI가 일자리에 미치는 영향")
    type_text(driver, By.NAME, "instructions", "AI가 일자리에 미치는 영향에 대해서 요약해줘")

    # =========================
    # Act (실행)
    # =========================
    click(driver, By.CSS_SELECTOR, "button[type='submit'][form='tool-factory-do_deep_research']")

    # 결과 다시 생성 팝업 처리
    try:
        find(driver, By.XPATH, "//*[contains(text(), '결과 다시 생성하기')]")
        click(driver, By.CSS_SELECTOR, "div[role='dialog'] button[type='submit'][form='tool-factory-do_deep_research']")
    except TimeoutException:
        pass

    # =========================
    # Assert (심층 조사 결과 생성 여부 확인)
    # 제목(h1) 요소가 생기면 결과 생성 완료로 판단
    # =========================
    result_title = WebDriverWait(driver, 600, poll_frequency=5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.css-1ypk2ex"))
    )
    assert result_title.text.strip() != "", "심층 조사 결과가 생성되지 않았습니다."

    print("✅ 심층 조사 결과 생성 확인 완료")