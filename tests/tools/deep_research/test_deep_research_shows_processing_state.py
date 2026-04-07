from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.tools.deep_research.assert_messages import (
    PROCESSING_STATE_NOT_DISPLAYED,
)
from tests.tools.deep_research.helpers import (
    _fill_deep_research_form,
    _find,
    _go_to_deep_research_page,
)


# =========================
# 심층 조사에서 제출 후 진행 상태 UI가 표시되는지 검증
# =========================
def test_deep_research_shows_processing_state(logged_in_driver, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    testlog.arrange("open_deep_research_tool_and_fill_form")
    _go_to_deep_research_page(driver)
    _fill_deep_research_form(
        driver,
        "AI가 일자리에 미치는 영향",
        "AI가 일자리에 미치는 영향에 대해서 요약해줘",
    )

    # ==========
    # Act
    # ==========
    testlog.act("submit_deep_research_request")
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
        _find(driver, By.XPATH, "//*[contains(text(), '결과 다시 생성하기')]", timeout=3)

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
    processing_state = _find(
        driver,
        By.XPATH,
        "//*[contains(text(), '작성하고 있어요') or contains(text(), 'Generating') or contains(text(), 'Phase:')]",
        timeout=30,
    )

    testlog.assert_(
        "deep_research_processing_state_visible",
        expected=True,
        actual=processing_state.is_displayed(),
    )
    assert processing_state.is_displayed(), PROCESSING_STATE_NOT_DISPLAYED
