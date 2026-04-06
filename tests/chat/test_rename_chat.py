from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_top_chat_item_option_button, get_top_chat_item_or_none, click_new_chat, send_chat_message, _get_top_chat_item

# =========================
# 이름 변경 기능 사용 시 정상적으로 변경이 되는 지 검증
# =========================
def test_can_rename_top_chat_item(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인
    logged_in_driver

    # 채팅 목록 확인
    chat = get_top_chat_item_or_none(wait)
    testlog.arrange("logged_in_driver_ready", has_existing_chat=(chat is not None))
    

    
    #==========
    # Act
    #==========

    testlog.act("open_rename_modal_and_submit_new_name")
    if chat is None:
        click_new_chat(wait)
        send_chat_message(wait, "A")

    # 채팅 옵션 열기
    click_top_chat_item_option_button(wait)

    # 이름 변경 메뉴 클릭
    rename_menu = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='이름 변경']"))
    )
    rename_menu.click()

    # 이름 입력창 확인
    input_box = wait.until(lambda d: d.find_element(By.CSS_SELECTOR,
        "div[role='dialog'] input[type='text']")
    )

    # 새 이름 입력
    if input_box.get_attribute("value").strip() != "123":
        new_name = "123"
    else:
        new_name = "456"
    input_box.send_keys(Keys.CONTROL + "a")
    input_box.send_keys(Keys.DELETE)
    input_box.send_keys(new_name)

    
    # 저장 버튼 클릭
    save_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    save_btn.click()
    #==========
    # Assert
    #==========
    # 이름 변경 창 종료 대기
    wait.until(EC.invisibility_of_element(input_box))
    
    # 최상단 채팅 요소 가져오기
    chat_item = _get_top_chat_item(wait)

    # 변경된 채팅 이름 확인
    is_renamed = new_name == chat_item.text.strip()
    testlog.assert_(
        "top_chat_item_renamed",
        expected=True,
        actual=is_renamed,
        expected_name=new_name,
        actual_name=chat_item.text.strip(),
    )
    assert is_renamed, "입력한 이름과 변경된 이름이 일치하지 않습니다."

    
