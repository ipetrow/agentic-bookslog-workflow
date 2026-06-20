from app.api.manager import MCPManager
from app.domain.book import Book
from app.llm.openai_service import OpenAIService

from .steps.extract_books_data_step import ExtractBooksDataStep
from .steps.insert_books_step import InsertBooksStep

class InputBooksWorkflow:

    def __init__(self, model: OpenAIService, mcp: MCPManager):
        self.extract_books_data_step = ExtractBooksDataStep(model, mcp)
        self.insert_books_step = InsertBooksStep(model, mcp)

    async def run(self):
        # Step 1: Extract books from PDF receipt
        books: list[Book] = await self.extract_books_data_step.run()

        # Step 2: Input extracted new books into the database
        return await self.insert_books_step.run(books)
        
        

