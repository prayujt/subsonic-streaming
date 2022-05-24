#!/usr/bin/env python3
import urllib.request
import re
import sys
import os
import eyed3
import ampache
import time
import requests
import json
from dotenv import dotenv_values

catalog_id = 3
client = ampache.API()

config = dotenv_values()
music = ''

id_file = open('/home/files/.scripts/music/choices.txt')
ids = id_file.readlines()
id_file.close()

choices_file = open('/home/files/.scripts/music/temp2.txt')
choices = choices_file.readlines()
choices_file.close()

combined = ''
for i in range(1, len(ids)):
    combined += ids[i]

items = combined.split('\n\n')
for i in range(0, len(items)):
    array = items[i].split('\n')
    music = array[int(choices[i+1].strip()) - 1]

split_value = music.split()
id_ = split_value[0]
music_type = split_value[1]

if music_type == 'track':
    command = "~/.local/bin/spotdl https://open.spotify.com/track/" + id_ + " --path-template '/home/files/Music/{artist}/{album}/{title}.{ext}'"
    os.system(command)
elif music_type == 'album':
    command = "~/.local/bin/spotdl https://open.spotify.com/album/" + id_ + " --path-template '/home/files/Music/{artist}/{album}/{title}.{ext}'"
    os.system(command)
elif music_type == 'artist':
    command = "~/.local/bin/spotdl https://open.spotify.com/artist/" + id_ + " --path-template '/home/files/Music/{artist}/{album}/{title}.{ext}'"
    os.system(command)
else:
    sys.exit()

time.sleep(1)
client.catalog_action('verify_catalog', catalog_id)
