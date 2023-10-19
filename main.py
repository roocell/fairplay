from flask import Flask, render_template, flash, redirect, url_for, request
import fairplay
from logger import log as log
import json
import player

# TODO: add flask_socketio if we need async updates to web
# TODO: should probably just hold python objects as dicts and then pass the entire
#       object back and forth to web over AJAX
# TODO: add flask_sqlalchemy if we need to persist data
# TODO: add flask_login if we need to persist login info
# TODO: add flask_wtf if we need to add form validation
# TODO: add flask_mail if we need to send emails
# TODO: add flask_bcrypt if we need to hash passwords
# TODO: generate notes under shifts with some explanations like
#        - 4 players get 2 shifts when there are 15 players.
# TODO: numbers and shifts as decorations rather than just text
# TODO: raise a red error div from the top if flask responds with error
#       like fairplay validation failed
# TODO: change drag image when over roster and when hoving over shift with duplicate player

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
  # run fairplay so we have all the data web the page comes up
  fairplay.load(
      "test/15p_3sl_0pv/players.json",
      "test/15p_3sl_0pv/stronglines.json",
      "test/15p_3sl_0pv/prevshifts.json",
  )

  return render_template('index.html')


# Define a route to handle form submission
@app.route('/updateshifts', methods=['POST'])
def updateshifts():
  # take shifts from web and update our local copy
  data = request.get_json()
  #log.debug(data)
  fairplay.updateshiftsfromweb(data)
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


@app.route('/runfairplay', methods=['GET'])
def runfairplay():
  # reset shifts - so if we continue to click fairplay - we don't exceed max shifts
  fairplay.reset_player_shifts()
  fairplay.shifts = []  # we're rebuilding shifts from scratch

  # will take player list and run alogorithm
  # returning shifts to web page
  fairplay.run_fairplay_algo(fairplay.players, fairplay.stronglines)

  return generate_json_data()


if __name__ == '__main__':
  # replit needs to use 0.0.0.0
  app.run(host='0.0.0.0', port=8080)
