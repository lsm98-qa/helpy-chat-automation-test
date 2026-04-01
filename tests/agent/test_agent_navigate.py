import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *


# =========================
# 에이전트 탐색 페이지 진입 테스트
# =========================
def test_navigate_to_agent_explore(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore

    # ==========
    # Act
    # ==========
    # 에이전트 탐색 페이지 제목 요소가 표시될 때까지 대기
    agent_title = wait.until(EC.presence_of_element_located(MENU_H2_TITLE))

    # ==========
    # Assert
    # ==========
    assert agent_title.text == "에이전트 탐색"
