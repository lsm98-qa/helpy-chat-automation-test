import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.agent_locators import AGENT_MY_AGENTS_BUTTON
from locators.agent_create_locators import AGENT_NAME_INPUT


AGENT_LIST_CONTAINER = (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
AGENT_ITEMS_XPATH = "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]"
AGENT_CARD_LINK_SELECTOR = "a[href*='/ai-helpy-chat/agents/']"
DRAFT_CHIP_XPATH = ".//span[contains(@class,'MuiChip-label') and normalize-space()='초안']"
AGENT_TITLE_IN_ITEM_XPATH = ".//p[contains(@class, 'MuiTypography-noWrap')]"
CHAT_INPUT = (By.NAME, "input")


# 에이전트 탐색 페이지에서 내 에이전트 페이지로 이동한다.
def _go_to_my_agents(wait):
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))


# 내 에이전트 카드 리스트가 로드될 때까지 기다린 뒤 카드 목록을 반환한다.
def _get_agent_items(driver, wait):
    wait.until(EC.presence_of_element_located(AGENT_LIST_CONTAINER))
    return driver.find_elements(By.XPATH, AGENT_ITEMS_XPATH)


# href에서 에이전트 ID를 추출한다.
def _extract_agent_id_from_href(href):
    marker = "/ai-helpy-chat/agents/"
    if marker not in href:
        return None
    return href.split(marker, 1)[1].split("/", 1)[0]


# 카드에서 제목/링크/ID를 추출한다.
def _extract_agent_meta_from_item(item):
    title_elements = item.find_elements(By.XPATH, AGENT_TITLE_IN_ITEM_XPATH)
    card_links = item.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR)

    if not card_links:
        return None

    title = (title_elements[0].text or "").strip() if title_elements else ""
    href = card_links[0].get_attribute("href")
    agent_id = _extract_agent_id_from_href(href)

    if not agent_id:
        return None

    return {
        "title": title,
        "href": href,
        "agent_id": agent_id,
    }


# 상태 조건에 맞는 첫 카드(초안/저장 완료)를 찾는다.
def _find_first_agent_item_by_status(agent_items, status):
    for item in agent_items:
        meta = _extract_agent_meta_from_item(item)
        if not meta:
            continue

        is_draft = bool(item.find_elements(By.XPATH, DRAFT_CHIP_XPATH)) or meta["href"].endswith("/builder")

        if status == "draft" and is_draft:
            return item, meta
        if status == "saved" and not is_draft:
            return item, meta

    return None, None


# 목록 페이지로 복귀한다.
def _return_to_my_agents(driver, wait):
    driver.back()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    wait.until(EC.presence_of_element_located(AGENT_LIST_CONTAINER))


# =========================
# 초안 에이전트 클릭 시 에이전트 만들기(편집) 페이지로 이동하는지 테스트
# =========================
def test_click_draft_agent_navigates_to_agent_edit_page(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)

    agent_items = _get_agent_items(driver, wait)
    draft_item, draft_meta = _find_first_agent_item_by_status(agent_items, "draft")

    if not draft_item or not draft_meta:
        pytest.skip("초안 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    draft_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()

    # ==========
    # Assert
    # ==========
    expected_path = f"/ai-helpy-chat/agents/{draft_meta['agent_id']}/builder"
    wait.until(EC.url_contains(expected_path))

    assert expected_path in driver.current_url, "초안 에이전트 클릭 후 편집 페이지 URL이 올바르지 않습니다."
    agent_name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    assert agent_name_input.is_displayed(), "편집 페이지에서 에이전트 이름 입력 필드가 표시되지 않습니다."


# =========================
# 저장 완료 에이전트 클릭 시 에이전트 채팅 페이지로 이동하는지 테스트
# =========================
def test_click_saved_agent_navigates_to_agent_chat_page(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)

    agent_items = _get_agent_items(driver, wait)
    saved_item, saved_meta = _find_first_agent_item_by_status(agent_items, "saved")

    if not saved_item or not saved_meta:
        pytest.skip("저장 완료 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    saved_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()

    # ==========
    # Assert
    # ==========
    expected_path = f"/ai-helpy-chat/agents/{saved_meta['agent_id']}"
    wait.until(EC.url_contains(expected_path))

    assert expected_path in driver.current_url, "저장 완료 에이전트 클릭 후 URL이 선택한 에이전트와 일치하지 않습니다."
    assert "/builder" not in driver.current_url, "저장 완료 에이전트가 편집(builder) 페이지로 이동했습니다."

    chat_input = wait.until(EC.presence_of_element_located(CHAT_INPUT))
    assert chat_input.is_displayed(), "저장 완료 에이전트 클릭 후 채팅 입력창이 표시되지 않습니다."

    if saved_meta["title"]:
        assert saved_meta["title"] in driver.find_element(By.TAG_NAME, "body").text, (
            "채팅 페이지에서 선택한 저장 완료 에이전트 정보(제목)가 확인되지 않습니다."
        )


# =========================
# 상태(초안/저장 완료)에 따라 라우팅이 서로 다르게 동작하는지 테스트
# =========================
def test_agent_click_routing_differs_by_status(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)

    agent_items = _get_agent_items(driver, wait)
    draft_item, draft_meta = _find_first_agent_item_by_status(agent_items, "draft")

    if not draft_item or not draft_meta:
        pytest.skip("초안 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    draft_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()
    draft_expected_path = f"/ai-helpy-chat/agents/{draft_meta['agent_id']}/builder"
    wait.until(EC.url_contains(draft_expected_path))
    draft_url = driver.current_url

    _return_to_my_agents(driver, wait)

    refreshed_items = _get_agent_items(driver, wait)
    saved_item, saved_meta = _find_first_agent_item_by_status(refreshed_items, "saved")

    if not saved_item or not saved_meta:
        pytest.skip("저장 완료 상태 에이전트를 찾지 못했습니다.")

    saved_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()
    saved_expected_path = f"/ai-helpy-chat/agents/{saved_meta['agent_id']}"
    wait.until(EC.url_contains(saved_expected_path))
    saved_url = driver.current_url

    # ==========
    # Assert
    # ==========
    assert "/builder" in draft_url, "초안 에이전트가 편집(builder) 페이지로 이동하지 않았습니다."
    assert "/builder" not in saved_url, "저장 완료 에이전트가 편집(builder) 페이지로 이동했습니다."
    assert draft_url != saved_url, "초안/저장 완료 에이전트의 라우팅 결과 URL이 동일합니다."

    chat_input = wait.until(EC.presence_of_element_located(CHAT_INPUT))
    assert chat_input.is_displayed(), "저장 완료 에이전트 라우팅 결과에서 채팅 입력창이 표시되지 않습니다."
