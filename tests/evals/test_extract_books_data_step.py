import os
import pytest

from app.api.manager import MCPManager
from app.api.servers.database.database import Database
from app.config import get_settings
from app.domain.book import Book
from app.llm.openai_service import OpenAIService
from app.workflow.steps.extract_books_data_step import ExtractBooksDataStep

from tests.data.books import BOOKS

@pytest.mark.asyncio
async def test_extract_books_data_step():

    llm = OpenAIService()

    async with MCPManager() as mcp:
        extract_books_data_step = ExtractBooksDataStep(llm, mcp)

        extracted_books: list[Book] = await extract_books_data_step.run()

    assert extracted_books == BOOKS