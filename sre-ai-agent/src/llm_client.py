"""LLM Client for Azure OpenAI"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Azure OpenAI"""

    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str,
        deployment: str,
    ):
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )
        self.deployment = deployment
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
        })

    def chat(
        self,
        message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a chat message and get response"""
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.extend(self.conversation_history)
        messages.append({
            "role": "user",
            "content": message,
        })

        try:
            kwargs = {
                "model": self.deployment,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            completion = self.client.chat.completions.create(**kwargs)

            response_message = completion.choices[0].message

            # Add user message to history
            self.add_message("user", message)

            # Only add assistant text responses to history
            # Don't store tool_calls in history to avoid compatibility issues
            if response_message.content and not response_message.tool_calls:
                self.add_message("assistant", response_message.content)

            return {
                "content": response_message.content,
                "tool_calls": response_message.tool_calls,
                "finish_reason": completion.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise

    def chat_streaming(
        self,
        message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ):
        """Send a chat message and get streaming response"""
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.extend(self.conversation_history)
        messages.append({
            "role": "user",
            "content": message,
        })

        try:
            kwargs = {
                "model": self.deployment,
                "messages": messages,
                "stream": True,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            stream = self.client.chat.completions.create(**kwargs)

            # Add user message to history
            self.add_message("user", message)

            # Yield streaming chunks
            full_content = ""
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_content += delta.content
                        yield delta.content

            # Add complete response to history
            if full_content:
                self.add_message("assistant", full_content)

        except Exception as e:
            logger.error(f"Error calling LLM with streaming: {e}")
            raise

    def chat_with_tool_result(
        self,
        tool_call_id: str,
        tool_name: str,
        tool_result: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Continue conversation with tool execution result"""
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        # Use full conversation history for better context
        messages.extend(self.conversation_history)

        # Add tool result as user message
        # Azure OpenAI supports "tool" role, but user role is more compatible
        messages.append({
            "role": "user",
            "content": f"도구 '{tool_name}' 실행 결과:\n{tool_result}\n\n위 결과를 바탕으로 사용자에게 답변해주세요.",
        })

        try:
            kwargs = {
                "model": self.deployment,
                "messages": messages,
            }

            # Azure OpenAI supports tools parameter in follow-up calls
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            completion = self.client.chat.completions.create(**kwargs)

            response_message = completion.choices[0].message

            if response_message.content:
                self.add_message("assistant", response_message.content)

            return {
                "content": response_message.content,
                "tool_calls": response_message.tool_calls,
                "finish_reason": completion.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Error calling LLM with tool result: {e}")
            raise

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
