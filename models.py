from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask import session
from logger import log as log
import player

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

def db_add_player_to_roster(user_id, player_name, player_number):
    player = Player(name=player_name, number=player_number, user_id=user_id)
    db.session.add(player)
    db.session.commit()

def db_remove_player_from_roster(user_id, player_name, player_number):
    query = Player.query.filter_by(user_id=user_id, name=player_name, number=player_number)
    player = query.one_or_none()
    if player:
        db.session.delete(player)
        db.session.commit()

def db_get_shifts(user_id):
    shifts = [[] for _ in range(8)] # 8 empty shifts
    return shifts;
def db_get_players(user_id):
    # read players from db
    query = Player.query.filter_by(user_id=user_id)
    dbplayers = query.all()
    log.debug(f"found {len(dbplayers)} players in database for user_id {user_id}")
    # create array of player.py players
    # TODO: in flask session ?

    players = []
    for dbp in dbplayers:
        p = player.Player(dbp.name, dbp.number)
        players.append(p)

    return players;
def db_get_stronglines(user_id):
    return [];

def db_get_players_and_shifts(user_id):
    return (db_get_players(user_id), db_get_shifts(user_id))

