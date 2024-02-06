from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask import session
from logger import log as log
import json
import commentjson
from mypusher import notify_shared_users_of_game_change

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
    group = db.Column(db.Integer)
    # ForeignKey establishes the relationship with the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shifts = db.relationship('PlayerShifts', backref='player', lazy=True)
    roster = db.relationship('PlayerRosters', backref='player', lazy=True)

    shiftcnt = 0
    colour = "white"
    dbl = [0] * 8  # an array of bools for each shift (doubleshift)
    violates = 0  # violates max shifts
    lts = [0] * 8  # an array of bools for each shift (lockedtoshift)
    
    def __init__(self, name, number, group, user_id):
        self.name = name
        self.number = number
        self.group = group
        self.user_id = user_id

    
# use a class encoder in order to dump python classes
class PlayerEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, Player):
      # Return a dictionary representation of your class
      player = {
          "name" : obj.name,
          "number" : obj.number,
          "group" : obj.group,
          "id" : obj.id,

          "shiftcnt" : obj.shiftcnt,
          "colour" : obj.colour,
          "dbl" : obj.dbl,
          "violates" : obj.violates,
          "lts" : obj.lts,
      }
      return player
    return super(PlayerEncoder, self).default(obj)

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

# Many-to-Many Relationship Table: PlayerRosters
class PlayerRosters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'), nullable=False)

class GameUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    shared_users = db.relationship('GameUsers', backref='game', lazy=True, cascade='all, delete-orphan')


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
    return player

def db_remove_player_from_roster(user_id, player_name, player_number):
    query = Player.query.filter_by(user_id=user_id, name=player_name, number=player_number)
    player = query.one_or_none()
    if player:
        db.session.delete(player)
        db.session.commit()

# return a list of groups
# each group is a list of players
# group are specific to the user
def db_get_groups(user_id):
    groups = []
    group_colours = ["#777777", "#999999", "#99CEAC", "#33B0AF", "#2E6C9D"]

    # query Player table and build groups
    for g in range(1,4):
        dbplayers = Player.query.filter_by(user_id=user_id, group=g).all()
        # adjust group colours
        colour = group_colours.pop()
        for p in dbplayers:
            p.colour = colour
        groups.append(dbplayers)

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

def db_get_full_roster(user_id):
    # read players from db
    query = Player.query.filter_by(user_id=user_id)
    dbplayers = query.all()
    log.debug(f"found {len(dbplayers)} players in database for user_id {user_id}")
    return dbplayers;


# gets the data to display on the webpage
def db_get_data(user_id, game_id):
    groups = db_get_groups(user_id) # must be first - sets colours
    (shifts, roster) = db_get_game(user_id, game_id)
    return (roster, shifts, groups)

def db_get_data_roster(user_id):
    groups = db_get_groups(user_id) # must be first - sets colours
    players = db_get_full_roster(user_id)
    return (players, groups)

# returns an array of shifts. each shift is an array of player.py:Player
# also return roster (roster is an array of player.py:Player)
def db_get_game(user_id, game_id):
    log.debug(f"db_get_game {game_id}")

    shiftsdb = (
        db.session.query(Shift)
        .filter(Shift.game_id == game_id)
        .options(db.joinedload(Shift.players).joinedload(PlayerShifts.player))
        .all()
    )

    shifts = [[] for _ in range(8)] # 8 empty shifts

    if not shiftsdb:
        return shifts, db_get_full_roster(user_id); # this happens for default game
    
    # Now 'shifts' contains all shifts associated with the specified game_id
    for s, shift in enumerate(shiftsdb):
        parr = []
        for shift_player in shift.players:
            # build player object from database
            dbp = Player.query.filter_by(id=shift_player.player_id).one()
            parr.append(dbp)
        shifts[s] = parr

    # get game roster
    rosterdb = Roster.query.filter_by(game_id=game_id).one()
    roster = []
    for roster_player in rosterdb.players:
        dbp = Player.query.filter_by(id=roster_player.player_id).one()
        roster.append(dbp)

    return (shifts, roster)

# input: an array of shifts. each shift is an array of player.py:Player
# assume the players in the shifts have player.id that is the database id for the Player table
def db_set_game(user_id, game_id, shifts, roster):
    # add game
    log.debug(f"db_set_game user_id={user_id} game_id={game_id}")

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

    # notify other shared users
    # JS will update game on screen if it's actively open
    gu = GameUsers.query.filter_by(game_id=game.id).all()
    if len(gu) > 0:
        notify_shared_users_of_game_change(game_id)

# returns a list of games as a dict
def db_get_games(user_id):
    games = []
    for g in Game.query.filter_by(user_id=user_id).all():
        game = {}
        game['id'] = g.id
        game['name'] = g.name
        games.append(game)

    # also return games that are shared
    for gu in GameUsers.query.filter_by(user_id=user_id).all():
        g = Game.query.filter_by(id=gu.game_id).one()
        if "default" in g.name:
            # don't add default game in shared list
            continue
        game = {}
        game['id'] = g.id
        game['name'] = g.name + "(s)"
        games.append(game)
    
    return games

