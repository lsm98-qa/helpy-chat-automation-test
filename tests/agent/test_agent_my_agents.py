import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

AGENT_LIST_CONTAINER = (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
AGENT_ITEMS_XPATH = "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]"
AGENT_CARD_LINK_SELECTOR = "a[href*='/ai-helpy-chat/agents/']"
DELETE_CONFIRM_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
DELETE_CONFIRM_BUTTON_XPATH = ".//button[normalize-space()='삭제']"


# 에이전트 탐색 페이지에서 내 에이전트 페이지로 이동한다.
def _go_to_my_agents(wait):
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))


# 내 에이전트 카드 리스트가 로드될 때까지 기다린 뒤 카드 목록을 반환한다.
def _get_agent_items(driver, wait):
    wait.until(EC.presence_of_element_located(AGENT_LIST_CONTAINER))
    return driver.find_elements(By.XPATH, AGENT_ITEMS_XPATH)


# 에이전트 상세 링크 href에서 에이전트 ID를 추출한다.
def _extract_agent_id_from_href(href):
    marker = "/ai-helpy-chat/agents/"
    if marker not in href:
        return None
    return href.split(marker, 1)[1].split("/", 1)[0]


# 카드 요소에서 링크를 찾아 에이전트 ID를 추출한다.
def _extract_agent_id_from_item(item):
    card_links = item.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR)
    if not card_links:
        return None

    href = card_links[0].get_attribute("href")
    return _extract_agent_id_from_href(href)


# 카드 목록에서 지정한 아이콘(예: pen, trash) 버튼이 있는 첫 카드를 찾는다.
def _find_first_icon_button(agent_items, icon_name):
    selector = f"button:has(svg[data-icon='{icon_name}'])"
    for item in agent_items:
        buttons = item.find_elements(By.CSS_SELECTOR, selector)
        if buttons:
            return item, buttons[0]
    return None, None


# 삭제 확인 모달에서 '삭제' 버튼을 눌러 삭제를 확정한다.
def _click_delete_confirm(wait):
    dialog = wait.until(EC.visibility_of_element_located(DELETE_CONFIRM_DIALOG))
    confirm_delete_button = dialog.find_element(By.XPATH, DELETE_CONFIRM_BUTTON_XPATH)
    wait.until(EC.element_to_be_clickable(confirm_delete_button)).click()
    return dialog


# =========================
# 내 에이전트 페이지 진입 테스트
# =========================
def test_navigate_to_my_agents(navigate_to_agent_explore, wait): 
    # ==========
    # Arrange
    # ==========
    _ = navigate_to_agent_explore
    
    # ==========
    # Act
    # ==========
    _go_to_my_agents(wait)
    
    # ==========
    # Assert
    # ==========
    my_agents_title = wait.until(EC.visibility_of_element_located(MENU_H6_TITLE))

    assert my_agents_title.text == "내 에이전트"

# =========================
# 에이전트 탐색 -> 내 에이전트 페이지에서 뒤로가기 버튼 테스트
# =========================
def test_navigate_back_to_agent_explore(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    _ = navigate_to_agent_explore
    _go_to_my_agents(wait)
    
    # ==========
    # Act
    # ==========
    # 뒤로가기 버튼으로 에이전트 탐색 페이지 복귀 동작 수행
    wait.until(EC.element_to_be_clickable(AGENT_BACK_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    
    # ==========
    # Assert
    # ==========
    agent_title = wait.until(EC.visibility_of_element_located(MENU_H2_TITLE))

    assert agent_title.text == "에이전트 탐색"

# =========================
# 내 에이전트 페이지의 각 에이전트 카드의 수정 버튼이 표시되는지 테스트
# =========================
def test_each_agent_card_shows_edit_button(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)

    # ==========
    # Act
    # ==========
    # 내 에이전트 목록에서 카드 리스트 조회
    agent_items = _get_agent_items(driver, wait)

    # ==========
    # Assert
    # ==========
    if not agent_items:
        pytest.skip("수정 버튼 노출 여부를 검증할 에이전트 카드가 없습니다.")

    for idx, item in enumerate(agent_items, start=1):
        # 각 카드에서 수정 아이콘 버튼 존재 여부 확인
        edit_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='pen'])",
        )
        assert len(edit_buttons) > 0, f"{idx}번째 에이전트 카드에 수정 버튼이 표시되지 않습니다."

# =========================
# 내 에이전트 페이지의 각 에이전트 카드의 삭제 버튼이 표시되는지 테스트
# =========================
def test_each_agent_card_shows_delete_button(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)

    # ==========
    # Act
    # ==========
    # 내 에이전트 목록에서 카드 리스트 조회
    agent_items = _get_agent_items(driver, wait)

    # ==========
    # Assert
    # ==========
    if not agent_items:
        pytest.skip("삭제 버튼 노출 여부를 검증할 에이전트 카드가 없습니다.")

    for idx, item in enumerate(agent_items, start=1):
        # 각 카드에서 삭제 아이콘 버튼 존재 여부 확인
        delete_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='trash'])",
        )
        assert len(delete_buttons) > 0, f"{idx}번째 에이전트 카드에 삭제 버튼이 표시되지 않습니다."


