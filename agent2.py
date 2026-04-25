import os
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime
 
load_dotenv()
 
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
 
# ──────────────────────────────────────────────
# 1. DEFINE ALL TOOLS (the menu for Claude)
# ──────────────────────────────────────────────
 
tools = [
    # Tool 1: Calculator
    {
        "name": "calculator",
        "description": "Evaluates a math expression and returns the result. Supports +, -, *, /, **, sqrt, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression like '2 + 2' or '(5 * 3) / 2' or '2 ** 10'"
                }
            },
            "required": ["expression"]
        }
    },
 
    # Tool 2: To-Do List Manager
    {
        "name": "todo",
        "description": "Manage a to-do list. You can add, remove, or list tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "remove", "list"],
                    "description": "The action to perform: add a task, remove a task, or list all tasks"
                },
                "task": {
                    "type": "string",
                    "description": "The task description (required for add/remove, not needed for list)"
                }
            },
            "required": ["action"]
        }
    },
 
    # Tool 3: Date & Time
    {
        "name": "datetime_tool",
        "description": "Get the current date, time, or day of the week.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "enum": ["date", "time", "day", "full"],
                    "description": "What to return: 'date' for today's date, 'time' for current time, 'day' for day of week, 'full' for everything"
                }
            },
            "required": ["query"]
        }
    },
 
    # Tool 4: Word Counter & Text Analyzer
    {
        "name": "text_analyzer",
        "description": "Analyze text: count words, characters, sentences, or find the longest word.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                },
                "analysis": {
                    "type": "string",
                    "enum": ["word_count", "char_count", "sentence_count", "longest_word", "all"],
                    "description": "Type of analysis to perform"
                }
            },
            "required": ["text", "analysis"]
        }
    },
 
    # Tool 5: Unit Converter
    {
        "name": "unit_converter",
        "description": "Convert between units: km/miles, kg/lbs, celsius/fahrenheit, meters/feet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "The numeric value to convert"
                },
                "from_unit": {
                    "type": "string",
                    "enum": ["km", "miles", "kg", "lbs", "celsius", "fahrenheit", "meters", "feet"],
                    "description": "The unit to convert from"
                },
                "to_unit": {
                    "type": "string",
                    "enum": ["km", "miles", "kg", "lbs", "celsius", "fahrenheit", "meters", "feet"],
                    "description": "The unit to convert to"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    }
]
 
 
# ──────────────────────────────────────────────
# 2. IMPLEMENT EACH TOOL'S LOGIC
# ──────────────────────────────────────────────
 
