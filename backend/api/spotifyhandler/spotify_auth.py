import requests
import json
import base64
from backend.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from api.utils import *

strb64encode = lambda x: base64.b64encode(x.encode('ascii'))
CLIENT_ID = SPOTIFY_CLIENT_ID
CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
REDIRECT_URI = "http://127.0.0.1:8000/api/callback/spotify/"
SCOPE_LIST = ["user-library-read", "playlist-read-collaborative", "playlist-read-private", "user-library-modify", "playlist-modify-private", "playlist-modify-public"]

def send_auth_request():
    endpoint = "https://accounts.spotify.com/authorize"
    params = {
        'client_id':CLIENT_ID,
        'response_type':'code',
        'redirect_uri': REDIRECT_URI,
        'state': "Jalepenos",
        'show_dialog':True,
        'scope': ' '.join(SCOPE_LIST)
    }
    
    response = requests.get(endpoint, params=params)
    return response, params

def exchange_code_for_token(auth_code):
    endpoint = "https://accounts.spotify.com/api/token"
    body = {
        'grant_type':'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(endpoint, data=body)
    if response.status_code == 200:
        response = json.loads(response.text)
        return response['access_token'], response['refresh_token']
    else:
        return response, None

def refresh_token(refresh_token:str) -> str:
    """Allows us to get a refreshed API Key"""
    print('Refresh Token:')
    print(refresh_token)
    if refresh_token is None:
        raise NoTokenException
    endpoint = "https://accounts.spotify.com/api/token"
    header = {
        'Authorization': 'Basic ' + str(strb64encode(CLIENT_ID + ':' + CLIENT_SECRET))[2:-1]
    }
    body = {
        'grant_type':'refresh_token',
        'refresh_token': refresh_token,
    }
    response = requests.post(endpoint, data=body, headers=header)
    print('Refresh request:')
    print(response.request.body)
    print('Refresh:')
    print(response.text)
    if response.status_code == 200:
        response = json.loads(response.text)
        return response
    else:
        return response