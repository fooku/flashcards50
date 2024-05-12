from flask import redirect, session
from functools import wraps
from sqlalchemy.orm import class_mapper

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def instance_to_dict(instance):
    columns = [c.key for c in class_mapper(instance.__class__).columns]

    return {c: getattr(instance, c) for c in columns}
