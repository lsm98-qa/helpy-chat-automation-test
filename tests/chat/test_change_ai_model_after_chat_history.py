from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_actions import click_new_chat, ensure_other_model_or_enable_in_settings, select_other_model, send_chat_message
import pytest

# =========================
# 대화 중 ai 모델 전환 시 채팅이 동일하게 로드 되는 지 검증
# =========================
@pytest.mark.xfail(reason = "대화 후 ai 모델 전환 시 처음 입력한 내 채팅만 화면에 출력되는 오류 발생")
def test_chat_persistence_after_change_ai_model(logged_in_driver, wait):
    #==========
    # Arrange
    #==========
    # 로그인
    driver = logged_in_driver

    # 로그인 요소가 사라질 때까지 대기
    wait.until(EC.invisibility_of_element_located((By.NAME, "loginId")))
    
    # 전환 가능한 모델 여부 확인 : 없을 시 모델 설정에서 활성화
    ensure_other_model_or_enable_in_settings(wait)

    #==========
    # Act
    #==========    
    # 새 대화 생성
    click_new_chat(wait)

    # AI 응답 영역 확인
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")
    before_count = len(driver.find_elements(*AI_MESSAGE_TEXTS))

    # 메시지 전송
    send_chat_message(wait, "hi")

    # AI 응답 대기
    wait.until(
        lambda d: len(d.find_elements(*AI_MESSAGE_TEXTS)) > before_count
    )

    
    # AI 모델 전환
    select_other_model(wait)

    #==========
    # Assert
    #==========    
    # AI 응답 일치 여부 검증
    ai_messages = driver.find_elements(*AI_MESSAGE_TEXTS)
    assert len(ai_messages) > 0, "AI 모델 전환환 후 응답 메시지가 확인되지 않습니다."