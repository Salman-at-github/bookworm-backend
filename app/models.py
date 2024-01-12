from datetime import datetime
from app import db


class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', '{self.genre}')"

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferred_authors = db.Column(db.String(500))  # Store preferred authors as a comma-separated string
    preferred_genres = db.Column(db.String(500))  # Store preferred genres as a comma-separated string


    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.phone}')"
