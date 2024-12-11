from flask import Flask, redirect, request, session, jsonify, send_from_directory
from flask_cors import CORS
from flask_session import Session
from flask_bcrypt import Bcrypt # allows for password hashing (tip: hashed passwords won't match w/ PLAIN TEXTS)

from models import db, User # importing models.py
from config import ApplicationConfig # importing app config from config.py

import os
import requests
import urllib.parse
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)



app = Flask(__name__) # create app instance / representation, + serving static files from frontend/build
app.config.from_object(ApplicationConfig) # initialize app config from config.py, this comes after importing config.py


frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")


bcrypt = Bcrypt(app) # initializes Bcrypt for app
CORS(app, supports_credentials= True, origins=[frontend_url]) # CORS allows react and flask to communicate, support_cred allows user auth to take place
server_session = Session(app) # initializes Redis session for app, 'server_session' makes it a server-sided sesh instead of client-side (client-side is very insecure)
db.init_app(app) # initializes database connection w/ application, this comes after importing models.py




# creates the database, only run once
with app.app_context():
    db.create_all()



#testing
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'homepage'}), 200







# # Add after_request decorator to set CORS headers
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response















# define get user route, provides info of currently logged in user
# can test in Postman, now if you get rid of session cookie and do a GET request to this endpoint, it will show as an invalid session
    # if you login again and POST request to login endpoint, session cookie will be restored
    # clarifies that session is now running w session cookie when user logs in
@app.route("/@me", methods = ['GET'])
def get_current_user():
    user_id = session.get('user_id')

    if user_id:
    # if user id in session:
        user = User.query.filter_by(id = user_id).first()
        return jsonify({'logged_in': True, 'id': user.id, 'username': user.username, 'session': session}), 200
    else:
        return jsonify({'logged_in': False}), 401 # ***** this is the line that runs for the error *****



# define register route
#'POST' because we are registering and sending new username/ password to backend
@app.route("/register", methods = ['POST'])
def register():
     # getting json of username and password (from user input from React app)
    username = request.json['username']
    password = request.json['password']


    user_exists = User.query.filter_by(username = username).first() is not None # making query for usrnm, returns if statement below if theres an existing user
    if user_exists:
        return jsonify({'message': 'Username or email already exists.'}), 400 # 400 HTTP reponse status = bad request (MAKE SURE to add this so react can determine what the error msg is)
    else:
        hashed_password = bcrypt.generate_password_hash(password) #.decode('utf-8') # hashing password, then DECODE from byte to string so its stored as string ?
        new_user = User(username = username, password = hashed_password) # match the created usrnm / pswrd with new_user definition
        db.session.add(new_user) # add new user to db
        db.session.commit() # commit it to the db

        # session['user_id'] = new_user.id
        # FOR API TESTING, what we receive after entering usrnm/ pswrd
        return jsonify ({'id': new_user.id, 'username': new_user.username}), 201 # 201 HTTP reponse status = success + creation of new resource
    



# define main login route
#'POST' because we are logging in and sending username/ password to backend
@app.route("/user-login", methods = ['POST'])
def login():
    # getting json of username and password (from user input from React app)
    username = request.json['username']
    password = request.json['password']

    # # if user already logged in. Also makes sure user does not get logged out by new login request
    # if 'user' in session:
    #     return jsonify(message = "Already logged in."), 200

    # making query to get usrnm and pswrd from database, and making sure they match w inputted ones
    user = User.query.filter_by(username = username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id # storing user_id in session, that will be used to authenticate user for that session
        return jsonify({'logged_in': True, 'id': user.id, 'username': user.username}), 200 # 200 HTTP reponse status = success + requested info can be obtained
    else:
        return jsonify({'message': 'Invalid username or password.'}), 401 # 401 HTTP reponse status = authentification failed, invalid credentials
    



# define logout route when user logs out
@app.route('/logout', methods = ['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'}), 200


























# make constants for sensitive env. data
    #os handles env variables
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI") # link after user logs in

# Spotify endpoints
AUTH_URL = "https://accounts.spotify.com/authorize" # /spotify_login (where user logs in to spotify) 
TOKEN_URL = "https://accounts.spotify.com/api/token" # /callback (Spotify's token URL where Spotify grants access tokens)
API_BASE_URL = "https://api.spotify.com/v1/" # where we get user playlists + other info




# define spotify /login route
# provide parameters (params) spotify needs to give app access to user info
# make GET request to AUTH_URL w/ required params
@app.route("/spotify-login", methods = ['GET'])
def spotify_login():
    scope = 'user-read-private user-read-email, user-library-read' # what user info we need from Spotify

    #parameters required by spotify, its listed in their documentation
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'show_dialog': True, #    **   FOR DEBUGGING PURPOSES, SO CAN TEST IF LOGIN AGAIN WORKS, set to FALSE when DELPOYING !!  **
    }

    # GET request (to obtain user info)
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    # redirect user to spot Auth URL
    return jsonify({'auth_url': auth_url}), 200 # 200






