import asyncio
from mcp import Client


async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools.tools:
            print(" -", tool.name)

        result = await client.call_tool("check_availability", {"date": "2026-09-20"})
        print("\ncheck_availability result:", result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())