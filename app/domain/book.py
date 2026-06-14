from dataclasses import dataclass

@dataclass
class Book:
    isbn: int
    title: str
    author: str
    pages_num: int

    @classmethod
    def from_dict(cls, book_data: dict) -> Book:
        return cls(**book_data)