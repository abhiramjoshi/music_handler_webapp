from ytmusicapi import YTMusic
from api.utils import *
#Create a YTMusic authenticated user class. Goal is to return JSON representations of playlists, songs, and other things.
#Youtube music already handles the authentication, important things here are cookie and google visitor id.
#Front end will attempt to log in, you can also continue as a guest. 
#If you log in then you will need to store the YTmusic headers in the background DB and retrieve them. 
#If the headers recieved are null then return null. 
class YTMusicHandler():
    def __init__(self, headers) -> None:
        self.auth = headers
        self.servicemanager = YTMusic(self.auth) #Get auth from frontend

    def authenticate(self, headers = None):
        """Authenticate the YTMusic session"""
        #headers = get_headers_from_db Check in frontend if headers exist, if not then get user input for headers.
        YTMusic.setup(filepath=None, headers_raw=headers)

    def sync_local_library(self):
        self.playlists = self.get_playlist()

    def get_playlist(self):
        try:
            playlists = self.servicemanager.get_library_playlists()
            #use the get playlist method to get details of each user playlist. Need description, need url.
            #full_playlists_infos = []
            for i,_ in enumerate(playlists):
                try:
                    playlist = playlists.pop(i)
                    playlist_ = self.servicemanager.get_playlist(playlistId=playlist['playlistId'], limit=0)
                    playlist_['url'] = f'https://music.youtube.com/playlist?list={playlist_["id"]}' 
                    playlists.insert(i, playlist_)
                except Exception as e:
                    print('Error at index', i)
                    print(str(e))
                    pass
            return playlists
        except AuthenticationError:
            return {}
        except Exception as e:
            if '403' in str(e):
                raise HeadersAuthenticationError

    def remove_duplicates(self, playlist):
        songs = {}
        raw_songs = self.servicemanager.get_playlist(playlist['id'], playlist['count'])['tracks']
        for song in raw_songs:
            songs.update({song["videoID"]:song})
        return list(songs.values())

    def merge_playlists(playlists_to_merge):
        merged_playlist = {}
        for playlist in playlists_to_merge:
            playlist_tracks = {track['videoID']: track for track in playlist['tracks']}
            merged_playlist.update(playlist_tracks)





if __name__ == "__main__":
    pass