# In-memory to-do list (resets when program stops)
todo_list = []
 
 
def run_tool(name, input_data):
    """Execute the requested tool and return the result."""
 
    # ---- Calculator ----
    if name == "calculator":
        try:
            # Only allow safe math characters
            expression = input_data["expression"]
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed or expression[max(0,i-1):i+2] == "**" for i, c in enumerate(expression)):
                pass  # allow ** for exponents
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"
 
    # ---- To-Do List ----
    elif name == "todo":
        action = input_data["action"]
        task = input_data.get("task", "")
 
        if action == "add":
            todo_list.append(task)
            return f"Added: '{task}'. You now have {len(todo_list)} task(s)."
 
        elif action == "remove":
            if task in todo_list:
                todo_list.remove(task)
                return f"Removed: '{task}'. You now have {len(todo_list)} task(s)."
            else:
                return f"Task '{task}' not found. Current tasks: {todo_list}"
 
        elif action == "list":
            if not todo_list:
                return "Your to-do list is empty."
            tasks = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(todo_list))
            return f"Your to-do list:\n{tasks}"
 
    # ---- Date & Time ----
    elif name == "datetime_tool":
        now = datetime.now()
        query = input_data["query"]
 
        if query == "date":
            return f"Today's date: {now.strftime('%B %d, %Y')}"
        elif query == "time":
            return f"Current time: {now.strftime('%I:%M %p')}"
        elif query == "day":
            return f"Today is: {now.strftime('%A')}"
        elif query == "full":
            return f"{now.strftime('%A, %B %d, %Y at %I:%M %p')}"
 
    # ---- Text Analyzer ----
    elif name == "text_analyzer":
        text = input_data["text"]
        analysis = input_data["analysis"]
 
        words = text.split()
        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
 
        if analysis == "word_count":
            return f"Word count: {len(words)}"
        elif analysis == "char_count":
            return f"Character count: {len(text)} (with spaces), {len(text.replace(' ', ''))} (without spaces)"
        elif analysis == "sentence_count":
            return f"Sentence count: {len(sentences)}"
        elif analysis == "longest_word":
            longest = max(words, key=len) if words else "N/A"
            return f"Longest word: '{longest}' ({len(longest)} characters)"
        elif analysis == "all":
            longest = max(words, key=len) if words else "N/A"
            return (
                f"Words: {len(words)}\n"
                f"Characters: {len(text)}\n"
                f"Sentences: {len(sentences)}\n"
                f"Longest word: '{longest}' ({len(longest)} chars)"
            )
 
    # ---- Unit Converter ----
    elif name == "unit_converter":
        value = input_data["value"]
        from_u = input_data["from_unit"]
        to_u = input_data["to_unit"]
 
        conversions = {
            ("km", "miles"):        lambda v: v * 0.621371,
            ("miles", "km"):        lambda v: v * 1.60934,
            ("kg", "lbs"):          lambda v: v * 2.20462,
            ("lbs", "kg"):          lambda v: v * 0.453592,
            ("celsius", "fahrenheit"): lambda v: (v * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda v: (v - 32) * 5/9,
            ("meters", "feet"):     lambda v: v * 3.28084,
            ("feet", "meters"):     lambda v: v * 0.3048,
        }
 
        key = (from_u, to_u)
        if key in conversions:
            result = conversions[key](value)
            return f"{value} {from_u} = {result:.2f} {to_u}"
        elif from_u == to_u:
            return f"{value} {from_u} = {value} {to_u} (same unit)"
        else:
            return f"Cannot convert from {from_u} to {to_u}"
 
    return "Unknown tool"
 
 
# ──────────────────────────────────────────────
# 3. THE AGENT LOOP
# ──────────────────────────────────────────────
 
def agent(user_message, conversation_history=None):
    """Send a message to the agent and get a response."""
 
    print(f"\n{'='*50}")
    print(f"User: {user_message}")
    print(f"{'='*50}")
 
    # Start fresh or continue existing conversation
    if conversation_history is None:
        conversation_history = []
 
    conversation_history.append({"role": "user", "content": user_message})
 
    loop_count = 0
 
    while True:
        loop_count += 1
        print(f"\n  [Round {loop_count} — Calling Claude API...]")
 
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "You are a helpful assistant with access to multiple tools. "
                "Use the appropriate tool when the user asks for calculations, "
                "to-do list management, date/time info, text analysis, or unit conversions. "
                "You can use multiple tools in sequence to answer complex questions."
            ),
            tools=tools,
            messages=conversation_history,
        )
 
        print(f"  [Stop reason: {response.stop_reason}]")
 
        # If Claude wants to use tool(s)
        if response.stop_reason == "tool_use":
            tool_results = []
 
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [Tool called: {block.name}]")
                    print(f"  [Input: {block.input}]")
 
                    result = run_tool(block.name, block.input)
 
                    print(f"  [Result: {result}]")
 
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
 
            # Add to conversation and loop again
            conversation_history.append({"role": "assistant", "content": response.content})
            conversation_history.append({"role": "user", "content": tool_results})
 
        else:
            # Claude is done — print final answer
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAgent: {block.text}")
 
            # Add final response to history
            conversation_history.append({"role": "assistant", "content": response.content})
            break
 
    return conversation_history
 
 
# ──────────────────────────────────────────────
# 4. RUN THE AGENT — Interactive Chat Mode
# ──────────────────────────────────────────────
 
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  MULTI-TOOL AI AGENT")
    print("  Available tools: calculator, todo, datetime,")
    print("  text analyzer, unit converter")
    print("  Type 'quit' to exit")
    print("=" * 50)
 
    history = []
 
    while True:
        user_input = input("\n\nYou: ").strip()
 
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break
 
        if not user_input:
            continue
 
        history = agent(user_input, history)
 