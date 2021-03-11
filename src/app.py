from api_key import client_id,client_secret,redirect_uri
import spotify_client
from flask import Flask, redirect, url_for, request, jsonify, render_template
import requests
import sys
import utils

app = Flask(__name__)
SpotifyClient = spotify_client.SpotifyClient(client_id, client_secret,redirect_uri)

@app.route('/')
def index():
    if SpotifyClient.is_authentificated():
        return render_template('index.html')
    else:
        return render_template('authentification.html')     

@app.route('/auth', methods = ['GET'])
def auth():
    if request.method == 'GET':
        if 'error' in request.args:
            return "Pourquoi t'as refusé, je veux juste créer une playlist :("
        elif 'code' in request.args:
            print("test", file=sys.stderr)
            SpotifyClient.auth = True
            SpotifyClient.code =  request.args.get('code')
            SpotifyClient.authentificate()
            return redirect('auth')
        elif SpotifyClient.auth == False:
            return redirect(SpotifyClient.authentificate())
        else:
            SpotifyClient.authentificate()
            return render_template('index.html')

@app.route('/token')
def token():
    return SpotifyClient.get_token()

@app.route('/create_playlist')
def print_artists_liked():
    if SpotifyClient.is_authentificated():
        data = utils.transform_json_artists_liked(SpotifyClient.get_artists_liked())
        return render_template('playlist.html',data = data)
    else:
        return redirect('auth')

@app.route('/creation' , methods=['GET','POST'])
def creation():
    if SpotifyClient.is_authentificated():
        playlist_id = SpotifyClient.create_playlist()["id"]
        artists_ids = request.form.getlist('mycheckbox')
        for id in artists_ids:
            uris_song = []
            for song in SpotifyClient.get_artist_top_tracks(id)["tracks"]:
                uris_song.append(song["uri"])
            SpotifyClient.add_tracks_to_playlist(playlist_id, uris_song)
        return "Votre playlist à du être créée"
    else:
        return redirect('auth')


if __name__ == "__main__":
    app.run(debug = True)