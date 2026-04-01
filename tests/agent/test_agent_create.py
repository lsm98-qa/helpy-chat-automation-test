import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.agent_create_locators import (
    AGENT_CONVERSATION_STARTER_INPUTS,
    AGENT_CREATE_CHAT_TAB,
    AGENT_CREATE_FORM_TAB,
    AGENT_CREATE_TOGGLE_GROUP,
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

# 에이전트 생성 토글의 상태를 기대값(chat/form)과 비교 검증하는 공통 헬퍼
def _assert_agent_create_tab_pressed_state(wait, chat_expected, form_expected):
    chat_expected_str = "true" if chat_expected else "false"
    form_expected_str = "true" if form_expected else "false"

    wait.until(lambda d: d.find_element(*AGENT_CREATE_CHAT_TAB).get_attribute("aria-pressed") == chat_expected_str)
    wait.until(lambda d: d.find_element(*AGENT_CREATE_FORM_TAB).get_attribute("aria-pressed") == form_expected_str)

    chat_actual = wait.until(EC.presence_of_element_located(AGENT_CREATE_CHAT_TAB)).get_attribute("aria-pressed")
    form_actual = wait.until(EC.presence_of_element_located(AGENT_CREATE_FORM_TAB)).get_attribute("aria-pressed")

    assert chat_actual == chat_expected_str, (
        f"chat 탭 aria-pressed 상태가 예상과 다릅니다. expected={chat_expected_str}, actual={chat_actual}"
    )
    assert form_actual == form_expected_str, (
        f"form 탭 aria-pressed 상태가 예상과 다릅니다. expected={form_expected_str}, actual={form_actual}"
    )

def _is_create_button_disabled(button):
    class_name = button.get_attribute("class") or ""
    return (
        (not button.is_enabled())
        or (button.get_attribute("disabled") is not None)
        or (button.get_attribute("aria-disabled") == "true")
        or ("Mui-disabled" in class_name)
    )


def _is_create_button_enabled(button):
    class_name = button.get_attribute("class") or ""
    return (
        button.is_enabled()
        and (button.get_attribute("disabled") is None)
        and (button.get_attribute("aria-disabled") != "true")
        and ("Mui-disabled" not in class_name)
    )


# 토글 탭(chat/form)의 초기 렌더링 및 기본 선택 상태(단일 선택)를 검증
def test_agent_create_tabs_initial_state(navigate_to_agent_create, wait):
    _ = navigate_to_agent_create

    # Arrange
    group = wait.until(EC.visibility_of_element_located(AGENT_CREATE_TOGGLE_GROUP))
    chat_tab = wait.until(EC.element_to_be_clickable(AGENT_CREATE_CHAT_TAB))
    settings_tab = wait.until(EC.element_to_be_clickable(AGENT_CREATE_FORM_TAB))

    # ==========
    # Assert
    assert group.is_displayed(), "대화/설정 토글 그룹이 화면에 표시되지 않았습니다."
    assert chat_tab.is_displayed() and chat_tab.is_enabled(), "chat 탭이 표시/활성 상태가 아닙니다."
    assert settings_tab.is_displayed() and settings_tab.is_enabled(), "form 탭이 표시/활성 상태가 아닙니다."
    assert chat_tab.get_attribute("value") == "chat", (
        f"chat 탭 value가 예상과 다릅니다. actual={chat_tab.get_attribute('value')}"
    )
    assert settings_tab.get_attribute("value") == "form", (
        f"form 탭 value가 예상과 다릅니다. actual={settings_tab.get_attribute('value')}"
    )

    initial_chat_pressed = chat_tab.get_attribute("aria-pressed")
    initial_form_pressed = settings_tab.get_attribute("aria-pressed")
    assert (initial_chat_pressed == "true") != (initial_form_pressed == "true"), (
        "초기 상태에서 chat/form 중 정확히 1개만 선택되어야 합니다. "
        f"chat={initial_chat_pressed}, form={initial_form_pressed}"
    )


# 토글 탭 전환을 순차 시나리오로 검증
def test_agent_create_tabs_switch_clickable(navigate_to_agent_create, wait):
    _ = navigate_to_agent_create

    # Arrange
    chat_tab = wait.until(EC.element_to_be_clickable(AGENT_CREATE_CHAT_TAB))
    settings_tab = wait.until(EC.element_to_be_clickable(AGENT_CREATE_FORM_TAB))
    assert chat_tab.is_enabled(), "chat 탭이 클릭 가능한 상태가 아닙니다."
    assert settings_tab.is_enabled(), "form 탭이 클릭 가능한 상태가 아닙니다."

    # Act(1): chat 탭으로 1차 전환
    chat_tab.click()

    # Assert(1): 1차 전환 결과 검증. 실패하면 시나리오를 중단한다.
    _assert_agent_create_tab_pressed_state(wait, chat_expected=True, form_expected=False)

    # Act(2): 1차 전환이 성공했을 때만 form 탭으로 역전환
    wait.until(EC.element_to_be_clickable(AGENT_CREATE_FORM_TAB)).click()

    # Assert(2): 역전환 결과 검증
    _assert_agent_create_tab_pressed_state(wait, chat_expected=False, form_expected=True)


# 필수 텍스트 입력 필드 editable, 입력값 반영 여부로 검증 확인 (이름, 규칙)
@pytest.mark.parametrize(
    "locator, test_value",
    [
        pytest.param(AGENT_NAME_INPUT, "qa_name_editable_check", id="name_input"),
        pytest.param(AGENT_SYSTEM_PROMPT_INPUT, "qa_system_prompt_editable_check", id="system_prompt_input"),
    ],
)
def test_agent_create_name_input_editable(navigate_to_agent_create, wait, locator, test_value):
    # Arrange
    _ = navigate_to_agent_create

    element = wait.until(EC.visibility_of_element_located(locator))
    assert element.is_enabled(), f"필수 입력 필드가 비활성 상태입니다. locator={locator}"
    assert element.get_attribute("readonly") is None, f"필수 입력 필드가 readonly 상태입니다. locator={locator}"

    # Act: 입력값 초기화 후 테스트 값 입력
    element.clear()
    element.send_keys(test_value)

    # Assert: 입력한 값이 실제 value에 반영되었는지 확인
    assert element.get_attribute("value") == test_value, (
        "필수 입력 필드에 입력한 값이 반영되지 않았습니다. "
        f"locator={locator}, expected={test_value}, actual={element.get_attribute('value')}"
    )


# 필수값 미입력 초기 상태에서 생성 버튼 비활성 확인
def test_agent_create_submit_button_disabled_when_required_fields_empty(navigate_to_agent_create, wait):
    # Arrange: 필수값 입력 필드 요소들을 가져온다. (이름, 규칙)
    create_button_locator = (By.XPATH, "//button[normalize-space()='만들기']")
    name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    system_prompt_input = wait.until(EC.visibility_of_element_located(AGENT_SYSTEM_PROMPT_INPUT))
    wait.until(EC.presence_of_element_located(create_button_locator))

    # Act: 필수값을 비워서 제출 불가능 상태를 만든다.
    name_input.clear()
    system_prompt_input.clear()
    wait.until(lambda d: (name_input.get_attribute("value") or "") == "")
    wait.until(lambda d: (system_prompt_input.get_attribute("value") or "") == "")

    # Assert: "만들기" 버튼이 비활성인지 검증한다.
    wait.until(lambda d: _is_create_button_disabled(d.find_element(*create_button_locator)))

    create_button = wait.until(EC.presence_of_element_located(create_button_locator))
    assert _is_create_button_disabled(create_button), '"만들기" 버튼이 비활성 상태가 아닙니다.'


# 필수값 입력 상태에서 생성 버튼 활성 전환 확인
def test_agent_create_submit_button_enabled_when_required_fields_filled(navigate_to_agent_create, wait):
    driver = navigate_to_agent_create

    # Arrange: 입력 필드와 "만들기" 버튼을 찾는다.
    create_button_locator = (By.XPATH, "//button[normalize-space()='만들기']")
    name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    system_prompt_input = wait.until(EC.visibility_of_element_located(AGENT_SYSTEM_PROMPT_INPUT))
    wait.until(EC.presence_of_element_located(create_button_locator))

    # Act: 필수값을 먼저 비워 비활성 상태를 만든 뒤, 유효한 값을 입력한다.
    name_input.clear()
    system_prompt_input.clear()
    wait.until(lambda d: (name_input.get_attribute("value") or "") == "")
    wait.until(lambda d: (system_prompt_input.get_attribute("value") or "") == "")
    wait.until(lambda d: _is_create_button_disabled(d.find_element(*create_button_locator)))

    name_input.send_keys("qa_submit_enable_name")
    system_prompt_input.send_keys("qa_submit_enable_system_prompt")
    wait.until(lambda d: (name_input.get_attribute("value") or "") == "qa_submit_enable_name")
    wait.until(lambda d: (system_prompt_input.get_attribute("value") or "") == "qa_submit_enable_system_prompt")
    
    # 마지막 입력 필드의 blur를 유도해 검증/상태 갱신이 완료된 뒤 버튼 활성 여부를 확인한다.
    driver.execute_script("arguments[0].blur();", system_prompt_input)

    # Assert: "만들기" 버튼이 활성 상태로 전환되는지 검증한다.
    wait.until(
        lambda d: _is_create_button_enabled(d.find_element(*create_button_locator))
    )

    create_button = wait.until(EC.presence_of_element_located(create_button_locator))
    assert _is_create_button_enabled(create_button), '"만들기" 버튼이 활성 상태로 전환되지 않았습니다.'


# 에이전트 생성 시 공개 설정 모달에서 저장 완료 후 성공 토스트가 노출되는지 검증
def test_agent_create_shows_success_toast(navigate_to_agent_create, wait):
    from uuid import uuid4

    # Arrange
    driver = navigate_to_agent_create
    create_button_locator = (By.XPATH, "//button[normalize-space()='만들기']")
    publish_modal_locator = (
        By.XPATH,
        "//div[@role='dialog' and .//form[@id='publish-setting-form']]",
    )
    publish_modal_save_button_locator = (
        By.XPATH,
        "//div[@role='dialog' and .//form[@id='publish-setting-form']]//button[@type='submit' and @form='publish-setting-form']",
    )

    # 랜덤한 이름 문자열 생성
    unique_agent_name = f"qa-agent-{uuid4().hex[:8]}"

    name_input = wait.until(EC.visibility_of_element_located(AGENT_NAME_INPUT))
    system_prompt_input = wait.until(EC.visibility_of_element_located(AGENT_SYSTEM_PROMPT_INPUT))

    name_input.clear()
    name_input.send_keys(unique_agent_name)
    system_prompt_input.clear()
    system_prompt_input.send_keys("You are a helpful assistant.")

    driver.execute_script("arguments[0].blur();", system_prompt_input)

    wait.until(lambda d: _is_create_button_enabled(d.find_element(*create_button_locator)))

    # Act
    wait.until(EC.element_to_be_clickable(create_button_locator)).click()
    wait.until(EC.visibility_of_element_located(publish_modal_locator))
    wait.until(EC.element_to_be_clickable(publish_modal_save_button_locator)).click()

    # Assert
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[@role='alert' and (contains(@class, 'notistack-MuiContent-success') or .//*[@data-testid='circle-checkIcon'])]",
            )
        )
    )
