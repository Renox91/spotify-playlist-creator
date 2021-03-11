import requests
import json
import base64
import sys
import datetime
from flask import jsonify

class SpotifyClient(object):
    def __init__(self,client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_creds_b64 = f"{self.client_id}:{self.client_secret}"
        self.client_creds_b64 = base64.b64encode(self.client_creds_b64.encode())
        self.redirect_uri = redirect_uri
        self.code = ""
        self.token = ""
        self.expires_in = 0
        self.refresh_token = ""
        self.auth = False
        self.token_received = False
        self.user_id = ""

    """=============================== PARTIE AUTHENTIFICATION ==============================="""
    def get_authorize_access(self):
        scopes = "user-follow-modify user-follow-read playlist-modify-private"
        url = "https://accounts.spotify.com/authorize"

        return f"{url}?client_id={self.client_id}&response_type=code&redirect_uri=http://localhost:5000/auth&scope={scopes}"

    def get_token(self):
        url = "https://accounts.spotify.com/api/token"
        token_data = {
            "grant_type": "authorization_code",
            "code" : self.code,
            "redirect_uri" : "http://localhost:5000/auth"
        }
        token_headers = {
            "Authorization": f"Basic {self.client_creds_b64.decode()}" # <base64 encoded client_id:client_secret>
        }

        response_json = requests.post(url, data=token_data, headers=token_headers).json()
        if not 'error' in response_json:
            self.token = response_json["access_token"]
            self.expires_in = datetime.datetime.now() + datetime.timedelta(seconds=response_json["expires_in"])
            self.refresh_token = response_json["refresh_token"]
            self.token_received = True


    def authentificate(self):
        if self.auth == False :
            return self.get_authorize_access()
        elif self.token_received == False or self.expires_in < datetime.datetime.now():
            return self.get_token()
        else:
            return f"Authentificated ! \n| code : {self.code} | token : {self.token} | expire in : {self.expires_in}"

    def is_authentificated(self):
        if self.auth == False :
            return False
        elif self.token_received == False and self.expires_in < datetime.datetime.now():
            return False
        return True

    """ =============================== PARTIE APPEL SPOTIFY API ==============================="""
    def get_user_id(self):
        url = 'https://api.spotify.com/v1/me'
        # self.user_id = response_json["id"]
        response_json = requests.get(
            url,
            headers ={
                "Authorization" : f"Bearer {self.token}"
            }
        ).json()

        if not 'error' in response_json:
            self.user_id = response_json["id"]
        print(response_json, file=sys.stderr)
    
    def get_artists_liked(self):
        url = 'https://api.spotify.com/v1/me/following?type=artist'
        response_json = requests.get(
            url,
            headers ={
                "Accept" : "application/json",
                "Content-Type" : "application/json",
                "Authorization" : f"Bearer {self.token}"
            },
            params={
                'limit':50
            }
        ).json()
        return response_json

    def get_artist_top_tracks(self, id):
        url = f'https://api.spotify.com/v1/artists/{id}/top-tracks'
        response_json = requests.get(
            url,
            headers ={
                "Authorization" : f"Bearer {self.token}"
                
            },
            params = {
                "market" : "FR"
            }
        ).json()
        return response_json

    def create_playlist(self):
        if self.user_id == "":
            self.get_user_id()

        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'
        data = {
            "name": "Automated playlist",
            "description": "Playlist created automatically with the website : ",
            "public": False
        }
        token_headers = {
            "Authorization" : f"Bearer {self.token}"
        }

        response_json = requests.post(url, json=data, headers=token_headers).json()
        return response_json

    def add_tracks_to_playlist(self,playlist_id, song_uris):

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        data = {
            "uris": song_uris,
        }
        token_headers = {
            "Content-Type": "application/json",
            "Authorization" : f"Bearer {self.token}"
        }

        response_json = requests.post(url, json=data, headers=token_headers).json()
        return response_json