import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By




def test_register_page_loaded_successfully(navigate_to_agent_explore, wait):
    
    driver = navigate_to_agent_explore
    tools_title = wait.until(EC.presence_of_element_located((By.TAG_NAME,"h2")))

    assert tools_title.text == "에이전트 탐색"

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
