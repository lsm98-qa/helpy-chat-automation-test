from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_top_chat_item_option_button, _get_top_chat_item, get_top_chat_item_or_none
import pytest
from selenium.webdriver.common.action_chains import ActionChains

def test_can_rename_top_chat_item(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인
    logged_in_driver

    # 채팅 목록 확인
    chat = get_top_chat_item_or_none(wait)
    if chat is None:
        pytest.skip("채팅 기록이 존재하지 않습니다.")

    
    #==========
    # Act
    #==========
    # 채팅 옵션 열기
    click_top_chat_item_option_button(wait)

    # 이름 변경 메뉴 클릭
    wait.until(
    lambda d: d.find_element(By.XPATH, "//li[normalize-space()='이름 변경']")
    ).click()

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
    # 최상단 채팅 요소 가져오기
    chat_item = _get_top_chat_item(wait)
    
    # 변경된 채팅 이름 확인
    wait.until(EC.invisibility_of_element(input_box)) # 이름 입력창 사라질 때 까지 대기
    assert new_name == chat_item.text.strip(), "입력한 이름과 변경된 이름이 일치하지 않습니다."

def test_chat_options_hidden_when_chat_list_empty(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인
    logged_in_driver
    # 채팅 목록이 비어있는지 확인
    chat = get_top_chat_item_or_none(wait)
    if chat is not None:
        pytest.skip("채팅 기록이 1개 이상 존재합니다.")

    driver = wait._driver

    # 채팅 영역 확인
    sidebar = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "aside")
    )

    chat_list_area = sidebar.find_element(
        By.CSS_SELECTOR, "[data-testid='virtuoso-scroller']"
    )

    #==========
    # Act
    #==========
    # 채팅 영역에 마우스 이동
    ActionChains(driver).move_to_element(chat_list_area).perform()

    #==========
    # Assert
    #==========
    # 옵션 버튼이 보이지 않는지 확인
    option_button = driver.find_elements(
        By.CSS_SELECTOR,
        "[data-testid='virtuoso-scroller'] svg[data-icon='ellipsis-vertical']",
    )

    assert len(option_button) == 0, "채팅 기록이 없는 상태에서 옵션 버튼이 확인됩니다."

    
