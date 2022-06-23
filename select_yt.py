#!/usr/bin/env python3
import requests
import json
from dotenv import dotenv_values
from youtube_search import YoutubeSearch
import sys

config = dotenv_values()

songs_file = open('/home/files/.scripts/music/choices.json', 'r')
lines = songs_file.readlines()
songs_file.close()

choices_file = open('/home/files/.scripts/music/temp2.txt', 'r')
choices = choices_file.readlines()
choices_file.close()

value = ''
choices2_file = open('/home/files/.scripts/music/choices2.json', 'w')
for i in range(0, len(lines)):
    _obj = json.loads(lines[i])[int(choices[i+1])-1]
    results = json.loads(YoutubeSearch(_obj['track'] + ' ' + _obj['artist'], max_results=15).to_json())
    choices2_file.write('[')
    if (len(results) == 0):
        print('No songs found')
        choices2_file.write('0]')
        if not i == len(lines) - 1:
            value += '----------\n'
            choices2_file.write('\n')
        continue

    for j in range(0, len(results['videos'])):
        video = results['videos'][j]
        _id = video['id']
        title = video['title']
        channel = video['channel']
        duration = video['duration']
        views = video['views']
        published = video['publish_time']
        value += '{0} ({1}) [{2}]'.format(title, duration, channel)

        choices2_file.write(_id)
        if j != len(results['videos']) - 1:
            choices2_file.write(',')
            value += '\n'
    choices2_file.write(']')
    if not i == len(lines) - 1:
        value += '\n----------\n'
        choices2_file.write('\n')

choices2_file.close()
print(value)
