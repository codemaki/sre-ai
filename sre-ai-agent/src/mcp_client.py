"""MCP Client for Jenkins - Streamable HTTP implementation"""

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPClient:
    """Client for communicating with Jenkins MCP server via Streamable HTTP"""

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session_id: Optional[str] = None
        self.request_id = 0
        self.tools: List[MCPTool] = []

    def _get_headers(self, streaming: bool = False) -> Dict[str, str]:
        """Get HTTP headers including authorization"""
        headers = {
            "Authorization": f"Basic {self.auth_token}",
            "Content-Type": "application/json",
        }
        if streaming:
            headers["Accept"] = "text/event-stream"
        else:
            headers["Accept"] = "text/event-stream, application/json"

        # Include session ID if we have one
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        return headers

    def _next_request_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id

    def _parse_sse_response(self, text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response format"""
        lines = text.strip().split('\n')
        data_lines = []

        for line in lines:
            if line.startswith('data: '):
                data_lines.append(line[6:])  # Remove 'data: ' prefix

        if data_lines:
            json_data = '\n'.join(data_lines)
            return json.loads(json_data)

        # If no data lines found, try to parse as regular JSON
        return json.loads(text)

    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP session"""
        logger.info("Initializing MCP session...")

        request_data = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {},
                },
                "clientInfo": {
                    "name": "jenkins-ai-agent",
                    "version": "0.1.0",
                },
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json=request_data,
                timeout=30.0,
            )
            response.raise_for_status()

            # Parse SSE response
            result = self._parse_sse_response(response.text)

            # Save session ID if provided
            if "mcp-session-id" in response.headers:
                self.session_id = response.headers["mcp-session-id"]
                logger.debug(f"Session ID: {self.session_id}")

            logger.info("MCP session initialized successfully")
            return result

    async def list_tools(self) -> List[MCPTool]:
        """List available tools from MCP server"""
        request_data = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json=request_data,
                timeout=30.0,
            )
            response.raise_for_status()

            # Parse SSE response
            result = self._parse_sse_response(response.text)

            if "result" in result and "tools" in result["result"]:
                self.tools = [MCPTool(**tool) for tool in result["result"]["tools"]]
                logger.info(f"Loaded {len(self.tools)} Jenkins tools")
                return self.tools
            else:
                logger.warning(f"Unexpected tools/list response")
                return []

    async def call_tool(
        self, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool and return the result"""
        logger.debug(f"Calling tool: {tool_name}")

        request_data = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json=request_data,
            )
            response.raise_for_status()

            # Parse SSE response
            result = self._parse_sse_response(response.text)
            return result

    async def call_tool_streaming(
        self, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Call a tool with streaming response"""
        logger.debug(f"Calling tool (streaming): {tool_name}")

        request_data = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }

        headers = self._get_headers(streaming=True)

        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                self.base_url,
                headers=headers,
                json=request_data,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip():
                            try:
                                data = json.loads(data_str)
                                yield data
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE data: {data_str}")

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI-compatible tool format"""
        llm_tools = []
        for tool in self.tools:
            llm_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            })
        return llm_tools
