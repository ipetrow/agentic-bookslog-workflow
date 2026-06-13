import sqlite3
import json
from pathlib import Path 
from typing import List
import sys

from mcp.server.fastmcp import FastMCP

from app.domain.book import Book
from app.config import get_settings

from .database import Database

db = Database(get_settings().database_path)

# Initialize FastMCP server
mcp = FastMCP("bookslog.db")

@mcp.tool()
def get_all_books() -> str:
    """
    Gets all the books from the database.

    Returns:
        A list with all the books in the database.
    """

    return db.get_all_books()

@mcp.tool()
def insert_books(books: list[Book]) -> None:
    """
    Insert new books in the database.

    Args: 
        books: A list with all the books to be inserted.

    Returns:
        None
    """

    db.insert_books(books=books)

if __name__ == "__main__":
    mcp.run(transport="stdio")