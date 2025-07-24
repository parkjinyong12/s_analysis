from backend.models.user import User
from backend.extensions import db

def create_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user

def get_all_users():
    return User.query.all() 