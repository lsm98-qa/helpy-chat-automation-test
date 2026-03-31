import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

#==========
# 내 에이전트 페이지 진입 테스트
#==========
def test_navigate_to_my_agents(navigate_to_agent_explore, wait): 

    # Arrange
    driver = navigate_to_agent_explore
    
    # Act
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # Assert
    my_agents_title = wait.until(EC.visibility_of_element_located(MENU_H6_TITLE))

    assert my_agents_title.text == "내 에이전트"

#==========
# 뒤로가기 버튼 테스트
#==========
def test_navigate_back_to_agent_explore(navigate_to_agent_explore, wait):

    # Arrange
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # Act
    wait.until(EC.element_to_be_clickable(AGENT_BACK_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    
    # Assert
    agent_title = wait.until(EC.visibility_of_element_located(MENU_H2_TITLE))

    assert agent_title.text == "에이전트 탐색"

#==========
# 내 에이전트 페이지의 각 에이전트 카드의 수정 버튼이 표시되는지 테스트
#==========
def test_each_agent_card_shows_edit_button(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
        )
    )

    # Act
    agent_items = driver.find_elements(
        By.XPATH,
        "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]",
    )

    # Assert
    if not agent_items:
        pytest.skip("내 에이전트 목록이 비어 있어 수정 버튼 노출 테스트를 수행할 수 없습니다.")

    for idx, item in enumerate(agent_items, start=1):
        edit_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='pen'])",
        )
        assert len(edit_buttons) > 0, f"{idx}번째 에이전트 카드에 수정 버튼이 노출되지 않았습니다."