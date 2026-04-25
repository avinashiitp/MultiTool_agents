# 🤖 Multi-Tool AI Agent with MCP

A Python-based AI agent powered by Claude (Anthropic) that evolves across five levels — from a single-tool agent, to multi-tool, to live API tools, to a full **MCP (Model Context Protocol)** architecture where tools are discovered automatically.

---

## 🧠 What is an AI Agent?

Unlike a regular chatbot that only generates text from memory, an **agent** can take actions. It follows a loop:

1. You ask a question
2. The AI decides which tool(s) to use
3. Your code executes the tool and returns results
4. The AI reads the results and decides if it needs more tools
5. Once satisfied, it gives you the final answer

This project builds that loop step by step — from simple to advanced.

---

## 📁 Project Structure

```
MultiTool_agents/
├── .env               ← Your API key goes here (never commit this)
├── .env.example       ← API key template
├── .gitignore         ← Keeps secrets and junk out of Git
├── requirements.txt   ← Python dependencies
├── README.md          ← You are here
│
├── agent.py           ← Level 1: Single tool (calculator only)
├── agent2.py          ← Level 2: 5 local tools (calculator, todo, datetime, text analyzer, converter)
├── agent3.py          ← Level 3: 6 live API tools (weather, GitHub, dictionary, country, location, facts)
│
├── mcp_server.py      ← Level 4: MCP server (exposes tools via protocol)
└── mcp_client.py      ← Level 4: MCP client (discovers & uses tools automatically)
```

---

## 🚀 Evolution — Five Levels

### Level 1 — `agent.py` — Single Tool Agent

The simplest possible agent. One tool (calculator), one loop. Start here to understand the fundamentals.

```bash
python agent.py
```

**What it does:** Hardcoded to run two questions — calculates math expressions using a single calculator tool.

**Tools:** calculator

**Key concept:** The agent loop — `question → Claude decides → tool runs → result back → final answer`

---

### Level 2 — `agent2.py` — Multi-Tool Agent (Local)

Same loop, but now Claude has 5 tools to choose from and an interactive chat interface.

```bash
python agent2.py
```

**Tools:** calculator, to-do list, date/time, text analyzer, unit converter

**Key concept:** Claude reads tool descriptions and **autonomously decides** which tool to use. It can chain multiple tools in one question.

**Try:**
```
You: What is 2 to the power of 16?
You: Add "buy groceries" to my todo
You: Convert 100 fahrenheit to celsius
You: How many words are in "the quick brown fox"?
You: What day is it today and what is 42 * 17?
```

---

### Level 3 — `agent3.py` — Live API Agent

Tools no longer run locally — they hit **real URLs on the internet** and return live data.

```bash
python agent3.py
```

**Tools:**

