from database.config.connection import get_connection

def create_db() -> None:
    """Creates an empty database with a single 'books' table."""

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS books")

    cur.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn INTEGER NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pages_num INTEGER NOT NULL
    )
    """)

    print(f"SQLite database created with a single 'books' table.")

def show_db_content():
    """Shows the whole content of the database."""

    conn = get_connection()
    cur = conn.cursor()

    table_list = [row for row in cur.execute("SELECT * FROM books")] 
    print(table_list)

    conn.commit()
    conn.close()