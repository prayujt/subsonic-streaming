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

def clean(value):
    value = value.replace('\'','').replace('\"','').replace('’','').replace('$','S').replace('/','')
    return value

def get_video(track, album, artist, release_date, track_num):
    original_track = track
    track = track.replace('$','S').replace('?','').replace('!','').replace('/','')
    new_track = clean(track)
    new_album = clean(album)
    new_artist = clean(artist)
    query = new_track + ' ' + new_artist + ' audio'
    query = clean(query).replace(' ', '+')
    print(query)
    try:
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    except UnicodeEncodeError as e:
        return
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_id = video_ids[0]
    artistExists = os.path.isdir('/home/files/Music/{0}'.format(new_artist))
    albumExists = os.path.isdir('/home/files/Music/{0}/{1}'.format(new_artist, new_album))
    trackExists = os.path.isfile('/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, track))
    if trackExists:
        print('skipped repeat...')
        return
    if not artistExists:
        os.system('mkdir \"/home/files/Music/{0}\"; mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
    else:
        if not albumExists:
            os.system('mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
    location = '/home/files/Music/{0}/{1}'.format(new_artist, new_album)
    os.system('node /home/files/.scripts/music/youtube_mp3.js {0} \"{1}.mp3\" \"{2}\"'.format(video_id,track,location))

    file_location = location + '/' + track + '.mp3'
    audiofile = eyed3.load(file_location)
    audiofile.tag.title = original_track
    audiofile.tag.album = album
    audiofile.tag.artist = artist
    audiofile.tag.release_date = release_date
    audiofile.tag.recording_date = release_date
    audiofile.tag.track_num = track_num
    # audiofile.tag.images.set(img_url=cover_photo)

    audiofile.tag.save()

    passphrase = client.encrypt_string(config['API_KEY'], 'prayuj')
    auth = client.handshake('http://prayujt.com:1025', passphrase)
    #client.catalog_action('clean_catalog', catalog_id)
    client.catalog_action('add_to_catalog', catalog_id)
    client.catalog_action('verify_catalog', catalog_id)
    client.catalog_action('clean_catalog', catalog_id)

def download_track(id_):
    r = requests.get('https://api.spotify.com/v1/tracks/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)
    album_name = response['album']['name']
    release_date = response['album']['release_date']
    artist_name = response['album']['artists'][0]['name']
    get_video(response['name'], album_name, artist_name, release_date, response['track_number'])

def download_album(id_):
    r = requests.get('https://api.spotify.com/v1/albums/{0}'.format(id_), headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}'.format(token=access_token),
    })
    response = json.loads(r.text)

    album_name = response['name']
    release_date = response['release_date']
    artist_name = response['artists'][0]['name']
    #cover_art = response['images'][0]['url']

    for track in response['tracks']['items']:
        get_video(track['name'], album_name, artist_name, release_date, track['track_number'])

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
        album_name = album['name']
        release_date = album['release_date']
        artist_name = album['artists'][0]['name']
        #cover_art = album['images'][0]['url']
        for track in album['tracks']['items']:
            track_num = track['track_number']
            get_video(track['name'], album_name, artist_name, release_date, track_num)

config = dotenv_values()
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
        download_track(id_)
    elif music_type == 'album':
        download_album(id_)
    elif music_type == 'artist':
        download_artist(id_)
    else:
        sys.exit()

time.sleep(1)
client.catalog_action('verify_catalog', catalog_id)