# define /callback route (where user is sent back to after logging in and accepting Oauth2.0 - redirect_URI)
# check if user successfully logins in (will receive query param) or error (will get an error msg)
    # this is where we will get access token by sending spotify info it needs in request_body
# obtain access token (more info on bottom)
@app.route("/callback", methods = ['GET'])
def callback():

    # if login error
    if 'error' in request.args:
        return jsonify({"Error": "Falied to login", "error": request.args['error']})
    
    # if login success, obtain auth code
    if 'code' in request.args:
        # params needed to request to Spotify for access token
        request_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }

    #send request body off to spotify
        # POST request to Spotify's token URL (TOKEN_URL)
    response = requests.post(TOKEN_URL, data = request_body)

    #if successful, access token comes back as JSON object
    # will give a access token, a refresh token, and a expires_in (says how long unitl token expires)
    token_json = response.json()

    # storing access and refresh tokens Spotify gave us into session
        # need to store these in betw requests
    # turn current datetime into a timestamp for expires_in
        # shows us how long until access token expires
    session['access_token'] = token_json['access_token'] # will use to send requests to Spotify API
    session['refresh_token'] = token_json['refresh_token'] # will use to refresh access token when it expires
    session['expires_at'] = datetime.now().timestamp() + token_json['expires_in'] # datetime expires at 3600 for spotify (one day)


    # bringing user to dashboard after spotify login / database input, once user is at dashboard, will request spotify playlists
    return jsonify({'success': True}), 200










# define /playlists route which will use access token to retrieve user playlists
# check if access token is in session or not, or if it expired
# this is where playlists will be given back to user
@app.route("/playlists", methods = ['GET'])
def get_playlists():

    if 'access_token' not in session:
        return redirect(f"{frontend_url}/dashboard") # change to redirect to /dashboard after debugging done
    
    # make sure access token has not expired
    if datetime.now().timestamp() > session['expires_at']: # if access token datetime > 3600 (expired)
        return redirect("/refresh-token") # refresh token will refresh access token so user doesn't have to re-enter password again

    #retrieve user playlist if access token is good
    headers = {
        'Authorization': f"Bearer {session['access_token']}" # provide access token in auth header
    }

    # GET request to Spotify's API (API_BASE_URL) to get user data
        # /me/playlist = endpoint targeted to retrieve user's playlists
        # headers contains access token
    response = requests.get(API_BASE_URL + "me/playlists", headers = headers)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch playlists'}), response.status_code
    # once get JSON response of playlists from Spotify:
    playlists = response.json()



    # return playlists to user as JSON response
    # after that, redirecting user to dashboard w/ their playlists
    return jsonify(playlists), 200












# define /refresh_token so refresh_token can refresh access_token if it expires
@app.route("/refresh_token")
def refresh_token():

    if 'refresh_token' not in session:
        return redirect("/spotify-login")
    
    # get fresh access token if access token expired
    if datetime.now().timestamp() > session['expires at']: # if access token datetime > 3600 (expired)
        # few params needed by Spotify to get fresh access token
        request_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }

        # POST request (sending params to Spotify for refresh token)
        reponse = requests.post(TOKEN_URL, data = request_body)
        # will give new access token and new expires_in
        new_token_json = reponse.json()

        # override old access token and old expiry date (will always keep using same refresh token)
        session['access_token'] = new_token_json['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_json['expires_in']

        return redirect("/callback")
    



# route handling unlinking playlist when user clicks unlink button
# post because 'p' variable is sent in regard to playlist.id
@app.route("/unlink-playlist", methods = ['POST']) 
def unlink_playlist():
    data = request.get_json # getting JSON playlist data from the popPlaylist POST request
    playlist_id = data.__get__('p')

    if not playlist_id:
        return jsonify({'Error': 'Playlist ID is required to unlink playlist'}), 400
    
    # try:
    return jsonify ({'success': True, 'message': 'Playlist successfully unlinked'}), 200
    # except:
    #     return jsonify ({'Error': 'Failed to unlink playlist'}), 500 # good practice to distinguish diff error messages and their correct HTTP response




if __name__ == "__main__":
    app.run()