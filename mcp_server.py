"""
MCP SERVER — Exposes tools via Model Context Protocol
=====================================================
This server exposes tools that any MCP client can discover and use.
Tools are defined with simple Python decorators — no JSON schemas needed.

Run this server:
    python mcp_server.py
"""

import json
import requests
from datetime import datetime
from mcp.server.fastmcp import FastMCP


# ──────────────────────────────────────────────
# 1. CREATE THE MCP SERVER
# ──────────────────────────────────────────────

mcp = FastMCP(
    name="MultiToolServer",
    instructions="A multi-tool server providing weather, dictionary, country info, GitHub lookup, and utility tools."
)


# ──────────────────────────────────────────────
# 2. DEFINE TOOLS (each is a simple function)
# ──────────────────────────────────────────────

# --- Tool 1: Weather ---
@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for any city. Returns temperature, humidity, wind speed, and conditions.

    Args:
        city: City name, e.g. 'London' or 'New York' or 'Bangalore'
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        data = response.json()
        current = data["current_condition"][0]
        return json.dumps({
            "city": city,
            "temperature_c": current["temp_C"],
            "temperature_f": current["temp_F"],
            "feels_like_c": current["FeelsLikeC"],
            "humidity": current["humidity"] + "%",
            "wind_speed_kmph": current["windspeedKmph"],
            "condition": current["weatherDesc"][0]["value"],
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool 2: Dictionary ---
@mcp.tool()
def get_definition(word: str) -> str:
    """Look up the definition of an English word.

    Args:
        word: The English word to look up, e.g. 'serendipity'
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return json.dumps({"error": f"Word '{word}' not found"})

        data = response.json()[0]
        meanings = []
        for meaning in data.get("meanings", []):
            part = meaning["partOfSpeech"]
            defs = [d["definition"] for d in meaning["definitions"][:2]]
            meanings.append({"part_of_speech": part, "definitions": defs})

        return json.dumps({
            "word": word,
            "phonetic": data.get("phonetic", "N/A"),
            "meanings": meanings,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool 3: Country Info ---
@mcp.tool()
def get_country_info(country: str) -> str:
    """Get detailed information about a country including population, capital, currency, and languages.

    Args:
        country: Country name, e.g. 'India' or 'Japan' or 'Brazil'
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return json.dumps({"error": f"Country '{country}' not found"})

        data = response.json()[0]
        currencies = data.get("currencies", {})
        currency_list = [f"{v['name']} ({v.get('symbol', '?')})" for v in currencies.values()]
        languages = list(data.get("languages", {}).values())

        return json.dumps({
            "name": data["name"]["common"],
            "official_name": data["name"]["official"],
            "capital": data.get("capital", ["N/A"])[0],
            "population": f"{data.get('population', 0):,}",
            "region": data.get("region"),
            "subregion": data.get("subregion"),
            "currencies": currency_list,
            "languages": languages,
            "flag_emoji": data.get("flag", ""),
            "area_km2": f"{data.get('area', 0):,} km²",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool 4: GitHub User ---
@mcp.tool()
def get_github_user(username: str) -> str:
    """Get public profile information about a GitHub user.

    Args:
        username: GitHub username, e.g. 'torvalds' or 'gvanrossum'
    """
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return json.dumps({"error": f"User '{username}' not found"})

        data = response.json()
        return json.dumps({
            "username": data["login"],
            "name": data.get("name", "N/A"),
            "bio": data.get("bio", "N/A"),
            "public_repos": data["public_repos"],
            "followers": data["followers"],
            "following": data["following"],
            "location": data.get("location", "N/A"),
            "created_at": data["created_at"],
            "profile_url": data["html_url"],
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool 5: Calculator ---
@mcp.tool()
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result.

    Args:
        expression: A math expression like '2 + 2' or '(42 * 17) + (99 / 3)' or '2 ** 10'
    """
    try:
        result = eval(expression)
        return json.dumps({"expression": expression, "result": str(result)})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool 6: Date & Time ---
@mcp.tool()
def get_datetime(query: str = "full") -> str:
    """Get the current date, time, or day of the week.

    Args:
        query: What to return — 'date', 'time', 'day', or 'full' for everything
    """
    now = datetime.now()
    if query == "date":
        return json.dumps({"date": now.strftime('%B %d, %Y')})
    elif query == "time":
        return json.dumps({"time": now.strftime('%I:%M %p')})
    elif query == "day":
        return json.dumps({"day": now.strftime('%A')})
    else:
        return json.dumps({"full": now.strftime('%A, %B %d, %Y at %I:%M %p')})


# ──────────────────────────────────────────────
# 3. DEFINE RESOURCES (data the client can read)
# ──────────────────────────────────────────────

@mcp.resource("info://server/about")
def server_about() -> str:
    """Information about this MCP server and its available tools."""
    return json.dumps({
        "name": "MultiToolServer",
        "version": "1.0.0",
        "tools": [
            "get_weather - Live weather for any city",
            "get_definition - English dictionary lookup",
            "get_country_info - Country facts and data",
            "get_github_user - GitHub profile lookup",
            "calculator - Math expression evaluator",
            "get_datetime - Current date and time",
        ],
    }, indent=2)


# ──────────────────────────────────────────────
# 4. DEFINE PROMPTS (reusable templates)
# ──────────────────────────────────────────────

@mcp.prompt()
def research_country(country: str) -> str:
    """Generate a prompt to research a country comprehensively."""
    return (
        f"Please research {country} thoroughly. Use the available tools to:\n"
        f"1. Get country information (capital, population, languages, currency)\n"
        f"2. Get the current weather in the capital city\n"
        f"3. Present all findings in a clear, organized summary."
    )


# ──────────────────────────────────────────────
# 5. RUN THE SERVER
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting MCP Server: MultiToolServer")
    print("Tools: weather, dictionary, country, github, calculator, datetime")
    mcp.run(transport="stdio")