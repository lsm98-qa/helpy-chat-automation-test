import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage
from locators.login_locators import *
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
def logged_in_driver(driver, login_url):
    driver.get(login_url)

    login_page = LoginPage(driver)
    login_page.enter_email(ACCOUNT_EMAIL)
    login_page.enter_password(ACCOUNT_PASSWORD)
    login_page.click_login()

    yield driver

