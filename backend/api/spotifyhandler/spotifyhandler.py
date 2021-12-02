#authenticate and create a class that will allow api calls.
import requests
from api.utils import *
import json
from pprint import pprint

class SpotifyHandler:
    def __init__(self, auth = None) -> None:
        self.auth = auth
        self.base_endpoint = "https://api.spotify.com/v1/"

    def authenticate(self):
        return 'Bearer ' + self.auth

    def _check_auth(self):
        if not self.auth:
            raise AuthenticationError('User needs to be authenticated to perform this function') 
    
    def send_get_request(self, endpoint, header, params = None):
        header = header
        header['Content-Type'] = 'application/json'
        params = params
        return requests.get(self.base_endpoint + endpoint, headers=header, params=params).json()

    def send_post_request(self, endpoint, header, data):
        header = header
        header['Content-Type'] = 'application/json'
        data = json.dumps(data)
        return requests.post(self.base_endpoint + endpoint, headers=header, data=data).json()
    
    def get_user(self):
        user_endpoint = "me"
        header = {'Authorization': 'Bearer ' + self.auth}
        return self.send_get_request(user_endpoint, header)

    def get_all_playlists(self):
        self._check_auth()
        playlists = []
        playlist_endpoint = "me/playlists"
        no_params = False
        while playlist_endpoint is not None:
            header = {'Authorization': 'Bearer ' + self.auth}
            params = {
                'limit':50,
                'fields':"description,external_urls,href,id,name,tracks"
            }
            
            if no_params:
                response = self.send_get_request(endpoint = playlist_endpoint, header = header, params = params)
            else:
                params = {
                    'fields':"description,external_urls,href,id,name,tracks"
                }
                response = self.send_get_request(endpoint=playlist_endpoint, header=header, params=params)
            
            try:
                playlist_endpoint = response['next']
                playlists += response['items']
                no_params = True
                #playlists = playlistJSONFormat(playlists)
            except KeyError:
                if response['error']['status'] in [401, 400]:
                    raise RefreshRequired
                else:
                    return response['error']
            except Exception:
                return None

            for playlist in playlists:
                playlist['tracks'] = self.get_playlist_tracks(playlist['id'], playlist["tracks"]["total"])
        
        return playlists
    
    def get_playlist(self, playlist_id):
        endpoint = f'playlists/{playlist_id}'
        header = {'Authorization': self.authenticate()}
        params = {
            'fields':"description,external_urls,href,id,name,tracks"
        }
        response = self.send_get_request(endpoint=endpoint, header=header, params=params)
        return response

    def get_playlist_tracks(self, playlist_id, total_tracks):
        self._check_auth()
        playlist_endpoint = f"playlists/{playlist_id}/tracks"
        header = {'Authorization': 'Bearer ' + self.auth}
        tracks = []
        for track_offset in range((total_tracks//100) + 1):
            params = {
                'market': 'from_token',
                'offset': (track_offset*100),
                'fields':'items(track(id,name,artists,duration_ms,uri))'
            }
            response = self.send_get_request(endpoint = playlist_endpoint, header=header, params= params)
            try:
                tracks += response['items']
            except KeyError:
                #print(response)
                raise NoTokenException
        return tracks
    
    def remove_duplicates(self, playlists, primary_pl=None):
        if primary_pl is None:
            primary_pl = playlists[0]
        total_tracks = self.get_playlist(primary_pl)['tracks']['total']
        tracks = [track['track']['uri'] for track in self.get_playlist_tracks(primary_pl, total_tracks)]
        tracks_present = set(tracks)    
        tracks_to_add = []
        for playlist in playlists:
            if playlist == primary_pl:
                continue
            total_tracks = self.get_playlist(primary_pl)['tracks']['total']
            tracks = [track['track']['uri'] for track in self.get_playlist_tracks(playlist, total_tracks)] #get tracklist 
            tracks_to_add.extend(set(tracks).difference(tracks_present)) #record unaccounted for tracks
            tracks_present.update(tracks_to_add) #update unaccounted for tracks
        return tracks_present, tracks_to_add
    
    def add_tracks(self, playlist, tracklist):
        add_tracks_endpoint = f'playlists/{playlist}/tracks'
        header = {'Authorization': self.authenticate()}
        data = {
            "uris": tracklist
        }
        response = self.send_post_request(add_tracks_endpoint, header, data)
        print(response)
        try:
            success = response['snapshot_id']
            return response
        except KeyError:
            if response['error']['status'] in [429]:
                raise NoTokenException


    def create_playlist(self, title, description, tracks, privacy_status = 'false'):
        user_id = self.get_user()['id']
        create_track_endpoint = f'users/{user_id}/playlists'
        header = {'Authorization': 'Bearer ' + self.auth}
        data = {
            "name": title,
            "description": description,
            "public": privacy_status
        }    
        response = self.send_post_request(create_track_endpoint, header, data)
        print(response)
        new_pl_id = response["id"]
        return self.add_tracks(new_pl_id, tracks)

    def merge_playlists(self, playlists_to_merge, merge_into = None, 
                        new_playlist_name=None, new_playlist_description=None, 
                        delete=False):

        """
        Merge playlists

        playlists_to_merge: List of playlist ids List[str]
        merge_into: Id of playlist to merge into, additional songs will be added to this playlist
        new_playslist_name: Name of newly created playlist (if not merging into existing)
        new_playslist_description: Description of newly created playlist
        delete: Delete playlists after merged
        """
        print('Spotify')
        if merge_into is not None:
            #add tracks to main playlist
            _, tracks_to_add = self.remove_duplicates(playlists_to_merge, merge_into)
            return self.add_tracks(merge_into, tracks_to_add)
        else:
            # create new playlist
            tracklist, t = self.remove_duplicates(playlists_to_merge)
            print('Creating PL')
            return self.create_playlist(new_playlist_name, new_playlist_description, list(tracklist))
                              
        