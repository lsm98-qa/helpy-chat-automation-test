import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from locators.auth_locators import EMAIL_INPUT, LOGIN_BUTTON, PASSWORD_INPUT
from dotenv import load_dotenv

#===================
# 환경변수 로드
#===================
load_dotenv()

ACCOUNT_EMAIL = os.getenv("ACCOUNT_EMAIL")
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")

#===================
# 드라이버 설정
#===================
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default="https://qaproject.elice.io/ai-helpy-chat",
        help="Base URL for the target application.",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode.",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("--base-url")

@pytest.fixture
def driver(pytestconfig: pytest.Config):

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if pytestconfig.getoption("--headless"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    chrome_service = Service()
    browser = webdriver.Chrome(service=chrome_service, options=options)
    browser.implicitly_wait(3)

    yield browser

    browser.quit()

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)



#===================
# 로그인 설정
#===================
@pytest.fixture
def login_url():
    return "https://accounts.elice.io/accounts/signin/me?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat&lang=en-US&org=qaproject"


@pytest.fixture
def logged_in_driver(driver, wait, login_url):
    driver.get(login_url)

    wait.until(EC.presence_of_element_located(EMAIL_INPUT))
    wait.until(EC.presence_of_element_located(PASSWORD_INPUT))
    wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))

    login_page = LoginPage(driver)
    login_page.enter_email(ACCOUNT_EMAIL)
    login_page.enter_password(ACCOUNT_PASSWORD)
    login_page.click_login()

    yield driver

# ===================
# 로그 설정
# ===================
logger = logging.getLogger(__name__)


def _safe_filename(text: str, max_len: int = 120) -> str:
    # Windows 금지 문자 및 제어문자를 치환해 파일명 저장 실패를 방지
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text)
    safe = safe.strip().rstrip(". ")
    if not safe:
        safe = "test"
    return safe[:max_len]

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if not report.failed:
        return

    failed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.error("=" * 80)
    logger.error(f"테스트 실패: {item.name} (phase={report.when})")
    logger.error(f"실패 시각: {failed_at}")

    driver = item.funcargs.get("driver")

    if driver:
        try:
            logger.error(f"현재 URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"현재 URL 조회 실패: {e}")

        try:
            screenshot_dir = Path("artifacts/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            safe_item_name = _safe_filename(item.name)
            screenshot_path = screenshot_dir / f"{safe_item_name}_{report.when}_{timestamp}.png"
            is_saved = driver.save_screenshot(str(screenshot_path))
            if is_saved and screenshot_path.exists():
                logger.error(f"스크린샷 저장: {screenshot_path}")
            else:
                logger.error(
                    f"스크린샷 저장 실패: WebDriver가 False를 반환했습니다. path={screenshot_path}"
                )

            # pytest-html 리포트에 실패 시점 스크린샷을 직접 첨부
            screenshot_base64 = driver.get_screenshot_as_base64()
            extras = getattr(report, "extras", [])
            extras.append(
                pytest_html.extras.png(
                    screenshot_base64, name=f"failure-screenshot-{report.when}"
                )
            )
            report.extras = extras
            logger.error("HTML 리포트에 스크린샷 첨부 완료")
        except Exception as e:
            logger.error(f"스크린샷 저장 실패: {e}")
    else:
        logger.error("driver fixture를 찾지 못했습니다.")

    logger.error("실패 상세:")
    logger.error(report.longrepr)
    logger.error("=" * 80)
