import urllib.request
import re
import sys
import os
from pytube import YouTube
from youtube_title_parse import get_artist_title
import eyed3
import ampache
import time
import requests
import json

def get_video(query):
    pass

def download_track(id_):
    r = requests.get('https://api.spotify.com/v1/tracks/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)
    print(os.path.isdir('/home/files/Music'))
    return response

def download_album(id_):
    r = requests.get('https://api.spotify.com/v1/albums/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)
    return response

    for track in response['tracks']['items']:
        id2 = track['id']
    #return response

def download_artist(id_):
    albums = ''
    r = requests.get('https://api.spotify.com/v1/artists/{0}/albums'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    for i in range(len(response['items'])):
        add = ','
        if i == len(response['items'])-1:
            add = ''
        albums += response['items'][i]['id'] + add
    r = requests.get('https://api.spotify.com/v1/albums?ids={0}'.format(albums), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    for album in response['albums']:
        artist = album['artists'][0]['name']
        print(artist)

    #return response

music = []

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

    if music_type == 'track':
        pass
        #print(download_track(id_))

    elif music_type == 'album':
        pass
        #print(download_album(id_))

    elif music_type == 'artist':
        #pass
        print(download_artist(id_))

    else:
        sys.exit()

"""
yt = YouTube("https://www.youtube.com/watch?v=" + song_id)
videoTitle = yt.title

os.system('node /home/files/.scripts/music/youtube_mp3.js {id} \"{title}.mp3\"'.format(id=song_id,title=title))

audiofile = eyed3.load("/home/files/Music/" + title + ".mp3")

try:
    album = response['tracks']['items'][0]['album']['name']
    audiofile.tag.album = album
except KeyError:
    pass
if artist == '':
    try:
        artist = response['tracks']['items'][0]['artists'][0]['name']
    except KeyError:
        pass
audiofile.tag.artist = artist
audiofile.tag.title = title
audiofile.tag.recording_date = year

audiofile.tag.save()

command = 'get_cover_art --path ' + '\"/home/files/Music/' + title + '.mp3\"'
os.system(command)

os.system('rm -r temp.txt temp2.txt choices.txt _cover_art')
"""

"""
track = song['name']
album = song['album']['name']
artist = song['album']['artists'][0]['name']
release_date = song['album']['release_date']
image_url = song['album']['images'][0]['url']
"""
