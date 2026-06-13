from app.domain.book import Book

EXTRACT_BOOK_DATA_PROMPT = """
    Extract all the ordered books from the receipt.

    OUTPUT FORMAT (STRICT)
    A valid JSON object in the following format:
    - each book should have ONLY the attributes: "isbn" of type int, "title" of type str, "author" of type str, "pages_num" representing the number of pages and should be of type int.  
    - the books items should be in a "books" array. 
    Example: { "books": [{"isbn": 1, "title": "", "author": "", "pages_num": 111}, {...}]}

    DO NOT return any other additional output, ONLY the json.
    """

def get_insert_book_prompt(isbn: int, title: str, author: str, pages_num: int) -> str:
    return f"""
    Add a new book with ISBN = {isbn}, title = '{title}', author = '{author}', pages = {pages_num}.
    """

def get_insert_books_prompt(books: list[Book]) -> str:
    books_list = [
        f"- Book: ISBN = {book.isbn}, title = '{book.title}', author = '{book.author}', pages = {book.pages_num}"
        for book in books
    ]

    prompt = (
        "Please add the following new books in the database:\n"
        + "\n".join(books_list)
        + "\n\nExecution guidance:"
        + "\n- If you need a function call provide a short reasoning why you need it."
        + "\n- Ensure that the books insertion has been successful."
        + "\n\nAnswer guidance: Communicate clearly whether the task has been successful or not. If yes, include in your answer the titles of the added books."
    )

    return prompt

