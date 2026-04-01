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


# 보호 페이지 접근이 로그인 페이지 이동 또는 접근 제한으로 차단되는지 확인한다.
def _is_protected_page_blocked(driver, wait, base_url):
    protected_url = f"{base_url}/agents/mine"
    driver.get(protected_url)
    wait.until(lambda d: _is_login_page(d) or "/agents/mine" not in d.current_url.lower())
    return _is_login_page(driver) or "/agents/mine" not in driver.current_url.lower()


# =========================
# 탭 간 로그아웃 세션 무효화 검증
# =========================
def test_logout_invalidates_session_after_refresh_in_other_tab(logged_in_driver, wait, base_url):
    # ==========
    # Arrange
    # ==========
    driver = logged_in_driver
    account_menu = AccountMenu(driver, wait)
    wait.until(EC.url_contains("/ai-helpy-chat"))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    # 테스트용 두 번째 탭 생성
    first_tab = driver.current_window_handle
    driver.execute_script("window.open(arguments[0], '_blank');", base_url)
    wait.until(lambda d: len(d.window_handles) == 2)
    second_tab = next(handle for handle in driver.window_handles if handle != first_tab)

    # ==========
    # Act
    # ==========
    # 두 번째 탭에서 로그인 상태를 확인한 뒤 첫 번째 탭에서 로그아웃
    driver.switch_to.window(second_tab)
    wait.until(EC.url_contains("/ai-helpy-chat"))
    wait.until(EC.presence_of_element_located(PROFILE_AVATAR))

    driver.switch_to.window(first_tab)
    account_menu.logout()
    wait.until(lambda d: _is_login_page(d))

    # 로그아웃 이후 두 번째 탭 새로고침으로 세션 상태 재확인
    driver.switch_to.window(second_tab)
    driver.refresh()
    wait.until(lambda d: _is_logged_out_or_restricted(d))
    blocked_protected_page = _is_protected_page_blocked(driver, wait, base_url)

    # ==========
    # Assert
    # ==========
    assert _is_logged_out_or_restricted(driver) and blocked_protected_page, (
        f"다른 탭 새로고침 후 세션 무효화 검증에 실패했습니다. "
        f"current_url={driver.current_url}, "
        f"blocked_protected_page={blocked_protected_page}"
    )
