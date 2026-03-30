from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.agent_locators import AGENT_CREATE_BUTTON
from locators.menu_locators import MENU_AGENT_EXPLORE


# 에이전트 탐색 페이지로 정상 진입되는지 확인
def test_navigate_to_agent_explore(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    # Act
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # Assert
    assert "/ai-helpy-chat/agents" in driver.current_url


# 만들기 버튼 클릭 시 에이전트 생성 페이지로 이동하는지 확인
def test_navigate_to_agent_create(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    # Act
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.url_contains("/builder"))
    back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label]")))

    # Assert
    assert back_button.is_displayed()
    assert "/builder" in driver.current_url


# 에이전트 생성 페이지에서 뒤로가기 시 탐색 페이지로 복귀하는지 확인
def test_navigate_back_to_agent_explore_from_agent_create(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label]")))

    # Act
    back_button.click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    wait.until(EC.presence_of_element_located(MENU_AGENT_EXPLORE))

    # Assert
    assert "/builder" not in driver.current_url
