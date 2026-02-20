from flask import session, redirect, url_for, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

def register_user(email, password):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, generate_password_hash(password))
        )
        db.commit()
        return True
    except:
        return False

def authenticate_user(email, password):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    if user and check_password_hash(user["password"], password):
        return user
    return None