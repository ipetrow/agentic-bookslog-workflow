import sqlite3
import json
from pathlib import Path 
from typing import List
from mcp.server.fastmcp import FastMCP

DATABASE_NAME = "bookslog"
FILE_BASE_DIR = Path(__file__).resolve()
DATABASE_PATH = f"{FILE_BASE_DIR}/{DATABASE_NAME}.db"
print(f"DEBUG: Database path: {DATABASE_PATH}")

# Initialize FastMCP server
mcp = FastMCP(DATABASE_PATH)

@mcp.tool()
def get_books() -> str:
    """
    Gets all the books from the database.

    Returns:
        A list with all the books in the database.
    """

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    query = "SELECT * FROM books"

    rows = [row for row in cur.execute(query)]

    books = [
        {
            "isbn": row[1],
            "title": row[2],
            "author": row[3],
            "pages_num": row[4]
        }
        for row in rows
    ]

    response = {
        "books": books
    }

    books_json = json.dumps(response, indent=2)

    conn.commit()
    conn.close()

    return books_json

@mcp.tool()
def get_books_titles() -> List[str]:
    """
    Gets all the book titles from the database.

    Returns:
        A list with all the book titles in the database.
    """

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    query = "SELECT title FROM books"

    rows = [row for row in cur.execute(query)]

    conn.commit()
    conn.close()

    return rows

@mcp.tool()
def insert_book(
        isbn: int,
        title: str,
        author: str,
        pages_num: int
) -> None:
    """
    Insert new book in the database.

    Args:
        isbn: The book's ISBN.
        title: The book's title.
        author: The book's author.
        pages_num: The books's number of pages.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    query="""
        INSERT INTO books (
            isbn, title, author, pages_num
        ) VALUES (?, ?, ?, ?)
    """

    cur.execute(query, (isbn, title, author, pages_num))

    conn.commit()
    conn.close()

@mcp.tool()
def delete_book(
        title: str
) -> None:
    """
    Deletes book with specified title.

    Args:
        title: The book's title.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    query="""
        DELETE FROM books 
        WHERE title = ?
    """

    cur.execute(query, (title,))

    conn.commit()
    conn.close()

@mcp.tool()
def update_book_title(
        isbn: int,
        title: str
) -> None:
    """
    Updates book data.

    Args:
        isbn: The book's ISBN.
        title: The book's title.

    Returns:
        None
    """

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    query = """
        UPDATE books 
        SET title = ? 
        WHERE isbn = ?
    """

    cur.execute(query, (title, isbn))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")