import os
import json

from app.api.manager import MCPManager
from app.domain.book import Book
from app.llm.openai_service import OpenAIService
from app.llm.models.models import (
    ContextRoleItem, 
    TextContent, 
    FileContent, 
)
from app.llm.models.llm_response import LLMResponse

from ..exceptions import WorkflowNoModelResponseError
from ..prompts.prompts import EXTRACT_BOOK_DATA_PROMPT

RESOURCE_URI = "file://receipts/receipt-001.pdf"
BOOKS_RESPONSE_ROOT = "books"

class ExtractBooksDataStep:
     
    def __init__(self, model: OpenAIService, mcp: MCPManager):
        self.model = model
        self.mcp = mcp

    async def run(self) -> dict:
        """
        Executes a workflow step that extracts books' data from a file.
        
        Returns:
            A list of extracted books.
        """

        resource_name = os.path.basename(RESOURCE_URI)
        resource_base64 = await self.mcp.get_resource(RESOURCE_URI)

        context_item = ContextRoleItem(
            role="user",
            content=[
                TextContent(
                    text=EXTRACT_BOOK_DATA_PROMPT
                ),
                FileContent(
                    file_name=resource_name,
                    file_data=resource_base64
                )
            ]
        )

        books = []
        books_response: LLMResponse = await self.model.process(context_item=context_item)
        books_dict = json.loads(books_response.response)
        
        # TODO Integrate the pydantic module 
        [ books.append(Book.from_dict(book_data = book_dict)) for book_dict in books_dict[BOOKS_RESPONSE_ROOT]]

        if not books:
            raise WorkflowNoModelResponseError("No books were successfully extracted!")
        
        print(f"Extracted books:")
        for book in books:
            print(f"Book name: {book.title}")

        return books