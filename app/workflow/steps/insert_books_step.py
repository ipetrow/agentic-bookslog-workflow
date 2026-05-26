from app.api.manager import MCPManager
from app.api.models.models import ToolCallResponse
from app.domain.book import Book
from app.llm.openai_service import OpenAIService
from app.llm.models.models import (
    ContextRoleItem, 
    TextContent, 
    ContextToolOutputItem
)
from app.llm.models.openai_response import OpenAIResponse

from ..exceptions import WorkflowExecutionError
from ..prompts.prompts import get_insert_book_prompt, get_insert_books_prompt

MAX_STEPS = 5 # maximum agentic loop iterations

class InsertBooksStep:
     
    def __init__(self, model: OpenAIService, mcp: MCPManager):
        self.model = model
        self.mcp = mcp

    async def run(self, books: list[Book]):
        available_tools = await self.mcp.get_tools()

        responses: list[OpenAIResponse] = []

        prompt = get_insert_books_prompt(books)

        context_item = ContextRoleItem(
            role="user",
            content=[
                TextContent(
                    text=prompt
                )
            ]
        )

        for _ in range(MAX_STEPS):
            response: OpenAIResponse = await self.model.process(context_item=context_item, available_tools=available_tools)

            tool_call = response.function_call
            if not tool_call: # no function calls - agentic loop termination
                responses.append(response.response)
                break
            
            tool_result: ToolCallResponse = await self.mcp.call_tool(tool_name = tool_call.tool_name, tool_args = tool_call.tool_args)

            responses.append(tool_result.log)

            context_item = ContextToolOutputItem(
                tool_call_id=tool_call.call_id,
                tool_output=tool_result.content
            )
        else:
            raise WorkflowExecutionError("The maximum allowed interactions with the agent has been reached!") 
            
        return "\n".join(responses)