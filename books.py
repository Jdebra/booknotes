

class Books:
    """Overal class to manage the book attributes in the library"""
    def __init__(self, title, author, genre, cover_image):
        self.title = title
        self.author = author
        self.genre = genre
        self.cover_image = cover_image
        self.notes = []
        self.quotes = []

    def add_note(self, note):
        self.notes.append(note)
    
    def add_quote(self, quote):
        self.quotes.append(quote)
