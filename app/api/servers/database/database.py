import json
import sqlite3

from app.domain.book import Book

class Database: 

    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def get_all_books(self) -> str:
        """
        Gets all the books from the database.

        Returns:
            A list with all the books in the database.
        """

        with self.connect() as conn:
            cur = conn.cursor()

            query = "SELECT * FROM books"

            books = [ 
                {
                    "isbn": row[1],
                    "title": row[2],
                    "author": row[3],
                    "pages_num": row[4]
                }
                for row in cur.execute(query)
            ]

            response = {
                "books": books
            }

            books_json = json.dumps(response, indent=2)

            conn.commit()

        return books_json

    def insert_books(self, books: list[Book]) -> None:
        """
        Insert new books in the database.

        Args: 
            books: A list with all the books to be inserted.

        Returns:
            None
        """

        query="""
            INSERT INTO books (
                isbn, title, author, pages_num
            ) VALUES (?, ?, ?, ?)
        """

        values = [
            (book.isbn, book.title, book.author, book.pages_num)
            for book in books
        ]

        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany(query, values)
            conn.commit()
    
    def delete_books_data(self) -> None:
        """
        Delete the books data.
            Returns:
                None
        """

        query = "DELETE FROM books"

        with self.connect() as conn:
            conn.cursor().execute(query)
            conn.commit