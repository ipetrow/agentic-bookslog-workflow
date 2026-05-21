EXTRACT_BOOK_DATA_PROMPT = """
    Extract all the ordered books from the receipt.

    OUTPUT FORMAT (STRICT)
    A valid JSON object in the following format:
    - each book should have ONLY the attributes: "isbn" of type int, "title" of type str, "author" of type str, "pages" representing the number of pages and should be of type int.  
    - the books items should be in a "books" array. 
    Example: { "books": [{"isbn": 1, "title": "", "author": "", "pages": 111}, {...}]}

    DO NOT return any other additional output, ONLY the json.
    """

def get_insert_book_prompt(isbn: int, title: str, author: str, pages_num: int) -> str:
    return f"""
    Add a new book with ISBN = {isbn}, title = '{title}', author = '{author}', pages = {pages_num}.
    """

