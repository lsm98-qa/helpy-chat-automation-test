import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *



def test_navigate_to_agent_explore(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    # Act
    agent_title = wait.until(EC.presence_of_element_located(MENU_H2_TITLE))

    # Assert
    assert agent_title.text == "에이전트 탐색"
