"""Slack AI Agent 앱"""
import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from ai_agent import AIAgentClient

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack 앱 초기화
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# AI Agent 클라이언트 초기화
ai_agent = AIAgentClient(
    api_url=os.environ.get("AI_AGENT_URL", "http://localhost:8000")
)


@app.command("/ai")
def handle_ai_command(ack, command, client):
    """
    /ai 슬래시 명령어 처리

    사용자가 '/ai <메시지>'를 입력하면:
    1. 즉시 응답 (3초 제한)
    2. AI Agent에 메시지 전달
    3. 응답을 스레드로 전송
    """
    # 즉시 응답 (Slack 3초 제한)
    ack("AI Agent에 요청을 전달하고 있습니다...")

    user_id = command["user_id"]
    channel_id = command["channel_id"]
    text = command["text"]

    # 명령어를 실행한 메시지의 timestamp (스레드용)
    # Socket Mode에서는 response_url을 통해 메시지를 보낸 후 해당 메시지의 ts를 얻어야 함

    try:
        # 먼저 채널에 "처리 중" 메시지 전송
        response = client.chat_postMessage(
            channel=channel_id,
            text=f"<@{user_id}>님의 요청을 처리하고 있습니다...\n> {text}"
        )
        thread_ts = response["ts"]

        logger.info(f"User {user_id} requested: {text}")

        # AI Agent에 메시지 전송
        ai_response = ai_agent.send_message(text)

        # 응답을 스레드로 전송
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=ai_response.get("response", "응답을 받지 못했습니다.")
        )

        logger.info(f"AI Agent response sent to thread {thread_ts}")

    except Exception as e:
        logger.error(f"Error processing AI request: {str(e)}")

        # 에러 발생 시 스레드로 에러 메시지 전송
        error_message = f"❌ 요청 처리 중 오류가 발생했습니다: {str(e)}"

        if 'thread_ts' in locals():
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=error_message
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=error_message
            )


@app.event("app_mention")
def handle_mention(event, client):
    """
    앱이 멘션되었을 때 처리 (선택적 기능)
    """
    channel_id = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])
    text = event["text"]

    # 멘션 제거
    message = text.split(">", 1)[-1].strip()

    try:
        # AI Agent에 메시지 전송
        ai_response = ai_agent.send_message(message)

        # 스레드로 응답
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=ai_response.get("response", "응답을 받지 못했습니다.")
        )

    except Exception as e:
        logger.error(f"Error processing mention: {str(e)}")
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"❌ 오류 발생: {str(e)}"
        )


def main():
    """앱 실행"""
    # Socket Mode 사용 (방화벽 뒤에서도 동작 가능)
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))

    logger.info("⚡️ Slack AI Agent 앱이 시작되었습니다!")
    handler.start()


if __name__ == "__main__":
    main()
