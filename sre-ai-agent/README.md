# Jenkins AI Agent

Jenkins MCP(Model Context Protocol)를 사용하여 Jenkins를 제어하는 AI Agent API 서버입니다.

## 주요 기능

- **REST API 제공**: Slack 앱, Streamlit 등 다양한 프론트엔드에서 호출 가능
- **Jenkins Job 상태 조회**
- **Jenkins Job 빌드/배포 실행**
- **실시간 빌드 진행 상황 모니터링** (SSE 스트리밍)
- **빌드 히스토리 및 로그 조회**
- **Azure OpenAI (GPT-4o) 기반 자연어 인터페이스**

## 기술 스택

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Python 패키지 관리
- FastAPI - REST API 프레임워크
- Uvicorn - ASGI 서버
- Azure OpenAI (GPT-4o)
- MCP (Model Context Protocol) - Streamable HTTP
- Docker & Docker Compose

## 프로젝트 구조

```
sre-ai-agent/
├── .env.example          # 환경 변수 템플릿
├── .gitignore
├── docker-compose.yml    # Docker Compose 설정
├── Dockerfile
├── pyproject.toml        # 프로젝트 의존성 (uv)
├── README.md
└── src/
    ├── __init__.py
    ├── main.py          # API 서버 진입점
    ├── api.py           # FastAPI 앱 (REST API 엔드포인트)
    ├── cli.py           # CLI 모드 (선택사항)
    ├── config.py        # 설정 관리
    ├── mcp_client.py    # MCP 클라이언트
    ├── llm_client.py    # LLM 클라이언트
    └── agent.py         # AI Agent 로직
```

## Quick Start

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 Azure OpenAI와 Jenkins MCP 정보 입력

# 2. Docker로 API 서버 실행
bash run-docker.sh

# 3. API 테스트
# Health Check
curl http://localhost:8000/health

# Chat API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Jenkins 상태 알려줘"}'

# Streaming Chat API
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "helloai 배포해줘"}'
```

## 설정

### 1. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
# LLM Configuration (Azure OpenAI)
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-05-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Jenkins MCP Configuration
JENKINS_MCP_URL=http://54.178.127.218:8080/mcp-server/mcp
JENKINS_MCP_TOKEN=your-jenkins-token-here

# Agent Configuration
AGENT_NAME=Jenkins AI Agent
LOG_LEVEL=INFO
```

### 2. 필수 정보

#### Azure OpenAI API
Azure OpenAI 리소스를 생성하고 다음 정보를 설정합니다:
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API 키
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI 엔드포인트 URL
- `AZURE_OPENAI_DEPLOYMENT`: 배포(deployment) 이름 (예: gpt-4o)

#### Jenkins MCP 인증
Jenkins MCP 서버의 인증 토큰을 `JENKINS_MCP_TOKEN`에 설정합니다.
- 형식: Base64 인코딩된 `username:api_token`
- 예시: `echo -n "username:api_token" | base64`로 생성

## 실행 방법

### Docker Compose 사용 (권장)

```bash
# 간편 실행 (권장)
bash run-docker.sh

# 또는 직접 실행
docker compose build
docker compose up -d

# 로그 확인
docker compose logs -f

# 종료
docker compose down
```

### 로컬 실행 (uv 사용)

#### 1. uv 설치

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# pip로 설치
pip install uv
```

#### 2. 의존성 설치 및 실행

```bash
# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# API 서버 실행
python -m src.main

# 또는 CLI 모드 실행 (선택사항)
python -m src.cli
```

## API 사용 예시

### API 엔드포인트

```
GET  /health              - 헬스 체크
GET  /docs                - API 문서 (Swagger UI)
POST /api/chat            - 채팅 (일반 응답)
POST /api/chat/stream     - 채팅 (스트리밍 응답)
POST /api/reset           - 대화 기록 초기화
```

### 예시 1: Jenkins 상태 확인

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Jenkins 상태 알려줘"}'
```

**응답:**
```json
{
  "response": "Jenkins 인스턴스는 현재 안정적이며 빌드가 가능한 상태입니다.\n- Quiet Mode: 비활성화\n- Queue Size: 0 (대기 중인 작업 없음)\n- Available Executors: 2\n- Root URL Status: OK",
  "session_id": null
}
```

### 예시 2: 빌드 트리거 (스트리밍)

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "helloai를 배포해줘"}'
```

**응답 (SSE):**
```
data:
[도구 실행 중: jenkins_trigger_build]

