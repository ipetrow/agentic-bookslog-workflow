import sqlite3

DB_NAME = "bookslog.db"

def get_connection() -> sqlite3.Connection:
    """
    Establishes connection to the database.
    
    Returns:
        The connection to the database.
    """

    return sqlite3.connect(DB_NAME)