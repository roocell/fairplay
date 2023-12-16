from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask import session
from logger import log as log
import player
import commentjson

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
    group = db.Column(db.Integer)
    # ForeignKey establishes the relationship with the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # if there's no players for roocell - then populate from json
    query = Player.query.filter_by(user_id=user_id)
    dbplayers = query.all()
    if len(dbplayers) == 0:
        with open("test/15p_3sl_0pv/players.json", "r") as file:
            file_contents = file.read()
            players_json = commentjson.loads(file_contents)   
        players = player.load(players_json, None)
        for p in players:
            db.session.add(Player(name=p.name, number=p.number, user_id=user_id))
        db.session.commit()

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

# return a list of groups
# each group is a list of players
def db_get_groups(user_id, players):
    groups = []
    group_colours = ["#777777", "#999999", "#99CEAC", "#33B0AF", "#2E6C9D"]

    # query Player table and build groups
    for g in range(1,4):
        dbplayers = Player.query.filter_by(user_id=user_id, group=g).all()
        parr = []
        # adjust group colours
        colour = group_colours.pop()
        for p in dbplayers:
            pp = player.find(players, p.name)
            if pp != None:
                pp.colour = colour
                parr.append(pp)
        groups.append(parr)

    return groups

def update_player_group(user_id, name, new_group):
    # Find the player with the specified name and number
    p = Player.query.filter_by(user_id=user_id, name=name).first()

    if p:
        p.group = new_group
        return True
    else:
        log.error(f"could not find player {name}")
        return False
    
def db_set_groups(user_id, groups):
    # groups are just an identifier in a Player
    # 0 = no group
    # 1,2,3  =  3 groups supported

    # reset all groups to 0
    Player.query.update({Player.group: 0})

    g_cnt = 0
    for group in groups:
        g_cnt += 1
        for p in group:
            update_player_group(user_id, p["name"], g_cnt)

    db.session.commit() # only do one commit

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

def db_get_data(user_id):
    players = db_get_players(user_id)
    return (players, db_get_shifts(user_id), db_get_groups(user_id, players))

