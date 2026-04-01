from selenium.webdriver.support import expected_conditions as EC

from locators.auth_locators import EMAIL_INPUT, LOGIN_BUTTON, PASSWORD_INPUT, PROFILE_AVATAR
from pages.account_menu import AccountMenu


# 로그인 화면 여부를 URL 또는 로그인 폼 요소 존재로 판별한다.
def _is_login_page(driver):
    current_url = driver.current_url.lower()
    if "accounts.elice.io/accounts/signin" in current_url:
        return True

    for locator in [EMAIL_INPUT, PASSWORD_INPUT, LOGIN_BUTTON]:
        if driver.find_elements(*locator):
            return True

    return False


# 현재 화면이 비로그인 상태이거나 인증이 필요한 화면 접근이 제한된 상태인지 확인한다.
def _is_logged_out_or_restricted(driver):
    current_url = driver.current_url.lower()
    if _is_login_page(driver):
        return True

    if "/ai-helpy-chat" not in current_url:
        return True

    return not driver.find_elements(*PROFILE_AVATAR)


def test_logout_invalidates_session_after_refresh_in_other_tab(logged_in_driver, wait, base_url):
    """한 탭에서 로그아웃한 뒤 다른 탭 새로고침 시 인증 상태가 무효화되는지 검증한다."""

    # Arrange
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    wait.until(EC.url_contains("/ai-helpy-chat"))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    first_tab = driver.current_window_handle
    driver.execute_script("window.open(arguments[0], '_blank');", base_url)
    wait.until(lambda d: len(d.window_handles) == 2)
    second_tab = next(handle for handle in driver.window_handles if handle != first_tab)

    driver.switch_to.window(second_tab)
    wait.until(EC.url_contains("/ai-helpy-chat"))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    # Act
    driver.switch_to.window(first_tab)
    account_menu.logout()
    wait.until(lambda d: _is_login_page(d))

    driver.switch_to.window(second_tab)
    driver.refresh()
    wait.until(lambda d: _is_logged_out_or_restricted(d))

    # Assert
    assert _is_login_page(driver) or _is_logged_out_or_restricted(driver), (
        f"다른 탭 새로고침 후에도 로그인 상태가 유지됩니다: {driver.current_url}"
    )

    protected_url = f"{base_url}/agents/mine"
    driver.get(protected_url)
    wait.until(lambda d: _is_login_page(d) or "/agents/mine" not in d.current_url.lower())
    assert _is_login_page(driver) or "/agents/mine" not in driver.current_url.lower(), (
        f"로그아웃 후에도 로그인 전용 페이지 접근이 가능합니다: {driver.current_url}"
    )
