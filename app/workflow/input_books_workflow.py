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
        # books: list[Book] = await self.extract_books_data_step.run()

        books = [Book(isbn=9781408855683, title='Harry Potter and the Goblet of Fire', author='J.K. Rowling', pages_num=640), Book(isbn=9781408855690, title='Harry Potter and the Order of the Phoenix', author='J.K. Rowling', pages_num=816), Book(isbn=9781408855706, title='Harry Potter and the Half-Blood Prince', author='J.K. Rowling', pages_num=560)]

        # Step 2: Input extracted new books into the database
        return await self.insert_books_step.run(books)
        
        

