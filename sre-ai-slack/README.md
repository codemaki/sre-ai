# Slack AI Agent 앱

AI Agent와 연동하여 Slack에서 AI 질의응답을 제공하는 봇입니다.

## 기능

- `/ai` 슬래시 명령어로 AI Agent에 질문
- 응답은 스레드로 자동 전송
- 앱 멘션(@bot)을 통한 대화 가능

## 설치 및 실행

### 1. 의존성 설치

uv를 사용하여 의존성을 설치합니다:

```bash
uv sync
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 값을 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일에 다음 값들을 설정합니다:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
AI_AGENT_URL=http://localhost:8000
```

### 3. 앱 실행

```bash
uv run python app.py
```

## Slack 앱 설정 가이드

### 1. Slack 앱 생성

1. https://api.slack.com/apps 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. 앱 이름과 워크스페이스 선택

### 2. Bot Token Scopes 설정

**OAuth & Permissions** 메뉴에서 다음 권한을 추가:

- `chat:write` - 메시지 전송
- `chat:write.public` - 봇이 추가되지 않은 채널에 메시지 전송 (선택사항)
- `commands` - 슬래시 명령어 사용
- `app_mentions:read` - 앱 멘션 감지 (선택사항)

### 3. Slash Command 설정

**Slash Commands** 메뉴에서:

1. "Create New Command" 클릭
2. 다음 정보 입력:
   - Command: `/ai`
   - Request URL: `https://your-domain.com/slack/events` (Socket Mode 사용 시 임시값 입력 가능)
   - Short Description: `AI Agent에게 질문하기`
   - Usage Hint: `[질문 내용]`

### 4. Socket Mode 활성화 (권장)

**Socket Mode** 메뉴에서:

1. "Enable Socket Mode" 활성화
2. App-Level Token 생성:
   - Token Name: `socket-mode`
   - Scope: `connections:write` 추가
3. 생성된 토큰(`xapp-`로 시작)을 `.env`의 `SLACK_APP_TOKEN`에 저장

### 5. Event Subscriptions 설정 (앱 멘션 기능 사용 시)

**Event Subscriptions** 메뉴에서:

1. "Enable Events" 활성화 (Socket Mode 사용 시 Request URL 불필요)
2. "Subscribe to bot events"에서 다음 이벤트 추가:
   - `app_mention` - 앱이 멘션되었을 때

### 6. 토큰 확인 및 설정

**OAuth & Permissions** 메뉴에서:

1. "Install to Workspace" 클릭
2. 권한 승인
3. 생성된 **Bot User OAuth Token** (`xoxb-`로 시작)을 `.env`의 `SLACK_BOT_TOKEN`에 저장

**Basic Information** 메뉴에서:

1. **Signing Secret**을 `.env`의 `SLACK_SIGNING_SECRET`에 저장

## 사용 방법

### 슬래시 명령어 사용

Slack 채널에서 다음과 같이 입력:

```
/ai helloai 마지막 배포 이력 알려줘
```

봇이 요청을 받아 AI Agent에 전달하고, 응답을 스레드로 전송합니다.

### 앱 멘션 사용 (선택사항)

```
@AI Agent Bot helloai 상태 확인해줘
```

## 프로젝트 구조

```
sre-ai-slack/
├── app.py              # 메인 Slack 앱
├── ai_agent.py         # AI Agent 통신 모듈
├── pyproject.toml      # 프로젝트 및 의존성 설정
├── .env.example        # 환경 변수 예시
├── .env                # 환경 변수 (git 무시)
└── README.md           # 본 파일
```

## AI Agent API 스펙

이 앱은 다음 형식의 AI Agent API를 사용합니다:

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "helloai 마지막 배포 이력 알려줘"}'
```

**Response:**
```json
{
  "response": "helloai 작업의 마지막 배포 이력은...",
  "session_id": null
}
```

## 트러블슈팅

### 앱이 응답하지 않는 경우

1. AI Agent가 실행 중인지 확인: `curl http://localhost:8000/api/chat`
2. `.env` 파일의 토큰들이 올바른지 확인
3. 앱 로그 확인: `uv run python app.py`

### Socket Mode 연결 오류

1. `SLACK_APP_TOKEN`이 `xapp-`로 시작하는지 확인
2. Socket Mode가 Slack 앱 설정에서 활성화되었는지 확인

### 권한 오류

1. Slack 앱 설정에서 필요한 Bot Token Scopes가 모두 추가되었는지 확인
2. 앱을 워크스페이스에 재설치: OAuth & Permissions > Reinstall App

## 라이선스

MIT
