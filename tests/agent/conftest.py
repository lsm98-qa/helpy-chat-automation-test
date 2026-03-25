import pytest
from selenium.webdriver.support import expected_conditions as EC
from locators.menu_locators import *
from pages.menu_section import MenuSection


#===================
# 에이전트 탐색 페이지 진입
#===================
@pytest.fixture
def navigate_to_agent_explore(logged_in_driver, wait, base_url):
    menu_section = MenuSection(logged_in_driver)

    wait.until(EC.url_to_be(base_url))
    current_url = logged_in_driver.current_url
    assert current_url == base_url, (
        f"Expected current URL to be '{base_url}', but got '{current_url}'."
    )

    menu_section.click_agent_explore()

    yield logged_in_driver
