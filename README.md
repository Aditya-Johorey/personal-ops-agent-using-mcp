# Personal Ops Agent — MCP + LangGraph

A personal operations agent that manages Google Calendar, Gmail, and a local task
tracker through a **hand-built MCP (Model Context Protocol) server**, connected to a
**LangGraph agent** running fully local, open-weight models via **Ollama**. The agent
has persistent, cross-session memory via **Mem0**, and gates risky actions (sending
email, creating calendar events) behind explicit human approval.

This project was built as a learning exercise in the MCP ecosystem: writing a custom
MCP server from scratch (rather than consuming a pre-built integration), understanding
transports (stdio vs. streamable HTTP), connecting a LangGraph agent as an MCP client,
adding memory, and implementing human-in-the-loop safety gates.

## Architecture

```
┌─────────────────┐   streamable HTTP    ┌──────────────────────┐
│  LangGraph Agent │ ───────────────────► │   Custom MCP Server   │
│  (agent/agent.py)│ ◄─────────────────── │ (mcp_server/server.py)│
└────────┬─────────┘                      └──────────┬───────────┘
         │                                            │
         │                                  ┌─────────┼─────────┐
         ▼                                  ▼         ▼         ▼
  ┌─────────────┐                    ┌───────────┐ ┌──────┐ ┌────────┐
  │    Mem0      │                   │  Google    │ │ Gmail│ │ Local  │
  │ (Qdrant, on- │                   │  Calendar  │ │ API  │ │ tasks. │
  │  disk vector │                   │    API     │ │      │ │ json   │
  │    store)    │                   └───────────┘ └──────┘ └────────┘
  └─────────────┘
         ▲
         │
┌────────┴─────────┐
│  Ollama (local)   │
│  - gemma4:12b     │  ← chat / tool-calling model
│  - llama3.1:8b    │  ← Mem0 fact-extraction model
│  - nomic-embed-   │  ← embedding model
│    text           │
└───────────────────┘
```

## Tools exposed by the MCP server

| Tool | Description | Risk level |
|---|---|---|
| `check_availability` | Checks free time slots on a given date/duration against real Google Calendar free/busy data | Safe — read-only |
| `create_event` | Creates a real event on the user's Google Calendar, with optional attendees | **Risky — requires human approval** |
| `add_task` | Adds a task to the local task tracker | Safe — local write |
| `list_tasks` | Lists current tasks | Safe — read-only |
| `send_email` | Sends a real email via the user's Gmail account | **Risky — requires human approval** |

## Tech stack

- **MCP Python SDK v2** (`mcp>=2.0`) — the MCP server itself, all five tools defined via `@mcp.tool()`
- **LangChain 1.4+ / LangGraph** — agent orchestration, `create_agent`, `HumanInTheLoopMiddleware`
- **`langchain.mcp.MCPAdapter`** — native LangChain MCP client (streamable HTTP transport)
- **Ollama** — fully local LLM inference (no cloud API keys required)
  - `gemma4:12b` — primary conversational/tool-calling model
  - `llama3.1:8b` — used internally by Mem0 for fact extraction (more reliable structured JSON output than Gemma 4 for this specific role)
  - `nomic-embed-text` — embedding model for semantic memory search
- **Mem0** (`mem0ai`) — persistent, cross-session semantic memory, backed by an embedded/on-disk **Qdrant** vector store (no Docker/server required)
- **Google Calendar API** + **Gmail API** — real read/write access via OAuth2 (`google-api-python-client`, `google-auth-oauthlib`)
- **LangSmith** — automatic tracing of every LLM call, tool call, and agent reasoning step (enabled via `LANGSMITH_TRACING=true`)

## Project structure

```
OpsAgentMCP/
├── agent/
│   ├── agent.py              # LangGraph agent, REPL loop, HITL handling
│   └── memory.py             # Mem0 wrapper (add_memory / search_memory)
├── mcp_server/
│   ├── server.py             # MCP server entrypoint, tool definitions
│   ├── google_auth.py        # Shared Google OAuth (Calendar + Gmail scopes)
│   ├── google_calendar.py    # check_availability, create_event logic
│   ├── gmail.py               # send_email logic
│   └── tasks.py               # add_task, list_tasks (local JSON store)
├── data/
│   └── tasks.json             # local task storage
├── requirements.txt
└── .gitignore
```

