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


def test_spec_create(logged_in_driver, wait):
    driver = logged_in_driver

    # 도구 → 세부 특기사항
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='세부 특기사항']")

    # 학교급 → 초등학교
    click(driver, By.XPATH, "//label[text()='학교급']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='중학교']")

    # 학년 → 6학년
    click(driver, By.XPATH, "//label[text()='학년']/following::div[1]")
    click(driver, By.XPATH, "//li[normalize-space()='3학년']")

    # 과목 → 국어
    click(driver, By.XPATH, "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']")
    type_text(driver, By.XPATH, "//input[@placeholder='과목을 선택해주세요. (직접 입력 가능)']", "국어")
    click(driver, By.XPATH, "//li[normalize-space()='국어']")

    # 단원 입력
    type_text(driver, By.XPATH, "//input[@placeholder='수업 단원을 입력해주세요.']", "1단원 : 문학작품감상")

    # 다음으로 버튼 클릭
    click(driver, By.XPATH, "//button[contains(text(),'다음으로')]")

    #  결과 화면 로딩 대기 (없으면 빈 화면 찍힘)
    time.sleep(2)

    # 스크린샷 저장
    driver.save_screenshot("result.png")

    print("스크린샷 저장 완료  (result.png)")
    input("엔터 누르면 종료")

     # 최초 진행 시 위 코드 그대로 진행 하지만 반복적으로 진행할 때는 진행 도중 [입력 내역 초기화] 버튼 클릭