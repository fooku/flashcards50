from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)

class Flashcards(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)

    # Define relationship with User
    users = db.relationship('Users', backref=db.backref('flashcards', lazy=True))

class Cards(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id'), nullable=False)
    term = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)

    # Define relationship with Flashcard
    flashcards = db.relationship('Flashcards', backref=db.backref('cards', lazy=True))
