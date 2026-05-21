import json
import os
from openai import OpenAI

from app.llm.base_service import LLMService

from app.llm.models.openai_response import OpenAIResponse

from app.llm.openai_mapper import OpenAIContextMapper
from app.llm.models.models import ContextRoleItem, ContextItem, ContextToolOutputItem

from app.llm.models.openai_response import Tool

MODEL = "" # TODO add respective model name
MAX_TOKENS = 1000
ENDPOINT = "" # TODO add azure endpoint
MAX_STEPS = 5 # maximum agentic loop iterations

class OpenAIService(LLMService):
    """Handles the communication between the OpenAI Chat Completion API and the MCP tool execution."""

    def __init__(self):
        # api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_key = os.getenv("not empty")
        # if not api_key:
        #     raise RuntimeError(
        #         "AZURE_OPENAI_API_KEY environment variable is empty."
        #     )
        
        # self.openai = OpenAI(
        #     api_key=api_key,
        #     base_url=ENDPOINT
        # )

        self.openai = OpenAI(
            api_key="not empty",
            base_url="not empty"
        )

        self.adapter = OpenAIContextMapper()
        self.context = []

    async def process(self, context_item: ContextItem, available_tools: list = None) -> OpenAIResponse:

        # TODO handle if the instance is not any of the specified subclsses
        
        item: ContextItem = None
        if isinstance(context_item, ContextRoleItem):
            item = await self.adapter.serialize_context_role_item(context_item)
        elif isinstance(context_item, ContextToolOutputItem):
            item = await self.adapter.serialize_context_tool_output_item(context_item)

        print(f"DEBUG: LLM process: {item}")

        self.context.append(item)

        serialize_tools = await self.adapter.serialize_tools(available_tools) if available_tools else None

        function_call: Tool = None       
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

                for content_item in output_item.content: # if the response contains multiple "output_text" items
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
                function_call = Tool(
                    name = output_item.name, 
                    args = json.loads(output_item.arguments or "{}")
                )

                self.context.append(
                    {
                        "role": "assistant",
                        "tool_calls": output_item
                    }
                )

        return OpenAIResponse(response = assisstent_response_text, function_call = function_call)