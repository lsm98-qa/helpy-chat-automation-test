from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import EMAIL_INPUT, LOGIN_BUTTON, PASSWORD_INPUT
from pages.account_menu import AccountMenu


# 현재 화면이 로그인 페이지인지 URL과 로그인 폼 요소로 판별한다.
def _is_login_page(driver):
    current_url = driver.current_url.lower()
    if "accounts.elice.io/accounts/signin" in current_url:
        return True

    for locator in [EMAIL_INPUT, PASSWORD_INPUT, LOGIN_BUTTON]:
        if driver.find_elements(*locator):
            return True

    return False


# 보호 페이지 접근이 로그인 페이지 이동 또는 접근 제한으로 차단되는지 확인한다.
def _is_protected_page_blocked(driver, wait, base_url):
    protected_url = f"{base_url}/agents/mine"
    driver.get(protected_url)
    wait.until(lambda d: _is_login_page(d) or "/agents/mine" not in d.current_url.lower())
    return _is_login_page(driver) or "/agents/mine" not in driver.current_url.lower()


# =========================
# 프로필 메뉴 로그아웃 성공 검증
# =========================
def test_logout_success_via_profile_avatar(logged_in_driver, wait, base_url, testlog):
    # ==========
    # Arrange
    # ==========
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    wait.until(EC.url_contains("/ai-helpy-chat"))
    testlog.arrange("logged_in_session_ready", base_url=base_url)

    # ==========
    # Act
    # ==========
    # 프로필 메뉴에서 로그아웃 수행
    testlog.act("logout_via_profile_menu")
    account_menu.logout()
    wait.until(lambda d: _is_login_page(d))

    # 히스토리 이동 후에도 보호 페이지 접근이 차단되는지 확인
    blocked_after_logout = _is_protected_page_blocked(driver, wait, base_url)
    driver.back()
    driver.refresh()
    blocked_after_history_navigation = _is_protected_page_blocked(driver, wait, base_url)

    # ==========
    # Assert
    # ==========
    is_logout_success = _is_login_page(driver) and blocked_after_logout and blocked_after_history_navigation
    testlog.assert_(
        "logout_session_blocked",
        expected=True,
        actual=is_logout_success,
        blocked_after_logout=blocked_after_logout,
        blocked_after_history_navigation=blocked_after_history_navigation,
        current_url=driver.current_url,
    )
    assert is_logout_success, (
        f"로그아웃 이후 세션 차단 검증에 실패했습니다. "
        f"current_url={driver.current_url}, "
        f"blocked_after_logout={blocked_after_logout}, "
        f"blocked_after_history_navigation={blocked_after_history_navigation}"
    )
