from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_new_chat, send_chat_message, get_top_chat_item_or_none, click_top_chat_item_option_button
from selenium.webdriver.common.keys import Keys


# =========================
#이름 변경에서 빈 값인 상태로 저장이 불가한 지 검증
# =========================
def test_input_empty_value_chat_name(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver

    # 채팅 목록 확인
    chat = get_top_chat_item_or_none(wait)
    testlog.arrange("logged_in_driver_ready", has_existing_chat=(chat is not None))
    
    #==========
    # Act
    #==========

    # 채팅이 없다면 1개 생성
    if chat is None:
        click_new_chat(wait)
        send_chat_message(wait, "A")

    #==========
    # Act
    #==========
    # 채팅 목록에서 옵션 열기
    testlog.act("open_rename_modal_and_clear_name")
    click_top_chat_item_option_button(wait)
    
    wait.until(lambda d: d.find_element(By.XPATH, "//li[normalize-space()='이름 변경']")
    ).click()

    input_box = wait.until(lambda d: d.find_element(By.CSS_SELECTOR,
        "div[role='dialog'] input[type='text']")
    )

    # 텍스트 삭제
    input_box.send_keys(Keys.CONTROL + "a")
    input_box.send_keys(Keys.DELETE)

    #==========
    # Assert
    #==========
    # input 빈 값 상태가 될 때까지 대기
    wait.until(lambda d: input_box.get_attribute("aria-invalid") == "true")
    
    # 저장 버튼 비활성화 여부 검증
    save_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    is_save_disabled = not save_btn.is_enabled()
    testlog.assert_("rename_save_button_disabled_on_empty_name", expected=True, actual=is_save_disabled)
    assert is_save_disabled, "저장 버튼이 비활성화 되지 않았습니다."
