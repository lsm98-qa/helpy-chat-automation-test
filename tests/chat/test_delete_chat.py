from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import get_top_chat_item_or_none, click_top_chat_item_option_button, get_top_chat_item
import pytest 

def test_can_delete_top_chat_item(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver
    chat = get_top_chat_item_or_none(wait)
    if chat is None:
        pytest.skip("채팅 기록이 존재하지 않습니다.")

    #==========
    # Act
    #==========
    # 채팅 목록에서 옵션 열기
    click_top_chat_item_option_button(wait)
    delete_before_top_chat = get_top_chat_item(wait)

    # 삭제 메뉴 클릭
    delete_menu = wait.until(EC.element_to_be_clickable(
        driver.find_element(By.CSS_SELECTOR, "li[tabindex='-1']")))
    delete_menu.click()

    # 삭제 확인 팝업의 '삭제' 버튼 클릭
    buttons = wait.until(
    lambda d: d.find_elements(By.CSS_SELECTOR, "div[role='dialog'] button")
    )
    delete_button = next(b for b in buttons if b.text.strip() == "삭제")
    
    delete_button.click()