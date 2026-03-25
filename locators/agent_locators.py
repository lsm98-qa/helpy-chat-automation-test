from selenium.webdriver.common.by import By

AGENT_CREATE_BUTTON = (By.CSS_SELECTOR, "a[href='/ai-helpy-chat/agents/builder']")
AGENT_MY_AGENTS_BUTTON = (By.CSS_SELECTOR, "a[href='/ai-helpy-chat/agents/mine']")

# 주의: 이 뒤로가기 버튼은 내 에이전트 페이지에서만 사용됩니다
AGENT_BACK_BUTTON = (By.CSS_SELECTOR, "a[href='/ai-helpy-chat/agents'] svg")