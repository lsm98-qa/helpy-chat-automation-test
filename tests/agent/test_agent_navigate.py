from selenium.webdriver.support import expected_conditions as EC

from locators.agent_locators import AGENT_CREATE_BUTTON, AGENT_CREATE_PAGE_BACK_BUTTON
from locators.menu_locators import MENU_AGENT_EXPLORE


# =========================
# 에이전트 탐색 페이지 진입 확인
# =========================
def test_navigate_to_agent_explore(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    testlog.arrange("navigate_to_agent_explore_page")

    # ==========
    # Act
    # ==========
    # 에이전트 탐색 메뉴 요소가 렌더링될 때까지 대기
    testlog.act("wait_for_agent_explore_menu")
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # ==========
    # Assert
    # ==========
    is_on_explore = "/ai-helpy-chat/agents" in driver.current_url
    testlog.assert_("agent_explore_url_visible", expected=True, actual=is_on_explore)
    assert is_on_explore


# =========================
# 만들기 버튼 클릭 시 생성 페이지 이동 확인
# =========================
def test_navigate_to_agent_create(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    testlog.arrange("on_agent_explore_ready_for_create")

    # ==========
    # Act
    # ==========
    # 만들기 버튼 클릭 후 생성 페이지 URL과 뒤로가기 버튼 노출 확인
    testlog.act("click_create_button_and_wait_builder")
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.url_contains("/builder"))
    back_button = wait.until(EC.element_to_be_clickable(AGENT_CREATE_PAGE_BACK_BUTTON))

    # ==========
    # Assert
    # ==========
    is_builder_page = back_button.is_displayed() and "/builder" in driver.current_url
    testlog.assert_("navigate_to_builder_success", expected=True, actual=is_builder_page)
    assert back_button.is_displayed()
    assert "/builder" in driver.current_url


# =========================
# 생성 페이지 뒤로가기 시 탐색 페이지 복귀 확인
# =========================
def test_navigate_back_to_agent_explore_from_agent_create(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    # 생성 페이지로 먼저 진입해 뒤로가기 가능한 상태를 준비
    driver = navigate_to_agent_explore
    testlog.arrange("prepare_builder_page_for_back_navigation")
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    back_button = wait.until(EC.element_to_be_clickable(AGENT_CREATE_PAGE_BACK_BUTTON))

    # ==========
    # Act
    # ==========
    # 생성 페이지 뒤로가기 버튼 클릭
    testlog.act("click_back_button_from_builder")
    back_button.click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # ==========
    # Assert
    # ==========
    is_back_to_explore = "/builder" not in driver.current_url
    testlog.assert_("back_navigation_to_explore", expected=True, actual=is_back_to_explore)
    assert is_back_to_explore
