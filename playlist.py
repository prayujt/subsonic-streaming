#!/usr/bin/env python3
import download
from dotenv import dotenv_values
import sys
import requests
import json

spotify_url = ''
playlist_name = ''

if len(sys.argv) == 1 and sys.argv[1] == 'shortcut':
    playlistFile = open('/home/files/.scripts/music/playlist.txt', 'r')
    lines = playlistFile.readlines()
    playlistFile.close()
    spotify_url = lines[0]
    playlist_name = lines[1]
elif len(sys.argv) < 3:
    print("not enough arguments")
    sys.exit()
else:
    spotify_url = sys.argv[1]
    playlist_name = sys.argv[2]

config = dotenv_values()

client_id = config['CLIENT_ID']
secret = config['CLIENT_SECRET']
r = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': secret
})
response = json.loads(r.text)
access_token = response['access_token']

client = download.Download(config['API_KEY'], access_token, config['AMPACHE_URL'], config['AMPACHE_USERNAME'])

client.download_playlist(spotify_url, playlist_name)
