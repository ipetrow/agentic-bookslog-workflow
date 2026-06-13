import pytest
import json

from app.api.manager import MCPManager
from app.api.servers.database.database import Database
from app.config import get_settings
from app.llm.openai_service import OpenAIService
from app.workflow.input_books_workflow import InputBooksWorkflow

from tests.data.books import BOOKS, INSERTED_BOOKS

@pytest.fixture
def clean_database():
    db = Database(get_settings().database_path)

    db.delete_books_data()

    yield db

    db.delete_books_data()

    books = json.loads(db.get_all_books())

    assert not books["books"]

@pytest.mark.asyncio
async def test_input_books_workflow(clean_database):

    llm = OpenAIService()

    async with MCPManager() as mcp:
        workflow = InputBooksWorkflow(
            model = llm,
            mcp = mcp
        )
        
        responses = await workflow.run()

    # asserts the llm listed the added book titles as requested in the prompt
    for book in BOOKS:
        book_title = book.title
        assert book_title in responses

    # asserts the books are added successfully in the database
    inserted_books = json.loads(clean_database.get_all_books())
    assert inserted_books == INSERTED_BOOKS