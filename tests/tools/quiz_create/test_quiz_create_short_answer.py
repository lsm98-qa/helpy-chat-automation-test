from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def find(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def click(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    ).click()


def type_text(driver, by, value, text, timeout=10):
    element = find(driver, by, value, timeout)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def select_dropdown_option(driver, label_text, option_text):
    # 드롭다운 열기
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//label[text()='{label_text}']/following::div[@role='combobox'][1]"
        ))
    )
    dropdown.click()

    # 열린 listbox 안에서 옵션 클릭
    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//ul[@role='listbox']//li[normalize-space()='{option_text}']"
        ))
    )
    option.click()

    # 선택값이 실제로 반영될 때까지 대기
    WebDriverWait(driver, 10).until(
        lambda d: option_text in d.find_element(
            By.XPATH,
            f"//label[text()='{label_text}']/following::div[@role='combobox'][1]"
        ).text
    )


def is_element_present(driver, by, value, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return True
    except TimeoutException:
        return False


def test_quiz_create_short_answer(logged_in_driver):
    driver = logged_in_driver

    # =========================
    # Arrange (준비)
    # =========================
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='퀴즈 생성']")

    # 유형 선택
    select_dropdown_option(driver, "유형", "주관식")

    # 난이도 선택
    select_dropdown_option(driver, "난이도", "상")

    # 주제 입력
    quiz_topic = "다음 중 프로그래밍의 기본 개념에 대한 설명으로 가장 적절한 것을 고르시오"
    type_text(
        driver,
        By.XPATH,
        "//label[text()='주제']/following::textarea[1]",
        quiz_topic
    )

    # =========================
    # Act (실행)
    # =========================
    generate_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[@type='submit' and (normalize-space()='자동 생성' or normalize-space()='다시 생성')]"
        ))
    )

    button_text = generate_button.text.strip()
    generate_button.click()

    if button_text == "다시 생성":
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//h2[normalize-space()='결과 다시 생성하기']"
            ))
        )

        click(
            driver,
            By.XPATH,
            "//div[@role='dialog']//button[normalize-space()='다시 생성']"
        )

    # =========================
    # Assert (검증)
    # =========================

    # 최대 3분(180초) 동안 A 선택지가 뜰 때까지 대기
    option_a = find(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='A']",
        timeout=180
    )

    assert option_a.is_displayed(), "주관식 퀴즈 생성 실패: A 선택지가 표시되지 않았습니다."

    # B 선택지는 없어야 함
    option_b_exists = is_element_present(
        driver,
        By.XPATH,
        "//div[contains(@class,'MuiPaper-root') and normalize-space()='B']",
        timeout=5
    )

    assert not option_b_exists, "주관식 퀴즈 생성 실패: B 선택지가 표시되었습니다."

    print("주관식 퀴즈 생성 완료!")