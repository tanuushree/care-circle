import asyncio
from fastmcp import Client


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    async with Client(MCP_SERVER_URL) as client:
        tools = await client.list_tools()

        print("Connected to Care Circle MCP server!")
        print()
        print("Available tools:")

        for tool in tools:
            print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())