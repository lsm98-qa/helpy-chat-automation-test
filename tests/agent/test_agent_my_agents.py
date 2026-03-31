import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from locators.menu_locators import *
from locators.agent_locators import *

#==========
# 내 에이전트 페이지 진입 테스트
#==========
def test_navigate_to_my_agents(navigate_to_agent_explore, wait): 

    # Arrange
    driver = navigate_to_agent_explore
    
    # Act
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # Assert
    my_agents_title = wait.until(EC.visibility_of_element_located(MENU_H6_TITLE))

    assert my_agents_title.text == "내 에이전트"

#==========
# 뒤로가기 버튼 테스트
#==========
def test_navigate_back_to_agent_explore(navigate_to_agent_explore, wait):

    # Arrange
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    
    # Act
    wait.until(EC.element_to_be_clickable(AGENT_BACK_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    
    # Assert
    agent_title = wait.until(EC.visibility_of_element_located(MENU_H2_TITLE))

    assert agent_title.text == "에이전트 탐색"

#==========
# 내 에이전트 페이지의 각 에이전트 카드의 수정 버튼이 표시되는지 테스트
#==========
def test_each_agent_card_shows_edit_button(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
        )
    )

    # Act
    agent_items = driver.find_elements(
        By.XPATH,
        "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]",
    )

    # Assert
    if not agent_items:
        pytest.skip("수정 버튼 노출 여부를 검증할 에이전트 카드가 없습니다.")

    for idx, item in enumerate(agent_items, start=1):
        edit_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='pen'])",
        )
        assert len(edit_buttons) > 0, f"{idx}번째 에이전트 카드에 수정 버튼이 표시되지 않습니다."

#==========
# 내 에이전트 페이지의 각 에이전트 카드의 삭제 버튼이 표시되는지 테스트
#==========
def test_each_agent_card_shows_delete_button(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
        )
    )

    # Act
    agent_items = driver.find_elements(
        By.XPATH,
        "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]",
    )

    # Assert
    if not agent_items:
        pytest.skip("삭제 버튼 노출 여부를 검증할 에이전트 카드가 없습니다.")

    for idx, item in enumerate(agent_items, start=1):
        delete_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='trash'])",
        )
        assert len(delete_buttons) > 0, f"{idx}번째 에이전트 카드에 삭제 버튼이 표시되지 않습니다."


#==========
# 수정 버튼 클릭 시 해당 에이전트의 수정 페이지로 이동하는지 테스트
#==========
def test_click_edit_button_navigates_to_edit_page(navigate_to_agent_explore, wait):
    # Arrange
    driver = navigate_to_agent_explore

    wait.until(EC.element_to_be_clickable(AGENT_MY_AGENTS_BUTTON)).click()
    wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@data-testid='virtuoso-item-list']")
        )
    )

    agent_items = driver.find_elements(
        By.XPATH,
        "//div[@data-testid='virtuoso-item-list']/div[@data-item-index]",
    )

    if not agent_items:
        pytest.skip("수정 페이지 이동을 검증할 에이전트 카드가 없습니다.")

    target_item = None
    target_agent_id = None

    # 수정 버튼 클릭 검증에 사용할 "유효한 카드 1개"를 찾는다.
    # 조건: 카드 링크와 수정 버튼이 모두 존재해야 한다.
    for item in agent_items:
        card_links = item.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/ai-helpy-chat/agents/']",
        )
        edit_buttons = item.find_elements(
            By.CSS_SELECTOR,
            "button:has(svg[data-icon='pen'])",
        )

        # 링크/수정 버튼 중 하나라도 없으면 대상 카드에서 제외한다.
        if not card_links or not edit_buttons:
            continue

        # 카드 링크에서 에이전트 ID를 추출해 클릭 후 이동 URL 검증에 사용한다.
        href = card_links[0].get_attribute("href")
        marker = "/ai-helpy-chat/agents/"
        if marker not in href:
            continue

        target_agent_id = href.split(marker, 1)[1].split("/", 1)[0]
        target_item = item
        # 첫 유효 카드 1개만 확보하면 충분하므로 반복을 종료한다.
        break

    if not target_item or not target_agent_id:
        pytest.skip("수정 버튼 클릭 검증이 가능한 에이전트 카드를 찾지 못했습니다.")

    # Act
    edit_button = target_item.find_element(
        By.CSS_SELECTOR,
        "button:has(svg[data-icon='pen'])",
    )

    wait.until(EC.element_to_be_clickable(edit_button)).click()

    # Assert
    expected_path = f"/ai-helpy-chat/agents/{target_agent_id}/builder"
    wait.until(EC.url_contains(expected_path))
    assert expected_path in driver.current_url, "수정 페이지 URL이 선택한 에이전트와 일치하지 않습니다."
