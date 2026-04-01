import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

# =========================
# 내 에이전트 페이지 진입 테스트
# =========================
def test_navigate_to_my_agents(navigate_to_agent_explore, wait): 
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    
    # ==========
    # Act
    # ==========
    # 내 에이전트 버튼 클릭 후 내 에이전트 페이지 URL로 이동
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # ==========
    # Assert
    # ==========
    my_agents_title = wait.until(EC.visibility_of_element_located(MENU_H6_TITLE))

    assert my_agents_title.text == "내 에이전트"

# =========================
# 에이전트 탐색 -> 내 에이전트 페이지에서 뒤로가기 버튼 테스트
# =========================
def test_navigate_back_to_agent_explore(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # ==========
    # Act
    # ==========
    # 뒤로가기 버튼으로 에이전트 탐색 페이지 복귀 동작 수행
    wait.until(EC.element_to_be_clickable(AGENT_BACK_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    
    # ==========
    # Assert
    # ==========
    agent_title = wait.until(EC.visibility_of_element_located(MENU_H2_TITLE))

    assert agent_title.text == "에이전트 탐색"
