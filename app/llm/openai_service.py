import json
import os

from openai import OpenAI

from .base_service import LLMService
from .models.llm_response import ToolUse
from .models.llm_response import LLMResponse
from .models.models import ContextRoleItem, ContextItem, ContextToolOutputItem
from .openai_mapper import OpenAIContextMapper

MODEL = "" # TODO add respective model name
MAX_TOKENS = 1000
ENDPOINT = "" # TODO add azure endpoint
MAX_STEPS = 5 # maximum agentic loop iterations

class OpenAIService(LLMService):
    """Handles the communication between the OpenAI Chat Completion API and the MCP tool execution."""

    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "AZURE_OPENAI_API_KEY environment variable is empty."
            )
        
        self.openai = OpenAI(
            api_key=api_key,
            base_url=ENDPOINT
        )

        self.adapter = OpenAIContextMapper()
        self.context = []

    async def process(self, context_item: ContextItem, available_tools: list = None) -> LLMResponse:
        """
        Handles a request to the OpenAI API.

        Args:
            context_item: the context item which will be appened to the context history (contains e.g., prompt, tools response).
            available_tools: the available tools the execution of which the LLM might request.

        Returns:
            The response from the OpenAI request. 
        """

        item: ContextItem = None
        if isinstance(context_item, ContextRoleItem):
            item = await self.adapter.serialize_context_role_item(context_item)
        elif isinstance(context_item, ContextToolOutputItem):
            item = await self.adapter.serialize_context_tool_output_item(context_item)

        self.context.append(item)

        serialize_tools = await self.adapter.serialize_tools(available_tools) if available_tools else None

        function_call: ToolUse = None       
        assisstent_response_text = None
        response = self.openai.responses.create(
                model=MODEL, 
                max_output_tokens=MAX_TOKENS, 
                input=self.context,
                tools=serialize_tools
            )
        
        # hadle all output items
        for output_item in response.output:
            
            # handle text/message if present
            if output_item.type == "message":
                for content_item in output_item.content:
                    if content_item.type == "output_text":
                        assisstent_response_text = content_item.text
                
                if assisstent_response_text:
                    self.context.append(
                        {
                            "role": "assistant",
                            "content": assisstent_response_text
                        }
                    )
            elif output_item.type == "function_call": # handle a tool call request if present
                function_call = ToolUse(
                    tool_name = output_item.name, 
                    tool_args = json.loads(output_item.arguments or "{}"),
                    call_id = output_item.call_id
                )

                self.context.append(
                    {
                        "type": "function_call",
                        "call_id": output_item.call_id, 
                        "name": output_item.name,
                        "arguments": output_item.arguments or {}
                    }
                )
       
        return LLMResponse(
            response = assisstent_response_text, 
            tool_use = function_call
        )