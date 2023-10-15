#!/usr/bin/env python3
from flask import Flask, request
from dotenv import dotenv_values
import urllib

import spotify_api as sp
import download

app = Flask(__name__)

choices = [[]]

config = dotenv_values()

client_id = config['CLIENT_ID']
secret = config['CLIENT_SECRET']
subsonic_url = config['SUBSONIC_URL']
subsonic_port = config['SUBSONIC_PORT']
subsonic_username = config['SUBSONIC_USERNAME']
subsonic_password = config['SUBSONIC_PASSWORD']
music_home = config['MUSIC_HOME']

sp_client = sp.SpotifyClient(client_id, secret)

@app.route('/select/music', methods=['POST'])
def select_songs():
    titles = request.json['titles']
    titles = titles.split('\n')
    value = ''

    counter = 0
    for title in titles:
        choices.append([])
        if value != '':
            value += '----------\n'
        song_count = 10
        album_count = 5
        artist_count = 3

        encoded_query = urllib.parse.urlencode({
            'q': title,
            'type': 'track,album,artist'
            })
        res = sp_client.api_req('/search?{0}'.format(encoded_query))

        songList = res['tracks']['items']
        albumList = res['albums']['items']
        artistList = res['artists']['items']

        if len(albumList) < album_count:
            song_count += album_count - len(albumList)
            album_count = len(albumList)
        if len(artistList) < artist_count:
            song_count += artist_count - len(artistList)
            artist_count = len(artistList)

        for j in range(song_count):
            if j > len(songList):
                break
            song = songList[j]
            track = song['name']
            album = song['album']['name']
            artist = song['album']['artists'][0]['name']
            release_date = song['album']['release_date']
            value += '{0} - {1} [{2}]___'.format(artist, track, album)
            choices[counter].append(('track', song['id']))

        for j in range(album_count):
            if j > len(albumList):
                break
            album = albumList[j]
            value += 'Album: {0} [{1}]___'.format(album['name'], album['artists'][0]['name'])
            choices[counter].append(('album', album['id']))

        for j in range(artist_count):
            if j > len(artistList):
                break
            artist = artistList[j]
            value += 'Artist: {0}___'.format(artist['name'])
            choices[counter].append(('artist', artist['id']))
        value = value[:-3]
        counter += 1
    return value.rstrip()

@app.route('/download', methods=['POST'])
def download_songs():
    indices = request.json['indices'].split('\n')[1:]

    client = download.Downloader(subsonic_url, subsonic_port, subsonic_username, subsonic_password, music_home, sp_client)
    for i in range(len(indices)):
        choice = choices[i]

        if choice[int(indices[i]) - 1][0] == 'track':
            client.download_track(choice[int(indices[i]) - 1][1])
        elif choice[int(indices[i]) - 1][0] == 'album':
            client.download_album(choice[int(indices[i]) - 1][1])
        elif choice[int(indices[i]) - 1][0] == 'artist':
            client.download_artist(choice[int(indices[i]) - 1][1])

    return 'done'
