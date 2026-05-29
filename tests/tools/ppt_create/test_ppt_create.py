import logging
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve
from zipfile import ZipFile

import pytest
from pptx import Presentation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.menu_locators import MENU_TOOLS

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
logger = logging.getLogger(__name__)

PPT_CREATE_MENU = (By.XPATH, "//p[text()='PPT 생성']")
TOPIC_INPUT = (By.NAME, "topic")
INSTRUCTIONS_INPUT = (By.NAME, "instructions")
SLIDES_COUNT_INPUT = (By.NAME, "slides_count")
SECTION_COUNT_INPUT = (By.NAME, "section_count")
SIMPLE_MODE_CHECKBOX = (By.NAME, "simple_mode")
SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
REGENERATE_MODAL = (By.XPATH, "//div[@role='presentation']")
REGENERATE_CONFIRM_BUTTON = (By.XPATH, ".//button[contains(.,'다시 생성')]")
DOWNLOAD_LINK = (By.XPATH, "//a[contains(., '생성 결과 다운로드')]")

PPT_TOPIC = "이미지 AI의 최신 트렌드와 활용"
PPT_INSTRUCTIONS = "2025년 기준으로 만들어줘"
EXPECTED_SLIDE_COUNT = 10
EXPECTED_SECTION_COUNT = 3
DOWNLOAD_DIR = Path("tests/tools/ppt_create/downloads")


# 요소가 화면에 표시될 때까지 기다린 뒤 반환하는 헬퍼
def _find(driver, by, value):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, value))
    )


# 요소가 클릭 가능할 때까지 기다린 뒤 클릭하는 헬퍼
def _click(driver, by, value):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    ).click()


# 입력 필드를 비운 뒤 새 텍스트를 입력하는 헬퍼
def _type_text(driver, by, value, text):
    element = _find(driver, by, value)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


# 제출 버튼 상태에 따라 생성 또는 다시 생성 플로우를 수행하는 헬퍼
def _submit_ppt_generation(wait, testlog):
    submit_button = wait.until(
        EC.element_to_be_clickable(SUBMIT_BUTTON)
    )
    submit_button_text = submit_button.text.strip()
    testlog.act("submit_generation_clicked", button_text=submit_button_text)

    if submit_button_text == "다시 생성":
        submit_button.click()
        modal = wait.until(
            EC.presence_of_element_located(REGENERATE_MODAL)
        )
        modal.find_element(*REGENERATE_CONFIRM_BUTTON).click()
    else:
        submit_button.click()


