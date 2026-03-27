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


def _assert_protected_page_blocked(driver, wait, base_url):
    """로그아웃 이후 보호 페이지 접근이 차단되는지 검증한다."""

    protected_url = f"{base_url}/agents/mine"
    driver.get(protected_url)
    wait.until(lambda d: _is_login_page(d) or "/agents/mine" not in d.current_url.lower())
    assert _is_login_page(driver) or "/agents/mine" not in driver.current_url.lower(), (
        f"로그아웃 후에도 보호 페이지에 접근 가능합니다: {driver.current_url}"
    )


def test_logout_success_via_profile_avatar(logged_in_driver, wait, base_url):
    """프로필 아바타 메뉴에서 로그아웃 성공 흐름을 검증한다."""
    
    # Arrange
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    wait.until(EC.url_contains("/ai-helpy-chat"))

    # Act
    account_menu.logout()

    # Assert
    wait.until(lambda d: _is_login_page(d))
    assert _is_login_page(driver), f"로그아웃 후 로그인 페이지로 이동하지 않았습니다: {driver.current_url}"
    _assert_protected_page_blocked(driver, wait, base_url)
    driver.back()
    driver.refresh()
    _assert_protected_page_blocked(driver, wait, base_url)

