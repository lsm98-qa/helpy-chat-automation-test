from locators.menu_locators import *

class MenuSection:
    def __init__(self, driver):
        self.driver = driver
    
    def click_new_chat(self):
        self.driver.find_element(*MENU_NEW_CHAT).click()
    
    def click_search_chat(self):
        self.driver.find_element(*MENU_SEARCH_CHAT).click()
    
    def click_tools(self):
        self.driver.find_element(*MENU_TOOLS).click()
    
    def click_agent_explore(self):
        self.driver.find_element(*MENU_AGENT_EXPLORE).click()