import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.contrib.facebook import facebook, make_facebook_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.consumer import OAuth2ConsumerBlueprint
from models import OAuth, db, User
import json
from logger import log as log

# if you failed to auth seems like cookies can get messed up and you get this error
# MismatchingStateError: mismatching_state: CSRF Warning! State not equal in request and response
# resolve it by closing tab, then browswer(app) completely and starting over.


# load keys from file
# get keys from
# https://console.cloud.google.com/
# https://developers.facebook.com/
json_file_path = 'services.json'
with open(json_file_path, 'r') as file:
    services = json.load(file)

for service, service_data in services.items():
    print(f"service: {service}")
    for key, value in service_data.items():
        print(f"    {key}: {value}")

# Facebook
facebook_blueprint = make_facebook_blueprint(
    client_id=services['facebook']['client'],
    client_secret=services['facebook']['secret'],
    scope=["email"],
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

# email permission requires business verification
@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    resp = facebook.get("/me?fields=id,name,email")
    if resp.ok:
        username = resp.json()["id"]
        name = resp.json()["name"]
        email = resp.json().get("email")
        service = "facebook"
        log.debug(f"name {name} email {email}")

        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username, service=service, name=name, email=email)            
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            log.debug(f"An unexpected error occurred: {e}")
        login_user(user)


# Google
google_blueprint = make_google_blueprint(
    client_id=services['google']['client'],
    client_secret=services['google']['secret'],
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):

  resp = blueprint.session.get("/oauth2/v1/userinfo")
  if resp.ok:
    username = resp.json()["id"]
    email = resp.json()["email"]
    service = "google"

    log.debug(f"google user_id {username} {email}")

    query = User.query.filter_by(username=username)
    try:
        user = query.one()
    except NoResultFound:
        user = User(username=username, service=service, email=email)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        log.debug(f"An unexpected error occurred: {e}")
    login_user(user)  
