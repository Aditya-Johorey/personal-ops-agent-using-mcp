import asyncio

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_ollama import ChatOllama

from memory import add_memory, search_memory

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"

SYSTEM_PROMPT = """You are a personal operations assistant. You help the user manage \
their calendar, tasks, and email using the tools available to you.

Guidelines:
- Use tools whenever a request requires real data (checking availability, listing tasks) \
  or a real action (creating an event, sending an email) — never guess or fabricate \
  information you could look up.
- Before creating a calendar event or sending an email, restate the key details (date, \
  time, recipient, subject) back to the user in your response so they can catch mistakes.
- Be concise and direct.
- If a request is ambiguous (e.g. missing a date or recipient), ask a clarifying question \
  instead of guessing.
- You may be given "Relevant memories" from past conversations — use them if helpful, \
  but do not mention the word "memory" explicitly unless the user asks what you remember.
"""


async def main():
    llm = ChatOllama(model="gemma4:12b")

    async with MCPAdapter(MCP_SERVER_URL) as adapter:
        tools = await adapter.list_tools()
        print(f"Loaded {len(tools)} tools from MCP server")
        for tool in tools:
            print(" -", tool.name)

        agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

        print("\nAgent ready. Type your requests (or 'quit' to exit).\n")
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in ("quit", "exit"):
                break

            # Pull relevant past facts and inject them as context for this turn only.
            relevant = search_memory(user_input)
            if relevant:
                memory_context = "Relevant memories: " + "; ".join(relevant)
                messages.append({"role": "user", "content": f"{user_input}\n\n[{memory_context}]"})
            else:
                messages.append({"role": "user", "content": user_input})

            result = await agent.ainvoke({"messages": messages})

            reply = result["messages"][-1]
            print("Agent:", reply.content)

            messages = result["messages"]
            add_memory(user_message=user_input, assistant_message=reply.content)


if __name__ == "__main__":
    asyncio.run(main())