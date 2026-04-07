from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.tools.deep_research.assert_messages import (
    RESEARCH_RESULT_HAS_ERROR,
    RESEARCH_RESULT_NOT_CREATED,
    RESEARCH_RESULT_TOO_SHORT,
)
from tests.tools.deep_research.helpers import (
    _fill_deep_research_form,
    _find_result_content,
    _go_to_deep_research_page,
)
from tests.tools.deep_research.input_values import (
    INSTRUCTIONS_INPUT,
    TOPIC_INPUT,
)


# 결과 영역의 현재 텍스트를 가져오는 헬퍼
def _get_current_result_text(driver):
    try:
        result_area = driver.find_element(
            By.XPATH,
            "//main//*[contains(text(), '생성 결과')]/ancestor::*[self::section or self::div][1]",
        )
        return result_area.text.strip()
    except Exception:
        return ""


# =========================
# 심층 조사에서 최종 결과가 새로 생성되는지 검증
# =========================
def test_deep_research_create(logged_in_driver, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    testlog.arrange("open_deep_research_tool_and_fill_form")
    _go_to_deep_research_page(driver)
    _fill_deep_research_form(driver, TOPIC_INPUT, INSTRUCTIONS_INPUT)

    # 생성 전 기존 결과 텍스트 저장
    previous_result_text = _get_current_result_text(driver)
    testlog.arrange("capture_previous_result_text", previous_result_len=len(previous_result_text.strip()))

    # ==========
    # Act
    # ==========
    testlog.act("submit_deep_research_generation")
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

    # 진행 상태를 한 번 거쳤는지 확인
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(), '작성하고 있어요') or contains(text(), 'Generating') or contains(text(), 'Phase:')]",
        ))
    )

    # ==========
    # Assert
    # ==========
    result_text = _find_result_content(driver, timeout=600)
    is_valid_result = (
        bool(result_text.strip())
        and len(result_text.strip()) >= 50
        and ("오류" not in result_text and "에러" not in result_text)
        and (result_text.strip() != previous_result_text)
    )
    testlog.assert_(
        "deep_research_result_generated",
        expected=True,
        actual=is_valid_result,
        result_len=len(result_text.strip()),
    )

    assert result_text.strip(), RESEARCH_RESULT_NOT_CREATED
    assert len(result_text.strip()) >= 50, RESEARCH_RESULT_TOO_SHORT
    assert "오류" not in result_text and "에러" not in result_text, RESEARCH_RESULT_HAS_ERROR
    assert result_text.strip() != previous_result_text, "심층 조사 결과 생성 실패: 이전 결과와 동일한 결과가 표시되었습니다."

    print("심층 조사 결과 생성 확인 완료")
