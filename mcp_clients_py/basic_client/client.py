import os
import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )


    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])


    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.annotations.parameters,
            }
        } for tool in response.tools]

        # Initial Claude API call
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []
        assistant_message_content = []
        reasoning = response.choices[0].finish_reason

        #for content in response.choices[0].message.content:
        if reasoning == 'tool_calls' and response.choices[0].message.tool_calls:
            # select tool to be called
            tool_name = response.choices[0].message.tool_calls[0].function.name
            tool_args = response.choices[0].message.tool_calls[0].function.arguments
            # Execute tool call
            result = await self.session.call_tool(tool_name, json.loads(tool_args))
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            # assistant_message_content.append(content)
            # add tool call to messages
            # so that the LLM can see the tool call and the result
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": response.choices[0].message.tool_calls[0].id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_args
                        }
                    }
                ]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": response.choices[0].message.tool_calls[0].id,
                "content": result.content[0].text
            })

            # Get next response from Claude
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            final_text.append(response.choices[0].message.content)
        else:
            final_text.append(response.choices[0].message.content)
            assistant_message_content.append(response.choices[0].message)
            
        return "\n".join(final_text)
    

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()



async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())
