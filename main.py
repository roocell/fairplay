from flask import Flask, render_template, flash, redirect, url_for, request
import fairplay
from logger import log as log

# TODO: add flask_socketio if we need async updates to web

app = Flask(
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)


@app.route('/')  # What happens when the user visits the site
def home_page():
  # run fairplay so we have all the data web the page comes up
  fairplay.load(
      "test/15p_3sl_0pv/players.json",
      "test/15p_3sl_0pv/stronglines.json",
      "test/15p_3sl_0pv/prevshifts.json",
  )

  return render_template(
      'index.html',  # Template file path, starting from the templates folder. 
      players=fairplay.players,
  )


# Define a route to handle form submission
@app.route('/updateshifts', methods=['POST'])
def updateshifts():
  # take shifts from web and update our local copy
  data = request.get_json()
  #log.debug(data)
  fairplay.updateshiftsfromweb(data)
  return ({"message": "JSON data received successfully"})


if __name__ == '__main__':
  # replit needs to use 0.0.0.0
  app.run(host='0.0.0.0', port=8080)