The following are required to run the project but are **not committed** (see
`.gitignore`) — you create/generate them yourself per the setup steps below:
- `.env` — LangSmith + timezone config
- `credentials/client_secret.json` — your own Google OAuth client secret
- `token.json` — auto-generated on first Google login
- `data/qdrant_storage/` — Mem0's local vector store, auto-generated at runtime

## Setup

### 1. Prerequisites
- Python **3.11+** (3.10 does not support LangGraph's `interrupt()` inside async code — this is a hard requirement, not a suggestion)
- [Ollama](https://ollama.com) installed
- A Google Cloud project with the Calendar API and Gmail API enabled

### 2. Clone and set up the environment
```powershell
git clone https://github.com/Aditya-Johorey/personal-ops-agent-using-mcp.git
cd OpsAgentMCP
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Pull the required Ollama models
```powershell
ollama pull gemma4:12b
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 4. Google OAuth setup
1. In [Google Cloud Console](https://console.cloud.google.com), create a project, enable the **Calendar API** and **Gmail API**.
2. Configure the OAuth consent screen (External user type is fine for personal use). **Publish the app** (Testing mode refresh tokens expire every 7 days).
3. Create an **OAuth client ID** of type **Desktop app**, download the JSON, save it as `credentials/client_secret.json`.

### 5. Environment variables
Create a `.env` file in the project root:
```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=ops-agent-mcp
USER_TIMEZONE=Asia/Kolkata
```

### 6. Run it
In one terminal, start the MCP server:
```powershell
python mcp_server/server.py
```
This will open a browser window for Google OAuth on first run, then print `Google auth OK` and start listening on `http://127.0.0.1:8000/mcp`.

In a second terminal, start the agent:
```powershell
python agent/agent.py
```

## Human-in-the-loop approval

`create_event` and `send_email` are gated by `HumanInTheLoopMiddleware`. When the agent
decides to call either tool, execution pauses and the CLI asks for explicit approval or
rejection before anything real happens. Safe, read-only or local-only tools
(`check_availability`, `add_task`, `list_tasks`) execute without interruption.

## Known limitations / lessons learned

- **Local models vary significantly in structured-output reliability.** Mem0's fact
  extraction silently failed (returned empty results with no error) when using
  `gemma4:12b` as the extraction LLM, despite Gemma 4 working well as the main chat
  model. Switching extraction specifically to `llama3.1:8b` fixed it — a good example
  of how "conversationally capable" and "reliably structured" are different
  capabilities that don't always come from the same model.
- **`mem0ai[extras]` is not lightweight.** It pulls in `sentence-transformers`,
  `torch`, `transformers`, `boto3`, and `elasticsearch` as dependencies, which can
  silently downgrade an already-working `langchain`/`langchain-core` install via pip's
  dependency resolver. Installing `fastembed` standalone (for BM25 support) avoids
  this entirely.
- **Python 3.10 cannot run LangGraph's `interrupt()` inside async code** — context
  variables aren't propagated across `await` boundaries until Python 3.11. This
  project requires 3.11+.
- **Google OAuth apps in "Testing" mode issue refresh tokens that expire after 7
  days.** Publishing the app (no verification needed for personal use) avoids
  needing to re-authenticate weekly.
- **VRAM matters a lot for local model speed.** An 8-9GB model on an 8GB GPU forces a
  CPU/GPU split, which is dramatically slower than full GPU residency.

## Possible next steps
- Move task storage from flat JSON to SQLite
- Support arbitrary-start-time scheduling in `check_availability` (currently checks a
  fixed set of candidate start times, not any free window in the day)
- Add `edit` as a HITL decision option (currently only approve/reject)
- Deploy the MCP server over streamable HTTP on a persistent host, rather than
  localhost-only
