from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import pytest

def click_new_chat(wait):
    """새 대화 버튼 클릭"""
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='새 대화']"))
    ).click()


def send_chat_message(wait, message):
    """채팅 입력 및 전송."""
    chat_input = wait.until(
        EC.presence_of_element_located((By.NAME, "input"))
    )
    chat_input.send_keys(message)
    chat_input.send_keys(Keys.ENTER)

def get_top_chat_item(wait):
    # 사이드 채팅 영역 확인
    sidebar = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "aside")
    )

    # 채팅 목록 중 최상단 채팅
    return sidebar.find_element(
        By.CSS_SELECTOR, "a.MuiListItemButton-root[data-index='0']"
    )
    
def click_top_chat_item_option_button(wait):
    chat_item = get_top_chat_item(wait)

    # 상단 채팅 포인터
    driver = wait._driver
    ActionChains(driver).move_to_element(chat_item).perform()

    # 옵션 버튼 클릭
    option_button = wait.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR,
            "aside a[data-index='0'] button.MuiIconButton-root",
        )
    )
    option_button.click()

def check_chat_exists_or_pass(wait):
    try:
        return get_top_chat_item(wait)
    except NoSuchElementException:
        pytest.skip("채팅 기록이 존재하지 않습니다.")