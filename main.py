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

# fairtimesport.com - registered
# fairplaytime.ca
# fairplayti.me
# fairplay.app
# fairplay.coach

# TODO: add flask_socketio if we need async updates to web (multi-user)
# TODO: add flask_wtf if we need to add form validation
# TODO: add flask_mail if we need to send emails
# TODO: generate notes under shifts with some explanations like
#        - 4 players get 2 shifts when there are 15 players.
# TODO: numbers and shifts as decorations rather than just text
# TODO: change drag image when over roster and when hoving over shift with duplicate player
# TODO: when dragging players around you could violate fairplay. we need to highlight this on the web somehow. red banner? roster could be over roster?
# TODO: separate page for roster creation but main page should be able to easily remove a player from the roster - a page refresh starts back from full roster. thish would mean the add player button and field would be on the roster creation page
# TODO: change player cursor: not-allowed if double players
# TODO: in python code change 'players' array to 'roster'
# TODO: need UI to adjust stronglines
# TODO: on mobile could display just number,initials/shifts on shift - to fit on iphone.
# TODO: switch frontend from JS to react-native. this will allow it to run as an app on
#       ios/andriod.
#       https://github.com/computerjazz/react-native-draggable-flatlist
#       https://github.com/marconunnari/trello-clone
# TODO: roster page should operate on full roster. fairplay page operates on game roster.
#       this way roster page can reset to full roster, then goto game roster and remove
#       players.
# TODO: widgetize to plugin to other sites
# TODO: teamsnap integration? parse webpage to get roster
# TODO: plan out multiple games at once. (like for a tournament). would have to save game in a table and adjust prevshifts accordingly. this is a lot of functionality - would have to work on MUCH later. save game title and notes section in a saved game.
# TODO: field to fill in game info for printing
# TODO: notes section for printout
# TODO: make another pass at the end to try and remove double shifts
# TODO: might be useful to sort the roster by shifts so it's easy to see who's got the low numbers (while planning multiple games)

app = Flask(
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)


def generate_json_data():
  data = {
      "players": json.dumps(fairplay.players, cls=player.PlayerEncoder),
      "shifts": json.dumps(fairplay.shifts, cls=player.PlayerEncoder)
  }
  #log.debug(data)
  return data


@app.route('/')  # What happens when the user visits the site
def home_page():
  current_file_path = os.path.abspath(__file__)
  current_directory = os.path.dirname(current_file_path)

  # run fairplay so we have all the data web the page comes up
  # only do this if there's nothing there yet.
  if len(fairplay.players) == 0:
    fairplay.load(
        current_directory + "/test/15p_3sl_0pv/players.json",
        current_directory + "/test/15p_3sl_0pv/stronglines.json",
        current_directory + "/test/15p_3sl_0pv/prevshifts.json",
    )

  return render_template('index.html')


# Define a route to handle form submission
@app.route('/updatedata', methods=['POST'])
def updatedata():
  # take shifts from web and update our local copy
  data = request.get_json()
  #log.debug(data)
  fairplay.update(data)
  # all the smarts are done in python code.
  # so when a player moves we need to run part of the
  # fairplay logic and feed back the information back to
  # the web to be displayed
  # for example - doubleshifts
  # this is ok - because we can remove the django code
  # in index.html - and generate the shifts all in the
  # same JS code.
  fairplay.fairplay_validation()
  return generate_json_data()


@app.route('/getdata', methods=['GET'])
def getdata():
  return generate_json_data()


@app.route('/roster', methods=['GET'])
def roster():
  return render_template('roster.html')


@app.route('/runfairplay', methods=['POST'])
def runfairplay():

  # load data - to see what's locked
  data = request.get_json()

  # only clear the shifts that aren't locked
  fairplay.clear_shifts_not_locked(data)

  # will take player list and run alogorithm
  # returning shifts to web page
  fairplay.run_fairplay_algo(fairplay.players, fairplay.stronglines)

  fairplay.print_shifts(fairplay.shifts)

  return generate_json_data()


# social login for flask using flask-dance
# https://testdriven.io/blog/flask-social-auth/

app.secret_key = "supersekritkey"
app.register_blueprint(google_blueprint, url_prefix="/login")
app.register_blueprint(facebook_blueprint, url_prefix="/login")
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 1
app.config['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 1 # google changes scope on us
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"


db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/google")
def google_login():
  if not google.authorized:
    session.clear() # in case there was a bad session in the browser cache
    redirect_url = url_for("google.authorized")
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






myport = 4466
if len(sys.argv) == 2:
  myport = sys.argv[1]

if __name__ == '__main__':
  # replit needs to use 0.0.0.0
  app.run(host='0.0.0.0', port=myport, ssl_context = 'adhoc', debug=True)
