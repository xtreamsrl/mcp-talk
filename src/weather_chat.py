import asyncio
from contextlib import AsyncExitStack
import json
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from openai import OpenAI

######################## RUN IT USING ################################
# uv run --env-file=.env src/weather_chat.py src/mcp_server_mock.py
######################################################################
class CoolAIApplication:
    def __init__(self):
        # Initialize session and client objects
        self.client_session: ClientSession | None = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.openai_client: OpenAI = OpenAI()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py)
        """
            
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        # establishing bidirectional communication channel between your client application and the MCP server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio = stdio_transport[0] 
        write = stdio_transport[1]
        self.client_session: ClientSession = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        
        _ = await self.client_session.initialize()
            
        # List available tools
        response = await self.client_session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.client_session.list_tools()
        available_tools = [{
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.openai_client.responses.create(
            model="gpt-4o",
            input=messages,
            tools=available_tools,
            tool_choice="auto",
        )

        messages += response.output
        for item in response.output:
            print(item)
            if item.type == 'function_call':
                tool_name = item.name
                tool_args = item.arguments
                
                result: CallToolResult = await self.client_session.call_tool(tool_name, json.loads(tool_args))

                logging.info(f"Calling tool {tool_name} with args {tool_args} gave result {result}")

                messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        tool_name: result.content[0].text
                    })
                })

        response = self.openai_client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful assistant using the tools provided to answer the user's question.",
            input=messages
        )
        
        return response.output_text

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
                print("\n " + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.exit_stack:
            await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = CoolAIApplication()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())