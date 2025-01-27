class Book:
    def __init__(self, book_id, title, author, genre, availability):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.availability = availability

    def __repr__(self):
        return f"Book({self.book_id}, {self.title}, {self.author}, {self.genre}, {self.availability})"