data: helloai job의 빌드를 시작합니다...

data: ✅ 빌드 #43이 성공적으로 트리거되었습니다.
```

### 예시 3: Python에서 사용

```python
import requests

# 일반 채팅
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "Jenkins 상태 알려줘"}
)
print(response.json()["response"])

# 스트리밍 채팅
response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={"message": "helloai 배포해줘"},
    stream=True
)
for line in response.iter_lines():
    if line.startswith(b"data: "):
        print(line.decode()[6:], end="", flush=True)
```

### 예시 4: Slack 앱 연동

```python
from slack_bolt import App
import requests

app = App(token="xoxb-your-token")

@app.message("배포")
def handle_deploy(message, say):
    user_message = message["text"]

    # Jenkins AI Agent API 호출
    response = requests.post(
        "http://jenkins-ai-agent:8000/api/chat",
        json={"message": user_message}
    )

    say(response.json()["response"])

app.start(port=3000)
```

## API 명령어

### 대화 기록 초기화

```bash
curl -X POST http://localhost:8000/api/reset
```

### 헬스 체크

```bash
curl http://localhost:8000/health
```

### API 문서 확인

브라우저에서 `http://localhost:8000/docs` 접속

## 개발

### 의존성 추가

```bash
# 프로덕션 의존성 추가
uv pip install <package-name>

# 개발 의존성 추가
uv pip install --dev <package-name>

# pyproject.toml 업데이트
uv pip freeze > requirements.txt
```

### 코드 포맷팅

```bash
# Black 포맷터
black src/

# Ruff 린터
ruff check src/
```

## 아키텍처

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Slack App   │    │  Streamlit   │    │   Frontend   │
│              │    │     App      │    │     Apps     │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ HTTP/SSE
                           ▼
           ┌───────────────────────────────┐
           │    FastAPI Server (api.py)    │
           │  - POST /api/chat             │
           │  - POST /api/chat/stream      │
           │  - POST /api/reset            │
           │  - GET  /health               │
           └───────────────┬───────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
       ┌────────────────┐    ┌────────────────┐
       │  LLM Client    │    │  MCP Client    │
       │ (llm_client.py)│    │ (mcp_client.py)│
       │ - 대화 관리    │    │ - 도구 호출    │
       │ - 도구 선택    │    │ - SSE 통신     │
       └────────┬───────┘    └────────┬───────┘
                │                     │
                ▼                     ▼
         ┌─────────────┐       ┌─────────────┐
         │Azure OpenAI │       │Jenkins MCP  │
         │  (GPT-4o)   │       │   Server    │
         └─────────────┘       └─────────────┘
```

## MCP (Model Context Protocol)

이 프로젝트는 Anthropic의 MCP를 사용하여 Jenkins와 통신합니다:

- **프로토콜**: JSON-RPC 2.0
- **전송 방식**: Streamable HTTP (SSE - Server-Sent Events)
- **인증**: HTTP Basic Authentication

### MCP 도구 호출 흐름

1. Agent 초기화 시 MCP 서버에서 사용 가능한 도구 목록 조회
2. LLM에게 도구 목록을 OpenAI 호환 형식으로 제공
3. 사용자 요청 시 LLM이 적절한 도구 선택
4. MCP 클라이언트가 선택된 도구 실행
5. 결과를 LLM에게 전달하여 최종 응답 생성

## 문제 해결

### Docker 빌드 실패

```bash
# 캐시 없이 재빌드
docker compose build --no-cache
docker compose up -d
```

### API 서버 시작 실패

```bash
# 로그 확인
docker compose logs -f

# 컨테이너 재시작
docker compose restart
```

### MCP 연결 오류

- Jenkins MCP 서버가 실행 중인지 확인
- `JENKINS_MCP_URL`이 올바른지 확인
- 인증 토큰이 올바른지 확인 (Basic 인증 형식)

### Azure OpenAI API 오류

- `AZURE_OPENAI_API_KEY`가 올바른지 확인
- `AZURE_OPENAI_ENDPOINT`가 올바른지 확인
- API 사용량 제한을 확인
- 네트워크 연결 확인

### 포트 충돌

```bash
# 8000 포트를 사용 중인 프로세스 확인
lsof -i :8000

# docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 호스트:컨테이너
```

## 라이선스

MIT License

## 기여

Issue와 Pull Request를 환영합니다!
