from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


# 새 대화 버튼을 클릭
def click_new_chat(wait):
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='새 대화']"))
    ).click()


# 채팅 입력창에 메시지를 입력하고 전송
def send_chat_message(wait, message):
    chat_input = wait.until(
        EC.presence_of_element_located((By.NAME, "input"))
    )
    chat_input.send_keys(message)
    chat_input.send_keys(Keys.ENTER)


# 최상단 채팅 항목을 반환하는 헬퍼
def _get_top_chat_item(wait):
    # 사이드바가 렌더링될 때까지 대기
    sidebar = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "aside")
    )

    # 채팅 목록의 첫 번째 항목 반환
    return sidebar.find_element(
        By.CSS_SELECTOR, "[data-testid='virtuoso-scroller'] a[data-index='0']"
    )

# 최상단 채팅 항목의 옵션 버튼을 클릭
def click_top_chat_item_option_button(wait):
    chat_item = _get_top_chat_item(wait)

    # 옵션 버튼이 클릭 가능할 때 까지 포인터 유지
    option_button = wait.until(lambda d: (
    ActionChains(d).move_to_element(chat_item).perform(),
    d.find_element(
        By.CSS_SELECTOR,
        "[data-testid='virtuoso-scroller'] a[data-index='0'] svg[data-icon='ellipsis-vertical']"
        )
    )[1])

    option_button.click()


# 최상단 채팅 항목이 있으면 반환하고, 없으면 None을 반환
def get_top_chat_item_or_none(wait):
    try:
        return _get_top_chat_item(wait)
    except NoSuchElementException:
        return None

        