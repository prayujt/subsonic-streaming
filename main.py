#!/usr/bin/env python3
import download
from dotenv import dotenv_values

music = []
config = dotenv_values()

id_file = open('/home/files/.scripts/music/choices.txt')
ids = id_file.readlines()
id_file.close()

choices_file = open('/home/files/.scripts/music/temp2.txt')
choices = choices_file.readlines()
choices_file.close()

access_token = ids[0].strip()

combined = ''
for i in range(1, len(ids)):
    combined += ids[i]

items = combined.split('\n\n')
for i in range(0, len(items)):
    array = items[i].split('\n')
    music.append(array[int(choices[i+1].strip()) - 1])

for value in music:
    split_value = value.split()
    id_ = split_value[0]
    music_type = split_value[1]
    client = download.Download(config['API_KEY'], access_token, config['AMPACHE_URL'], config['AMPACHE_USERNAME'])

    if len(split_value) == 3:
        client.download_hindi(music_type, id_)
    if music_type == 'track':
        client.download_track(id_)
    elif music_type == 'album':
        client.download_album(id_)
    elif music_type == 'artist':
        client.download_artist(id_)
    else:
        sys.exit()
