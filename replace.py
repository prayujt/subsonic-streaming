#!/usr/bin/env python3
import download
from dotenv import dotenv_values
import sys
import requests
import json

if len(sys.argv) < 3 and sys.argv[1] != 'shortcut':
    print("not enough arguments")
    sys.exit()

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

client = download.Download(client_id, secret, config['SUBSONIC_URL'], config['SUBSONIC_PORT'], config['SUBSONIC_USERNAME'], config['SUBSONIC_PASSWORD'], access_token)

if (len(sys.argv) == 2):
    temp_file = open('/home/files/.scripts/music/choices.json', 'r')
    choices = temp_file.readlines()
    temp_file.close()

    temp_file = open('/home/files/.scripts/music/temp2.txt', 'r')
    temp1 = temp_file.readlines()
    temp_file.close()

    temp_file = open('/home/files/.scripts/music/choices2.json', 'r')
    yt_choices = temp_file.readlines()
    temp_file.close()

    temp_file = open('/home/files/.scripts/music/temp3.txt', 'r')
    temp2 = temp_file.readlines()
    temp_file.close()

    for i in range(1, len(temp1)):
        choice = json.loads(choices[i-1])[int(temp1[i])-1]
        track = choice['track']
        album = choice['album']
        artist = choice['artist']
        id_ = json.loads(yt_choices[i-1])[int(temp2[i])-1]
        client.replace_song(track, album, artist, id_)
else:
    client.download_track_manual(sys.argv[1], sys.argv[2])
