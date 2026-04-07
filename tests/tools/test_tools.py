import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from locators.menu_locators import MENU_H2_TITLE, MENU_TOOLS


def test_navigate_to_tool_menu(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인 완료 상태
    driver = logged_in_driver
    testlog.arrange("logged_in_driver_ready")

    #==========
    # Act
    #==========
    # 도구 페이지 진입 
    testlog.act("click_tools_menu")
    wait.until(EC.element_to_be_clickable(MENU_TOOLS)).click()

    #==========
    # Assert
    #==========
    tools_title = wait.until(EC.presence_of_element_located(MENU_H2_TITLE))
    testlog.assert_("tools_menu_title_visible", expected="도구 목록", actual=tools_title.text)
    assert tools_title.text == "도구 목록"
