from datetime import date

class Notes:
    """A class to manage the notes inside each book in the library"""
    def __init__(self, page, text):
        self.page = page
        self.text = text
        self.date = date.today()