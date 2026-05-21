class Book:
    def __init__(self, isbn, title, author, pages_num):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.pages_num = pages_num

    def __str__(self):
        return f"Book: isbn={self.isbn}, title={self.title}, author={self.author}, pages_num={self.pages_num}"