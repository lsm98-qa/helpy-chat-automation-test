from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_new_chat
from selenium.common.exceptions import ElementClickInterceptedException
import pytest

# =========================
# 웹 브라우저 창을 일정 크기로 조정 시 플러스 버튼 동작 여부 검증
# =========================
@pytest.mark.xfail(reason="창 크기 조정 시 클릭 불가한 영역 발생")
def test_plus_button_click_triggers_action_in_resized_window(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    driver = logged_in_driver

    #==========
    # Act
    #==========

    # 새 대화 생성
    click_new_chat(wait)

    # 창 크기 조정 (가로 폭 767px이하, 세로 폭 800px 이상)
    driver.set_window_size(767, 800)

    #==========
    # Assert
    #==========
    # 채팅 입력칸 옆 플러스 아이콘 확인인
    plus_btn = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='plusIcon']")
        )
    )

    # 1차 : 플러스 버튼이 표시되는 지 검증
    assert plus_btn.is_displayed(), "플러스 버튼이 표시되지 않습니다."

    # 2차 : 플러스 버튼 클릭 시 동작하는 지 검증
    try:
        plus_btn.click()
    except ElementClickInterceptedException:
        assert False, "+ 버튼 클릭이 동작하지 않습니다."