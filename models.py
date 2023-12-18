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
    shifts = db.relationship('PlayerShifts', backref='player', lazy=True)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    players = db.relationship('PlayerShifts', backref='shift', lazy=True, cascade='all, delete-orphan')
    # cacade makes sure that when a shift is deleted any connected entries in PlayerShifts also get removed

# Many-to-Many Relationship Table: PlayerShifts
class PlayerShifts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)


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

        for p in players_json:
            db_player = db.session.add(Player(name=p["name"], number=p["number"], user_id=user_id))
            db.session.flush() # to get player.id
        db.session.commit()

    return User.query.get(user_id)

def db_add_player_to_roster(user_id, player_name, player_number):
    player = Player(name=player_name, number=player_number, user_id=user_id)
    db.session.add(player)
    db.session.commit()
    return player.id

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

def db_get_players(user_id):
    # read players from db
    query = Player.query.filter_by(user_id=user_id)
    dbplayers = query.all()
    log.debug(f"found {len(dbplayers)} players in database for user_id {user_id}")
    # create array of player.py players
    # TODO: in flask session ?

    players = []
    for dbp in dbplayers:
        p = player.Player(dbp.name, dbp.number, dbp.id)
        players.append(p)

    return players;

# gets the data to display on the webpage
def db_get_data(user_id):
    players = db_get_players(user_id)
    return (players, db_get_shifts(user_id, game_id=1,players=players), db_get_groups(user_id, players))

# returns an array of shifts. each shift is an array of player.py:Player
def db_get_shifts(user_id, game_id, players):
    # default game is game_id=1

    shiftsdb = (
        db.session.query(Shift)
        .filter(Shift.game_id == game_id)
        .options(db.joinedload(Shift.players).joinedload(PlayerShifts.player))
        .all()
    )

    shifts = [[] for _ in range(8)] # 8 empty shifts

    if not shiftsdb:
        print(f"No shifts found for Game ID: {game_id}")
        return shifts;
    
    # Now 'shifts' contains all shifts associated with the specified game_id
    for s, shift in enumerate(shiftsdb):
        parr = []
        print(f"Shift ID: {shift.id}, Game ID: {shift.game_id}")
        print("Players:")
        for player_shift in shift.players:
            print(f"  - Player ID: {player_shift.player.id}, Name: {player_shift.player.name}")
            p = player.find(players, player_shift.player.name)
            if p != None:
                parr.append(p)
        shifts[s] = parr
    return shifts

# input: an array of shifts. each shift is an array of player.py:Player
# assume the players in the shifts have player.id that is the database id for the Player table
def db_set_shifts(user_id, game_id, shifts):
    # add game
    game = Game.query.filter_by(id=game_id).one_or_none()
    if not game:
        game = Game(name="default")
        db.session.add(game)
        db.session.flush() # to get game.id

    # remove all shifts for this game_id
    # TODO: maybe this is expensive on every fairplay.update() ?
    # Delete associated PlayerShifts records (cascade option doesn't seem to work)
    for shift_to_delete in Shift.query.filter_by(game_id=game_id).all():
        for player_shift in shift_to_delete.players:
            db.session.delete(player_shift)
    Shift.query.filter_by(game_id=game_id).delete()

    for shift in shifts:
        log.debug(f"game.id {game.id}")
        s = Shift(game_id=game.id)
        db.session.add(s)
        db.session.flush() # to get shift id
        for p in shift:
            ps = PlayerShifts(player_id=p.id, shift_id=s.id)
            db.session.add(ps)

    db.session.commit()