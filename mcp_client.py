"""
MCP CLIENT — Connects to an MCP server and uses Claude as the AI brain
=======================================================================
This client:
  1. Connects to an MCP server (discovers tools automatically)
  2. Sends user messages to Claude along with available tools
  3. When Claude wants to use a tool, calls it via MCP
  4. Returns Claude's final answer

Run:
    python mcp_client.py mcp_server.py
"""

import os
import sys
import json
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    """
    An AI agent that connects to any MCP server,
    discovers its tools, and uses Claude to interact with them.
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.available_tools = []
        self.conversation_history = []

    # ──────────────────────────────────────────
    # STEP 1: Connect to an MCP server
    # ──────────────────────────────────────────

    async def connect_to_server(self, server_script_path: str):
        """
        Launch and connect to an MCP server.
        The server runs as a subprocess, and we talk to it via stdio.
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"

        # Configure stdio transport (server runs as a child process)
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )

        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport

        # Create an MCP session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialize the connection (handshake)
        await self.session.initialize()

        # Discover what tools the server has
        response = await self.session.list_tools()
        self.available_tools = response.tools

        print(f"\n{'='*60}")
        print(f"  Connected to MCP Server!")
        print(f"  Discovered {len(self.available_tools)} tools:")
        for tool in self.available_tools:
            desc = tool.description.split('\n')[0][:60] if tool.description else "No description"
            print(f"    - {tool.name}: {desc}")
        print(f"{'='*60}")

    # ──────────────────────────────────────────
    # STEP 2: Convert MCP tools → Claude format
    # ──────────────────────────────────────────

    def get_tools_for_claude(self):
        """
        MCP tools and Claude tools use slightly different formats.
        This converts MCP tool definitions into what Claude expects.
        """
        claude_tools = []
        for tool in self.available_tools:
            claude_tools.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            })
        return claude_tools

    # ──────────────────────────────────────────
    # STEP 3: The Agent Loop
    # ──────────────────────────────────────────

    async def process_message(self, user_message: str) -> str:
        """
        The core agent loop:
          1. Send user message + tools to Claude
          2. If Claude wants a tool → call it via MCP → send result back
          3. Repeat until Claude gives a final text answer
        """
        print(f"\n{'─'*60}")
        print(f"You: {user_message}")
        print(f"{'─'*60}")

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        claude_tools = self.get_tools_for_claude()
        loop_count = 0

        while True:
            loop_count += 1
            print(f"\n  [Round {loop_count} — Calling Claude API...]")

            response = self.anthropic.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=(
                    "You are a helpful assistant connected to an MCP server. "
                    "Use the available tools when needed. "
                    "You can chain multiple tools to answer complex questions. "
                    "Present results clearly and concisely."
                ),
                tools=claude_tools,
                messages=self.conversation_history,
            )

            print(f"  [Stop reason: {response.stop_reason}]")

            # ── Claude wants to use tool(s) ──
            if response.stop_reason == "tool_use":
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_args = block.input

                        print(f"\n  >>> MCP Tool Call: {tool_name}")
                        print(f"  >>> Arguments: {json.dumps(tool_args)}")

                        # *** KEY MCP DIFFERENCE ***
                        # Instead of running tool logic locally,
                        # we call it through the MCP session.
                        # The MCP server executes it and returns the result.
                        result = await self.session.call_tool(
                            tool_name, arguments=tool_args
                        )

                        result_text = ""
                        if result.content:
                            result_text = result.content[0].text
                        print(f"  >>> Result: {result_text[:200]}...")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text,
                        })

                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results,
                })

            # ── Claude is done ──
            else:
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                })

                print(f"\nAgent: {final_text}")
                return final_text

    # ──────────────────────────────────────────
    # STEP 4: Interactive chat loop
    # ──────────────────────────────────────────

    async def chat_loop(self):
        """Run an interactive chat session."""
        print("\n" + "=" * 60)
        print("  MCP AGENT — Interactive Chat")
        print("  Tools are auto-discovered from the MCP server.")
        print("  Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n\nYou: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                await self.process_message(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <path_to_server.py>")
        print("Example: python mcp_client.py mcp_server.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = MCPClient()

    try:
        await client.connect_to_server(server_path)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())