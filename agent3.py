import os
import json
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ──────────────────────────────────────────────
# 1. DEFINE TOOLS (menu for Claude)
# ──────────────────────────────────────────────

tools = [
    # Tool 1: Weather (free, no API key needed)
    {
        "name": "get_weather",
        "description": "Get current weather for any city. Returns temperature, humidity, wind speed, and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'London' or 'New York'"
                }
            },
            "required": ["city"]
        }
    },

    # Tool 2: Random Fact
    {
        "name": "get_random_fact",
        "description": "Get a random fun fact.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },

    # Tool 3: Dictionary — Word Definition
    {
        "name": "get_definition",
        "description": "Look up the definition of an English word using a dictionary API.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The English word to look up"
                }
            },
            "required": ["word"]
        }
    },

    # Tool 4: IP Geolocation (your public IP location)
    {
        "name": "get_my_location",
        "description": "Get the user's approximate location based on their public IP address.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },

    # Tool 5: GitHub User Info
    {
        "name": "get_github_user",
        "description": "Get public profile information about a GitHub user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "GitHub username, e.g. 'torvalds'"
                }
            },
            "required": ["username"]
        }
    },

    # Tool 6: Country Information
    {
        "name": "get_country_info",
        "description": "Get detailed information about a country: population, capital, currency, languages, region.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Country name, e.g. 'India' or 'Japan'"
                }
            },
            "required": ["country"]
        }
    }
]


# ──────────────────────────────────────────────
# 2. TOOL IMPLEMENTATIONS — Each hits a real URL
# ──────────────────────────────────────────────

def run_tool(name, input_data):
    """Execute the tool by calling an external API."""

    try:

        # ---- Tool 1: Weather ----
        # API: wttr.in (free, no key needed)
        if name == "get_weather":
            city = input_data["city"]
            url = f"https://wttr.in/{city}?format=j1"
            print(f"  [Hitting URL: {url}]")

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
            })

        # ---- Tool 2: Random Fact ----
        # API: uselessfacts.jsph.pl (free, no key needed)
        elif name == "get_random_fact":
            url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
            print(f"  [Hitting URL: {url}]")

            response = requests.get(url, timeout=10)
            data = response.json()
            return json.dumps({
                "fact": data["text"],
                "source": data.get("source", "unknown")
            })

        # ---- Tool 3: Dictionary ----
        # API: dictionaryapi.dev (free, no key needed)
        elif name == "get_definition":
            word = input_data["word"]
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            print(f"  [Hitting URL: {url}]")

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
                "meanings": meanings
            })

        # ---- Tool 4: IP Geolocation ----
        # API: ip-api.com (free, no key needed)
        elif name == "get_my_location":
            url = "http://ip-api.com/json/"
            print(f"  [Hitting URL: {url}]")

            response = requests.get(url, timeout=10)
            data = response.json()
            return json.dumps({
                "city": data.get("city"),
                "region": data.get("regionName"),
                "country": data.get("country"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
                "ip": data.get("query")
            })

        # ---- Tool 5: GitHub User ----
        # API: api.github.com (free, no key needed for public data)
        elif name == "get_github_user":
            username = input_data["username"]
            url = f"https://api.github.com/users/{username}"
            print(f"  [Hitting URL: {url}]")

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
                "profile_url": data["html_url"]
            })

        # ---- Tool 6: Country Info ----
        # API: restcountries.com (free, no key needed)
        elif name == "get_country_info":
            country = input_data["country"]
            url = f"https://restcountries.com/v3.1/name/{country}"
            print(f"  [Hitting URL: {url}]")

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return json.dumps({"error": f"Country '{country}' not found"})

            data = response.json()[0]

            # Extract currency info
            currencies = data.get("currencies", {})
            currency_list = [
                f"{v['name']} ({v.get('symbol', '?')})"
                for v in currencies.values()
            ]

            # Extract languages
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
                "area_km2": f"{data.get('area', 0):,} km²"
            })

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except requests.exceptions.Timeout:
        return json.dumps({"error": f"API request timed out for {name}"})
    except requests.exceptions.ConnectionError:
        return json.dumps({"error": f"Could not connect to API for {name}. Check your internet."})
    except Exception as e:
        return json.dumps({"error": f"Error in {name}: {str(e)}"})


# ──────────────────────────────────────────────
# 3. THE AGENT LOOP
# ──────────────────────────────────────────────

def agent(user_message, conversation_history=None):
    """Send a message to the agent and get a response."""

    print(f"\n{'='*60}")
    print(f"You: {user_message}")
    print(f"{'='*60}")

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": user_message})

    loop_count = 0

    while True:
        loop_count += 1
        print(f"\n  --- Round {loop_count}: Calling Claude API ---")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "You are a helpful assistant with access to live internet tools. "
                "Use the appropriate tool when the user asks about weather, word definitions, "
                "country info, GitHub profiles, their location, or wants a random fact. "
                "You can use multiple tools in one turn to answer complex questions. "
                "Always present the data in a clear, friendly way."
            ),
            tools=tools,
            messages=conversation_history,
        )

        print(f"  [Stop reason: {response.stop_reason}]")

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n  >>> Tool: {block.name}")
                    print(f"  >>> Input: {block.input}")

                    result = run_tool(block.name, block.input)

                    print(f"  >>> Result: {result[:200]}...")  # show first 200 chars

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            conversation_history.append({"role": "assistant", "content": response.content})
            conversation_history.append({"role": "user", "content": tool_results})

        else:
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAgent: {block.text}")

            conversation_history.append({"role": "assistant", "content": response.content})
            break

    return conversation_history


# ──────────────────────────────────────────────
# 4. INTERACTIVE CHAT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MULTI-TOOL AGENT (Live API Edition)")
    print("  ")
    print("  Available tools:")
    print("    - Weather       → 'What is the weather in Tokyo?'")
    print("    - Dictionary    → 'Define the word serendipity'")
    print("    - Country Info  → 'Tell me about India'")
    print("    - GitHub User   → 'Look up torvalds on GitHub'")
    print("    - My Location   → 'Where am I?'")
    print("    - Random Fact   → 'Give me a fun fact'")
    print("  ")
    print("  Type 'quit' to exit")
    print("=" * 60)

    history = []

    while True:
        user_input = input("\n\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        history = agent(user_input, history)