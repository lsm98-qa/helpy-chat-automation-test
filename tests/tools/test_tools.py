import pytest
from selenium.webdriver.support import expected_conditions as EC

from locators.menu_locators import MENU_H2_TITLE
from pages.menu_section import MenuSection


def test_navigate_to_tool_menu(logged_in_driver, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = logged_in_driver
    menu_section = MenuSection(driver, wait)
    expected_title = "도구 목록"
    testlog.arrange("logged_in_driver_ready")

    # ==========
    # Act
    # ==========
    testlog.act("click_tools_menu")
    menu_section.click_tools()

    # ==========
    # Assert
    # ==========
    tools_title = wait.until(EC.presence_of_element_located(MENU_H2_TITLE))
    actual_title = tools_title.text

    testlog.assert_(
        "tools_menu_title_visible",
        expected=expected_title,
        actual=actual_title,
    )
    assert actual_title == expected_title, (
        f"도구 메뉴 진입 후 제목이 기대값과 다릅니다. "
        f"expected={expected_title}, actual={actual_title}"
    )