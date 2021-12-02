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

    def get_all_playlists(self):
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

    def get_playlist(self, playlist):
        playlist_obj = self.servicemanager.get_playlist(playlist, limit=1)
        track_count = playlist_obj["trackCount"]
        playlist_obj = self.servicemanager.get_playlist(playlist, limit=track_count)
        return playlist_obj

    def get_playlist_tracks(self, playlist):
        """
        Returns playlist track IDs (videoIds)
        """
        playlist = self.servicemanager.get_playlist(playlist)
        id = [track['videoId'] for track in playlist['tracks']]
        return id

    def create_playlist(self, title, description, video_ids, privacy_status='PRIVATE'):
        return self.servicemanager.create_playlist(title, description, privacy_status, video_ids)

    def add_tracks(self, playlist, tracklist):
        """
        Add songs to an existing playlist

        playlistId: Playlist id
        videoIds: List of Video ids
        """
        return self.servicemanager.add_playlist_items(playlist, tracklist)

    def remove_duplicates(self, playlists, primary_pl=None):
        """
        Remove duplicates from a set of playlists. Returns a set of collated playlist
        tracks with duplicates removed as well as a set of tracks that that are not 
        present in the 'primary playlist' provided.

        playlists: list of playlist IDs from which duplicates will be removed
        primary_pl: specify the 'primary playlist' in the provided set. 
        """
        if primary_pl is None:
            primary_pl = playlists[0]

        tracks_present = set(self.get_playlist_tracks(primary_pl))    
        tracks_to_add = []
        for playlist in playlists:
            if playlist == primary_pl:
                continue
            tracks = self.get_playlist_tracks(playlist) #get tracklist 
            tracks_to_add.extend(set(tracks).difference(tracks_present)) #record unaccounted for tracks
            tracks_present.update(tracks_to_add) #update unaccounted for tracks
        return tracks_present, tracks_to_add

    def merge_playlists(self, playlists_to_merge, merge_into = None, 
                        new_playslist_name=None, new_playlist_description=None, 
                        delete=False):
        """
        Merge playlists

        playlists_to_merge: List of playlist ids List[str]
        merge_into: Id of playlist to merge into, additional songs will be added to this playlist
        new_playslist_name: Name of newly created playlist (if not merging into existing)
        new_playslist_description: Description of newly created playlist
        delete: Delete playlists after merged
        """
        print('YT')
        if merge_into is not None:
            #add tracks to main playlist
            _, tracks_to_add = self.remove_duplicates(playlists_to_merge, merge_into)
            return self.add_tracks(merge_into, tracks_to_add)
        else:
            # create new playlist
            tracklist, _ = self.remove_duplicates(playlists_to_merge)
            
            #return self.create_playlist(new_playslist_name, new_playlist_description, list(tracklist))

if __name__ == "__main__":
    pass