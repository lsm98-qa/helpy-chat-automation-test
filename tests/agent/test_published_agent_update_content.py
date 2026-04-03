from datetime import datetime

from tests.agent.agent_update_helpers import (
    click_save,
    find_agent_card_by_id,
    get_card_title,
    open_saved_agent_builder,
    return_to_my_agents_from_builder,
    update_agent_name,
    wait_for_save_feedback,
)


# =========================
# 게시된 에이전트 이름 수정 후 목록 반영/유지 여부 확인
# =========================
def test_update_published_agent_name_reflects_in_ui(navigate_to_agent_explore, wait):
    # ==========
    # Arrange
    # ==========
    driver = navigate_to_agent_explore
    agent_id, old_name = open_saved_agent_builder(driver, wait)
    new_name = f"published-agent-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # ==========
    # Act
    # ==========
    update_agent_name(wait, new_name)
    click_save(wait)
    wait_for_save_feedback(driver, wait)
    return_to_my_agents_from_builder(driver, wait)

    # ==========
    # Assert
    # ==========
    updated_card = find_agent_card_by_id(driver, wait, agent_id)
    updated_title = get_card_title(updated_card)
    assert updated_title == new_name, (
        "수정 후 목록 카드 제목이 변경값과 일치하지 않습니다. "
        f"expected={new_name}, actual={updated_title}"
    )
