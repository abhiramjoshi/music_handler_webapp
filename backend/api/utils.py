import base64
import json
from ytmusicapi import helpers

"""Errors"""
class RefreshRequired(Exception):
    pass

class NoTokenException(Exception):
    pass

class HeadersAuthenticationError(Exception):
    pass

class AuthenticationError(Exception):
    pass

def stringbase64encode(message:str):
    bytes = message.encode()
    b64 = base64.b64encode(bytes)
    return b64

def playlistJSONFormat(playlist_objects, keys = ['id', 'name', 'description', 'external_urls', 'images', 'tracks']):
    filtered_playlist_objs = []
    for playlist_obj in playlist_objects:
        playlist = {key:playlist_obj[key] for key in keys}
        filtered_playlist_objs.append(playlist)
    return filtered_playlist_objs 

def standardPlaylistJSON(playlist_objects, keys = ['id', 'name', 'description', 'external_urls', 'images', 'tracks']):
    """Returns a standardized format for playlist JSON objects"""
    standard_pls = []
    for playlist in playlist_objects:
        pl = {}
        pl['id'] = playlist['id']
        pl['description'] = playlist['description']
        pl['tracks'] = playlist['tracks']
        try:
            pl['title'] = playlist['title']
        except KeyError:
            pl['title'] = playlist['name']
        try:
            pl['url'] = playlist['url']
        except KeyError:
            pl['url'] = playlist['external_urls']['spotify']
        try:
            pl['image'] = playlist['thumbnails'][-1]['url']
        except KeyError:
            try:    
                pl['image'] = playlist['images'][0]['url']
            except IndexError:
                print(playlist)

        standard_pls.append(pl)
    
    return standard_pls


def parse_string_dict(str_dict:str):
    key_value_pairs = str_dict.split(';')
    key_value_pairs = [pairs.split(':') for pairs in key_value_pairs]
    return_dict = {key_value[0]:key_value[1] for key_value in key_value_pairs}
    return return_dict

def headers_format(headers_dict:str):
    """Input headers in a dictionary-like format and return a string that is accepted by the ytmusicapi setup function"""
    headers_dict = json.loads(headers_dict)
    str_headers = '\n'.join([f'{key}: {headers_dict[key]}' for key in headers_dict])
    return str_headers

def verify_cookie(cookie):
    try:
        sapisid = helpers.sapisid_from_cookie(cookie)
    except KeyError as e:
        raise Exception(str(e))

def verify_x_goog_auth_user(x_goog_auth_user):
    if x_goog_auth_user not in [0,1,'0','1']:
        raise Exception('Invalid value for x-goog-authuser')

def verify_x_goog_visitor_id(x_goog_visitor_id):
    pass

def verify_ytheaders(headers):
    cookie = headers.get('cookie', headers.get('Cookie'))
    verify_cookie(cookie)
    x_goog_auth_user = headers.get('x-goog-authuser')
    verify_x_goog_auth_user(x_goog_auth_user)
    x_goog_visitor_id = headers.get('x-goog-visitor-id')
    verify_x_goog_visitor_id(x_goog_visitor_id)
