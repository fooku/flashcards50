from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Users, Flashcards, Cards

from helpers import login_required, instance_to_dict


# Configure application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///flashcard.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('uesrname')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        errs = {}
        if not username:
            errs["username"] = "Must provide username!"
        elif len(username) < 3 or len(username) > 15:
            errs["username"] = "Username length must between 3 and 15!"
        if not password:
            errs["password"] = "Must provide password!"
        elif len(username) < 3 or len(username) > 15:
            errs["password"] = "Password length must between 6 and 15!"
        if not confirm:
            errs["confirm"] = "Must provide confirm!"
        elif password != confirm:
            errs["confirm"] = "Passwords don't match!"

        if errs:
            return render_template("signup.html",errs=errs)

        with app.app_context():
            rows = Users.query.filter_by(username=username).all()

            if len(rows) > 0:
                errs["username"] = f"Username {username} is exist!"
                return render_template("signup.html",errs=errs)

            db.session.add(Users(username=username, hash=generate_password_hash(password)))
            db.session.commit()

        return redirect("/login")


    return render_template("signup.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('uesrname')
        password = request.form.get('password')
        errs = {}
        if not username:
            errs["username"] = "Must provide username!"
        elif len(username) < 3 or len(username) > 15:
            errs["username"] = "Username length must between 3 and 15!"
        if not password:
            errs["password"] = "Must provide password!"
        elif len(username) < 3 or len(username) > 15:
            errs["password"] = "Password length must between 6 and 15!"

        if errs:
            return render_template("login.html",errs=errs)

        with app.app_context():
            rows = Users.query.filter_by(username=username).all()

            if len(rows) != 1:
                errs["username"] = "Incorrect username"
                return render_template("login.html",errs=errs)
            elif not check_password_hash(rows[0].hash , password):
                errs["password"] = "Incorrect password!"
                return render_template("login.html",errs=errs)

        session["user_id"] = rows[0].id
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/cards")
@login_required
def cards():
    rows = Flashcards.query.filter_by(user_id=session["user_id"]).all()
    return render_template("cards.html", flashcards=rows)

@app.route('/cards/<flashcard_id>')
def page(flashcard_id):
    print(flashcard_id)
    with app.app_context():
        flashcards = Flashcards.query.filter_by(id=flashcard_id, user_id=session["user_id"]).all()
        cards = Cards.query.filter_by(flashcard_id=flashcard_id).all()

        if len(flashcards) != 1:
            return render_template("flashcard.html", errs="error")

    flashcard_data = instance_to_dict(flashcards[0])
    cards_data = [instance_to_dict(card) for card in cards]

    return render_template("flashcard.html", flashcard=flashcard_data, cards=cards_data)

@app.route("/cards/create", methods=["GET","POST"])
@login_required
def create_cards():
    if request.method == "POST":
        data = request.json

        errs = {}
        if not data:
            errs["data"] = "Invalid data!"
        elif not data["title"]:
            errs["title"] = "Must provide title!"
        elif len(data["title"]) < 1 or len(data["title"]) > 45:
            errs["title"] = "Title length must between 1 and 45!"

        if not data["cards"]:
            errs["cards-err-msg"] = "Invalid cards!"
        elif len(data["cards"]) == 0:
            errs["cards-err-msg"] = "Invalid cards!"
        else:
            for card in data["cards"]:
                print("card:", card)
                if not card:
                    errs["cards-err-msg"] = "Invalid cards!"
                else:
                    if not card['term']:
                        errs[card["term-id"]] = "Must provide term!"
                    elif len(card['term']) < 1 or len(card['term']) > 45:
                        errs[card["term-id"]] = "Term length must between 1 and 45!"
                    if not card['definition']:
                        errs[card["definition-id"]] = "Must provide definition!"
                    elif len(card['definition']) < 1 or len(card['definition']) > 45:
                        errs[card["definition-id"]] = "definition length must between 1 and 45!"

        if errs:
            return jsonify(errs), 400

        with app.app_context():
            try:
                db.session.begin()

                flashcard = Flashcards(user_id=session["user_id"], title=data["title"])
                db.session.add(flashcard)
                db.session.flush()

                for card in data["cards"]:
                    print(card)
                    db.session.add(Cards(flashcard_id=flashcard.id, term=card["term"], definition=card["definition"]))

                db.session.commit()
            except ValueError:
                db.session.rollback()

        return jsonify(""), 201


    return render_template("create-cards.html")

if __name__ == "__main__":
    app.run(debug=True)