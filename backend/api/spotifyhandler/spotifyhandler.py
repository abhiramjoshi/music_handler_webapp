#authenticate and create a class that will allow api calls.
import requests
from api.utils import *
from ytmusicapi.helpers import AuthenticationError
import json

class SpotifyHandler:
    def __init__(self, auth = None) -> None:
        self.auth = auth
        self.base_endpoint = "https://api.spotify.com/v1/"

    def authenticate(self):
        #authentication flow
        pass

    def _check_auth(self):
        if not self.auth:
            raise AuthenticationError('User needs to be authenticated to perform this function') 
    
    def send_get_request(self, endpoint, header, params):
        header = header
        params = params
        return requests.get(self.base_endpoint + endpoint, headers=header, params=params)

    def send_post_request(header, endpoint, params):
        pass
    
    def get_playlists(self):
        self._check_auth()
        playlist_endpoint = "me/playlists"
        #print('self.auth:')
        #print(self.auth)
        header = {'Authorization': 'Bearer ' + self.auth}
        params = {
            'limit':50,
            'fields':"description,external_urls,href,id,name,tracks"
        }
        response = self.send_get_request(endpoint = playlist_endpoint, header = header, params = params).json()
        #print('Playlist:')
        #print(response)
        try:
            playlists = response['items']
            playlists = playlistJSONFormat(playlists)
        except KeyError:
            if response['error']['status'] in [401, 400]:
               raise RefreshRequired
            else:
                return response['error']
        for playlist in playlists:
            playlist['tracks'] = self.get_playlist_tracks(playlist['id'], playlist["tracks"]["total"])
        return playlists

    def get_playlist_tracks(self, playlist_id, total_tracks):
        self._check_auth()
        playlist_endpoint = f"playlists/{playlist_id}/tracks"
        header = {'Authorization': 'Bearer ' + self.auth}
        tracks = []
        for track_offset in range((total_tracks//100) + 1):
            params = {
                'market': 'from_token',
                'offset': (track_offset*100),
                'fields':'items(track(id,name,artists,duration_ms))'
            }
            response = self.send_get_request(endpoint = playlist_endpoint, header=header, params= params).json()
            try:
                tracks += response['items']
            except KeyError:
                #print(response)
                raise NoTokenException
        return tracks

    def merge_playlists():
        pass

    def create_playlist():
        pass                                          
        