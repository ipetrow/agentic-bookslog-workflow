import json
import os

from anthropic import AnthropicFoundry

from .base_service import LLMService
from .models.llm_response import ToolUse
from .models.llm_response import LLMResponse
from .models.models import ContextRoleItem, ContextItem, ContextToolOutputItem
from .anthropic_mapper import AnthropicContextMapper

MODEL = "" # TODO add respective model name
MAX_TOKENS = 1000
ENDPOINT = "" # TODO add azure endpoint

class AnthropicService(LLMService):
    """Handles the communication between the Anthropic Claude Message API and the MCP tool execution."""

    def __init__(self):
        api_key = os.getenv("AZURE_ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "AZURE_ANTHROPIC_API_KEY environment variable is empty."
            )
        
        self.anthropic = AnthropicFoundry(
            api_key=api_key,
            base_url=ENDPOINT
        )

        self.adapter = AnthropicContextMapper()
        self.context = []

    async def process(self, context_item: ContextItem, available_tools: list = None) -> LLMResponse:
        """
        Handles a request to the Anthropic Claude Message API.

        Args:
            context_item: the context item which will be appened to the context history (contains e.g., prompt, tools response).
            available_tools: the available tools the execution of which the LLM might request.

        Returns:
            The response from the Anthropic request. 
        """

        item: ContextItem = None
        if isinstance(context_item, ContextRoleItem):
            item = await self.adapter.serialize_context_role_item(context_item)
        elif isinstance(context_item, ContextToolOutputItem):
            item = await self.adapter.serialize_context_tool_output_item(context_item)

        self.context.append(item)

        serialized_tools = await self.adapter.serialize_tools(available_tools) if available_tools else []

        tool_use: ToolUse = None       
        assisstent_response_text = None
        try:
            response = self.anthropic.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    tools=serialized_tools,
                    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
                    messages=self.context
                )
        except Exception as ex:
            print(f"Exception: {ex}")
        
        self.context.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        # hadle all output items
        for content_item in response.content:
            
            # handle text/message if present
            if content_item.type == "text":
                assisstent_response_text = content_item.text
            elif content_item.type == "tool_use" and response.stop_reason == "tool_use": # handle a tool call request if present
                tool_use = ToolUse(
                    tool_name = content_item.name, 
                    tool_args = content_item.input,
                    call_id = content_item.id
                )
       
        return LLMResponse(
            response = assisstent_response_text, 
            tool_use = tool_use
        )