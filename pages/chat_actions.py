from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# 새 대화 버튼 클릭
def click_new_chat(wait):
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='새 대화']"))
    ).click()


# 채팅 입력 및 전송
def send_chat_message(wait, message):
    chat_input = wait.until(
        EC.presence_of_element_located((By.NAME, "input"))
    )
    chat_input.send_keys(message)
    chat_input.send_keys(Keys.ENTER)

# 최상단 채팅 항목을 반환하는 헬퍼
def _get_top_chat_item(wait):
    # 사이드 채팅 영역 확인
    sidebar = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "aside")
    )

    # 채팅 목록 중 최상단 채팅
    return sidebar.find_element(
        By.CSS_SELECTOR, "[data-testid='virtuoso-scroller'] a[data-index='0']"
    )
 
# 최상단 채팅 항목의 옵션 버튼 클릭
def click_top_chat_item_option_button(wait):
    chat_item = _get_top_chat_item(wait)

    # 옵션 버튼이 클릭 가능할 때까지 포인터 유지
    option_button = wait.until(lambda d: (
        ActionChains(d).move_to_element(chat_item).perform() or
        d.find_element(By.CSS_SELECTOR, "a[data-index='0'] button")
    ))
    option_button.click()

# 최상단 채팅 항목이 있으면 반환하고, 없으면 None 반환
def get_top_chat_item_or_none(wait):
    try:
        return _get_top_chat_item(wait)
    except NoSuchElementException:
        return None
    

# 채팅 기록 수집
def get_all_chat_titles(wait):
    driver = wait._driver
    scroller = driver.find_element(By.CSS_SELECTOR, "div[data-testid='virtuoso-scroller']")

    # 채팅 스크롤 위치 초기화 하고 시작
    driver.execute_script("arguments[0].scrollTop = 0", scroller)
    wait.until(lambda d: d.execute_script("return arguments[0].scrollTop", scroller) == 0)
    
    titles = []

    # 이미 추가한 채팅 링크 저장하여 중복 제외
    seen = set()

    while True:
        try:
            # 현재 화면에 보이는 채팅 항목 수집
            chat_items = driver.find_elements(By.CSS_SELECTOR, "a[data-index]")

            for item in chat_items:
                # 채팅 제목과 링크 가져오기
                title = item.text.strip()
                link = item.get_attribute("href")

                # 제목이 있고, 아직 저장하지 않은 채팅이면 목록에 추가
                if title and link and link not in seen:
                    seen.add(link)
                    titles.append(title)

        except StaleElementReferenceException:
            continue

        prev_scroll = driver.execute_script("return arguments[0].scrollTop", scroller)
        driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight", scroller)
        curr_scroll = driver.execute_script("return arguments[0].scrollTop", scroller)

        # 더 이상 스크롤 할 공간이 없다면 종료료
        if curr_scroll == prev_scroll:
            break

    return titles


# 검색 메뉴 버튼 클릭
def click_search_menu(wait):
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='검색']"))
    ).click()        
        
# 검색 입력창에 키워드 입력
def input_search_keyword(wait, keyword):
    search_input = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
    )
    search_input.clear()
    search_input.send_keys(keyword)
    return search_input

# 화면에 보이는 검색 결과 제목 수집
def get_visible_search_result_titles(wait):
    dialog = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "div[role='dialog']")
    )

    items = dialog.find_elements(By.CSS_SELECTOR, "ul > li")

    search_chat_titles = []
    for item in items:
        # 비어 있지 않은 제목만 수집
        text = item.text.strip()
        if text:
            search_chat_titles.append(text)

    return search_chat_titles
