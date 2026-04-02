from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


AGENT_SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='AI 에이전트 검색']")
AGENT_LIST_CONTAINER = (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
AGENT_LIST_ITEMS = (By.XPATH, "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]")

AGENT_NO_RESULTS_TITLE = (By.XPATH, "//h6[normalize-space()='검색 결과가 없습니다.']")
AGENT_NO_RESULTS_DESCRIPTION = (
    By.XPATH,
    "//p[normalize-space()='원하는 에이전트가 없다면, 직접 만들어 보세요!']",
)
AGENT_NO_RESULTS_CREATE_BUTTON = (
    By.XPATH,
    "//a[normalize-space()='에이전트 만들기' and contains(@href, '/ai-helpy-chat/agents/builder')]",
)


# 검색창에 키워드를 입력해 결과를 필터링하는 공통 헬퍼
def _search_agent_by_keyword(wait, keyword):
    search_input = wait.until(EC.visibility_of_element_located(AGENT_SEARCH_INPUT))
    wait.until(EC.presence_of_element_located(AGENT_LIST_CONTAINER))

    search_input.clear()
    search_input.send_keys(keyword)
    wait.until(lambda d: (search_input.get_attribute("value") or "") == keyword)


# =========================
# 존재하지 않는 검색어 입력 시 빈 상태 UI가 표시되는지 테스트
# =========================
def test_agent_search_shows_empty_state_when_no_results(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    _ = navigate_to_agent_explore
    search_keyword = "사과"

    # ==========
    # Act
    # ==========
    _search_agent_by_keyword(wait, search_keyword)

    # ==========
    # Assert
    # ==========
    # 검색 결과 카드 대신 빈 상태 UI가 노출되는지 검증
    wait.until(lambda d: len(d.find_elements(*AGENT_LIST_ITEMS)) == 0)

    no_results_title = wait.until(EC.visibility_of_element_located(AGENT_NO_RESULTS_TITLE))
    no_results_description = wait.until(
        EC.visibility_of_element_located(AGENT_NO_RESULTS_DESCRIPTION)
    )
    create_button = wait.until(
        EC.element_to_be_clickable(AGENT_NO_RESULTS_CREATE_BUTTON)
    )

    assert no_results_title.text == "검색 결과가 없습니다."
    assert no_results_description.text == "원하는 에이전트가 없다면, 직접 만들어 보세요!"
    assert create_button.is_displayed(), "'에이전트 만들기' 버튼이 표시되지 않습니다."


# =========================
# 검색 결과 없음 빈 상태에서 '에이전트 만들기' 클릭 시 생성 화면으로 이동하는지 테스트
# =========================
def test_agent_search_empty_state_create_button_navigates_to_builder(
    navigate_to_agent_explore,
    wait,
):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = "사과"
    _search_agent_by_keyword(wait, search_keyword)
    create_button = wait.until(EC.element_to_be_clickable(AGENT_NO_RESULTS_CREATE_BUTTON))

    # ==========
    # Act
    # ==========
    create_button.click()

    # ==========
    # Assert
    # ==========
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.url_contains("/builder"))
    assert "/builder" in driver.current_url
