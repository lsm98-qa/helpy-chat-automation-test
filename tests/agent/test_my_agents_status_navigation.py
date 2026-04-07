import pytest
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.agent_locators import AGENT_MY_AGENTS_BUTTON
from locators.agent_create_locators import AGENT_NAME_INPUT


AGENT_LIST_CONTAINER = (By.XPATH, "//*[@data-testid='virtuoso-item-list']")
AGENT_LIST_SCROLLER = (By.XPATH, "//div[@data-testid='virtuoso-scroller']")
AGENT_ITEMS_XPATH = "./*[@data-item-index or @data-index]"
AGENT_CARD_LINK_SELECTOR = "a[href*='/ai-helpy-chat/agents/']"
SAVED_AGENT_LINK_XPATH = (
    "//a[contains(@href,'/ai-helpy-chat/agents/') and not(contains(@href,'/builder'))]"
)
DRAFT_CHIP_XPATH = ".//span[contains(@class,'MuiChip-label') and normalize-space()='초안']"
STATUS_CHIP_LABELS_XPATH = ".//span[contains(@class,'MuiChip-label')]"
AGENT_TITLE_IN_ITEM_XPATH = ".//p[contains(@class, 'MuiTypography-noWrap')]"
CHAT_INPUT = (By.NAME, "input")


# 에이전트 탐색 페이지에서 내 에이전트 페이지로 이동한다.
def _go_to_my_agents(wait):
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))


# 내 에이전트 카드 리스트가 로드될 때까지 기다린 뒤 카드 목록을 반환한다.
def _get_agent_items(driver, wait):
    last_error = None
    for _ in range(5):
        try:
            container = _wait_for_agent_list_container(driver, wait)
            try:
                wait.until(lambda d: len(container.find_elements(By.XPATH, AGENT_ITEMS_XPATH)) > 0)
            except TimeoutException:
                return []
            return container.find_elements(By.XPATH, AGENT_ITEMS_XPATH)
        except StaleElementReferenceException as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    return []


def _scroll_my_agents_list_one_page(driver, wait):
    scroller = _get_active_scroll_container(driver, wait)
    previous_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
        scroller,
    )
    current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
    reached_bottom = driver.execute_script(
        "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
        scroller,
    )
    return previous_scroll_top, current_scroll_top, reached_bottom


def _get_visible_item_indexes(driver):
    items = _get_agent_items(driver, WebDriverWait(driver, 2))
    indexes = []
    for item in items:
        idx = _safe_int(_extract_item_index(item), default=-1)
        if idx >= 0:
            indexes.append(idx)
    return indexes


def _scroll_scroller_and_wait_update(driver, wait):
    scroller = _get_active_scroll_container(driver, wait)
    previous_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
    previous_indexes = _get_visible_item_indexes(driver)

    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollTop + Math.max(arguments[0].clientHeight * 0.9, 240);",
        scroller,
    )

    try:
        wait.until(
            lambda d: (
                driver.execute_script("return arguments[0].scrollTop;", scroller) > previous_scroll_top
                or _get_visible_item_indexes(driver) != previous_indexes
                or driver.execute_script(
                    "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
                    scroller,
                )
            )
        )
    except TimeoutException:
        pass

    current_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
    reached_bottom = driver.execute_script(
        "return arguments[0].scrollTop + arguments[0].clientHeight >= arguments[0].scrollHeight - 2;",
        scroller,
    )
    current_indexes = _get_visible_item_indexes(driver)
    return previous_scroll_top, current_scroll_top, reached_bottom, previous_indexes, current_indexes


def _find_agent_list_container_with_agents(driver):
    containers = driver.find_elements(*AGENT_LIST_CONTAINER)
    for container in containers:
        try:
            if container.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR):
                return container
        except StaleElementReferenceException:
            continue
    return None


def _wait_for_agent_list_scroller(wait):
    return wait.until(EC.presence_of_element_located(AGENT_LIST_SCROLLER))


def _wait_for_agent_list_container(driver, wait):
    wait.until(EC.presence_of_all_elements_located(AGENT_LIST_CONTAINER))
    container = wait.until(lambda d: _find_agent_list_container_with_agents(d))
    return container


