"""CLI mode for Jenkins AI Agent (legacy)"""

import asyncio
import logging
import sys
from src.config import settings
from src.mcp_client import MCPClient
from src.llm_client import LLMClient
from src.agent import JenkinsAgent

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress verbose HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def main():
    """Main function for CLI mode"""
    try:
        mcp_client = MCPClient(
            base_url=settings.jenkins_mcp_url,
            auth_token=settings.jenkins_mcp_token,
        )

        llm_client = LLMClient(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            deployment=settings.azure_openai_deployment,
        )

        agent = JenkinsAgent(mcp_client, llm_client)

        await agent.initialize()

        print("\n" + "=" * 60)
        print(f"  {settings.agent_name}")
        print("=" * 60)
        print("Jenkins AI Agent가 준비되었습니다!")
        print("명령어를 입력하세요 (종료하려면 'quit' 또는 'exit'):")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("\n사용자: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "종료"]:
                    print("\n종료합니다...")
                    break

                if user_input.lower() in ["clear", "reset", "초기화"]:
                    llm_client.reset_conversation()
                    print("대화 기록이 초기화되었습니다.")
                    continue

                print("\nAgent: ", end="", flush=True)

                if "배포" in user_input or "빌드" in user_input or "build" in user_input.lower():
                    async for update in agent.process_message_with_streaming(user_input):
                        print(update, end="", flush=True)
                    print()
                else:
                    response = await agent.process_message(user_input)
                    print(response)

            except KeyboardInterrupt:
                print("\n\n종료합니다...")
                break
            except EOFError:
                print("\n\n종료합니다...")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                print(f"\n오류가 발생했습니다: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to start agent: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
