import os
import time
import uuid

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import EMAIL_INPUT, LOGIN_BUTTON, PASSWORD_INPUT, PROFILE_AVATAR


ERROR_MESSAGE_LOCATORS = [
    (By.CSS_SELECTOR, "p.MuiFormHelperText-root.Mui-error"),
    (By.CSS_SELECTOR, "[id$='-helper-text'].Mui-error"),
]

INVALID_EMAIL_FORMAT_MESSAGE = "Invalid email format."
INVALID_CREDENTIALS_MESSAGE = "Email or password does not match"
TEMP_SYSTEM_ERROR_MESSAGE = "Oops, Something went wrong. Please try again later."


# 현재 페이지가 로그인 성공 상태인지 확인한다.
def _is_chat_home(driver, base_url):
    current_url = driver.current_url.lower()
    return "/ai-helpy-chat" in current_url and base_url.lower() in current_url


# 로그인 페이지를 열고 입력 필드/버튼이 준비될 때까지 대기한다.
def _open_login_page(driver, wait, login_url):
    driver.get(login_url)
    wait.until(EC.presence_of_element_located(EMAIL_INPUT))
    wait.until(EC.presence_of_element_located(PASSWORD_INPUT))
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))


# 기존 입력값을 확실히 지운 뒤 새 값을 입력한다.
def _clear_and_type(driver, element, value):
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)

    if element.get_attribute("value"):
        driver.execute_script(
            "arguments[0].value = '';"
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            element,
        )

    element.send_keys(value)


# 화면에 보이는 로그인 에러 메시지를 중복 없이 수집한다.
def _collect_visible_error_texts(driver):
    messages = []
    seen = set()
    for locator in ERROR_MESSAGE_LOCATORS:
        for element in driver.find_elements(*locator):
            if not element.is_displayed():
                continue
            text = element.text.strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            messages.append(text)
    return messages


# 수집된 메시지 목록에 기대 문구가 정확히 포함되는지 확인한다.
def _contains_message(texts, expected_message):
    normalized_expected = expected_message.strip().lower()
    return any(normalized_expected == text.strip().lower() for text in texts)


# 로그인 실패 후에도 성공 전환/버튼 고정 비활성 같은 비정상 상태가 없는지 확인한다.
def _assert_failed_login_without_stuck_ui(driver, wait, base_url):
    assert not _is_chat_home(driver, base_url), f"비정상 입력인데 로그인에 성공했습니다: {driver.current_url}"
    assert not driver.find_elements(*PROFILE_AVATAR), "비정상 입력인데 로그인 상태 UI가 보입니다."
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))
    login_button = driver.find_element(*LOGIN_BUTTON)
    is_disabled = login_button.get_attribute("disabled")
    aria_disabled = login_button.get_attribute("aria-disabled")
    assert not is_disabled and aria_disabled != "true", "로그인 버튼이 실패 후에도 비활성 상태로 유지됩니다."


# 로그인 시도 후 입력값/에러 메시지/브라우저 validation 메시지를 관찰값으로 반환한다.
def _submit_and_observe(driver, wait, email, password):
    email_input = driver.find_element(*EMAIL_INPUT)
    password_input = driver.find_element(*PASSWORD_INPUT)
    _clear_and_type(driver, email_input, email)
    _clear_and_type(driver, password_input, password)

    entered_email = email_input.get_attribute("value")
    entered_password = password_input.get_attribute("value")

    driver.find_element(*LOGIN_BUTTON).click()
    time.sleep(0.5)
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))

    email_after = driver.find_element(*EMAIL_INPUT).get_attribute("value")
    password_after = driver.find_element(*PASSWORD_INPUT).get_attribute("value")
    errors = _collect_visible_error_texts(driver)

    email_validation_message = driver.execute_script(
        "return arguments[0].validationMessage || '';", driver.find_element(*EMAIL_INPUT)
    ).strip()
    password_validation_message = driver.execute_script(
        "return arguments[0].validationMessage || '';", driver.find_element(*PASSWORD_INPUT)
    ).strip()

    return {
        "entered_email": entered_email,
        "entered_password": entered_password,
        "email_after": email_after,
        "password_after": password_after,
        "errors": errors,
        "email_validation_message": email_validation_message,
        "password_validation_message": password_validation_message,
    }


