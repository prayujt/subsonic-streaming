#!/usr/bin/env python3
import requests
import ampache
import json
from dotenv import dotenv_values

config = dotenv_values()

songs = open('/home/files/.scripts/music/temp.txt', 'r')
lines = songs.readlines()
songs.close()

API_KEY = config['API_KEY']
URL = config['AMPACHE_URL']
USERNAME = config['AMPACHE_USERNAME']
CATALOG_ID = 3
client = ampache.API()
client.set_format('json')
passphrase = client.encrypt_string(API_KEY, USERNAME)
auth = client.handshake(URL, passphrase)

choices_file = open('/home/files/.scripts/music/choices.json', 'w')
value = ''
for i in range(0, len(lines)):
    line = lines[i].strip()
    songs = client.songs(filter_str=line, exact=0)['song']
    choices_file.write('[')
    if (len(songs) == 0):
        print('No songs found')
        json_object = json.dumps(_obj, indent = 4)
        choices_file.write(']\n')
        if not i == len(lines) - 1:
            value += '----------\n'
        continue

    for j in range(0, len(songs)):
        add = '\n'
        if j == len(songs) - 1 and i == len(lines) - 1:
            add = ''
        song = songs[j]
        track = song['title']
        album = song['album']['name']
        artist = song['artist']['name']
        number = song['id']
        value += artist + ' - ' + track + ' [' + album + ']' + add

        _obj = {
                "artist": artist,
                "album": album,
                "track": track,
                "number": number,
        }
        json.dump(_obj, choices_file)
        if j != len(songs) - 1:
            choices_file.write(',')
    choices_file.write(']')
    if not i == len(lines) - 1:
        value += '----------\n'
        choices_file.write('\n')
choices_file.close()
print(value)
