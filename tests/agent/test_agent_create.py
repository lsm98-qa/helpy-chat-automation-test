import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

#==========
# 에이전트 생성 페이지 진입 테스트
#==========
def test_navigate_to_agent_create(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    # Act
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    create_title = wait.until(EC.presence_of_element_located((By.XPATH, "//p[text()='새 에이전트 만들기']")))

    # Assert
    assert create_title.text == "새 에이전트 만들기"

#==========
# 뒤로가기 버튼 테스트
#==========
def test_navigate_back_to_agent_explore(navigate_to_agent_explore, wait):

    # Arrange
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    
    # Act
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='뒤로가기']"))).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    
    # Assert
    agent_title = wait.until(EC.visibility_of_element_located(MENU_H2_TITLE))

    assert agent_title.text == "에이전트 탐색"


# def test_register_form_is_visible():
#     pass
# def test_register_required_toggles_are_present():
#     pass
# def test_register_toggles_are_interactable():
#     pass
# def test_register_image_upload_button_is_enabled():
#     pass
# def test_register_singleline_input_is_editable():
#     pass
# def test_register_multiline_input_is_editable():
#     pass
# def test_register_required_fields_are_rendered():
#     pass
