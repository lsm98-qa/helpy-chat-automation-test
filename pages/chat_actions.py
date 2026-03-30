from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

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
        By.CSS_SELECTOR, "[data-testid='virtuoso-scroller'] a[data-index='0']"
    )
    
def click_top_chat_item_option_button(wait):
    chat_item = get_top_chat_item(wait)

    # 옵션 버튼이 클릭 가능할 때 까지 포인터 유지
    option_button = wait.until(lambda d: (
    ActionChains(d).move_to_element(chat_item).perform(),
    d.find_element(
        By.CSS_SELECTOR,
        "[data-testid='virtuoso-scroller'] a[data-index='0'] svg[data-icon='ellipsis-vertical']"
        )
    )[1])

    option_button.click()

def get_top_chat_item_or_none(wait):
    try:
        return get_top_chat_item(wait)
    except NoSuchElementException:
        return None

        