import pytest
from selenium.webdriver.common.by import By
from pages.chat_actions import click_new_chat, send_chat_message
from tests.chat.constants import GREETING_REPLY_TEST_CASES


@pytest.mark.parametrize(
    "question, expected_keywords",
    GREETING_REPLY_TEST_CASES,
)

# =========================
# 질문이나 대화를 전송했을 때 그에 맞는 키워드가 포함된 응답을 하는 지 검증
# =========================
def test_new_chat_receives_expected_greeting_reply(logged_in_driver, wait, question, expected_keywords):
    #==========
    # Arrange
    #==========
    # 로그인
    _ = logged_in_driver

    #==========
    # Act
    #==========
    # 새 대화 시작
    click_new_chat(wait)

    # 대화말 또는 질문 전송
    send_chat_message(wait, question)

    #==========
    # Assert
    #==========

    
    # 내가 보낸 대화와 다른 내용의 응답이 있는지 / 응답 안에 기대 키워드가 하나 이상 포함되어 있는지 검증
    AI_MESSAGE_TEXTS = (By.CSS_SELECTOR, "div[data-status='complete'].elice-aichat__markdown p")


    assert wait.until(
    lambda d: any(
        len(t) > 4
        and t != question
        and any(keyword in t for keyword in expected_keywords)
        for t in (
            el.text.strip()
            for el in d.find_elements(*AI_MESSAGE_TEXTS)
            )
        )
    ), f"질문 '{question}'에 대한 응답이 기대 키워드 {expected_keywords}를 포함하지 않습니다."
