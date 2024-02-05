#!/usr/bin/env python3

from flask import Flask, render_template, flash, redirect, url_for, request
import fairplay
from logger import log as log
import json
import player
import os
import strong
import sys

from flask import Flask, jsonify, render_template, flash, redirect, url_for, request, session
from flask_dance.contrib.google import google
from flask_dance.contrib.facebook import facebook
from flask_login import logout_user, login_required, current_user
from models import db, login_manager, User
from oauth import google_blueprint, facebook_blueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError
from models import db_get_data, db_get_data_roster, db_set_game, db_get_games, db_save_game, db_delete_game, db_change_game
from models import db_get_shared_users, db_add_shared_user, db_del_shared_user
from context_processors import git_commit_id
import logging



# fairtimesport.com - registered
# fairplaytime.ca
# fairplayti.me
# fairplays.app
# fairplay.coach
# fairplayball.ca
# lineupgen.com - registered

# TODO: add flask_socketio if we need async updates to web (multi-user)
# TODO: add flask_wtf if we need to add form validation
# TODO: add flask_mail if we need to send emails
# TODO: generate notes under shifts with some explanations like
#        - 4 players get 2 shifts when there are 15 players.
# TODO: change drag image when over roster and when hoving over shift with duplicate player
# TODO: when dragging players around you could violate fairplay. we need to highlight this on the web somehow. red banner? roster could be over roster?
# TODO: separate page for roster creation but main page should be able to easily remove a player from the roster - a page refresh starts back from full roster. thish would mean the add player button and field would be on the roster creation page
# TODO: change player cursor: not-allowed if double players
# TODO: in python code change 'players' array to 'roster'
# TODO: on mobile could display just number,initials/shifts on shift - to fit on iphone.
# TODO: switch frontend from JS to react-native. this will allow it to run as an app on
#       ios/andriod.
#       https://github.com/computerjazz/react-native-draggable-flatlist
#       https://github.com/marconunnari/trello-clone
# TODO: widgetize to plugin to other sites
# TODO: teamsnap integration? parse webpage to get roster
# TODO: plan out multiple games at once. (like for a tournament). would have to save game in a table and adjust prevshifts accordingly. this is a lot of functionality - would have to work on MUCH later. save game title and notes section in a saved game.
#       save games and present them in a dropdown list in toolbar - load when selected.
# TODO: field to fill in game info for printing
# TODO: notes section for printout
# TODO: make another pass at the end to try and remove double shifts
# TODO: might be useful to sort the roster by shifts so it's easy to see who's got the low numbers (while planning multiple games)
# TODO: mobile (phone) should be a menu rather than buttons
# TODO: hover over roster header should display what the fairplay is for the roster size.
# TODO: could move python fairplay code to client side (better for scaling)
# TODO: lockedtoshift (lts) corresponds to players - not the saved shifts.
# TODO: need to logout and be able to choose a different google user.
# TODO: when shift is created, sort by colour, then number. either that or preserve shift/group order when saved
# TODO: mobile UI should be swipe left/right for shifts/groups
# TODO: extend player db object with non-db params and get rid of player.py (only one representation of a Player)
# TODO: need to get email permission from facebook login as well.
# TODO: limit text field size - and optimze length of text in database to match.
# TODO: consider using Celery for pipelining requests
# TODO: option to enable prevshifts. considering all saved games when running fairplay on default.
# TODO: multiple rosters under one user (if coach for more than one team)
# TODO: tooltip to explain what the player colours are for.
# TODO: colour shift decoration if outlier. i.e. - if 13 players highlight the one with 4 shifts. if 15 players - hightlight the ones with 2 shifts.
# TODO: use pusher.com for concurrent editing with multiple users
# TODO: consider supabase.com for db hosting and social authentiation
# TODO: limit login to one profile per email. (so can't go google and facebook with same email)
# TODO: fairplay fails if more than 15 players in roster
# TODO: proper error reporting from server red banner with error (otherwise it's silent)

app = Flask(
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)


handler = logging.FileHandler('your_log_file.log')  # Specify the log file
handler.setLevel(logging.INFO)  # Set the logging level
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.context_processor
def inject_git_commit_id():
    return git_commit_id()

def generate_json_data(roster, shifts, groups):
  data = {
      "status" : "ok",
      "players": json.dumps(roster, cls=player.PlayerEncoder),
      "shifts": json.dumps(shifts, cls=player.PlayerEncoder),
      "groups": json.dumps(groups, cls=player.PlayerEncoder),
  }
  #log.debug(data)
  return data


@app.route('/')
def home_page():
  # data will be loaded with onload and the getdata route
  app.logger.info(f"Incoming request from IP address: {request.remote_addr}")
  return render_template('index.html')

# this route is for any form submission,
# moving players, deleting players
@app.route('/updatedata', methods=['POST'])
def updatedata():
  # take shifts from web and update our local copy
  data = request.get_json()
  #log.debug(data)
  roster, shifts, groups = fairplay.update(data) # uses data["roster"] inside
  # all the smarts are done in python code.
  # so when a player moves we need to run part of the
  # fairplay logic and feed back the information back to
  # the web to be displayed
  # for example - doubleshifts
  # this is ok - because we can remove the django code
  # in index.html - and generate the shifts all in the
  # same JS code.
  if data["game_id"] != 0: # will be 0 for roster page
    fairplay.fairplay_validation(roster, shifts)
    db_set_game(current_user.id, game_id=data["game_id"], shifts=shifts, roster=roster)
  return generate_json_data(roster, shifts, groups)


