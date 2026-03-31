from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_search_menu, get_all_chat_titles, input_search_keyword, get_visible_search_result_titles


def test_search_chat_and_open_chat_matches_title(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    logged_in_driver

    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[data-index]")) > 0) # 채팅 기록이 로드될 때까지 대기
    
    all_chat_titles = get_all_chat_titles(wait)
    
    click_search_menu(wait)

    keyword = "B"
    input_search_keyword(wait, keyword)

     # 검색 결과 로드 대기
    wait.until(lambda d: all(keyword in el.text for el in d.find_elements(By.CSS_SELECTOR, "div[role='dialog'] ul > li") if el.text.strip()))

    search_chat_titles = get_visible_search_result_titles(wait) # 검색 결과 제목 조회, 수집

    # 수집된 기록 중 검색어에 맞지 않는 결과 조회
    expected = [t for t in all_chat_titles if keyword in t]

    invalid_results = [t for t in expected if keyword not in t] # 검색어 미포함 결과
    missing_results = [t for t in expected if t not in search_chat_titles] # 누락된 채팅 확인

    errors = []

    if invalid_results:
        errors.append(f"검색어 '{keyword}'가 포함되지 않은 결과가 있습니다.: {invalid_results}")

    if missing_results:
        errors.append(f"누락된 결과가 있습니다.: {missing_results}")

    assert not errors, "\n".join(errors)