def db_save_game(user_id, game_id):
    g = Game.query.filter_by(user_id=user_id, id=game_id).one()

    # move default to new game
    if g.name == "default":
        new_game_name = "game" +str(Game.query.filter_by(user_id=user_id).count()+1)

        new_g = Game(user_id=user_id, name=new_game_name)
        db.session.add(new_g)
        db.session.flush() # to get id

        # we can cheat here because we've already saved the 
        # default game to the db (for page refreshes)
        # so all we really need to do is set the game_id on all the 
        # shifts to this saved one
        # just need to be sure to display the new game when saved   
        Shift.query.filter_by(game_id=g.id).update({'game_id': new_g.id})
        Roster.query.filter_by(game_id=g.id).update({'game_id': new_g.id})

        db.session.commit()
    # duplicate an existing game
    else:
        new_game_name = g.name + "_" + str(Game.query.filter_by(user_id=user_id).count()+1)
        new_g = Game(user_id=user_id, name=new_game_name)
        db.session.add(new_g)
        db.session.flush() # to get id

        # create a new set of Shifts, Playershifts, Roster, PlayerRosters
        shifts = Shift.query.filter_by(game_id=g.id).all()
        for shift in shifts:
            new_s = Shift(game_id=new_g.id)
            db.session.add(new_s)
            db.session.flush() # to get shift id
            pshifts = PlayerShifts.query.filter_by(shift_id=shift.id)
            for p in pshifts:
                ps = PlayerShifts(player_id=p.player_id, shift_id=new_s.id)
                db.session.add(ps)

        roster = Roster.query.filter_by(game_id=g.id).one()
        new_r = Roster(game_id=new_g.id)
        db.session.add(new_r)
        db.session.flush() # to get roster id

        prosters = PlayerRosters.query.filter_by(roster_id=roster.id)
        for p in prosters:
            pr = PlayerRosters(player_id=p.player_id, roster_id=new_r.id)
            db.session.add(pr)
        db.session.commit()

    log.debug(f"saved game {new_game_name}")

    # return all games
    return db_get_games(user_id)

def db_delete_game(user_id, game_id):
    for shift_to_delete in Shift.query.filter_by(game_id=game_id).all():
        for player_shift in shift_to_delete.players:
            db.session.delete(player_shift)

    Shift.query.filter_by(game_id=game_id).delete()
    Game.query.filter_by(user_id=user_id, id=game_id).delete()

    roster = Roster.query.filter_by(game_id=game_id).one()
    prosters = PlayerRosters.query.filter_by(roster_id=roster.id).all()
    for pr in prosters:
        PlayerRosters.query.filter_by(roster_id=pr.id).delete()
    Roster.query.filter_by(game_id=game_id).delete()
    db.session.commit()

def db_change_game(user_id, game_id, name):
    log.debug(f"changing game {game_id} to {name}")
    Game.query.filter_by(id=game_id).update({'name': name})
    db.session.commit()

def db_get_shared_users(user_id):
    # the database is geared to sharing individual games
    # but (for now) we're sharing all games
    # for now assume all games are shared
    # so just 
    # get a game_id from a game owned by current user
    # get all GameUsers entries for that game_id
    # those are the shared users ids
    # load up shared users emails to return
    unique_emails = set()
    shared_users = []
    game = Game.query.filter_by(user_id=user_id).first()
    for gu in GameUsers.query.filter_by(game_id=game.id).all():
        shared_user = {}
        user = User.query.filter_by(id=gu.user_id).one()
        if not user:
            log.error(f"couldn't find user_id {user_id}")
            continue
        if user.email not in unique_emails:
            shared_user['id'] = user.id
            shared_user['email'] = user.email
            log.debug(shared_user)
            shared_users.append(shared_user)
            unique_emails.add(user.email)
    return shared_users

def db_add_shared_user(user_id, email):
    log.debug(f"db_add_shared_user email {email}")
    share_user = User.query.filter_by(email=email).one()
    if not share_user:
        # could happen if user entered invalid email
        log.debug(f"could not find email {email}")
        return False
    if share_user.id == user_id:
        log.debug(f"can't add self {email}")
        return False
    # share all games with user
    # but first remove all entries in GameUser
    # (in case person is added more than once)
    GameUsers.query.filter_by(user_id=share_user.id).delete()
    for g in Game.query.filter_by(user_id=user_id).all():
        # note: share default game - but dont return it for shared game list
        newentry = GameUsers(game_id=g.id, user_id=share_user.id)
        db.session.add(newentry)
    db.session.commit()
    return True

def db_del_shared_user(user_id, email):
    log.debug(f"db_del_shared_user email {email}")
    share_user = User.query.filter_by(email=email).one()
    if not share_user:
        # should never happen
        log.error(f"del could not find email {email}")
        return False
    # share all games with user
    # but first remove all entries in GameUser
    # (in case person is added more than once)
    GameUsers.query.filter_by(user_id=share_user.id).delete()
    db.session.commit()
    return True