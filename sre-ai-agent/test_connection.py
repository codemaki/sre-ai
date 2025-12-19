"""Test MCP connection and tool listing"""

import asyncio
import logging
import sys
from src.config import settings
from src.mcp_client import MCPClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_mcp_connection():
    """Test MCP connection and list available tools"""
    try:
        print("\n" + "=" * 60)
        print("  MCP Connection Test")
        print("=" * 60)
        print(f"Jenkins MCP URL: {settings.jenkins_mcp_url}")
        print("=" * 60 + "\n")

        mcp_client = MCPClient(
            base_url=settings.jenkins_mcp_url,
            auth_token=settings.jenkins_mcp_token,
        )

        print("✅ Step 1: Initializing MCP session...")
        init_result = await mcp_client.initialize()
        print(f"   Session initialized: {init_result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")

        print("\n✅ Step 2: Listing available tools...")
        tools = await mcp_client.list_tools()
        print(f"   Found {len(tools)} tools:\n")

        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool.name}")
            print(f"      {tool.description}")
            print()

        print("=" * 60)
        print("✅ MCP Connection Test Passed!")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MCP Connection Test Failed!")
        print("=" * 60)
        logger.error(f"Error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)