@pytest.mark.parametrize(
    ("email", "password", "expected_text_error", "allow_html5_email_msg", "allow_html5_password_msg"),
    [
        # 이메일 형식이 잘못된 입력에서 형식 오류 메시지를 검증한다.
        pytest.param(
            "test@",
            "wrong-password-1",
            INVALID_EMAIL_FORMAT_MESSAGE,
            True,
            False,
            id="invalid-email-format",
        ),
        # 이메일/비밀번호를 공백으로 입력한 경우의 실패 메시지를 검증한다.
        pytest.param(
            "   ",
            "   ",
            INVALID_CREDENTIALS_MESSAGE,
            True,
            True,
            id="empty-email-password",
        ),
        # 특수문자 및 앞뒤 공백이 포함된 입력의 실패 메시지를 검증한다.
        pytest.param(
            " !@# ",
            "  !@#bad-pass  ",
            INVALID_EMAIL_FORMAT_MESSAGE,
            True,
            False,
            id="special-characters-and-whitespace",
        ),
    ],
)
# =========================
# 비정상 입력 클라이언트 검증 메시지 노출 검증
# =========================
def test_login_negative_client_side_validation(
    driver,
    wait,
    base_url,
    login_url,
    email,
    password,
    expected_text_error,
    allow_html5_email_msg,
    allow_html5_password_msg,
    testlog,
):
    # ==========
    # Arrange
    # ==========
    _open_login_page(driver, wait, login_url)
    testlog.arrange(
        "open_login_with_invalid_inputs",
        email=email,
        expected_text_error=expected_text_error,
        allow_html5_email_msg=allow_html5_email_msg,
        allow_html5_password_msg=allow_html5_password_msg,
    )

    # ==========
    # Act
    # ==========
    # 비정상 입력으로 로그인 시도 후 관찰값 수집
    testlog.act("submit_invalid_credentials")
    observed = _submit_and_observe(driver, wait, email=email, password=password)
    _assert_failed_login_without_stuck_ui(driver, wait, base_url)

    has_text_error = _contains_message(observed["errors"], expected_text_error)
    has_html5_email_error = allow_html5_email_msg and bool(observed["email_validation_message"])
    has_html5_password_error = allow_html5_password_msg and bool(observed["password_validation_message"])

    # ==========
    # Assert
    # ==========
    is_error_visible = has_text_error or has_html5_email_error or has_html5_password_error
    testlog.assert_(
        "client_side_validation_error_visible",
        expected=True,
        actual=is_error_visible,
        observed_errors=observed["errors"],
        email_validation_message=observed["email_validation_message"],
        password_validation_message=observed["password_validation_message"],
    )
    assert is_error_visible, (
        "클라이언트 입력 검증 에러 메시지를 확인하지 못했습니다. "
        f"errors={observed['errors']}, "
        f"email_validation_message='{observed['email_validation_message']}', "
        f"password_validation_message='{observed['password_validation_message']}'"
    )


# =========================
# 미존재 계정 로그인 실패 메시지 노출 검증
# =========================
def test_login_negative_non_existing_account(driver, wait, base_url, login_url, testlog):
    # ==========
    # Arrange
    # ==========
    _open_login_page(driver, wait, login_url)
    non_existing_email = f"autotest-non-existing-{uuid.uuid4().hex[:10]}@example.invalid"
    testlog.arrange("open_login_with_non_existing_account", email=non_existing_email)

    # ==========
    # Act
    # ==========
    # 존재하지 않는 계정으로 로그인 시도
    testlog.act("submit_non_existing_account")
    observed = _submit_and_observe(driver, wait, email=non_existing_email, password="AnyWrongPass123!")
    _assert_failed_login_without_stuck_ui(driver, wait, base_url)

    # ==========
    # Assert
    # ==========
    has_invalid_credentials = _contains_message(observed["errors"], INVALID_CREDENTIALS_MESSAGE)
    has_temp_system_error = _contains_message(observed["errors"], TEMP_SYSTEM_ERROR_MESSAGE)
    is_expected_error_visible = has_invalid_credentials or has_temp_system_error
    testlog.assert_(
        "non_existing_account_error_visible",
        expected=True,
        actual=is_expected_error_visible,
        observed_errors=observed["errors"],
    )
    assert is_expected_error_visible, (
        "존재하지 않는 계정 시 기대 메시지(인증 실패/임시 시스템 오류)를 찾지 못했습니다. "
        f"errors={observed['errors']}"
    )


# =========================
# 정상 이메일 + 오입력 비밀번호 실패 메시지 검증
# =========================
def test_login_negative_wrong_password(driver, wait, base_url, login_url, testlog):
    # ==========
    # Arrange
    # ==========
    account_email = os.getenv("ACCOUNT_EMAIL")
    if not account_email:
        pytest.skip("ACCOUNT_EMAIL 환경변수가 없어 정상 이메일 + 틀린 비밀번호 시나리오를 건너뜁니다.")
    _open_login_page(driver, wait, login_url)
    testlog.arrange("open_login_with_wrong_password", email=account_email)

    # ==========
    # Act
    # ==========
    # 정상 이메일과 틀린 비밀번호 조합으로 로그인 시도
    testlog.act("submit_wrong_password")
    observed = _submit_and_observe(driver, wait, email=account_email, password="WrongPassword!234")
    _assert_failed_login_without_stuck_ui(driver, wait, base_url)

    # ==========
    # Assert
    # ==========
    has_invalid_credentials = _contains_message(observed["errors"], INVALID_CREDENTIALS_MESSAGE)
    testlog.assert_(
        "wrong_password_error_visible",
        expected=True,
        actual=has_invalid_credentials,
        observed_errors=observed["errors"],
    )
    assert has_invalid_credentials, (
        "비밀번호 불일치/인증 실패 메시지를 찾지 못했습니다. "
        f"errors={observed['errors']}"
    )
