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

#### 로컬 실행

```bash
uv run python app.py
```

#### Docker Compose로 실행 (AWS 배포용)

**방법 1: 배포 스크립트 사용 (가장 간단 - macOS/Ubuntu 자동 감지)**

```bash
# 배포 (빌드 + 시작)
./deploy.sh

# 로그 확인
./deploy.sh logs

# 재시작
./deploy.sh restart

# 중지
./deploy.sh down

# 상태 확인
./deploy.sh status
```

**방법 2: Makefile 사용 (권장 - macOS/Ubuntu 모두 호환)**

```bash
# 빌드 및 시작
make up

# 로그 확인
make logs

# 재시작
make restart

# 중지
make down

# 전체 배포 (빌드 + 시작)
make deploy
```

**방법 3: Docker Compose 직접 사용**

```bash
# macOS (docker-compose)
docker-compose up -d

# Ubuntu/AWS (docker compose)
docker compose up -d

# 로그 확인
docker-compose logs -f  # macOS
docker compose logs -f  # Ubuntu

# 중지
docker-compose down  # macOS
docker compose down  # Ubuntu
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

## AWS 서버 배포 가이드

### 사전 요구사항

- Docker 및 Docker Compose 설치된 AWS EC2 인스턴스
- Git 설치

### 배포 단계

#### 1. 코드 클론

```bash
git clone <your-repository-url>
cd sre-ai-slack
```

#### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (vi, nano 등 사용)
vi .env
```

`.env` 파일에 Slack 토큰 입력:
```
SLACK_BOT_TOKEN=xoxb-실제-토큰
SLACK_APP_TOKEN=xapp-실제-토큰
SLACK_SIGNING_SECRET=실제-시크릿
AI_AGENT_URL=http://your-ai-agent:8000
```

**중요**: AI_AGENT_URL은 AI Agent 서버의 실제 주소로 변경하세요.
- 같은 Docker 네트워크 내: `http://ai-agent-container:8000`
- 다른 서버: `http://ai-agent-server-ip:8000`

#### 3. Docker Compose로 실행

```bash
# 방법 1: 배포 스크립트 사용 (가장 간단 - 자동 감지)
./deploy.sh

# 방법 2: Makefile 사용
make up

# 방법 3: docker compose 직접 사용 (Ubuntu)
docker compose up -d

# 로그 확인 (앱이 정상 시작되었는지 확인)
./deploy.sh logs
# 또는
make logs
# 또는
docker compose logs -f slack-bot
```

정상 실행 시 다음과 같은 로그가 보입니다:
```
⚡️ Slack AI Agent 앱이 시작되었습니다!
```

#### 4. 서버 재부팅 시 자동 실행 설정 (선택사항)

```bash
# systemd 서비스 파일 생성
sudo vi /etc/systemd/system/sre-ai-slack.service
```

다음 내용 입력:
```ini
[Unit]
Description=SRE AI Slack Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/sre-ai-slack
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

서비스 활성화:
```bash
sudo systemctl enable sre-ai-slack
sudo systemctl start sre-ai-slack
```

#### 5. 업데이트 배포

코드 업데이트 시:
```bash
git pull

# 방법 1: 배포 스크립트 사용 (가장 간단)
./deploy.sh

# 방법 2: Makefile 사용
make deploy

# 방법 3: docker compose 직접 사용
docker compose down
docker compose build
docker compose up -d
```

### AWS EC2 보안 그룹 설정

Socket Mode를 사용하므로 **인바운드 규칙 추가 불필요**합니다.
- 앱이 Slack으로 outbound 연결만 합니다
- 기본 outbound 규칙(모두 허용)만 있으면 됩니다

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
