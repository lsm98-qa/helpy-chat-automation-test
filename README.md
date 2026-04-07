# Helpy Chat Automation Test TEAM2

Selenium + Pytest 기반 E2E(UI) 자동화 테스트 프로젝트입니다.  
`https://qaproject.elice.io/ai-helpy-chat` 서비스의 인증, 채팅, 에이전트, 도구 기능을 검증합니다.

## 기술 스택

- Python
- Pytest
- Selenium WebDriver (Chrome)
- python-dotenv
- pytest-html (HTML 리포트)
- python-pptx / xlsxwriter (생성 산출물 검증)

## 디렉터리 구조

```text
.
|- conftest.py                  # 공통 fixture, webdriver, 로그인, 실패 스크린샷 훅
|- pytest.ini                   # 공통 pytest 옵션 
|- pages/                       # 페이지 객체/액션
|- locators/                    # UI locator
|- tests/
|  |- auth/                     # 로그인/로그아웃
|  |- chat/                     # 채팅 기능
|  |- agent/                    # 에이전트 기능
|  `- tools/                    # 도구 기능
|     |- behavior_create/
|     |- deep_research/
|     |- lesson_plan/
|     |- ppt_create/
|     |- quiz_create/
|     `- spec_detail/
|- artifacts/                   # 리포트/로그/스크린샷 산출물
|- requirements.txt
|- SETUP.md
`- CHANGELOG.md
```

## 사전 준비

- Python 3.10+ 권장
- Google Chrome 설치
- 테스트용 계정

## 설정 및 실행

프로젝트 초기 설정(가상환경, 의존성 설치, `.env` 설정, 실행 옵션)은 `SETUP.md`를 참고하세요.

## 기본 pytest 설정 (pytest.ini)

- `-ra -rxX`: skip/xfail/xpass 요약 및 reason 출력
- `--html=artifacts/reports/report.html --self-contained-html`: HTML 리포트 생성
- 로그 파일: `artifacts/logs/pytest.log`
- 실패 시 스크린샷: `artifacts/screenshots/`

## 주요 테스트 범위

- `auth`: 로그인 성공/실패, 로그아웃, 멀티탭 로그아웃
- `chat`: 대화 생성/검색/수정/삭제, 히스토리/리로드/재로그인 동작, 이미지 생성
- `agent`: 에이전트 탐색/검색, 내 에이전트 생성/검색/상태 확인/수정
- `tools`: 세부 특기사항, 행동특성 및 종합의견, 수업지도안, PPT 생성, 퀴즈 생성, 심층 조사

## 참고 사항

- 일부 케이스는 알려진 이슈로 `xfail`이 설정되어 있습니다.
- 실패 테스트는 `pytest_html` 리포트에 스크린샷이 첨부됩니다.
- 변경 이력은 `CHANGELOG.md`를 참고하세요.
