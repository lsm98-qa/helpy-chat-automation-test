import pytest
from selenium.webdriver.common.by import By
from pages.chat_actions import click_new_chat, send_chat_message
from tests.chat.constants import GREETING_REPLY_TEST_CASES


@pytest.mark.parametrize(
    "question, expected_keywords",
    GREETING_REPLY_TEST_CASES,
)
def test_new_chat_receives_expected_greeting_reply(logged_in_driver, wait, question, expected_keywords):
    #==========
    # Arrange
    #==========
    _ = logged_in_driver

    #==========
    # Act
    #==========
    click_new_chat(wait)
    send_chat_message(wait, question)

    #==========
    # Assert
    #==========
    assert wait.until(
        lambda d: any(
            len(t) > 4 and t != question and any(keyword in t for keyword in expected_keywords)
            for t in (p.text.strip() for p in d.find_element(By.TAG_NAME, "body").find_elements(By.TAG_NAME, "p"))
        )
    ), f"질문 '{question}'에 대한 응답이 기대 키워드 {expected_keywords}를 포함하지 않습니다."