@app.route('/getdata', methods=['POST'])
def getdata():
  if current_user.is_authenticated == False:
     return json.dumps({"status" : "not_logged_in"})
  data = request.get_json()
  roster, shifts, groups = db_get_data(current_user.id, data["game_id"])
  fairplay.fairplay_validation(roster, shifts) # to mark dbl/violate
  fairplay.fairplay_updateshiftcount(shifts, roster)
  return generate_json_data(roster, shifts, groups)

@app.route('/getdataroster', methods=['GET'])
def getdataroster():
  if current_user.is_authenticated == False:
     return json.dumps({"status" : "not_logged_in"})
  players, groups = db_get_data_roster(current_user.id)
  return generate_json_data(players, [], groups)

@app.route('/settings', methods=['GET'])
def roster():
  return render_template('settings.html')


@app.route('/runfairplay', methods=['POST'])
def runfairplay():

  # load data - to see what's locked
  data = request.get_json()

  # will take player list and run alogorithm
  # returning shifts to web page
  roster, shifts = fairplay.run_fairplay_algo(data) # uses data["roster"] inside
  db_set_game(current_user.id, game_id=data["game_id"], shifts=shifts, roster=roster)

  return generate_json_data(roster, shifts, [])


@app.route('/getgames', methods=['GET'])
def getgames():
  if current_user.is_authenticated == False:
     return json.dumps({"status" : "not_logged_in"})
  games = db_get_games(current_user.id)

  data = {
    "status" : "ok",
    "games": json.dumps(games)
  }
  return data

@app.route('/savegame', methods=['POST'])
def savegame():
  data = request.get_json()
  games = db_save_game(current_user.id, data["game_id"])
  data = {
    "status" : "ok",
    "games": json.dumps(games)
  }
  return data

@app.route('/updatesettings', methods=['POST'])
def updatesettings():
  data = request.get_json()
  if db_add_shared_user(current_user.id, data["share_email"]) == False:
    status = "failed"
  else :
    status = "ok"
  shared_users = db_get_shared_users(current_user.id)
  data = {
    "status" : status,
    "shared_users": json.dumps(shared_users)
  }
  return data

@app.route('/deleteshareduser', methods=['POST'])
def deleteshareduser():
  data = request.get_json()
  if db_del_shared_user(current_user.id, data["share_email"]) == False:
    data = {
      "status" : "failed",
      "reason" : "could not find email"
    }
  else :
    shared_users = db_get_shared_users(current_user.id)
    data = {
      "status" : "ok",
      "shared_users": json.dumps(shared_users)
    }
  return data

@app.route('/getsettings', methods=['POST'])
def getsettings():
  shared_users = db_get_shared_users(current_user.id)
  data = {
    "status" : "ok",
    "shared_users": json.dumps(shared_users)
  }
  return data

@app.route('/deletegame', methods=['POST'])
def deletegame():
  data = request.get_json()
  log.debug(f"deleting game {data['game_id']}")
  games = db_delete_game(current_user.id, data["game_id"])
  data = {
    "status" : "ok",
  }
  return data

@app.route('/changegamename', methods=['POST'])
def changegamename():
  data = request.get_json()
  log.debug(data)
  games = db_change_game(current_user.id, data["game_id"], data["name"])
  data = {
    "status" : "ok",
  }
  return data







# social login for flask using flask-dance
# https://testdriven.io/blog/flask-social-auth/

app.secret_key = "supersekritkey"
app.register_blueprint(google_blueprint, url_prefix="/login")
app.register_blueprint(facebook_blueprint, url_prefix="/login")
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 1
app.config['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 1 # google changes scope on us
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./fairplay.db"


db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/google")
def google_login():
  if not google.authorized:
    session.clear() # in case there was a bad session in the browser cache
    redirect_url = url_for("google.authorized")
    log.debug(redirect_url)
    return redirect(redirect_url)
  # try:
  #   resp = google_blueprint.session.get("/oauth2/v1/userinfo")
  # except TokenExpiredError:
  #   print("token is expired: logging out")
  #   logout_user()
  #   # this doens't work - had to remove database
  #   return redirect(url_for("home_page"))

@app.route("/facebook")
def facebook_login():
  if not facebook.authorized:
    session.clear() # in case there was a bad session in the browser cache
    redirect_url = url_for("facebook.authorized")
    log.debug(redirect_url)
    return redirect(redirect_url)
    # try:
    #   return redirect(redirect_url)
    # except MismatchingStateError as e:
    #   log.debug(f"Caught MismatchingStateError: {e}")
    #   session.clear()
    # except Exception as e:
    #   log.debug(f"Caught unexpected exception: {e}")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))

# use free Certificate Authority (CA) https://letsencrypt.org/getting-started/
# https://pimylifeup.com/raspberry-pi-ssl-lets-encrypt/
# open port 80 for roocell.com
# run
# sudo certbot certonly --standalone -d roocell.com -d www.roocell.com
# this starts a webserver on port 80 to authorize with the server.
# this generates certs locally with an expiry date (put these in the app.run() below)
# have to rerun to renew

# force https redirect
@app.before_request
def before_request():
    if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

myport = 4466
if len(sys.argv) == 2:
  myport = sys.argv[1]

if __name__ == '__main__':
  # replit needs to use 0.0.0.0
    app.run(host='0.0.0.0', port=myport, debug=True,
          ssl_context=("/etc/letsencrypt/live/roocell.com/fullchain.pem", 
                       "/etc/letsencrypt/live/roocell.com/privkey.pem")
          )
  # app.run(host='0.0.0.0', port=myport, debug=False)