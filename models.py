from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    service = db.Column(db.String(32), unique=False)
    email = db.Column(db.String(128), unique=False)
    name = db.Column(db.String(128), unique=False)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    number = db.Column(db.Integer)
    prevshifts = db.Column(db.Integer)
    strongline = db.Column(db.Integer)
    # ForeignKey establishes the relationship with the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def db_get_shifts(user_id):
    shifts = [[] for _ in range(8)] # 8 empty shifts
    return shifts;
def db_get_players(user_id):
    return [];
def db_get_stronglines(user_id):
    return [];

def db_get_players_and_shifts(user_id):
    return (db_get_players(user_id), db_get_shifts(user_id))

