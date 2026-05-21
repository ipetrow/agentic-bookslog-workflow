from database.config.connection import get_connection
from database.models.book import Book

def input_initial_data():
    """Inputs the initial books data in the database."""

    conn = get_connection()
    cur = conn.cursor()

    books = [ 
        Book("9781408855652", "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 352),
        Book("9781408855669", "Harry Potter and the Chamber of Secrets", "J.K. Rowling", 384),
        Book("9781408855676", "Harry Potter and the Prisoner of Azkaban", "J.K. Rowling", 480)
        # Book("9781408855683", "Harry Potter and the Goblet of Fire", "J.K. Rowling", 640)
     ]
    
    for book in books:
        cur.execute("""
            INSERT INTO books (
                isbn, title, author, pages_num
            ) VALUES (?, ?, ?, ?)
        """, (book.isbn, book.title, book.author, book.pages_num)
        )

    conn.commit()
    conn.close()

