from flask import Flask, render_template, flash, redirect, url_for, request
import fairplay

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
@app.route('/groups', methods=['GET'])
def groups():
  if request.method == 'GET':
    # Call your function when the form is submitted
    g = fairplay.get_groups()
    print(len(g))
    fairplay.print_groups(g)
    return render_template(
        'groups.html',
        groups=g,
    )


if __name__ == '__main__':
  # replit needs to use 0.0.0.0
  app.run(host='0.0.0.0', port=8080)
