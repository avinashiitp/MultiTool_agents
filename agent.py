import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Define tools the agent can use
tools = [
    {
        "name": "calculator",
        "description": "Evaluates a math expression and returns the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression like '2 + 2'"
                }
            },
            "required": ["expression"]
        }
    }
]

# Tool logic
def run_tool(name, input_data):
    if name == "calculator":
        try:
            result = eval(input_data["expression"])
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    return "Unknown tool"

# Agent loop
def agent(user_message):
    print(f"\nUser: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system="You are a helpful assistant. Use tools when needed.",
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [Tool: {block.name}({block.input})]")
                    result = run_tool(block.name, block.input)
                    print(f"  [Result: {result}]")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"Agent: {block.text}")
            break

# Run the agent
if __name__ == "__main__":
    agent("What is time in india now?")
    agent("What is 2 to the power of 10?")