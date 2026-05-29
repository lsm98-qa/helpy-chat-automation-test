from selenium.webdriver.support import expected_conditions as EC

from locators.menu_locators import (
    MENU_AGENT_EXPLORE,
    MENU_NEW_CHAT,
    MENU_SEARCH_CHAT,
    MENU_TOOLS,
)


class MenuSection:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def _click_menu(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def click_new_chat(self):
        self._click_menu(MENU_NEW_CHAT)

    def click_search_chat(self):
        self._click_menu(MENU_SEARCH_CHAT)

    def click_tools(self):
        self._click_menu(MENU_TOOLS)

    def click_agent_explore(self):
        self._click_menu(MENU_AGENT_EXPLORE)