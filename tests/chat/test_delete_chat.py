from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import get_top_chat_item_or_none, click_top_chat_item_option_button, _get_top_chat_item, click_new_chat, send_chat_message

# =========================
# 채팅 삭제 기능이 정상적으로 동작하는 지 검증
# =========================
def test_can_delete_top_chat_item(logged_in_driver, wait):
    #==========
    # Arrange
    #========
    # 로그인
    driver = logged_in_driver
    chat = get_top_chat_item_or_none(wait)
    

    #==========
    # Act
    #==========
    if chat is None:
        click_new_chat(wait)
        send_chat_message(wait, "A")
    
    # 채팅 목록에서 옵션 열기
    click_top_chat_item_option_button(wait)
    delete_before_top_chat = _get_top_chat_item(wait)

    # 삭제 메뉴 클릭
    delete_menu = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='삭제']"))
    )
    delete_menu.click()

    # 삭제 확인 버튼 클릭
    buttons = wait.until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "div[role='dialog'] button")
    )
    delete_button = next(b for b in buttons if b.text.strip() == "삭제")
    delete_button.click()

    #==========
    # Assert
    #==========
    # 삭제 전 채팅 요소가 사라질 때까지 대기
    wait.until(EC.staleness_of(delete_before_top_chat))
    
    
    driver = wait._driver

    # 채팅 기록 확인
    chat_items = driver.find_elements(
        By.CSS_SELECTOR,
        "[data-testid='virtuoso-scroller'] a[data-index]"
    )
    
    # 채팅이 남아 있으면 최상단 항목 비교
    if len(chat_items) > 0:
        delete_after_top_chat = _get_top_chat_item(wait)
        assert delete_after_top_chat != delete_before_top_chat, "채팅 기록이 삭제되지 않았습니다."

    else:
        assert len(chat_items) == 0, "채팅 기록이 삭제되지 않았습니다."