import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def test_navigate_to_tool_menu(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인 완료 상태
    driver = logged_in_driver

    #==========
    # Act
    #==========
    # 도구 페이지 진입 
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/ai-helpy-chat/tools']"))).click()

    #==========
    # Assert
    #==========
    tools_title = wait.until(EC.presence_of_element_located((By.TAG_NAME,"h2")))
    assert tools_title.text == "도구 목록"
