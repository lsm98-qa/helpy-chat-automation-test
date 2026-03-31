from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_search_menu, get_all_chat_titles, input_search_keyword


def test_search_chat_and_open_chat_matches_title(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    logged_in_driver

    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[data-index]")) > 0) # 채팅 기록이 로드될 때까지 대기
    
    get_all_chat_titles(wait)
    
    click_search_menu(wait)

    keyword = "B"
    input_search_keyword(wait, keyword)