from dotenv import load_dotenv
load_dotenv()  # must run BEFORE importing langchain/langgraph, so env vars are set first

from langchain_ollama import ChatOllama
from langsmith import traceable

llm = ChatOllama(model="gemma4:12b")

@traceable(name="test_ollama_call")
def ask(question: str) -> str:
    response = llm.invoke(question)
    return response.content

if __name__ == "__main__":
    answer = ask("In one sentence, what is MCP in the context of AI agents?")
    print(answer)