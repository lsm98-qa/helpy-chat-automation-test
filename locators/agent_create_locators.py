from selenium.webdriver.common.by import By

AGENT_IMAGE_PLUS_BUTTON = (
    By.XPATH,
    "//button[.//*[name()='svg' and @data-testid='plusIcon']]",
)
AGENT_NAME_INPUT = (By.NAME, "name")
AGENT_DESCRIPTION_INPUT = (By.CSS_SELECTOR, "input[name='description']")
AGENT_PURPOSE_COMBOBOX = (By.CSS_SELECTOR, "div[role='combobox']#agent-builder-purpose")
AGENT_PURPOSE_INPUT = (By.CSS_SELECTOR, "input[name='purpose']")
AGENT_SYSTEM_PROMPT_INPUT = (By.NAME, "systemPrompt")
AGENT_CONVERSATION_STARTER_INPUTS = (
    By.CSS_SELECTOR,
    "input[name^='conversationStarters.'][name$='.value']",
)
AGENT_FILE_UPLOAD_LABEL = (
    By.XPATH,
    "//label[.//input[@type='file' and @multiple and contains(@accept,'.pdf')]]",
)
AGENT_FILE_UPLOAD_INPUT = (
    By.XPATH,
    "//label[.//input[@type='file' and @multiple and contains(@accept,'.pdf')]]//input[@type='file']",
)
AGENT_TOOL_CHECKBOXES = (By.CSS_SELECTOR, "input[type='checkbox'][name='toolIds']")
AGENT_PREVIEW_PANEL_TITLE = (By.XPATH, "//*[normalize-space()='미리보기']")
