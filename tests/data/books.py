from app.domain.book import Book

BOOKS = [
    Book(
        isbn = 9781408855683, 
        title = "Harry Potter and the Goblet of Fire", 
        author = "J.K. Rowling", 
        pages_num = 640
    ),
    Book(
        isbn = 9781408855690, 
        title = "Harry Potter and the Order of the Phoenix", 
        author = "J.K. Rowling", 
        pages_num = 816
    ),
    Book(
        isbn = 9781408855706, 
        title = "Harry Potter and the Half-Blood Prince", 
        author = "J.K. Rowling", 
        pages_num = 560
    )
]

INSERTED_BOOKS = {
    'books': [
        {
            'isbn': 9781408855683, 
            'title': 'Harry Potter and the Goblet of Fire', 
            'author': 'J.K. Rowling', 
            'pages_num': 640
        }, 
        {
            'isbn': 9781408855690, 
            'title': 'Harry Potter and the Order of the Phoenix', 
            'author': 'J.K. Rowling', 
            'pages_num': 816
        }, 
        {
            'isbn': 9781408855706, 
            'title': 'Harry Potter and the Half-Blood Prince', 
            'author': 'J.K. Rowling', 
            'pages_num': 560
        }
    ]
}