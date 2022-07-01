#!/usr/bin/env python3
import requests
import libsonic
import json
from dotenv import dotenv_values
import sys

config = dotenv_values()

songs = open('/home/files/.scripts/music/temp.txt', 'r')
lines = songs.readlines()
songs.close()

url = config['SUBSONIC_URL']
port = config['SUBSONIC_PORT']
username = config['SUBSONIC_USERNAME']
password = config['SUBSONIC_PASSWORD']

connection = libsonic.Connection(url, username, password, port)

choices_file = open('/home/files/.scripts/music/choices.json', 'w')
value = ''

def simplifyQuery(value):
    characters = ['(', '[', '{', '-', ')', ']', '}']
    for character in characters:
        value = value.replace(character, '')
    value = value.replace(':', ' ')
    return value

for i in range(0, len(lines)):
    line = lines[i].strip()
    songs = connection.search2(simplifyQuery(line))['searchResult2']

    choices_file.write('[')
    if not 'song' in songs:
        print('No songs found')
        json_object = json.dumps(_obj, indent = 4)
        choices_file.write(']\n')
        if not i == len(lines) - 1:
            value += '----------\n'
        continue
    songs = songs['song']

    for j in range(0, len(songs)):
        add = '\n'
        if j == len(songs) - 1 and i == len(lines) - 1:
            add = ''
        song = songs[j]
        track = song['title']
        album = song['album']
        artist = song['artist']
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
