from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_top_chat_item_option_button, get_top_chat_item, get_top_chat_item_or_none
import pytest
from selenium.webdriver.common.action_chains import ActionChains

def test_rename_chat(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    logged_in_driver
    chat = get_top_chat_item_or_none(wait)
    if chat is None:
        pytest.skip("채팅 기록이 존재하지 않습니다.")

    
    #==========
    # Act
    #==========
    # 채팅 목록에서 옵션 열기
    click_top_chat_item_option_button(wait)

    wait.until(
    lambda d: d.find_element(By.XPATH, "//li[normalize-space()='이름 변경']")
    ).click()

    input_box = wait.until(lambda d: d.find_element(By.CSS_SELECTOR,
        "div[role='dialog'] input[type='text']")
    )

    if input_box.get_attribute("value").strip() != "123":
        new_name = "123"
    else:
        new_name = "456"
    input_box.send_keys(Keys.CONTROL + "a")
    input_box.send_keys(Keys.DELETE)
    input_box.send_keys(new_name)

    
    save_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    save_btn.click()
    #==========
    # Assert
    #==========
    # 최상단 채팅 요소 가져오기
    chat_item = get_top_chat_item(wait)
    
    wait.until(EC.invisibility_of_element(input_box)) # 이름 입력창 사라질 때 까지 대기
    assert new_name == chat_item.text.strip(), "입력한 이름과 변경된 이름이 일치하지 않습니다."

def test_no_chat(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    logged_in_driver
    chat = get_top_chat_item_or_none(wait)
    if chat is not None:
        pytest.skip("채팅 기록이 1개 이상 존재합니다.")

    driver = wait._driver

    sidebar = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "aside")
    )

    chat_list_area = sidebar.find_element(
        By.CSS_SELECTOR, "[data-testid='virtuoso-scroller']"
    )

    #==========
    # Act
    #==========
    ActionChains(driver).move_to_element(chat_list_area).perform()

    #==========
    # Assert
    #==========
    option_button = driver.find_elements(
        By.CSS_SELECTOR,
        "[data-testid='virtuoso-scroller'] svg[data-icon='ellipsis-vertical']",
    )

    assert len(option_button) == 0, "채팅 기록이 없는 상태에서 옵션 버튼이 확인됩니다."

    
