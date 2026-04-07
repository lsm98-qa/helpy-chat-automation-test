from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


AGENT_SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='AI 에이전트 검색']")
AGENT_LIST_CONTAINER = (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
AGENT_LIST_ITEMS = (
    By.XPATH,
    "//div[@data-testid='virtuoso-item-list']/div[@data-item-index or @data-index]",
)

AGENT_NO_RESULTS_TITLE = (By.XPATH, "//h6[normalize-space()='검색 결과가 없습니다.']")
AGENT_NO_RESULTS_DESCRIPTION = (
    By.XPATH,
    "//p[normalize-space()='원하는 에이전트가 없다면, 직접 만들어 보세요!']",
)
AGENT_NO_RESULTS_CREATE_BUTTON = (
    By.XPATH,
    "//a[normalize-space()='에이전트 만들기' and contains(@href, '/ai-helpy-chat/agents/builder')]",
)
AGENT_CARD_TITLE_IN_ITEM = (
    By.XPATH,
    ".//a[contains(@href, '/ai-helpy-chat/agents/')]//p[contains(@class, 'MuiTypography-noWrap')]",
)
NO_RESULT_SEARCH_KEYWORD = "사과"
RESULT_SEARCH_KEYWORD = "회의"


# 검색창에 키워드를 입력해 결과를 필터링하는 공통 헬퍼
def _search_agent_by_keyword(wait, keyword):
    search_input = wait.until(EC.visibility_of_element_located(AGENT_SEARCH_INPUT))
    wait.until(EC.presence_of_element_located(AGENT_LIST_CONTAINER))

    search_input.clear()
    search_input.send_keys(keyword)
    wait.until(lambda d: (search_input.get_attribute("value") or "") == keyword)


# 검색 입력창 포커스를 해제해 검색 결과 반영을 유도하는 공통 헬퍼
def _blur_agent_search_input(driver, wait):
    search_input = wait.until(EC.visibility_of_element_located(AGENT_SEARCH_INPUT))
    driver.execute_script("arguments[0].blur();", search_input)


# 검색 입력 + blur를 한 번에 수행하는 공통 헬퍼
def _search_and_blur(driver, wait, keyword):
    _search_agent_by_keyword(wait, keyword)
    _blur_agent_search_input(driver, wait)


# 검색 결과 카드들의 제목 목록을 추출하는 공통 헬퍼
def _extract_agent_card_titles(driver):
    result_items = driver.find_elements(*AGENT_LIST_ITEMS)
    titles = []
    for item in result_items:
        title_elements = item.find_elements(*AGENT_CARD_TITLE_IN_ITEM)
        if not title_elements:
            continue
        titles.append((title_elements[0].text or "").strip())
    return titles


# 검색 결과 아이템 목록을 조회하는 공통 헬퍼
def _get_result_items(wait):
    return wait.until(lambda d: d.find_elements(*AGENT_LIST_ITEMS) or False)


# 검색 반영 후 제목에 키워드가 포함된 결과가 나타날 때까지 대기하는 공통 헬퍼
def _wait_until_titles_contain_keyword(driver, wait, keyword):
    wait.until(
        lambda d: any(keyword in title for title in _extract_agent_card_titles(d))
    )


# =========================
# 존재하지 않는 검색어 입력 시 빈 상태 UI가 표시되는지 테스트
# =========================
def test_agent_search_shows_empty_state_when_no_results(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = NO_RESULT_SEARCH_KEYWORD
    testlog.arrange("prepare_agent_search_empty_state_case", keyword=search_keyword)

    # ==========
    # Act
    # ==========
    testlog.act("search_agent_with_no_result_keyword")
    _search_agent_by_keyword(wait, search_keyword)
    _blur_agent_search_input(driver, wait)

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

    testlog.assert_(
        "empty_state_ui_visible_for_no_result",
        expected=True,
        actual=(
            no_results_title.text == "검색 결과가 없습니다."
            and no_results_description.text == "원하는 에이전트가 없다면, 직접 만들어 보세요!"
            and create_button.is_displayed()
        ),
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
    testlog,
):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = NO_RESULT_SEARCH_KEYWORD
    testlog.arrange("prepare_empty_state_create_button_navigation", keyword=search_keyword)
    _search_agent_by_keyword(wait, search_keyword)
    _blur_agent_search_input(driver, wait)
    create_button = wait.until(EC.element_to_be_clickable(AGENT_NO_RESULTS_CREATE_BUTTON))

    # ==========
    # Act
    # ==========
    testlog.act("click_empty_state_create_button")
    create_button.click()

    # ==========
    # Assert
    # ==========
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.url_contains("/builder"))
    is_builder = "/builder" in driver.current_url
    testlog.assert_("empty_state_create_button_navigates_builder", expected=True, actual=is_builder)
    assert is_builder


# =========================
# 검색어 입력 시 하단 결과 목록이 1개 이상 표시되는지 테스트
# =========================
def test_agent_search_shows_result_list(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = RESULT_SEARCH_KEYWORD
    testlog.arrange("prepare_agent_search_result_list_case", keyword=search_keyword)

    # ==========
    # Act
    # ==========
    testlog.act("search_agent_with_result_keyword")
    _search_and_blur(driver, wait, search_keyword)

    # ==========
    # Assert
    # ==========
    result_items = _get_result_items(wait)
    testlog.assert_("agent_search_result_list_visible", expected=True, actual=(len(result_items) > 0), result_count=len(result_items))
    assert len(result_items) > 0, "검색 결과가 1개 이상 표시되지 않았습니다."


# =========================
# 검색 결과가 있는 경우 빈 상태 UI가 표시되지 않는지 테스트
# =========================
def test_agent_search_hides_empty_state_when_results_exist(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = RESULT_SEARCH_KEYWORD
    testlog.arrange("prepare_hide_empty_state_case", keyword=search_keyword)

    # ==========
    # Act
    # ==========
    testlog.act("search_agent_and_load_results")
    _search_and_blur(driver, wait, search_keyword)
    _ = _get_result_items(wait)

    # ==========
    # Assert
    # ==========
    no_results_elements = driver.find_elements(*AGENT_NO_RESULTS_TITLE)
    testlog.assert_("empty_state_hidden_when_results_exist", expected=0, actual=len(no_results_elements))
    assert len(no_results_elements) == 0, "결과 목록 대신 빈 상태 UI가 표시되었습니다."


# =========================
# 검색 결과 제목이 검색어와 관련 있는지 테스트
# =========================
def test_agent_search_returns_titles_related_to_keyword(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    search_keyword = RESULT_SEARCH_KEYWORD
    testlog.arrange("prepare_search_title_keyword_match_case", keyword=search_keyword)

    # ==========
    # Act
    # ==========
    testlog.act("search_agent_and_wait_titles")
    _search_and_blur(driver, wait, search_keyword)
    _ = _get_result_items(wait)
    _wait_until_titles_contain_keyword(driver, wait, search_keyword)

    # ==========
    # Assert
    # ==========
    titles = _extract_agent_card_titles(driver)
    has_related_title = any(search_keyword in title for title in titles)
    testlog.assert_(
        "search_titles_related_to_keyword",
        expected=True,
        actual=(len(titles) > 0 and has_related_title),
        title_count=len(titles),
    )
    assert len(titles) > 0, "검색 결과 제목을 찾지 못했습니다."
    assert any(search_keyword in title for title in titles), (
        "검색어를 포함한 결과 제목이 없습니다. "
        f"keyword={search_keyword}, titles={titles}"
    )
