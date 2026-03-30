from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_top_chat_item_option_button

def rename_chat(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    logged_in_driver
    
    #==========
    # Act
    #==========
    # 채팅 목록에서 옵션 열기
    click_top_chat_item_option_button(wait)

    wait.until(
    lambda d: d.find_element(By.XPATH, "//li[normalize-space()='이름 변경']")
    ).click()