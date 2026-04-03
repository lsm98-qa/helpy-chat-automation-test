from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 요소가 화면에 표시될 때까지 기다린 뒤 반환하는 헬퍼
def _find(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


# 요소가 클릭 가능할 때까지 기다린 뒤 클릭하는 헬퍼
def _click(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    ).click()


# 입력 필드를 비운 뒤 새 텍스트를 입력하는 헬퍼
def _type_text(driver, by, value, text, timeout=10):
    element = _find(driver, by, value, timeout)
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)
    return element


# 심층 조사 페이지로 진입하는 헬퍼
def _go_to_deep_research_page(driver):
    _click(driver, By.XPATH, "//span[text()='도구']")
    _click(driver, By.XPATH, "//p[text()='심층 조사']")


# 심층 조사 입력값을 채우는 헬퍼
def _fill_deep_research_form(driver, topic, instructions):
    topic_input = _type_text(driver, By.NAME, "topic", topic)
    instructions_input = _type_text(driver, By.NAME, "instructions", instructions)

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.NAME, "topic").get_attribute("value").strip() == topic
    )
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.NAME, "instructions").get_attribute("value").strip() == instructions
    )

    # 마지막 입력 필드에서 blur가 발생하도록 탭 이동
    instructions_input.send_keys(Keys.TAB)

# 심층 조사 결과 본문 영역을 찾는 헬퍼
def _find_result_content(driver, timeout=600):
    return WebDriverWait(driver, timeout, poll_frequency=5).until(
        lambda d: _get_result_text(d)
    )


# 심층 조사 결과 텍스트를 반환하는 헬퍼
def _get_result_text(driver):
    candidates = driver.find_elements(
        By.XPATH,
        "//main//*[self::h1 or self::h2 or self::h3 or self::p or self::div][normalize-space()]",
    )

    texts = []
    for candidate in candidates:
        text = candidate.text.strip()
        if len(text) >= 20:
            texts.append(text)

    if not texts:
        return False

    merged_text = "\n".join(texts)
    return merged_text if merged_text.strip() else False
