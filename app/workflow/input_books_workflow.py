import os
import json

from app.llm.openai_service import OpenAIService
from app.llm.models.models import (
    ContextRoleItem, 
    TextContent, 
    FileContent, 
    ContextToolOutputItem,
)

from app.infra.manager import MCPManager

from app.workflow.exceptions import WorkflowNoModelResponseError, WorkflowExecutionError
from app.workflow.prompts.prompts import EXTRACT_BOOK_DATA_PROMPT, get_insert_book_prompt

RESOURCE_URI = "file://receipts/receipt-001.pdf"
MAX_STEPS = 5 # maximum agentic loop iterations

class InputBooksWorkflow:

    def __init__(self, model: OpenAIService, mcp: MCPManager):
        self.model = model
        self.mcp = mcp

    async def extract_books_data(self) -> dict:
        resource_name = os.path.basename(RESOURCE_URI)
        resource_base64 = await self.mcp.get_resource(RESOURCE_URI)

        item = ContextRoleItem(
            role="user",
            content=[
                TextContent(
                    text=EXTRACT_BOOK_DATA_PROMPT
                ),
                FileContent(
                    file_name=resource_name,
                    file_base64=resource_base64
                )
            ]
        )

        books_response = await self.model.process(context_item=item)

        books_dict = json.load("{ 'books': [{'isbn': 1, 'title': 'Title 1', 'author': 'Author 1', 'pages': 111}, {'isbn': 2, 'title': 'Title 2', 'author': 'Author 2', 'pages': 111}]}")
        # books_dict = json.load(books_response.response)
        print(f"DEBUG: {books_dict}")

        if not books_dict:
            raise WorkflowNoModelResponseError("No books were successfully extracted!")

        return books_dict
    
    async def insert_books(self, books: dict):
        # TODO use pydantic with a book model to create book object and call step 2 with them instead of dict.

        available_tools = self.mcp.get_tools()

        responses = []

        for book in books["books"]:
            update_db_prompt = get_insert_book_prompt(
                isbn = book["isbn"], 
                title = book["title"], 
                author = book["author"], 
                pages_num = book["pages"]
            )

            item2 = ContextRoleItem(
                role="user",
                content=[
                    TextContent(
                        text=update_db_prompt
                    )
                ]
            )

            for _ in range(MAX_STEPS):
                response1 = await self.model.process(context_item=item2, available_tools=available_tools)

                if not response1.has_function_call: # no function calls - agentic loop termination
                    break

                tool_result = await self.mcp.call_tool(response1)
                responses.append(tool_result[1])

                item3 = ContextToolOutputItem(
                    tool_call_id=response1.call_id,
                    tool_output=tool_result[0]
                )
                response2 = await self.model.process(context_item=item3, available_tools=available_tools)
                
                responses.append(response2)
            else:
                raise WorkflowExecutionError("The maximum allowed interactions with the agent has been reached!") 

        return "\n".join(responses)

    async def run(self):
        print(f"DEBUG: WF run: STEP 1")
        
        # Step 1: Extract books from PDF receipt
        book_dict = await self.extract_books_data()

        print(f"DEBUG: WF run: STEP 2")
        # Step 2: Input extracted new books into the database
        return await self.insert_books(book_dict)
        
        

