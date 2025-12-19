"""Jenkins AI Agent - Main orchestration logic"""

import json
import logging
from typing import Any, Dict, Optional
from src.mcp_client import MCPClient
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


class JenkinsAgent:
    """AI Agent that controls Jenkins using MCP and LLM"""

    SYSTEM_PROMPT = """You are a Jenkins AI Agent that helps users manage Jenkins jobs.

You have access to Jenkins tools through MCP (Model Context Protocol). Use these tools to:
- Check job status and information
- Trigger builds and deployments
- Monitor build progress
- View build history and logs
- Manage Jenkins resources

When a user asks to deploy or build a job:
1. First check the current status of the job
2. Inform the user about the status
3. Trigger the build
4. Monitor and report progress updates

Be proactive, informative, and provide real-time updates when possible.
Respond in Korean when the user writes in Korean."""

    def __init__(self, mcp_client: MCPClient, llm_client: LLMClient):
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.tools = []

    async def initialize(self):
        """Initialize the agent by connecting to MCP and loading tools"""
        await self.mcp_client.initialize()
        self.tools = await self.mcp_client.list_tools()
        logger.info(f"Agent ready with {len(self.tools)} Jenkins tools")

    async def process_message(self, user_message: str) -> str:
        """Process a user message and return the agent's response"""
        logger.debug(f"Processing: {user_message[:50]}...")

        llm_tools = self.mcp_client.get_tools_for_llm()
        max_iterations = 10
        iteration = 0

        response = self.llm_client.chat(
            message=user_message,
            tools=llm_tools,
            system_prompt=self.SYSTEM_PROMPT,
        )

        while iteration < max_iterations:
            iteration += 1

            if response["finish_reason"] == "stop":
                return response["content"] or "작업을 완료했습니다."

            if response["finish_reason"] == "tool_calls" and response["tool_calls"]:
                tool_results = []

                for tool_call in response["tool_calls"]:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments
                    tool_call_id = tool_call.id

                    try:
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                    except json.JSONDecodeError:
                        tool_args = {}

                    logger.info(f"Executing: {tool_name}")

                    try:
                        result = await self.mcp_client.call_tool(tool_name, tool_args)

                        if "result" in result:
                            tool_result = json.dumps(result["result"], ensure_ascii=False)
                        else:
                            tool_result = json.dumps(result, ensure_ascii=False)

                        tool_results.append({
                            "tool_call_id": tool_call_id,
                            "tool_name": tool_name,
                            "result": tool_result,
                        })

                    except Exception as e:
                        error_msg = f"Error executing {tool_name}: {str(e)}"
                        logger.error(error_msg)
                        tool_results.append({
                            "tool_call_id": tool_call_id,
                            "tool_name": tool_name,
                            "result": json.dumps({"error": error_msg}),
                        })

                if not tool_results:
                    break

                for tool_result in tool_results:
                    response = self.llm_client.chat_with_tool_result(
                        tool_call_id=tool_result["tool_call_id"],
                        tool_name=tool_result["tool_name"],
                        tool_result=tool_result["result"],
                        tools=llm_tools,
                        system_prompt=self.SYSTEM_PROMPT,
                    )

                continue

            break

        if iteration >= max_iterations:
            return "최대 반복 횟수에 도달했습니다. 작업을 계속하려면 다시 시도해주세요."

        return response.get("content") or "응답을 생성할 수 없습니다."

    async def process_message_with_streaming(self, user_message: str):
        """Process message and yield streaming updates

        Note: This provides streaming for simple responses.
        For complex tool-calling scenarios, falls back to non-streaming mode.
        """
        logger.debug(f"Processing with streaming: {user_message[:50]}...")

        llm_tools = self.mcp_client.get_tools_for_llm()

        # First, check if tool calling is needed
        response = self.llm_client.chat(
            message=user_message,
            tools=llm_tools,
            system_prompt=self.SYSTEM_PROMPT,
        )

        # If no tool calls needed, use streaming for the response
        if response["finish_reason"] == "stop" and not response["tool_calls"]:
            if response["content"]:
                yield response["content"]
            return

        # If tool calls are needed, process them
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            if response["finish_reason"] == "stop":
                if response["content"]:
                    yield response["content"]
                return

            if response["finish_reason"] == "tool_calls" and response["tool_calls"]:
                tool_results = []

                for tool_call in response["tool_calls"]:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments
                    tool_call_id = tool_call.id

                    try:
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                    except json.JSONDecodeError:
                        tool_args = {}

                    logger.info(f"Executing: {tool_name}")
                    yield f"\n[도구 실행 중: {tool_name}]\n"

                    try:
                        result = await self.mcp_client.call_tool(tool_name, tool_args)

                        if "result" in result:
                            tool_result = json.dumps(result["result"], ensure_ascii=False)
                        else:
                            tool_result = json.dumps(result, ensure_ascii=False)

                        tool_results.append({
                            "tool_call_id": tool_call_id,
                            "tool_name": tool_name,
                            "result": tool_result,
                        })

                    except Exception as e:
                        error_msg = f"Error executing {tool_name}: {str(e)}"
                        logger.error(error_msg)
                        yield f"\n[오류: {error_msg}]\n"
                        tool_results.append({
                            "tool_call_id": tool_call_id,
                            "tool_name": tool_name,
                            "result": json.dumps({"error": error_msg}),
                        })

                if not tool_results:
                    break

                # Process tool results
                for tool_result in tool_results:
                    response = self.llm_client.chat_with_tool_result(
                        tool_call_id=tool_result["tool_call_id"],
                        tool_name=tool_result["tool_name"],
                        tool_result=tool_result["result"],
                        tools=llm_tools,
                        system_prompt=self.SYSTEM_PROMPT,
                    )

                continue

            break

        if iteration >= max_iterations:
            yield "\n최대 반복 횟수에 도달했습니다. 작업을 계속하려면 다시 시도해주세요."
        elif response.get("content"):
            yield response["content"]