def _get_active_scroll_container(driver, wait):
    # 전역에서 첫 스크롤러를 고르면 사이드바가 잡힐 수 있으므로,
    # 리스트 자신의 조상 체인에서만 스크롤 컨테이너를 찾는다(=본문 영역 우선).
    last_error = None
    for _ in range(5):
        try:
            list_container = _wait_for_agent_list_container(driver, wait)
            return driver.execute_script(
                """
                const list = arguments[0];
                const hasScrollableY = (el) => {
                  if (!el) return false;
                  const style = getComputedStyle(el);
                  const oy = style.overflowY;
                  return (oy === 'auto' || oy === 'scroll') && (el.scrollHeight - el.clientHeight > 2);
                };

                // list 자신/조상 중 실제 스크롤 가능한 가장 가까운 요소
                let el = list;
                while (el) {
                  if (hasScrollableY(el)) return el;
                  el = el.parentElement;
                }

                // fallback
                return list;
                """,
                list_container,
            )
        except StaleElementReferenceException as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    raise TimeoutException("활성 스크롤 컨테이너를 찾지 못했습니다.")


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


def _extract_status_texts_from_item(item):
    chips = item.find_elements(By.XPATH, STATUS_CHIP_LABELS_XPATH)
    return [(chip.text or "").strip() for chip in chips if (chip.text or "").strip()]


def _extract_item_index(item):
    return item.get_attribute("data-index") or item.get_attribute("data-item-index") or "unknown"


def _safe_int(value, default=-1):
    try:
        return int(value)
    except Exception:
        return default


def _classify_item_status(item, href: str):
    status_texts = _extract_status_texts_from_item(item)
    lowered = [text.lower() for text in status_texts]

    # 상태 칩 텍스트를 최우선으로 신뢰한다.
    if any("초안" in text for text in status_texts):
        return "draft", status_texts
    if any(("저장" in text) or ("완료" in text) or ("게시" in text) for text in status_texts):
        return "saved", status_texts
    if any(("public" in text) or ("private" in text) for text in lowered):
        return "saved", status_texts

    # 칩이 없을 때만 href를 fallback으로 사용한다.
    if "/builder" in href:
        return "draft", status_texts
    return "saved", status_texts


# 상태 조건에 맞는 첫 카드(초안/저장 완료)를 찾는다.
def _find_first_agent_item_by_status(agent_items, status):
    for idx, item in enumerate(agent_items, start=1):
        meta = _extract_agent_meta_from_item(item)
        if not meta:
            continue

        item_status, status_texts = _classify_item_status(item, meta["href"])

        if status == "draft" and item_status == "draft":
            return item, meta
        if status == "saved" and item_status == "saved":
            return item, meta

    return None, None


def _find_first_agent_item_by_status_with_scroll(driver, wait, status, max_scroll_pages=30):
    scroller = _get_active_scroll_container(driver, wait)
    driver.execute_script("arguments[0].scrollTop = 0;", scroller)
    seen_indexes = set()

    for page in range(max_scroll_pages):
        agent_items = _get_agent_items(driver, wait)
        visible_indexes = [_extract_item_index(item) for item in agent_items]
        seen_indexes.update(visible_indexes)
        target_item, target_meta = _find_first_agent_item_by_status(agent_items, status)
        if target_item and target_meta:
            return target_item, target_meta

        previous_scroll_top, current_scroll_top, reached_bottom = _scroll_my_agents_list_one_page(driver, wait)
        if reached_bottom or current_scroll_top <= previous_scroll_top:
            break

    return None, None


def _find_first_saved_agent_item_with_scroll(driver, wait, max_scroll_pages=60):
    scroller = _get_active_scroll_container(driver, wait)
    driver.execute_script("arguments[0].scrollTop = 0;", scroller)

    previous_scroll_top = -1
    for page in range(max_scroll_pages):
        saved_links = driver.find_elements(By.XPATH, SAVED_AGENT_LINK_XPATH)
        if saved_links:
            link = saved_links[0]
            href = link.get_attribute("href") or ""
            agent_id = _extract_agent_id_from_href(href)
            item = link.find_element(By.XPATH, "./ancestor::div[@data-item-index or @data-index][1]")
            title_elements = item.find_elements(By.XPATH, AGENT_TITLE_IN_ITEM_XPATH)
            title = (title_elements[0].text or "").strip() if title_elements else ""
            return item, {"title": title, "href": href, "agent_id": agent_id}

        (
            scrolled_from,
            scrolled_to,
            reached_bottom,
            indexes_before,
            indexes_after,
        ) = _scroll_scroller_and_wait_update(driver, wait)
        if reached_bottom or scrolled_to <= previous_scroll_top:
            break

        previous_scroll_top = scrolled_to

    return None, None


