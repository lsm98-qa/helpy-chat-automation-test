from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_search_menu, get_all_chat_titles, click_new_chat, send_chat_message, get_visible_search_result_titles
import pytest

# =========================
# 검색 화면에서 조회되는 채팅이 내 보유 채팅과 일치하는 지 검증
# =========================
@pytest.mark.xfail(reason="Known issue: 검색 결과 UI는 최대 20개까지만 표시하여 전체 채팅 개수와 일치하지 않음")
def test_search_box_shows_all_chats(logged_in_driver, wait, testlog):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver
    testlog.arrange("logged_in_driver_ready")

    # 채팅 기록이 로드될 때까지 대기
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[data-index]")) > 0)
    
    #==========
    # Act
    #==========
    testlog.act("collect_all_chats_and_open_search")
    # 전체 채팅 제목 수집
    all_chat_titles = get_all_chat_titles(wait)

    # 채팅이 21개 미만이면 부족한 개수만큼 추가 생성
    missing_count = 21 - len(all_chat_titles)
    created = False

    for _ in range(max(0, missing_count)):
        created = True
        click_new_chat(wait)

        AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
        before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))
        # 최대 3번까지 재시도
        for _ in range(3):
            if before_count == 0:
                break
            click_new_chat(wait)
            before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))
        else:
            raise AssertionError("새 채팅 초기화 실패")

        send_chat_message(wait, "A")

        # AI 응답까지 대기(과부하 방지)
        wait.until(
            lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count
        )

    # 반복 생성 완료 후 최종 채팅 목록 다시 수집
    if created:
        all_chat_titles = get_all_chat_titles(wait)
    
    
    click_search_menu(wait)

    #==========
    # Assert
    #==========
    all_chat_titles_count = len(all_chat_titles)
    # 검색 화면에 조회된 채팅 개수 확인
    search_chat_count = len(get_visible_search_result_titles(wait))
    print(search_chat_count, all_chat_titles_count)

    is_same_count = all_chat_titles_count == search_chat_count
    testlog.assert_(
        "search_result_count_matches_all_chats",
        expected=all_chat_titles_count,
        actual=search_chat_count,
    )
    assert is_same_count, f"전체 채팅 개수({all_chat_titles_count})와 검색 창의 채팅 개수({search_chat_count})가 일치하지 않습니다."