| Tool | API Source | Example |
|------|-----------|---------|
| 🌤 Weather | [wttr.in](https://wttr.in) | *"What's the weather in Tokyo?"* |
| 📖 Dictionary | [dictionaryapi.dev](https://dictionaryapi.dev) | *"Define serendipity"* |
| 🌍 Country Info | [restcountries.com](https://restcountries.com) | *"Tell me about India"* |
| 👤 GitHub User | [api.github.com](https://api.github.com) | *"Look up torvalds on GitHub"* |
| 📍 My Location | [ip-api.com](http://ip-api.com) | *"Where am I?"* |
| 🎲 Random Fact | [uselessfacts.jsph.pl](https://uselessfacts.jsph.pl) | *"Give me a fun fact"* |

All external APIs are **free and require no API keys**.

**Key concept:** Your code is just the middleman — it receives Claude's request, forwards it to the right URL, and sends the response back.

**Try multi-tool chaining:**
```
You: What's the weather in the capital of France?
```
Agent will: Country Info → Paris → Weather for Paris → combined answer.

---

### Level 4 — `mcp_server.py` + `mcp_client.py` — MCP Architecture

Tools are separated into a **server**. The **client** discovers them automatically at runtime — zero hardcoded tool definitions in the client.

```bash
python mcp_client.py mcp_server.py
```

You don't run the server separately — the client launches it as a subprocess.

**Key concept:** The client knows NOTHING about tools in advance. It connects to the server, asks "what tools do you have?", and gets back a list. Swap the server = different tools, zero client changes.

---

## 🔌 What is MCP?

**Model Context Protocol (MCP)** is an open standard by Anthropic. Think of it as **USB-C for AI**.

### The Shift

| Level 1-3 (without MCP) | Level 4 (with MCP) |
|--------------------------|---------------------|
| Tools hardcoded in agent | Tools discovered at runtime |
| Adding a tool = editing agent code | Adding a tool = editing server only |
| One agent = one set of tools | Any client connects to any server |
| Tight coupling | Loose coupling |

### How MCP Works

```
┌─────────────────┐    stdio    ┌─────────────────┐       ┌──────────┐
│                 │◄───────────►│                 │──────►│  APIs    │
│   MCP Client    │             │   MCP Server    │       │  wttr.in │
│                 │             │                 │       │  github  │
│  • Claude API   │  discover   │  • Tool logic   │       │  etc.    │
│  • Agent loop   │────────────►│  • Resources    │       └──────────┘
│  • Chat UI      │  call tools │  • Prompts      │
│                 │────────────►│                 │
└─────────────────┘             └─────────────────┘

Client knows NOTHING        Server knows EVERYTHING
about tools in advance.     about tools.
```

### MCP Flow

1. Client launches `mcp_server.py` as a subprocess
2. Handshake → Client asks "What tools do you have?"
3. Server responds with 6 tool schemas
4. User asks a question
5. Client sends question + discovered tools → Claude API
6. Claude picks a tool → Client calls `session.call_tool()` via MCP
7. Server executes → returns result
8. Loop continues until Claude gives final answer

---

## ⚙️ Configuration — API Key Setup

> **⚠️ IMPORTANT:** This project requires an **Anthropic API key** with billing credits.

### Step 1: Get Your API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **Settings → API Keys**
4. Click **Create Key** and copy it immediately
5. Go to **Settings → Billing** and add a payment method

### Step 2: Create the `.env` File

```bash
cp .env.example .env
```

Edit `.env` and paste your real key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-paste-your-real-key-here
```

**Rules:** No quotes. No spaces around `=`. File named exactly `.env`.

### Step 3: Verify

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); k=os.environ.get('ANTHROPIC_API_KEY','NOT FOUND'); print(k[:20]+'...')"
```

### 🔒 Security

- **NEVER** commit `.env` to GitHub
- **NEVER** hardcode API keys in Python files
- The `.gitignore` already excludes `.env`

---

## 📦 Installation

```bash
git clone https://github.com/avinashiitp/MultiTool_agents.git
cd MultiTool_agents
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your real Anthropic API key
```

---

## ▶️ Quick Start

```bash
# Level 1 — Single tool
python agent.py

# Level 2 — 5 local tools (interactive chat)
python agent2.py

# Level 3 — 6 live API tools (interactive chat)
python agent3.py

# Level 4 — MCP (auto-discovery)
python mcp_client.py mcp_server.py
```

Type `quit` to exit any interactive agent.

---

## 🛠 Adding New Tools

### Level 2 & 3 — Manual (3 steps)

1. Add tool definition to the `tools` list
2. Add `elif name == "your_tool":` in `run_tool()`
3. Update the system prompt

### Level 4 — MCP (1 step)

Add a function in `mcp_server.py`:

```python
@mcp.tool()
def get_joke() -> str:
    """Get a random programming joke."""
    r = requests.get("https://official-joke-api.appspot.com/jokes/programming/random", timeout=10)
    joke = r.json()[0]
    return json.dumps({"setup": joke["setup"], "punchline": joke["punchline"]})
```

Client discovers it automatically. **No client changes.**

---

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `AuthenticationError: invalid x-api-key` | Check `.env` has your real key + billing credits |
| `No such file or directory` | `cd` to the project folder first |
| `ModuleNotFoundError: anthropic` | Run `pip install -r requirements.txt` |
| `ModuleNotFoundError: mcp` | Run `pip install mcp` |
| `ConnectionError` for API tools | Check your internet connection |

---

## 📚 Learn More

- [MCP Documentation](https://modelcontextprotocol.io)
- [Anthropic API Docs](https://docs.anthropic.com)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## Tech Stack

- **Python 3.9+**
- **Anthropic SDK** — Claude API client
- **MCP SDK** — Model Context Protocol
- **python-dotenv** — Environment variables
- **requests** — HTTP client for API calls

---

## License

MIT License — free to use, modify, and distribute.

---

Built with [Claude](https://www.anthropic.com/claude) by Anthropic.
