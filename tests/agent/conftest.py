import pytest
from selenium.webdriver.support import expected_conditions as EC
from locators.menu_locators import *
from pages.menu_section import MenuSection


# 에이전트 탐색 페이지 진입
@pytest.fixture
def navigate_to_agent_explore(logged_in_driver, wait, base_url):
    menu_section = MenuSection(logged_in_driver)

    wait.until(EC.url_to_be(base_url))
    current_url = logged_in_driver.current_url
    assert current_url == base_url, (
        f"현재 URL은 '{base_url}'이어야 하지만, 실제 URL은 '{current_url}'입니다."
    )

    menu_section.click_agent_explore()

    yield logged_in_driver
