# 초기 프로젝트 세팅

## 1) 사전 준비

- Python 3.10+ 권장
- Google Chrome 설치
- 테스트 계정 준비

## 2) 가상환경 생성 (Windows PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) 의존성 설치

```bash
pip install -r requirements.txt
```

## 4) `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 입력하세요.

```env
ACCOUNT_EMAIL=your_account_email
ACCOUNT_PASSWORD=your_account_password
```

`conftest.py`에서 `python-dotenv`로 환경변수를 로드합니다.

## 5) 기본 실행 확인

```bash
pytest
```

기본 설정(`pytest.ini`)에 따라 아래가 자동 적용됩니다.

- `--html=artifacts/reports/report.html --self-contained-html`
- `-ra -rxX` (skip/xfail/xpass 요약 + xfail reason 출력)
- 실시간 콘솔 로그 + 파일 로그 (`artifacts/logs/pytest.log`)

## 6) 자주 쓰는 실행 옵션

기본 URL 변경:

```bash
pytest --base-url "https://qaproject.elice.io/ai-helpy-chat"
```

헤드리스 실행:

```bash
pytest --headless
```

특정 영역만 실행:

```bash
pytest tests/auth
pytest tests/chat
pytest tests/agent
pytest tests/tools
```

특정 파일만 실행:

```bash
pytest tests/chat/test_search_chat.py
```

## 7) 산출물 경로

- HTML 리포트: `artifacts/reports/report.html`
- 테스트 로그: `artifacts/logs/pytest.log`
- 실패 스크린샷: `artifacts/screenshots/`

## 8) 실행 팁

- 채팅/에이전트 시나리오는 데이터 상태 영향이 있어, 테스트 계정의 잔여 데이터 유무를 확인하고 실행하는 것이 안정적입니다.
