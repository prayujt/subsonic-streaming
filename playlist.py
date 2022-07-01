#!/usr/bin/env python3
import download
from dotenv import dotenv_values
import sys
import requests
import json

spotify_url = ''
playlist_name = ''
username = ''
password = ''

config = dotenv_values()

if len(sys.argv) == 2 and sys.argv[1] == 'shortcut':
    playlistFile = open('/home/files/.scripts/music/playlist.txt', 'r')
    lines = playlistFile.readlines()
    playlistFile.close()
    username = lines[0].strip()
    password = lines[1].strip()
    spotify_url = lines[2].strip()
    playlist_name = lines[3].strip()
elif len(sys.argv) < 3:
    print("not enough arguments")
    sys.exit()
else:
    username = config['SUBSONIC_USERNAME']
    password = config['SUBSONIC_PASSWORD']
    spotify_url = sys.argv[1]
    playlist_name = sys.argv[2]

client_id = config['CLIENT_ID']
secret = config['CLIENT_SECRET']
r = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': secret
})
response = json.loads(r.text)
access_token = response['access_token']

client = download.Download(client_id, secret, config['SUBSONIC_URL'], config['SUBSONIC_PORT'], username, password, access_token)

client.download_playlist(spotify_url, playlist_name)
