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
    roster = db.relationship('PlayerRosters', backref='player', lazy=True)

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

class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    players = db.relationship('PlayerRosters', backref='roster', lazy=True, cascade='all, delete-orphan')

# Many-to-Many Relationship Table: PlayerShifts
class PlayerRosters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'), nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    query = Player.query.filter_by(user_id=user_id)
    dbplayers = query.all()

    user = User.query.get(user_id)
    file = None
    # if there's no players for roocell - then populate from json
    if len(dbplayers) == 0 and user is not None:
        if user.email is not None and "kappuchino" in user.email.lower():
            file = "test/12p_3sl_0pv/players.json"
        if user.email is not None and "roocell" in user.email:
            file = "test/15p_3sl_0pv/players.json"


    if file is not None:
        with open(file, "r") as file:
            file_contents = file.read()
            players_json = commentjson.loads(file_contents)   

        for p in players_json:
            log.debug(p)
            db_player = db.session.add(Player(name=p["name"], number=p["number"], user_id=user_id))
            db.session.flush() # to get player.id
        db.session.commit()


    # if there's no games for this user - create a default game
    games = Game.query.filter_by(user_id=user_id).all()
    if len(games) == 0:
        g = Game(user_id=user_id, name="default")
        db.session.add(g)
        db.session.commit()
    return user

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
def db_get_data(user_id, game_id):
    players = db_get_players(user_id)
    (shifts, roster) = db_get_game(user_id, game_id, players=players)
    return (roster, shifts, db_get_groups(user_id, players))

def db_get_data_roster(user_id):
    players = db_get_players(user_id)
    return (players, db_get_groups(user_id, players))

# returns an array of shifts. each shift is an array of player.py:Player
# also return roster (roster is an array of player.py:Player)
def db_get_game(user_id, game_id, players):
    log.debug(f"db_get_game {game_id}")
    # default game is game_id=1

    shiftsdb = (
        db.session.query(Shift)
        .filter(Shift.game_id == game_id)
        .options(db.joinedload(Shift.players).joinedload(PlayerShifts.player))
        .all()
    )

    shifts = [[] for _ in range(8)] # 8 empty shifts

    if not shiftsdb:
        return shifts, players; # players = full roster
    
    # Now 'shifts' contains all shifts associated with the specified game_id
    for s, shift in enumerate(shiftsdb):
        parr = []
        for shift_player in shift.players:
            p = player.find(players, shift_player.player.name)
            if p != None:
                parr.append(p)
        shifts[s] = parr

    if game_id == 1:
        # return full roster if default game
        return (shifts, players)

    # get game roster
    rosterdb = Roster.query.filter_by(game_id=game_id).one()
    roster = []
    for roster_player in rosterdb.players:
        p = player.find(players, roster_player.player.name)
        if p != None:
            roster.append(p)

    return (shifts, roster)

# input: an array of shifts. each shift is an array of player.py:Player
# assume the players in the shifts have player.id that is the database id for the Player table
def db_set_game(user_id, game_id, shifts, roster):
    # add game
    log.debug(f"db_set_game game_id {game_id}")

    game = Game.query.filter_by(id=game_id).one_or_none()
    if not game:
        game = Game(name="default", user_id=user_id)
        db.session.add(game)
        db.session.flush() # to get game.id

    # remove all shifts for this game_id
    # TODO: maybe this is expensive on every fairplay.update() ?
    # Delete associated PlayerShifts records (cascade option doesn't seem to work)
    for shift_to_delete in Shift.query.filter_by(game_id=game_id).all():
        for player_shift in shift_to_delete.players:
            db.session.delete(player_shift)
    Shift.query.filter_by(game_id=game_id).delete()

    # delete existing roster for this game and we'll recreate it
    for roster_to_delete in Roster.query.filter_by(game_id=game_id).all():
        for player_roster in roster_to_delete.players:
            db.session.delete(player_roster)
    Roster.query.filter_by(game_id=game_id).delete()

    # commit those deletes
    db.session.commit()

    for shift in shifts:
        s = Shift(game_id=game.id)
        db.session.add(s)
        db.session.flush() # to get shift id
        for p in shift:
            ps = PlayerShifts(player_id=p.id, shift_id=s.id)
            db.session.add(ps)

    r = Roster(game_id=game.id)
    db.session.add(r)
    db.session.flush() # to get roster id

    for p in roster:
        pr = PlayerRosters(player_id=p.id, roster_id=r.id)
        db.session.add(pr)

    db.session.commit()

# returns a list of games as a dict
def db_get_games(user_id):
    games = []
    for g in Game.query.filter_by(user_id=user_id).all():
        game = {}
        game['id'] = g.id
        game['name'] = g.name
        games.append(game)
    return games

def db_save_game(user_id, gamename):
    if gamename == "":
        gamename = "game" +str(Game.query.filter_by(user_id=user_id).count()+1)

    log.debug(f"saving game {gamename}")

    g = Game(user_id=user_id, name=gamename)
    db.session.add(g)
    db.session.flush() # to get id

    # we can cheat here because we've already saved the 
    # default game to the db (for page refreshes)
    # so all we really need to do is set the game_id on all the 
    # shifts to this saved one
    # just need to be sure to display the new game when saved   
    target_game_id = 1 # default game
    Shift.query.filter_by(game_id=1).update({'game_id': g.id})
    Roster.query.filter_by(game_id=1).update({'game_id': g.id})

    db.session.commit()
 
    # return all games
    return db_get_games(user_id)

def db_delete_game(user_id, game_id):
    for shift_to_delete in Shift.query.filter_by(game_id=game_id).all():
        for player_shift in shift_to_delete.players:
            db.session.delete(player_shift)
    Shift.query.filter_by(game_id=game_id).delete()

    Game.query.filter_by(user_id=user_id, id=game_id).delete()
    db.session.commit()

def db_change_game(user_id, game_id, name):
    log.debug(f"changing game {game_id} to {name}")
    Game.query.filter_by(id=game_id).update({'name': name})
    db.session.commit()
