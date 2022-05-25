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

class Download:
    def __init__(self, API_KEY, access_token, url, username):
        self.catalog_id = 3
        self.client = ampache.API()
        self.access_token = access_token
        passphrase = self.client.encrypt_string(API_KEY, username)
        auth = self.client.handshake(url, passphrase)

    def clean(self, value):
        value = value.replace('\'','').replace('\"','').replace('$','S').replace('/','').replace('#','').replace('?','').replace('!','')
        return value

    def search(self, track, album, artist):
        new_track = self.clean(track)
        new_album = self.clean(album)
        new_artist = self.clean(artist)
        query = self.clean(new_track + ' ' + new_artist + ' audio').replace('  ', '+').replace(' ' , '+')
        print(query)
        try:
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        except UnicodeEncodeError as e:
            print('invalid name... skipping')
            return
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        video_id = video_ids[0]
        return video_id

    def get_video(self, track, album, artist, release_date, track_num, video_id):
        if video_id == '':
            video_id = self.search(track, album, artist)
        artistExists = os.path.isdir('/home/files/Music/{0}'.format(new_artist))
        albumExists = os.path.isdir('/home/files/Music/{0}/{1}'.format(new_artist, new_album))
        trackExists = os.path.isfile('/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track))
        if trackExists:
            print('skipped repeat...')
            return
        if not artistExists:
            os.system('mkdir \"/home/files/Music/{0}\"; mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
        else:
            if not albumExists:
                os.system('mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
        location = '/home/files/Music/{0}/{1}'.format(new_artist, new_album)
        os.system('node /home/files/.scripts/music/youtube_mp3.js {0} \"{1}.mp3\" \"{2}\"'.format(video_id,new_track,location))

        file_location = location + '/' + new_track + '.mp3'
        print(file_location)
        try:
            audiofile = eyed3.load(file_location)
        except Exception as e:
            return
        audiofile.tag.title = track
        audiofile.tag.album = album
        audiofile.tag.artist = artist
        audiofile.tag.release_date = release_date
        audiofile.tag.recording_date = release_date
        audiofile.tag.track_num = track_num
        # audiofile.tag.images.set(img_url=cover_photo)

        audiofile.tag.save()

        self.client.catalog_action('add_to_catalog', self.catalog_id)
        self.client.catalog_action('verify_catalog', self.catalog_id)
        self.client.catalog_action('clean_catalog', self.catalog_id)

    def download_track(self, id_):
        r = requests.get('https://api.spotify.com/v1/tracks/{0}'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        response = json.loads(r.text)
        album_name = response['album']['name']
        release_date = response['album']['release_date']
        artist_name = response['album']['artists'][0]['name']
        self.get_video(response['name'], album_name, artist_name, release_date, response['track_number'], '')
        time.sleep(1)
        self.client.catalog_action('verify_catalog', self.catalog_id)

    def download_album(self, id_):
        r = requests.get('https://api.spotify.com/v1/albums/{0}'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        response = json.loads(r.text)

        album_name = response['name']
        release_date = response['release_date']
        artist_name = response['artists'][0]['name']
        #cover_art = response['images'][0]['url']

        for track in response['tracks']['items']:
            self.get_video(track['name'], album_name, artist_name, release_date, track['track_number'], '')
        time.sleep(1)
        self.client.catalog_action('verify_catalog', self.catalog_id)

    def download_artist(self, id_):
        albums = ''
        r = requests.get('https://api.spotify.com/v1/artists/{0}/albums'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        response = json.loads(r.text)
        length = len(response['items'])

        for i in range(length):
            add = ','
            if i == length - 1:
                add = ''
            albums += response['items'][i]['id'] + add
        r = requests.get('https://api.spotify.com/v1/albums?ids={0}'.format(albums), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        response = json.loads(r.text)

        for album in response['albums']:
            album_name = album['name']
            release_date = album['release_date']
            artist_name = album['artists'][0]['name']
            #cover_art = album['images'][0]['url']
            for track in album['tracks']['items']:
                track_num = track['track_number']
                self.get_video(track['name'], album_name, artist_name, release_date, track_num, '')
        time.sleep(1)
        self.client.catalog_action('verify_catalog', self.catalog_id)

    def download_hindi(self, music_type, id_):
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
        self.client.catalog_action('verify_catalog', self.catalog_id)

    def download_track_manual(self, id_, url):
        r = requests.get('https://api.spotify.com/v1/tracks/{0}'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        response = json.loads(r.text)
        album_name = ''
        try:
            album_name = response['album']['name']
        except KeyError:
            print('Invalid spotify url')
            sys.exit()
        release_date = response['album']['release_date']
        artist_name = response['album']['artists'][0]['name']
        new_track = self.clean(track)
        new_album = self.clean(album)
        new_artist = self.clean(artist)

        filePath = '/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track)
        trackExists = os.path.isfile(filePath)
        if trackExists:
            os.system('rm {0}'.format(filePath))

        self.get_video(response['name'], album_name, artist_name, release_date, response['track_number'], url)
        time.sleep(1)
        self.client.catalog_action('verify_catalog', self.catalog_id)
