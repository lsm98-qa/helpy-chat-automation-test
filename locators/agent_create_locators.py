from selenium.webdriver.common.by import By

# 에이전트 프로필 이미지 추가 버튼(+ 아이콘)
AGENT_IMAGE_PLUS_BUTTON = (
    By.XPATH,
    "//button[.//*[name()='svg' and @data-testid='plusIcon']]",
)
# 에이전트 이름 입력 필드
AGENT_NAME_INPUT = (By.NAME, "name")

# 에이전트 한줄 소개 입력 필드
AGENT_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "input[name='description']")

# 카테고리 선택 콤보박스 컨테이너
AGENT_PURPOSE_COMBOBOX = (By.CSS_SELECTOR, "div[role='combobox']#agent-builder-purpose")

# 카테고리 값 입력 필드(콤보박스 내부)
AGENT_PURPOSE_INPUT = (By.CSS_SELECTOR, "input[name='purpose']")

# 규칙(System Prompt) 입력 필드
AGENT_SYSTEM_PROMPT_INPUT = (By.NAME, "systemPrompt")

# 시작 대화 입력 필드 목록(모든 행)
AGENT_CONVERSATION_STARTER_INPUTS = (
    By.CSS_SELECTOR,
    "input[name^='conversationStarters.'][name$='.value']",
)

# 파일 업로드 input을 감싸는 라벨 영역
AGENT_FILE_UPLOAD_LABEL = (
    By.XPATH,
    "//label[.//input[@type='file' and @multiple and contains(@accept,'.pdf')]]",
)

# 실제 파일 업로드 input 요소
AGENT_FILE_UPLOAD_INPUT = (
    By.XPATH,
    "//label[.//input[@type='file' and @multiple and contains(@accept,'.pdf')]]//input[@type='file']",
)

# 기능 옵션 체크박스(toolIds 그룹)
AGENT_TOOL_CHECKBOXES = (By.CSS_SELECTOR, "input[type='checkbox'][name='toolIds']")

# 우측 미리보기 패널 제목 요소
AGENT_PREVIEW_PANEL_TITLE = (By.XPATH, "//*[normalize-space()='미리보기']")

# chat/form 탭을 모두 포함하는 토글 그룹
AGENT_CREATE_TOGGLE_GROUP = (
    By.XPATH,
    "//div[@role='group' and .//button[@type='button' and @value='chat'] and .//button[@type='button' and @value='form']]",
)

# 대화로 만들기 탭 버튼(value='chat')
AGENT_CREATE_CHAT_TAB = (
    By.XPATH,
    "//div[@role='group' and .//button[@type='button' and @value='chat'] and .//button[@type='button' and @value='form']]"
    "//button[@type='button' and @value='chat']",
)

# 설정 탭 버튼(value='form')
AGENT_CREATE_FORM_TAB = (
    By.XPATH,
    "//div[@role='group' and .//button[@type='button' and @value='chat'] and .//button[@type='button' and @value='form']]"
    "//button[@type='button' and @value='form']",
)

