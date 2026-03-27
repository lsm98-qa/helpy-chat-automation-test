from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import PROFILE_AVATAR


# 현재 URL이 Helpy Chat 메인 홈인지 확인한다.
def _is_chat_home(driver, base_url):
    return "/ai-helpy-chat" in driver.current_url.lower() and base_url.lower() in driver.current_url.lower()


# 정상 로그인 후 메인 화면 진입과 사용자 아바타 노출을 검증한다.
def test_login_success(logged_in_driver, wait, base_url):
    """정상 로그인 시 메인 페이지로 이동하는지 검증한다."""

    # Arrange
    driver = logged_in_driver

    # Act
    wait.until(lambda d: _is_chat_home(d, base_url))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    # Assert
    assert _is_chat_home(driver, base_url), f"로그인 후 메인 페이지로 이동하지 않았습니다: {driver.current_url}"
    assert driver.find_elements(*PROFILE_AVATAR), "로그인 후 프로필 아바타가 보이지 않습니다."
