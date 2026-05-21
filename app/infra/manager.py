import json

from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dataclasses import dataclass
from enum import Enum

class ItemType(Enum):
    TOOL = "tool"
    RESOURCE = "resource"

@dataclass(frozen=True)
class ItemKey:
    type: ItemType
    name: str

class MCPManager:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = {}

    async def __aenter__(self):
        await self._connect_to_servers()
        return self
    
    async def __aexit__(self, *_):
        await self.exit_stack.aclose()

    async def _connect_to_server(self, server_name, server_config) -> ClientSession:
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            # read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            # client_session = await self.exit_stack.enter_async_context(ClientSession(read, write))

            await session.initialize()

            print(f"DEBUG: _connect_to_server: about to map the server session {session}")
            await self._map_server_primitives_to_session(session)
            await self._notify_server_connection_successful(server_name, session)

            return session
        except Exception as e:
            raise RuntimeError(f"Error trying to connect to MCP Server {server_name}: {e}")
    
    async def _map_server_primitives_to_session(self, session: ClientSession):
        try:
            # tools
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"DEBUG: _map_server_primitives_to_session: Mapping tool {tool.name} to session {session}")
                self.sessions[ItemKey(ItemType.TOOL, tool.name)] = session
                    
            # resources
            resources_response = await session.list_resources()
            if resources_response and resources_response.resources:
                for resource in resources_response.resources:
                    resource_uri = str(resource.uri)
                    print(f"DEBUG: _map_server_primitives_to_session: Mapping resource {resource_uri} to session {session}")
                    self.sessions[ItemKey(ItemType.RESOURCE, resource_uri)] = session
        
        except Exception as e:
            print(f"Error mapping the server primitives to the respective client session: {e}")
    
    async def _connect_to_servers(self):
        print(f"DEBUG: Inside _connect_to_servers")
        try:
            with open("app/infra/server_config.json", "r") as file:
                data = json.load(file)
            servers = data.get("servers", {})
            print(f"DEBUG: _connect_to_servers > {servers}")
            for server_name, server_config in servers.items():
                print(f"DEBUG: _connect_to_servers > Connecting to server {server_name}, {server_config}")
                await self._connect_to_server(server_name, server_config)

            for session_item in self.sessions:
                print(f"DEBUG: _connect_to_servers > Session item: {session_item}")
        except Exception as e:
            raise RuntimeError(f"Error loading the server configuration file: {e}")

    async def get_tools(self) -> list:
        tools = []

        for session in self.sessions.values():
            tools.extend(await session.list_tools())

        return tools
    
    async def call_tool(self, tool_name, tool_args):
        session = self.sessions[tool_name]

        if not session:
            raise ValueError(f"No session found for tool with name: {tool_name}")

        try:
            log = f"[Log: Calling tool with name = {tool_name} and args = {tool_args}]]"
            result = await session.call_tool(tool_name, tool_args)
            content = result.content[0].text if result.content else ""
        except Exception as e:
            content = f"Error: {e}"
            log = f"[{content}]"

        # TODO Return an object not a Tuple
        return (content, log)
    
    async def get_resource(self, resource_uri: str) -> str:
        """
        Gets the content of a receipt pdf file as a base64 encoded string.
        
        Args:
            resource_uri: a resource uri exposed from the mcp-server for a specific resource.

        Returns: the content of the pdf file in a base64 encoded string.
        """

        session = await self._get_session(type = ItemType.RESOURCE, name = resource_uri)
        
        try:
            print(f"\nRequesting the resource: {resource_uri}")
            result = await session.read_resource(uri=resource_uri)
            if result and result.contents:
                return result.contents[0].text
            else:
                print("No content available.")
        except Exception as e:
            print(f"Error: {e}")

    async def _get_session(self, type: ItemType, name: str) -> ClientSession:
        session = self.sessions[ItemKey(type, name)]

        if not session:
            raise ValueError(f"No session found for {name}")
        
        return session
        
    async def _notify_server_connection_successful(self, server_name, session):
        print(f"\n- MCP Server: {server_name} successfully connected")

        try:
            tools_response = await session.list_tools()
            if tools_response and tools_response.tools:
                print("\n----- Tools: ", [tool.name for tool in tools_response.tools])

            resources_response = await session.list_resources()
            if resources_response and resources_response.resources:
                print(f"\n----- Resources: ", [resource.name for resource in resources_response.resources])

            prompts_response = await session.list_prompts()
            if prompts_response and prompts_response.prompts:
                print(f"\n----- Prompts: ", [prompt.name for prompt in prompts_response.prompts])
        except Exception as e:
            print(f"Error {e}")