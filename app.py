# main Flask app
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, Note
from werkzeug.security import generate_password_hash, check_password_hash

# mock data to search for books
MOCK_BOOKS = [
    {
        "id": 1,
        "title": "The Little Prince",
        "author": "Antoine de Saint-Exupéry",
        "cover": ""
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "cover": ""
    },
    {
        "id": 3,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "cover": ""
    },
]

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///booknotes.db"

db.init_app(app)

# as this is an extension, must be initialized before routes
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    if current_user.is_authenticated:
        return f"""
        <h1>Hello {current_user.username}</h1>
        <a href="/logout">Logout</a>
        """
    return '<a href="/login">Login</a>'

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # hash password
        hashed_password = generate_password_hash(password)

        # create user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid username or password")

    return render_template("login.html")

@app.route("/add-book", methods=["GET", "POST"]) #manually insert a new book to personal library
@login_required
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]

        new_book = Book(
            title=title,
            author=author,
            user_id=current_user.id
        )

        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("library"))

    return render_template("add_book.html")

@app.route("/book/<int:book_id>", methods=["GET", "POST"])
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == "POST":
        content = request.form.get("content")

        if content:
            note = Note(
                content=content,
                book_id=book.id
            )
            db.session.add(note)
            db.session.commit()

        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("book_detail.html", book=book)

@app.route("/library")
@login_required
def library():
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template("library.html", books=books)

@app.route("/add-mock-book", methods=["POST"]) #search for a book and add the book to personal library
@login_required
def add_mock_book():
    title = request.form["title"]
    author = request.form["author"]

    new_book = Book(
        title=title,
        author=author,
        user_id=current_user.id
    )

    db.session.add(new_book)
    db.session.commit()

    return redirect(url_for("library"))

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    results = []

    if request.method == "POST":
        query = request.form["query"].lower()

        results = [
            book for book in MOCK_BOOKS
            if query in book["title"].lower()
        ]

    return render_template("search.html", results=results)

@app.route("/book/<int:book_id>/add-note", methods=["POST"]) #the route to add notes to a book
@login_required
def add_note(book_id):
    book = Book.query.get_or_404(book_id)

    # Security check
    if book.user_id != current_user.id:
        abort(403)

    content = request.form["content"]

    new_note = Note(
        content=content,
        book_id=book.id
    )

    db.session.add(new_note)
    db.session.commit() # writes it permanently to the data base

    return redirect(url_for("book_detail", book_id=book.id)) # reloads the page, queries DB again, now includes the new note

@app.route("/note/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    book = Book.query.get(note.book_id)

    # Security check
    if book.user_id != current_user.id:
        abort(403)

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("book_detail", book_id=book.id))

@app.route("/logout")
# Only logged users can log out
@login_required
def logout():
    # clears user session
    logout_user()
    # send user back to login page
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)