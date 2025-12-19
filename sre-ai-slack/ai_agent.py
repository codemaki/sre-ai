"""AI Agent 통신 모듈"""
import requests
from typing import Optional, Dict, Any


class AIAgentClient:
    """AI Agent와 통신하는 클라이언트"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.chat_endpoint = f"{self.api_url}/api/chat"

    def send_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        AI Agent에 메시지를 전송하고 응답을 받습니다.

        Args:
            message: 전송할 메시지
            session_id: 세션 ID (선택사항)

        Returns:
            AI Agent의 응답 딕셔너리

        Raises:
            requests.RequestException: API 호출 실패 시
        """
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id

        try:
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception("AI Agent 응답 시간 초과 (30초)")
        except requests.RequestException as e:
            raise Exception(f"AI Agent 호출 실패: {str(e)}")