# 생성 결과 다운로드 링크가 제한 시간 내 .pptx로 준비되는지 확인하는 헬퍼
def _wait_for_ppt_link(driver, timeout_seconds=600, poll_interval=10):
    for attempt in range(timeout_seconds // poll_interval):
        time.sleep(poll_interval)
        elapsed_sec = (attempt + 1) * poll_interval

        try:
            download_link = driver.find_element(*DOWNLOAD_LINK)
            href = download_link.get_attribute("href")
            logger.info("ppt_link_poll elapsed_sec=%s href=%s", elapsed_sec, href)

            if href and ".pptx" in href:
                logger.info("ppt_link_ready href=%s", href)
                return href
        except Exception:
            logger.info("ppt_link_poll elapsed_sec=%s status=processing", elapsed_sec)

    logger.error("ppt_link_timeout timeout_seconds=%s", timeout_seconds)
    raise AssertionError("PPT 링크가 제한 시간 내 생성되지 않았습니다.")


# 생성된 PPT 파일이 정상적으로 다운로드되는지 확인하는 헬퍼
def _download_with_retry(href, download_dir, retries=5, delay_seconds=3):
    file_name = Path(urlparse(href).path).name or f"ppt_{int(time.time())}.pptx"
    download_dir.mkdir(parents=True, exist_ok=True)
    download_path = download_dir / file_name
    errors = []

    for attempt in range(1, retries + 1):
        try:
            urlretrieve(href, download_path)
            if download_path.exists() and download_path.stat().st_size > 0:
                print("PPT 다운로드 완료:", download_path)
                return download_path

            print(f"다운로드 실패({attempt}/{retries}): 다운로드 파일 크기가 0입니다.")
            errors.append(f"{attempt}/{retries}: 다운로드 파일 크기가 0입니다.")
        except Exception as download_error:
            print(f"다운로드 실패({attempt}/{retries}): {download_error}")
            errors.append(
                f"{attempt}/{retries}: {type(download_error).__name__}: {download_error}"
            )

        time.sleep(delay_seconds)

    raise AssertionError(
        "PPT 다운로드에 실패했습니다.\n"
        f"재시도 횟수: {retries}, 대기 간격(초): {delay_seconds}\n"
        "실패 내역:\n"
        + "\n".join(errors)
    )


# 다운로드된 PPT의 슬라이드 수 및 섹션 수를 검증하는 헬퍼
def _verify_slide_count(ppt_file_path, expected_slide_count, expected_section_count):
    logger.info(
        "verify_slide_count_start file=%s expected_slides=%s expected_sections=%s",
        ppt_file_path,
        expected_slide_count,
        expected_section_count,
    )

    with ZipFile(ppt_file_path) as zf:
        presentation_xml = zf.read("ppt/presentation.xml")

    root = ET.fromstring(presentation_xml)
    actual_slide_count = len(root.findall("./p:sldIdLst/p:sldId", NS))

    presentation = Presentation(str(ppt_file_path))
    actual_section_count = sum(
        1
        for slide in presentation.slides
        if (slide.slide_layout.name or "").strip().lower() == "section_title"
    )
    logger.info(
        "verify_slide_count_actual actual_slides=%s actual_sections=%s",
        actual_slide_count,
        actual_section_count,
    )

    errors = []

    if actual_slide_count != expected_slide_count:
        logger.error(
            "slide_count_mismatch expected=%s actual=%s",
            expected_slide_count,
            actual_slide_count,
        )
        errors.append(
            f"슬라이드 수 불일치 expected={expected_slide_count}, actual={actual_slide_count}"
        )

    if actual_section_count != expected_section_count:
        logger.error(
            "section_count_mismatch expected=%s actual=%s",
            expected_section_count,
            actual_section_count,
        )
        errors.append(
            f"섹션 수 불일치 expected={expected_section_count}, actual={actual_section_count}"
        )

    if errors:
        raise AssertionError("\n".join(errors))

    logger.info("verify_slide_count_pass")
    return actual_slide_count, actual_section_count


# =========================
# PPT 생성 및 다운로드 파일의 슬라이드 수와 섹션 수가 요청값과 일치하는지 검증
# =========================
@pytest.mark.xfail(reason="PPT 생성 도구의 불안정성으로 인해 현재 PPT 슬라이드 수 불일치 버그 존재")
def test_ppt_create(logged_in_driver, wait, testlog):
    driver = logged_in_driver

    # ==========
    # Arrange
    # ==========
    # 도구 메뉴에서 PPT 생성 페이지로 진입
    _click(driver, *MENU_TOOLS)
    _click(driver, *PPT_CREATE_MENU)
    testlog.arrange("tool_page_opened")

    # 생성 조건 입력
    _type_text(driver, *TOPIC_INPUT, PPT_TOPIC)
    _type_text(driver, *INSTRUCTIONS_INPUT, PPT_INSTRUCTIONS)
    _type_text(driver, *SLIDES_COUNT_INPUT, str(EXPECTED_SLIDE_COUNT))
    _type_text(driver, *SECTION_COUNT_INPUT, str(EXPECTED_SECTION_COUNT))
    testlog.arrange(
        "ppt_form_filled",
        expected_slide_count=EXPECTED_SLIDE_COUNT,
        expected_section_count=EXPECTED_SECTION_COUNT,
    )

    # 심플조사 모드가 선택되어 있으면 해제
    simple_mode_checkbox = driver.find_element(*SIMPLE_MODE_CHECKBOX)
    if simple_mode_checkbox and simple_mode_checkbox.is_selected():
        simple_mode_checkbox.click()

    # ==========
    # Act
    # ==========
    _submit_ppt_generation(wait, testlog)
    print("PPT 생성 시작")

    # ==========
    # Assert
    # ==========
    # 생성 결과 다운로드 링크가 노출되는지 확인
    ppt_link = _wait_for_ppt_link(driver)
    testlog.assert_(
        "ppt_link_ready",
        expected=True,
        actual=(".pptx" in (ppt_link or "")),
        href=ppt_link,
    )

    # 결과 파일이 정상적으로 다운로드되는지 확인
    downloaded_ppt = _download_with_retry(
        ppt_link,
        DOWNLOAD_DIR,
    )

    # 다운로드된 PPT의 슬라이드 수 및 섹션 수가 요청값과 일치하는지 확인
    actual_slide_count, actual_section_count = _verify_slide_count(
        downloaded_ppt,
        EXPECTED_SLIDE_COUNT,
        EXPECTED_SECTION_COUNT,
    )
    testlog.assert_(
        "ppt_file_verified",
        expected=True,
        actual=(
            actual_slide_count == EXPECTED_SLIDE_COUNT
            and actual_section_count == EXPECTED_SECTION_COUNT
        ),
        downloaded_ppt=str(downloaded_ppt),
        expected_slide_count=EXPECTED_SLIDE_COUNT,
        actual_slide_count=actual_slide_count,
        expected_section_count=EXPECTED_SECTION_COUNT,
        actual_section_count=actual_section_count,
    )