# 목록 페이지로 복귀한다.
def _return_to_my_agents(driver, wait):
    driver.back()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    _wait_for_agent_list_container(driver, wait)


# =========================
# 초안 에이전트 클릭 시 에이전트 만들기(편집) 페이지로 이동하는지 테스트
# =========================
def test_click_draft_agent_navigates_to_agent_edit_page(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    testlog.arrange("prepare_draft_agent_navigation_check")
    _go_to_my_agents(wait)

    draft_item, draft_meta = _find_first_agent_item_by_status_with_scroll(driver, wait, "draft")

    if not draft_item or not draft_meta:
        pytest.skip("초안 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    testlog.act("click_draft_agent_card")
    draft_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()

    # ==========
    # Assert
    # ==========
    expected_path = f"/ai-helpy-chat/agents/{draft_meta['agent_id']}/builder"
    wait.until(EC.url_contains(expected_path))
    testlog.assert_(
        "draft_agent_navigates_to_builder",
        expected=True,
        actual=(expected_path in driver.current_url),
        expected_path=expected_path,
    )

    assert expected_path in driver.current_url, "초안 에이전트 클릭 후 편집 페이지 URL이 올바르지 않습니다."
    agent_name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    assert agent_name_input.is_displayed(), "편집 페이지에서 에이전트 이름 입력 필드가 표시되지 않습니다."


# =========================
# 저장 완료 에이전트 클릭 시 에이전트 채팅 페이지로 이동하는지 테스트
# =========================
def test_click_saved_agent_navigates_to_agent_chat_page(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    testlog.arrange("prepare_saved_agent_navigation_check")
    _go_to_my_agents(wait)

    saved_item, saved_meta = _find_first_saved_agent_item_with_scroll(driver, wait)

    if not saved_item or not saved_meta:
        pytest.skip("저장 완료 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    testlog.act("click_saved_agent_card")
    saved_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()

    # ==========
    # Assert
    # ==========
    expected_path = f"/ai-helpy-chat/agents/{saved_meta['agent_id']}"
    wait.until(EC.url_contains(expected_path))
    is_saved_route_valid = expected_path in driver.current_url and "/builder" not in driver.current_url
    testlog.assert_(
        "saved_agent_navigates_to_chat_page",
        expected=True,
        actual=is_saved_route_valid,
        expected_path=expected_path,
    )

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
def test_agent_click_routing_differs_by_status(navigate_to_agent_explore, wait, testlog):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    testlog.arrange("prepare_status_based_routing_check")
    _go_to_my_agents(wait)

    draft_item, draft_meta = _find_first_agent_item_by_status_with_scroll(driver, wait, "draft")

    if not draft_item or not draft_meta:
        pytest.skip("초안 상태 에이전트를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    testlog.act("open_draft_then_saved_agent_and_compare_routes")
    draft_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()
    draft_expected_path = f"/ai-helpy-chat/agents/{draft_meta['agent_id']}/builder"
    wait.until(EC.url_contains(draft_expected_path))
    draft_url = driver.current_url

    _return_to_my_agents(driver, wait)

    saved_item, saved_meta = _find_first_agent_item_by_status_with_scroll(driver, wait, "saved")

    if not saved_item or not saved_meta:
        pytest.skip("저장 완료 상태 에이전트를 찾지 못했습니다.")

    saved_item.find_element(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR).click()
    saved_expected_path = f"/ai-helpy-chat/agents/{saved_meta['agent_id']}"
    wait.until(EC.url_contains(saved_expected_path))
    saved_url = driver.current_url

    # ==========
    # Assert
    # ==========
    routing_differs = ("/builder" in draft_url) and ("/builder" not in saved_url) and (draft_url != saved_url)
    testlog.assert_(
        "routing_differs_by_agent_status",
        expected=True,
        actual=routing_differs,
        draft_url=draft_url,
        saved_url=saved_url,
    )
    assert "/builder" in draft_url, "초안 에이전트가 편집(builder) 페이지로 이동하지 않았습니다."
    assert "/builder" not in saved_url, "저장 완료 에이전트가 편집(builder) 페이지로 이동했습니다."
    assert draft_url != saved_url, "초안/저장 완료 에이전트의 라우팅 결과 URL이 동일합니다."