# =========================
# 수정 버튼 클릭 시 해당 에이전트의 수정 페이지로 이동하는지 테스트
# =========================
def test_click_edit_button_navigates_to_edit_page(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)
    agent_items = _get_agent_items(driver, wait)

    if not agent_items:
        pytest.skip("수정 페이지 이동을 검증할 에이전트 카드가 없습니다.")

    target_item = None
    target_agent_id = None

    # 수정 버튼 클릭 검증에 사용할 "유효한 카드 1개"를 찾는다.
    # 조건: 카드 링크와 수정 버튼이 모두 존재해야 한다.
    for item in agent_items:
        card_links = item.find_elements(By.CSS_SELECTOR, AGENT_CARD_LINK_SELECTOR)
        edit_buttons = item.find_elements(By.CSS_SELECTOR, "button:has(svg[data-icon='pen'])")

        # 링크/수정 버튼 중 하나라도 없으면 대상 카드에서 제외한다.
        if not card_links or not edit_buttons:
            continue

        # 카드 링크에서 에이전트 ID를 추출해 클릭 후 이동 URL 검증에 사용한다.
        href = card_links[0].get_attribute("href")
        target_agent_id = _extract_agent_id_from_href(href)
        if not target_agent_id:
            continue

        target_item = item
        # 첫 유효 카드 1개만 확보하면 충분하므로 반복을 종료한다.
        break

    if not target_item or not target_agent_id:
        pytest.skip("수정 버튼 클릭 검증이 가능한 에이전트 카드를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    # 대상 카드의 수정 버튼 클릭
    edit_button = target_item.find_element(
        By.CSS_SELECTOR,
        "button:has(svg[data-icon='pen'])",
    )

    wait.until(EC.element_to_be_clickable(edit_button)).click()

    # ==========
    # Assert
    # ==========
    expected_path = f"/ai-helpy-chat/agents/{target_agent_id}/builder"
    wait.until(EC.url_contains(expected_path))
    assert expected_path in driver.current_url, "수정 페이지 URL이 선택한 에이전트와 일치하지 않습니다."


# =========================
# 삭제 버튼 클릭 시 확인 모달이 정상적으로 시작되는지 테스트
# =========================
def test_click_delete_button_opens_delete_confirmation_modal (navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)
    agent_items = _get_agent_items(driver, wait)

    if not agent_items:
        pytest.skip("삭제 버튼 클릭 동작을 검증할 에이전트 카드가 없습니다.")

    _, target_delete_button = _find_first_icon_button(agent_items, "trash")

    if not target_delete_button:
        pytest.skip("삭제 버튼이 있는 에이전트 카드를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    # 삭제 버튼 클릭으로 확인 모달 오픈
    wait.until(EC.element_to_be_clickable(target_delete_button)).click()

    # ==========
    # Assert
    # ==========
    dialog = wait.until(EC.visibility_of_element_located(DELETE_CONFIRM_DIALOG))
    assert dialog.is_displayed(), "삭제 확인 모달이 표시되지 않습니다."
    assert "에이전트 삭제" in dialog.text, "삭제 확인 모달 제목이 올바르지 않습니다."
    assert "취소" in dialog.text and "삭제" in dialog.text, "삭제 확인 모달 버튼이 표시되지 않습니다."


# =========================
# 삭제 수행 후 해당 에이전트가 목록에서 사라지는지 테스트
# =========================
def test_deleted_agent_is_removed_from_list(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)
    agent_items = _get_agent_items(driver, wait)

    if not agent_items:
        pytest.skip("삭제 동작을 검증할 에이전트 카드가 없습니다.")

    target_agent_id = None
    target_delete_button = None

    for item in agent_items:
        _, delete_button = _find_first_icon_button([item], "trash")
        if not delete_button:
            continue

        agent_id = _extract_agent_id_from_item(item)
        if not agent_id:
            continue

        target_agent_id = agent_id
        target_delete_button = delete_button
        break

    if not target_agent_id or not target_delete_button:
        pytest.skip("삭제 가능한 에이전트 카드를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    # 삭제 버튼 클릭 후 확인 모달에서 삭제 확정
    wait.until(EC.element_to_be_clickable(target_delete_button)).click()
    _click_delete_confirm(wait)

    # ==========
    # Assert
    # ==========
    target_agent_link_selector = f"a[href*='/ai-helpy-chat/agents/{target_agent_id}']"
    wait.until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, target_agent_link_selector)) == 0
    )
    remaining_links = driver.find_elements(By.CSS_SELECTOR, target_agent_link_selector)
    assert len(remaining_links) == 0, (
        f"삭제 후에도 대상 에이전트({target_agent_id})가 목록에 남아 있습니다."
    )


# =========================
# 삭제 수행 후 성공 토스트가 표시되는지 테스트
# =========================
def test_delete_agent_shows_success_toast(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    _go_to_my_agents(wait)
    agent_items = _get_agent_items(driver, wait)

    if not agent_items:
        pytest.skip("삭제 동작을 검증할 에이전트 카드가 없습니다.")

    _, target_delete_button = _find_first_icon_button(agent_items, "trash")

    if not target_delete_button:
        pytest.skip("삭제 버튼이 있는 에이전트 카드를 찾지 못했습니다.")

    # ==========
    # Act
    # ==========
    # 삭제 버튼 클릭 후 확인 모달에서 삭제 확정
    wait.until(EC.element_to_be_clickable(target_delete_button)).click()
    _click_delete_confirm(wait)

    # ==========
    # Assert
    # ==========
    toast_message = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div[role='alert'] #notistack-snackbar")
        )
    )
    assert toast_message.is_displayed(), "삭제 성공 토스트가 표시되지 않습니다."
    assert "에이전트가 삭제되었습니다." in toast_message.text, "삭제 성공 토스트 문구가 올바르지 않습니다."

