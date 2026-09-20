import os
os.environ["MEM0_TELEMETRY"] = "False"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from mem0 import Memory

USER_ID = "primary_user"  # single-user project, so this is just a fixed identifier

MEM0_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": "data/qdrant_storage",
            "collection_name": "ops_agent_memory",
            "embedding_model_dims": 768,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:8b",
            "temperature": 0,
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434",
        },
    },
}

_memory = Memory.from_config(MEM0_CONFIG)

def add_memory(user_message:str, assistant_message:str) -> None:
    """Extract and store any durable facts from this exchange."""
    _memory.add(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ],
        user_id=USER_ID,
    )

def search_memory(query: str, limit: int = 5) -> list[str]:
    """Retrieve facts relevant to the current query."""
    results = _memory.search(query, filters={"user_id": USER_ID}, limit=limit)
    return [r["memory"] for r in results.get("results", results)]