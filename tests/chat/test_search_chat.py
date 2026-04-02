from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_search_menu, get_all_chat_titles, input_search_keyword, get_visible_search_result_titles

# =========================
# 검색어에 맞게 올바르게 검색 값이 나오는 지, 클릭한 채팅으로 정상 진입 되는 지 검증
# =========================
def test_search_chat_and_open_chat_matches_title(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인
    logged_in_driver

    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[data-index]")) > 0) # 채팅 기록이 로드될 때까지 대기
    
    # 전체 채팅 제목 수집
    all_chat_titles = get_all_chat_titles(wait)

    #==========
    # Act
    #==========
    click_search_menu(wait)

    keyword = " "

    # 검색어 입력
    search_input = input_search_keyword(wait, keyword)

    keyword_lower = keyword.lower()

    
    #==========
    # Assert
    #==========
    # 검색어가 포함된 제목만 기대값으로 사용

    if keyword.strip() == "":
    # 검색어가 공백인 경우 NONE이 아닌 전체 타이틀 수집
        expected = [
            t for t in all_chat_titles
            if t is not None and keyword in t
        ]
    else:
        # 공백이 아닌 경우 대소문자 무시하고 타이틀 수집
        expected = [
            t for t in all_chat_titles
            if t is not None and keyword.lower() in t.lower()
        ]
    
    # 검색 결과에 기대값이 아닌 문자가 없을 때 까지 대기
    wait.until(
        lambda d: all(
            (el.get_attribute("textContent") or "") in expected
            for el in d.find_elements(By.CSS_SELECTOR, "div[role='dialog'] ul > li")
        )
    )


    search_chat_titles = get_visible_search_result_titles(wait) # 검색 결과 제목 조회
    
    invalid_results = [t for t in search_chat_titles if keyword_lower not in (t or "").lower()] # 검색어 미포함 결과
    missing_results = [t for t in expected if t not in search_chat_titles] # 누락된 채팅 확인

    
    errors = []

    if invalid_results:
        errors.append(f"검색어 '{keyword}'가 포함되지 않은 결과가 있습니다.: {invalid_results}")

    if missing_results:
        errors.append(f"누락된 결과가 있습니다.: {missing_results}")

    assert not errors, "\n".join(errors)

    if search_chat_titles:
        #==========
        # Act
        #==========
        # 최상단 검색 결과 제목 저장
        top_chat_title = wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, "div[role='dialog'] ul > li span")
        ).get_attribute("textContent")
        
        # 최상단 검색 결과 클릭
        first_item = wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, "div[role='dialog'] ul > li")
        )
        first_item.click()

        wait.until(EC.invisibility_of_element(search_input)) # 검색 입력창이 사라질 때까지 대기

        # 메인 영역의 옵션 버튼 클릭
        chat_option_btn = wait.until(
        lambda d: next(
            (btn for btn in d.find_elements(By.CSS_SELECTOR, "main button[type='button']")
                if btn.is_displayed() and btn.is_enabled() and not btn.text.strip()
            ), False
            )
        )
        chat_option_btn.click()

        # 옵션 메뉴의 첫 번째 항목 클릭
        rename_menu = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "ul[role='menu'] > li[role='menuitem']:first-child")
        ) 
        wait.until(lambda d: rename_menu.is_displayed() and rename_menu.is_enabled()) 
        rename_menu.click()
        
        #==========
        # Assert
        #==========
        # 이름 입력값 확인
        name_input_box = wait.until(
        lambda d: d.find_element(By.CSS_SELECTOR, "input[name='name']")
        )

        name_input_value = name_input_box.get_attribute("value")
        assert name_input_value == top_chat_title, "선택한 채팅과 이름이 일치하지 않습니다."
