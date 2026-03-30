from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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


def test_ppt_create(logged_in_driver, wait):
    driver = logged_in_driver

    # =========================
    # Arrange
    # =========================

    # 도구 → PPT 생성
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='PPT 생성']")

    # 입력
    type_text(driver, By.NAME, "topic", "AI가 일자리에 미치는 영향")
    type_text(driver, By.NAME, "instructions", "2025년 기준으로 만들어줘")
    type_text(driver, By.NAME, "slides_count", "10")
    type_text(driver, By.NAME, "section_count", "3")

    # =========================
    # Act
    # =========================

    # 생성 버튼 클릭
    click(driver, By.XPATH, "//button[contains(text(),'다시 생성')]")

    modal = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='presentation']"))
    )

    # 모달 안 다시 생성 버튼 클릭
    modal.find_element(By.XPATH, ".//button[contains(text(),'다시 생성')]").click()

    print("PPT 생성 시작")

    # =========================
    # Assert
    # =========================

    success = False

    # 최대 600초 동안 확인
    for i in range(60):   # 60 * 10초 = 600초
        time.sleep(10)

        try:
            # 생성 결과 다운받기 링크 찾기
            download_link = driver.find_element(
                By.XPATH, "//a[contains(., '생성 결과 다운받기')]"
            )

            href = download_link.get_attribute("href")
            print(f"{(i+1)*5}초 경과 - 현재 href: {href}")

            # href 안에 실제 pptx 링크가 생겼는지 확인
            if href and ".pptx" in href:
                print("PPT 생성 완료")
                print("다운로드 링크:", href)
                success = True
                break

        except:
            print(f"{(i+1)*5}초 경과 - 아직 생성 중...")

    assert success, "PPT 생성이 완료되지 않았습니다."


