import re
import requests
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Book(db.Model):
    isbn = db.Column(db.String(15), primary_key=True)
    title = db.Column(db.String(255), unique=False, nullable=False)
    cover = db.Column(db.String(500), unique=True, nullable=True)
    state = db.Column(db.Integer, unique=False, nullable=False, default=-1)
    timestamp = db.Column(db.DateTime, unique=False)

    def __repr__(self):
        return f'<Book {self.title}, {self.timestamp}>'

# count = 5

@app.route('/', methods=["POST", "GET"])
def index():
    # global count
    # if request.method == "POST":
    #     request_data = request.get_json()
    #     if request_data and 'count' in request_data:
    #             count += request_data['count']
    books = Book.query.order_by(Book.state).all()
    return render_template("index.html", error = request.args.get("error") if request.args.get("error") else None, books = books)

@app.route('/search', methods=["POST"])
def search():
    if request.method == "POST":
        book_input = request.form['book']
        if book_input:
            isISBN = re.compile(r'^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$')
            isISBN = isISBN.search(book_input)
            if not isISBN:
                return redirect(url_for('index', error = "Il campo inserito non è un codice ISBN!"))
            # value_if_true if condition else value_if_false
            requestBook = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{book_input.replace('-', '')}&maxResults=1").json()
            if requestBook["totalItems"] != 0:
                book = requestBook['items'][0]["volumeInfo"]
                isbn = book["industryIdentifiers"][0]["identifier"]
                title = book["title"] if "title" in book.keys() else None
                cover = book["imageLinks"]["thumbnail"] if "imageLinks" in book.keys() else None
                book = Book(isbn=isbn, title=title, cover=cover, timestamp=datetime.now())
                if not Book.query.filter_by(isbn = isbn).first():
                    db.session.add(book)
                    db.session.commit()
                return redirect(url_for('index'))
    return redirect(url_for('index', error = "Nessun libro trovato!"))

@app.route("/deleteBook", methods=["POST"])
def deleteBook():
    if request.method == "POST":
        isbn = request.json["isbn"]
        book = Book.query.filter_by(isbn=isbn).first()
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for("index"))

@app.route("/changeState", methods=["POST"])
def changeState():
    if request.method == "POST":
        isbn = request.json["isbn"]
        state = request.json["state"]
        book = Book.query.filter_by(isbn = isbn).first()
        book.state = state
        db.session.commit()
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)