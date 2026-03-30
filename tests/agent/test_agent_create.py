import pytest
from selenium.webdriver.support import expected_conditions as EC

from locators.agent_create_locators import (
    AGENT_CONVERSATION_STARTER_INPUTS,
    AGENT_DESCRIPTION_INPUT,
    AGENT_FILE_UPLOAD_INPUT,
    AGENT_FILE_UPLOAD_LABEL,
    AGENT_IMAGE_PLUS_BUTTON,
    AGENT_NAME_INPUT,
    AGENT_PREVIEW_PANEL_TITLE,
    AGENT_PURPOSE_COMBOBOX,
    AGENT_PURPOSE_INPUT,
    AGENT_SYSTEM_PROMPT_INPUT,
    AGENT_TOOL_CHECKBOXES,
)
from locators.agent_locators import AGENT_CREATE_BUTTON


@pytest.fixture
def navigate_to_agent_create(navigate_to_agent_explore, wait):
    driver = navigate_to_agent_explore
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_BUTTON)).click()
    wait.until(EC.url_contains('/ai-helpy-chat/agents'))
    wait.until(EC.url_contains('/builder'))
    return driver


# 좌측 폼 핵심 요소 렌더링 확인 스모크 테스트
# {이름, 한줄 소개, 카테고리, 규칙, 시작 대화, 파일 업로드, 기능 체크박스} 중 하나라도 렌더링 안되면 실패
def test_agent_create_form_core_elements_rendered(navigate_to_agent_create, wait):
    driver = navigate_to_agent_create

    # 에이전트 이미지 설정 (+ 버튼)
    plus_button = wait.until(EC.element_to_be_clickable(AGENT_IMAGE_PLUS_BUTTON))
    assert plus_button.is_displayed(), "에이전트 이미지 설정 '+' 버튼이 화면에 표시되지 않았습니다."

    # 이름
    name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    assert name_input.is_displayed(), "이름 입력창이 화면에 표시되지 않았습니다."
    assert name_input.is_enabled(), "이름 입력창이 비활성 상태입니다."

    # 한줄 소개 (name='description'인 input)
    description_input = wait.until(EC.visibility_of_element_located(AGENT_DESCRIPTION_INPUT))
    assert description_input.is_displayed(), "한줄 소개 입력창이 화면에 표시되지 않았습니다."
    assert description_input.is_enabled(), "한줄 소개 입력창이 비활성 상태입니다."

    # 카테고리 (role='combobox' + name='purpose' input)
    purpose_combobox = wait.until(EC.visibility_of_element_located(AGENT_PURPOSE_COMBOBOX))
    purpose_input = wait.until(EC.presence_of_element_located(AGENT_PURPOSE_INPUT))
    assert purpose_combobox.is_displayed(), "카테고리 콤보박스가 화면에 표시되지 않았습니다."

    # 규칙
    system_prompt_input = wait.until(EC.visibility_of_element_located(AGENT_SYSTEM_PROMPT_INPUT))
    assert system_prompt_input.is_displayed(), "규칙 입력창이 화면에 표시되지 않았습니다."

    # 시작 대화: 초기 진입 시 1개만 노출되고 index 0 이어야 함
    starter_inputs = wait.until(
        lambda d: d.find_elements(*AGENT_CONVERSATION_STARTER_INPUTS) or False
    )
    assert len(starter_inputs) == 1, (
        f"시작 대화 입력창 개수가 1개가 아닙니다. actual={len(starter_inputs)}"
    )
    assert starter_inputs[0].is_displayed(), "시작 대화 입력창(conversationStarters.0.value)이 표시되지 않았습니다."
    assert starter_inputs[0].get_attribute('name') == 'conversationStarters.0.value', (
        "시작 대화 입력창 name 값이 예상과 다릅니다. "
        f"actual={starter_inputs[0].get_attribute('name')}"
    )

    # 파일 업로드: label 가시성 + file input 존재를 속성 기반으로 확인
    file_upload_label = wait.until(EC.visibility_of_element_located(AGENT_FILE_UPLOAD_LABEL))
    file_input = wait.until(EC.presence_of_element_located(AGENT_FILE_UPLOAD_INPUT))
    assert file_upload_label.is_displayed(), "파일 업로드 라벨 영역이 화면에 표시되지 않았습니다."
    assert file_input.get_attribute("type") == "file", (
        "파일 업로드 input 타입이 file이 아닙니다. "
        f"actual={file_input.get_attribute('type')}"
    )

    # 기능 체크박스: 섹션 타이틀 텍스트 없이 toolIds 4종(value)로 확인
    expected_tool_values = {
        "web_search",
        "web_browsing",
        "image_generation",
        "code_execution",
    }
    tool_checkboxes = wait.until(
        lambda d: d.find_elements(*AGENT_TOOL_CHECKBOXES) or False
    )
    actual_tool_values = {checkbox.get_attribute("value") for checkbox in tool_checkboxes}
    assert expected_tool_values.issubset(actual_tool_values), (
        "기능 체크박스 value 구성이 예상과 다릅니다. "
        f"expected_subset={sorted(expected_tool_values)}, actual={sorted(actual_tool_values)}"
    )

    # 우측 미리보기 패널 렌더링 확인
    preview_panel = wait.until(EC.visibility_of_element_located(AGENT_PREVIEW_PANEL_TITLE))
    assert preview_panel.is_displayed(), "우측 미리보기 패널이 화면에 표시되지 않았습니다."
