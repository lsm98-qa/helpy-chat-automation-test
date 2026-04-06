from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import PROFILE_AVATAR


# 현재 URL이 Helpy Chat 메인 홈인지 확인한다.
def _is_chat_home(driver, base_url):
    return "/ai-helpy-chat" in driver.current_url.lower() and base_url.lower() in driver.current_url.lower()


# =========================
# 정상 로그인 성공 상태 노출 검증
# =========================
def test_login_success(logged_in_driver, wait, base_url, testlog):
    # ==========
    # Arrange
    # ==========
    driver = logged_in_driver
    testlog.arrange("logged_in_driver_ready", base_url=base_url)

    # ==========
    # Act
    # ==========
    # 메인 홈 진입과 아바타 노출까지 대기
    testlog.act("wait_for_chat_home_and_avatar")
    wait.until(lambda d: _is_chat_home(d, base_url))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    # ==========
    # Assert
    # ==========
    has_profile_avatar = bool(driver.find_elements(*PROFILE_AVATAR))
    is_login_success = _is_chat_home(driver, base_url) and has_profile_avatar
    testlog.assert_(
        "login_success_state_visible",
        expected=True,
        actual=is_login_success,
        has_profile_avatar=has_profile_avatar,
        current_url=driver.current_url,
    )
    assert is_login_success, (
        f"로그인 성공 상태 검증에 실패했습니다. "
        f"current_url={driver.current_url}, "
        f"has_profile_avatar={has_profile_avatar}"
    )
