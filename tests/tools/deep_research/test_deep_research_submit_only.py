from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.tools.deep_research.helpers import (
    _fill_deep_research_form,
    _go_to_deep_research_page,
)
from tests.tools.deep_research.input_values import (
    INSTRUCTIONS_INPUT,
    TOPIC_INPUT,
)


# =========================
# 심층 조사에서 제출 시 생성 요청이 정상 시작되는지 검증
# =========================
def test_deep_research_submit_only(logged_in_driver):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    _go_to_deep_research_page(driver)
    _fill_deep_research_form(driver, TOPIC_INPUT, INSTRUCTIONS_INPUT)

    # ==========
    # Act
    # ==========
    submit_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//button[normalize-space()='자동 생성' or normalize-space()='다시 생성']",
        ))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
        submit_button,
    )

    try:
        submit_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", submit_button)

    # 다시 생성 확인 모달이 뜨는 경우에만 처리
    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), '결과 다시 생성하기')]",
            ))
        )

        confirm_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@role='dialog']//button[normalize-space()='다시 생성']",
            ))
        )

        try:
            confirm_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", confirm_button)

    except TimeoutException:
        pass

    # ==========
    # Assert
    # ==========
    processing_state = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(), '작성하고 있어요') or contains(text(), 'Generating') or contains(text(), 'Phase:')]",
        ))
    )

    assert processing_state.is_displayed(), "심층 조사 제출 실패: 생성 요청 후 진행 상태 UI가 표시되지 않았습니다."
