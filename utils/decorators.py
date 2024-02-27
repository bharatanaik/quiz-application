from functools import wraps
from flask import session, request, url_for, redirect
from config import ADMIN_MAILS

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user-token"):
            return func(*args, **kwargs)
        else:
            next_url = request.path if request.path != url_for('login') else None
            return redirect(url_for('login', next=next_url))
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user-token") in ADMIN_MAILS:
            return func(*args, **kwargs)
        else:
            next_url = request.path if request.path != url_for('login') else None
            return redirect(url_for('login', next=next_url))
    return wrapper


