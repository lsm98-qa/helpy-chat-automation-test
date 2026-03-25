import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

def test_navigate_to_my_agents(navigate_to_agent_explore, wait): 

    # Arrange
    driver = navigate_to_agent_explore
    
    # Act
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # Assert
    my_agents_title = wait.until(EC.visibility_of_element_located(MENU_H6_TITLE))

    assert my_agents_title.text == "내 에이전트"