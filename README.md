# 🤖 Multi-Tool AI Agent

A Python-based AI agent powered by Claude (Anthropic) that can autonomously decide which tools to use, chain multiple tools together, and fetch live data from external APIs — all through a simple interactive chat interface.

## What is an AI Agent?

Unlike a regular chatbot that only generates text from memory, an **agent** can take actions. It follows a loop:

1. You ask a question
2. The AI decides which tool(s) to use
3. Your code executes the tool and returns results
4. The AI reads the results and decides if it needs more tools
5. Once satisfied, it gives you the final answer

This project demonstrates that loop with real, working tools.

## Available Tools

| Tool | API Source | Example Prompt |
|------|-----------|----------------|
| 🌤 Weather | [wttr.in](https://wttr.in) | *"What's the weather in Tokyo?"* |
| 📖 Dictionary | [dictionaryapi.dev](https://dictionaryapi.dev) | *"Define the word serendipity"* |
| 🌍 Country Info | [restcountries.com](https://restcountries.com) | *"Tell me about India"* |
| 👤 GitHub User | [api.github.com](https://api.github.com) | *"Look up torvalds on GitHub"* |
| 📍 My Location | [ip-api.com](http://ip-api.com) | *"Where am I?"* |
| 🎲 Random Fact | [uselessfacts.jsph.pl](https://uselessfacts.jsph.pl) | *"Give me a fun fact"* |

All external APIs are **free and require no API keys**.

## Project Structure

```
multi-tool-agent/
├── .env               ← Your API key goes here (never commit this)
├── .gitignore         ← Keeps secrets and junk out of Git
├── agent.py           ← Simple agent with local tools (calculator, todo, etc.)
├── agent_api.py       ← Advanced agent with live API tools (weather, GitHub, etc.)
├── requirements.txt   ← Python dependencies
├── venv/              ← Virtual environment (auto-generated)
└── README.md          ← You are here
```

## Prerequisites

- **Python 3.9+** installed on your machine
- **VS Code** (recommended) or any code editor
- An **Anthropic API key** (see Configuration below)

---

## ⚙️ Configuration — API Key Setup

> **IMPORTANT:** This project requires an Anthropic API key to function. The agent calls Claude's API to power the AI reasoning, and this requires a valid key with billing credits.

### Step 1: Get Your API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **Settings → API Keys**
4. Click **Create Key** and copy it immediately (you can only see it once)
5. Go to **Settings → Billing** and add a payment method / credits

Your key will look like this: `sk-ant-api03-xxxxxxxxxxxxxxxxxxxx`

### Step 2: Create the `.env` File

Create a file named `.env` in the project root directory:

```env
ANTHROPIC_API_KEY=sk-ant-api03-paste-your-real-key-here
```

**Rules for the `.env` file:**
- No quotes around the key
- No spaces before or after the `=` sign
- No blank lines after the key
- The file must be named exactly `.env` (with the dot)

### Step 3: Verify Your Key Loads Correctly

Run this command to confirm the key is being read:

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); key=os.environ.get('ANTHROPIC_API_KEY','NOT FOUND'); print(key[:20]+'...' if len(key)>20 else key)"
```

You should see the first 20 characters of your key printed.

### 🔒 Security Warning

- **NEVER** commit your `.env` file to GitHub
- **NEVER** hardcode your API key directly in Python files
- **NEVER** share your API key publicly
- The included `.gitignore` file already excludes `.env` — do not remove that entry

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-tool-agent.git
cd multi-tool-agent
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install anthropic python-dotenv requests
```

### 4. Set Up Your API Key

Create the `.env` file as described in the Configuration section above.

### 5. Run the Agent

**Simple agent (local tools):**
```bash
python agent.py
```

**API agent (live internet tools):**
```bash
python agent_api.py
```

---

## Usage Examples

Once the agent is running, try these prompts:

**Single tool usage:**
```
You: What's the weather in Bangalore?
You: Define the word "ephemeral"
You: Tell me about Japan
You: Look up torvalds on GitHub
```

**Multi-tool chaining (the agent calls multiple tools automatically):**
```
You: What's the weather in the capital of France?
```
The agent will: call Country Info → learn capital is Paris → call Weather for Paris → give combined answer.

```
You: Where am I and what's the weather there?
```
The agent will: call Location → get your city → call Weather for that city → respond.

**Type `quit` to exit.**

---

## How It Works

The core agent loop:

```
┌─────────────────────────────────────────────┐
│  User asks a question                       │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  Send question + tool definitions to Claude │
└──────────────────┬──────────────────────────┘
                   ▼
          ┌────────────────┐
          │ Claude responds │
          └───────┬────────┘
                  ▼
        ┌───────────────────┐
        │ stop_reason =  ?  │
        └───┬───────────┬───┘
            ▼           ▼
      "tool_use"    "end_turn"
            │           │
            ▼           ▼
    ┌──────────────┐  ┌──────────────────┐
    │ Run the tool │  │ Print the answer │
    │ (call API)   │  │ Break the loop   │
    └──────┬───────┘  └──────────────────┘
           ▼
    ┌──────────────────┐
    │ Send result back │
    │ to Claude        │
    └──────┬───────────┘
           │
           └──── Loop back to top
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError: invalid x-api-key` | API key is wrong or placeholder | Check your `.env` file has a real key |
| `No such file or directory: agent.py` | Terminal is in the wrong folder | Run `cd` to the project folder first |
| `ModuleNotFoundError: anthropic` | Package not installed | Run `pip install anthropic` |
| `ModuleNotFoundError: dotenv` | Package not installed | Run `pip install python-dotenv` |
| `ConnectionError` for tool APIs | No internet or API is down | Check your internet connection |
| `DeprecationWarning` for model | Model string is outdated | Update the model string in the code |

---

## Extending the Agent

To add a new tool:

1. **Define it** — Add a new entry to the `tools` list with a name, description, and input schema
2. **Implement it** — Add an `elif name == "your_tool":` block in `run_tool()` that calls an API
3. **Update the system prompt** — Mention the new tool so Claude knows when to use it

Free APIs you could add:
- [Open Trivia DB](https://opentdb.com/api_config.php) — Quiz questions
- [PokeAPI](https://pokeapi.co) — Pokémon data
- [JokeAPI](https://jokeapi.dev) — Random jokes
- [NewsAPI](https://newsapi.org) — Headlines (requires free key)
- [ExchangeRate-API](https://www.exchangerate-api.com) — Currency conversion

---

## Tech Stack

- **Python 3.9+**
- **Anthropic SDK** — Claude API client
- **python-dotenv** — Environment variable management
- **requests** — HTTP client for API calls

---

## License

MIT License — feel free to use, modify, and distribute.

---

## Acknowledgments

Built with [Claude](https://www.anthropic.com/claude) by Anthropic.
