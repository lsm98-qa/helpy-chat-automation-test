# Helpy Chat Automation Test TEAM2

Selenium + Pytest 기반의 E2E(UI) 자동화 테스트 프로젝트입니다.  
`https://qaproject.elice.io/ai-helpy-chat` 서비스의 로그인, 채팅, 에이전트, 도구(PPT 생성) 핵심 시나리오를 검증합니다.

## 1) 기술 스택

- Python
- Pytest
- Selenium WebDriver (Chrome)
- python-dotenv
- python-pptx (PPT 생성 결과 검증용)

## 2) 디렉터리 구조

```text
.
├─ conftest.py                  # 공통 fixture/드라이버/로그인 설정
├─ pages/                       # 페이지 액션
├─ locators/                    # UI locator 모음
├─ tests/
│  ├─ auth/                     # 로그인/로그아웃
│  ├─ chat/                     # 채팅 기능
│  ├─ agent/                    # 에이전트 기능
│  └─ tools/                    # 도구 기능 (PPT 생성 등)
├─ requirements.txt
└─ SETUP.md
```

## 3) 사전 준비

- Python 3.10+ 권장
- Google Chrome 설치
- 테스트 계정 준비

## 4) 설치

```bash
pip install -r requirements.txt
```

## 5) 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 설정합니다.

```env
ACCOUNT_EMAIL=your_account_email
ACCOUNT_PASSWORD=your_account_password
```

`conftest.py`에서 위 값을 로드해 로그인 fixture에서 사용합니다.

## 6) 테스트 실행

전체 실행:

```bash
pytest
```

헤드리스 실행:

```bash
pytest --headless
```

기본 URL 변경:

```bash
pytest --base-url "https://qaproject.elice.io/ai-helpy-chat"
```

영역별 실행 예시:

```bash
pytest tests/auth
pytest tests/chat
pytest tests/agent
pytest tests/tools
```

## 7) 주요 테스트 범위

- `auth`: 로그인 성공/실패, 로그아웃, 멀티탭 로그아웃
- `chat`: 새 채팅 생성, 히스토리 관련 동작, 채팅 이름 변경, 이미지 생성
- `agent`: 에이전트 탐색/생성 화면 이동 및 기본 동작
- `tools`: 도구 메뉴 진입, PPT 생성 및 결과 파일 검증

## 8) 참고 사항

- `tests/tools/ppt_create/test_ppt_create.py`는 현재 알려진 이슈로 `xfail` 처리되어 있습니다.
- PPT 생성 테스트 결과물은 `tests/tools/ppt_create/downloads` 경로에 저장됩니다.
- 브라우저 실행 옵션/공통 fixture는 루트 `conftest.py`를 기준으로 관리합니다.
- 각 기능 단위 별 fixture와 constants는 해당 디렉토리에서 관리합니다.
