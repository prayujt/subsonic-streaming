#!/usr/bin/env python3
import urllib.request
import eyed3
import requests
import json
from dotenv import dotenv_values

config = dotenv_values()

songs = open('/home/files/.scripts/music/temp.txt', 'r')
lines = songs.readlines()
songs.close()

client_id = config['CLIENT_ID']
secret = config['CLIENT_SECRET']
r = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': secret
})
response = json.loads(r.text)
access_token = response['access_token']

choices_file = open('/home/files/.scripts/music/choices.txt', 'w')
choices_file.write(access_token + '\n')
value = ''
for i in range(0, len(lines)):
    line = lines[i]
    song_count = 5
    album_count = 5
    artist_count = 2
    hindi = false

    if line.startswith('hindi') or line.endswith('hindi'):
        hindi = true
        line = line.replace('hindi', '')

    query = line.strip().replace(' ', '%20')

    r = requests.get('https://api.spotify.com/v1/search?q={search}&type=track,album,artist'.format(search=query), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    songList = response['tracks']['items']
    albumList = response['albums']['items']
    artistList = response['artists']['items']

    if len(albumList) < album_count:
        song_count += album_count - len(albumList)
        album_count = len(albumList)
    if len(artistList) < artist_count:
        song_count += artist_count - len(artistList)
        artist_count = len(artistList)

    for j in range(0, song_count):
        add = '\n'
        if album_count == 0 and artist_count == 0 and j == song_count - 1 and i == len(lines) - 1:
            add = ''
        if hindi:
            add = ' hindi' + add
        song = songList[j]
        track = song['name']
        album = song['album']['name']
        artist = song['album']['artists'][0]['name']
        release_date = song['album']['release_date']
        value += artist + ' - ' + track + ' [' + album + ']' + add
        choices_file.write(song['id'] + ' track' + add)
    for j in range(0, album_count):
        add = '\n'
        if artist_count == 0 and j == album_count - 1 and i == len(lines) - 1:
            add = ''
        if hindi:
            add = ' hindi' + add
        album = albumList[j]
        value += 'Album: ' + album['name'] + ' [' + album['artists'][0]['name'] + ']' + add
        choices_file.write(album['id'] + ' album' + add)
    for j in range(0, artist_count):
        add = '\n'
        if j == artist_count - 1 and i == len(lines) - 1:
            add = ''
        if hindi:
            add = ' hindi' + add
        artist = artistList[j]
        value += 'Artist: ' + artist['name'] + add
        choices_file.write(artist['id'] + ' artist' + add)
    if not i == len(lines) - 1:
        value += '----------\n'
        choices_file.write('\n')
choices_file.close()
print(value)
