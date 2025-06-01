from contextlib import AsyncExitStack

from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from typing import List
import asyncio
import nest_asyncio
import os

nest_asyncio.apply()

load_dotenv()


class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.exit_stack = AsyncExitStack()
        self.session: ClientSession = None
        self.anthropic = Anthropic(api_key=os.getenv("api_key"))
        self.available_tools: List[dict] = []
        self.sessions={}

    async def get_resource(self, resource_uri):
        session = self.sessions.get(resource_uri)

        # Fallback for papers URIs - try any papers resource session
        if not session and resource_uri.startswith("images://"):
            for uri, sess in self.sessions.items():
                if uri.startswith("images://"):
                    session = sess
                    break

        if not session:
            print(f"Resource '{resource_uri}' not found.")
            return

        try:
            result = await session.read_resource(uri=resource_uri)
            if result and result.contents:
                print(f"\nResource: {resource_uri}")
                print("Content:")
                print(result.contents[0].text)
            else:
                print("No content available.")
        except Exception as e:
            print(f"Error: {e}")

    async def process_query(self, query):
        messages = [{'role': 'user', 'content': query}]
        response = self.anthropic.messages.create(max_tokens=2024,
                                                  model='claude-3-7-sonnet-20250219',
                                                  tools=self.available_tools,
                                                  messages=messages)
        process_query = True
        while process_query:
            assistant_content = []
            for content in response.content:
                if content.type == 'text':
                    print(content.text)
                    assistant_content.append(content)
                    if (len(response.content) == 1):
                        process_query = False
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    messages.append({'role': 'assistant', 'content': assistant_content})
                    tool_id = content.id
                    tool_args = content.input
                    tool_name = content.name

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # Call a tool
                    # result = execute_tool(tool_name, tool_args)
                    result = await self.session.call_tool(tool_name, arguments=tool_args)
                    messages.append({"role": "user",
                                     "content": [
                                         {
                                             "type": "tool_result",
                                             "tool_use_id": tool_id,
                                             "content": result.content
                                         }
                                     ]
                                     })
                    response = self.anthropic.messages.create(max_tokens=2024,
                                                              model='claude-3-7-sonnet-20250219',
                                                              tools=self.available_tools,
                                                              messages=messages)

                    if (len(response.content) == 1 and response.content[0].type == "text"):
                        print(response.content[0].text)
                        process_query = False

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        print("Use @folders to see available books")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                if query.startswith('@'):
                    resource_uri = "images://folders"

                    await self.get_resource(resource_uri)
                    continue

                await self.process_query(query)
                print("\n")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server_and_run(self):

        async with sse_client("http://0.0.0.0:8001/sse") as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()

                # List available tools
                response = await session.list_tools()

                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

                resources_response = await session.list_resources()
                if resources_response and resources_response.resources:
                    for resource in resources_response.resources:
                        resource_uri = str(resource.uri)
                        self.sessions[resource_uri] = session

                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()


if __name__ == "__main__":
    asyncio.run(main())