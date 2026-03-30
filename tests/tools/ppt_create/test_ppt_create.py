import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from pptx import Presentation

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}

# 주어진 locator가 보일 때까지 기다린 뒤 요소를 반환한다.
def find(driver, by, value):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, value))
    )

# 주어진 locator가 클릭 가능해질 때까지 기다린 뒤 클릭한다.
def click(driver, by, value):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    ).click()

# 입력 필드를 비운 후 새 텍스트를 입력한다.
def type_text(driver, by, value, text):
    element = find(driver, by, value)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def wait_for_ppt_link(driver, timeout_seconds=600, poll_interval=10):
    """
    생성 결과 다운로드 링크가 제한 시간 내 .pptx로 준비되는지 검증한다.
    시간 내 링크가 준비되지 않으면 AssertionError를 발생시킨다.
    """
    # poll_interval(초) 간격으로 최대 timeout_seconds // poll_interval회 확인한다.
    for i in range(timeout_seconds // poll_interval):
        time.sleep(poll_interval)

        try:
            download_link = driver.find_element(
                By.XPATH, "//a[contains(., '생성 결과 다운받기')]"
            )
            href = download_link.get_attribute("href")
            print(f"{(i+1)*poll_interval}초 경과 - 현재 href: {href}")

            if href and ".pptx" in href:
                print("PPT 생성 완료")
                print("다운로드 링크:", href)
                return href
        except:
            print(f"{(i+1)*poll_interval}초 경과 - 아직 생성 중...")

    raise AssertionError("PPT 링크가 제한 시간 내 생성되지 않았습니다.")


def download_with_retry(href, download_dir, retries=5, delay_seconds=3):
    """
    생성된 PPT 파일이 실제로 정상 다운로드되는지 검증한다.
    모든 시도 실패 시 누적된 실패 내역과 함께 AssertionError를 발생시킨다.
    """
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


def verify_slide_count(ppt_file_path, expected_slide_count, expected_section_count):
    """
    다운로드된 PPT의 슬라이드 수와 섹션 수가 기대값과 일치하는지 검증한다.
    presentation.xml 기반 슬라이드 수와 section_title 레이아웃 기반 섹션 수를 계산하고,
    불일치 항목을 누적해 하나라도 다르면 AssertionError를 발생시킨다.
    """
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

    errors = []
    if actual_slide_count != expected_slide_count:
        errors.append(
            f"슬라이드 수 불일치: expected={expected_slide_count}, actual={actual_slide_count}"
        )
    if actual_section_count != expected_section_count:
        errors.append(
            f"섹션 수 불일치: expected={expected_section_count}, actual={actual_section_count}"
        )

    if errors:
        raise AssertionError("\n".join(errors))

@pytest.mark.xfail(reason="PPT 생성 도구의 불안정성으로 인해 현재 PPT 슬라이드 수 불일치 버그 존재")
def test_ppt_create(logged_in_driver, wait):
    driver = logged_in_driver
    expected_slide_count = 10
    expected_section_count = 3

    # =========================
    # Arrange
    # =========================

    # 도구 → PPT 생성
    click(driver, By.XPATH, "//span[text()='도구']")
    click(driver, By.XPATH, "//p[text()='PPT 생성']")

    # 입력
    type_text(driver, By.NAME, "topic", "이미지 AI의 최신 트렌드와 전망")
    type_text(driver, By.NAME, "instructions", "2025년 기준으로 만들어줘")
    type_text(driver, By.NAME, "slides_count", str(expected_slide_count))
    type_text(driver, By.NAME, "section_count", str(expected_section_count))

    # 심층조사 모드 체크 해제
    simple_mode_checkboxes = driver.find_element(By.NAME, "simple_mode")
    if simple_mode_checkboxes and simple_mode_checkboxes.is_selected():
        simple_mode_checkboxes.click()

    # =========================
    # Act
    # =========================

    # 버튼 텍스트에 따라 다르게 처리
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    submit_button_text = submit_button.text.strip()

    if submit_button_text == "다시 생성":
        submit_button.click()
        modal = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='presentation']"))
        )
        modal.find_element(By.XPATH, ".//button[contains(.,'다시 생성')]").click()
    else:
        submit_button.click()

    print("PPT 생성 시작")

    # =========================
    # Assert
    # =========================

    # 1) 생성 완료 신호: 결과 다운로드 링크(.pptx)가 노출되는지 확인
    ppt_link = wait_for_ppt_link(driver)

    # 2) 결과물 유효성: PPT 파일이 실제로 다운로드되는지 확인
    downloaded_ppt = download_with_retry(
        ppt_link, Path("tests/tools/ppt_create/downloads")
    )

    # 3) 산출물 내용 검증: 요청한 슬라이드 수/섹션 수와 일치하는지 확인
    verify_slide_count(downloaded_ppt, expected_slide_count, expected_section_count)
