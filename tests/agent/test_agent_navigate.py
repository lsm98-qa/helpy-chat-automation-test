from selenium.webdriver.support import expected_conditions as EC

from locators.agent_locators import AGENT_CREATE_BUTTON, AGENT_CREATE_PAGE_BACK_BUTTON
from locators.menu_locators import MENU_AGENT_EXPLORE


# =========================
# 에이전트 탐색 페이지 진입 확인
# =========================
def test_navigate_to_agent_explore(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore

    # ==========
    # Act
    # ==========
    # 에이전트 탐색 메뉴 요소가 렌더링될 때까지 대기
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # ==========
    # Assert
    # ==========
    assert "/ai-helpy-chat/agents" in driver.current_url


# =========================
# 만들기 버튼 클릭 시 생성 페이지 이동 확인
# =========================
def test_navigate_to_agent_create(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore

    # ==========
    # Act
    # ==========
    # 만들기 버튼 클릭 후 생성 페이지 URL과 뒤로가기 버튼 노출 확인
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.url_contains("/builder"))
    back_button = wait.until(EC.element_to_be_clickable(AGENT_CREATE_PAGE_BACK_BUTTON))

    # ==========
    # Assert
    # ==========
    assert back_button.is_displayed()
    assert "/builder" in driver.current_url


# =========================
# 생성 페이지 뒤로가기 시 탐색 페이지 복귀 확인
# =========================
def test_navigate_back_to_agent_explore_from_agent_create(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    # 생성 페이지로 먼저 진입해 뒤로가기 가능한 상태를 준비
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    back_button = wait.until(EC.element_to_be_clickable(AGENT_CREATE_PAGE_BACK_BUTTON))

    # ==========
    # Act
    # ==========
    # 생성 페이지 뒤로가기 버튼 클릭
    back_button.click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # ==========
    # Assert
    # ==========
    assert "/builder" not in driver.current_url
