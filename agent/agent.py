import asyncio

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_ollama import ChatOllama

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"

async def main():
    llm = ChatOllama(model = "gemma4:12b")

    async with MCPAdapter(MCP_SERVER_URL) as adapter:
        tools = await adapter.list_tools()
        print(f"Loaded {len(tools)} tools from MCP server")
        for tool in tools:
            print(" -", tool.name)

        agent  = create_agent(llm, tools)

        print("\nAgent ready. Type your requests (or 'quit' to exit).\n")
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in ("quit", "exit"):
                break

            messages.append({"role": "user", "content": user_input})
            result = await agent.ainvoke({"messages": messages})

            reply = result["messages"][-1]
            print("Agent:", reply.content)

            messages = result["messages"]

if __name__ == "__main__":
    asyncio.run(main())