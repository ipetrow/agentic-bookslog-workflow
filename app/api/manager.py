import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .models.models import ItemKey, ItemType, ToolCallResponse

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
        """
        Established a MCP Client-Server connection.

        Args:
            server_name: the name of the server to which a connection will be stablished.
            server_config: the server configuration information used for connecting to the server.
        
        Returns:
            A client session.
        """
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

            await self._map_server_primitives_to_session(session)
            await self._notify_server_connection_successful(server_name, session)

            return session
        except Exception as e:
            raise RuntimeError(f"Error trying to connect to MCP Server {server_name}: {e}")
    
    async def _map_server_primitives_to_session(self, session: ClientSession):
        """
        Maps the available server primitives (tools, resources) to their respective client session.

        Args:
            session: The client session to which the server primitives will be mapped.
        """
        try:
            # tools
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                self.sessions[ItemKey(ItemType.TOOL, tool.name)] = session
                    
            # resources
            resources_response = await session.list_resources()
            if resources_response and resources_response.resources:
                for resource in resources_response.resources:
                    resource_uri = str(resource.uri)
                    self.sessions[ItemKey(ItemType.RESOURCE, resource_uri)] = session
        
        except Exception as e:
            print(f"Error mapping the server primitives to the respective client session: {e}")
    
    async def _connect_to_servers(self):
        """Reads the server configuration files and established all the MCP Client-Server connections."""

        try:
            with open("app/api/server_config.json", "r") as file:
                data = json.load(file)
            servers = data.get("servers", {})
            for server_name, server_config in servers.items():
                await self._connect_to_server(server_name, server_config)

        except Exception as e:
            raise RuntimeError(f"Error loading the server configuration file: {e}")

    async def get_tools(self) -> list:
        """
        Returns a list of all the tools available in all the started client sessions. 

        Returns:
            A list of all the available tools.
        """

        tools = []

        unique_sessions = set(self.sessions.values())

        for session in unique_sessions:
            tools_response = await session.list_tools()
            tools.extend(tools_response.tools)

        return tools
    
    async def call_tool(self, tool_name, tool_args) -> ToolCallResponse:
        """
        Executes a tool by specified name and arguments.
        
        Args:
            tool_name: The name of the tool that will be executed.
            tool_args: The required arguments of the tool that will be executed.
        Returns:
            The tool response - the content and logs.
        """

        session = self.sessions[ItemKey(ItemType.TOOL, tool_name)]

        if not session:
            raise ValueError(f"No session found for tool with name: {tool_name}")

        try:
            log = f"[Log: Calling tool with name = {tool_name} and args = {tool_args}]]"
            result = await session.call_tool(tool_name, tool_args)
            content = result.content[0].text if result.content else ""
        except Exception as e:
            content = f"Error: {e}"
            log = f"[{content}]"

        return ToolCallResponse(content = content, log = log)
    
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
        """
        Returns the corresponding session to the specified server primitive item type (tool, resource).

        Args:
            type: The type of the server primitive.
            name: The session name.

        Returns:
            A client session.
        """

        session = self.sessions[ItemKey(type, name)]

        if not session:
            raise ValueError(f"No session found for {name}")
        
        return session
        
    async def _notify_server_connection_successful(self, server_name, session):
        """
        Notifies when a successful connection to a server is established by listing all its available primitives.

        Args:
            server_name: The sever name to which a connection is established.
            session: The client session corresponding to the server.
        """

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