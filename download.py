#!/usr/bin/env python3
import urllib.request
import re
import sys
import os
import eyed3
from eyed3.id3.frames import ImageFrame
import ampache
import time
import requests
import json
import unicodedata

from spotdl.parsers import parse_query
from spotdl.search import SpotifyClient

class Download:
    def __init__(self, client_id, client_secret, api_key, ampache_url, username, access_token=None):
        self.catalog_id = 3
        self.client = ampache.API()
        self.client.set_format('json')
        self.access_token = access_token
        passphrase = self.client.encrypt_string(api_key, username)
        auth = self.client.handshake(ampache_url, passphrase)

        try:
            SpotifyClient.init(
                client_id=client_id,
                client_secret=client_secret,
                user_auth=False,
            )
        except Exception:
            pass

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except NameError: # unicode is a default on python 3 
            pass

        text = unicodedata.normalize('NFD', text)\
               .encode('ascii', 'ignore')\
               .decode("utf-8")

        return str(text)

    def tag_file(self, file_location, track, album, artist, release_date, track_num, cover_art=None, img_data=None):
        if os.path.isfile(file_location):
            try:
                audiofile = eyed3.load(file_location)
            except Exception as e:
                print('couldn\'t load file to set tags')
                return
            audiofile.tag.title = track
            audiofile.tag.album = album
            audiofile.tag.artist = artist
            audiofile.tag.release_date = release_date
            audiofile.tag.recording_date = release_date
            audiofile.tag.track_num = track_num
            audiofile.tag.genre = ''
            if cover_art != None:
                img_data = requests.get(cover_art).content
            audiofile.tag.images.set(ImageFrame.FRONT_COVER, img_data, 'image/jpeg')

            audiofile.tag.save(version=eyed3.id3.ID3_V2_3)

            try:
                self.client.catalog_file(file_location, 'add', self.catalog_id)
                self.client.catalog_action('gather_art', self.catalog_id)
            except json.decoder.JSONDecodeError:
                print('failed to add to catalog')
                pass
            return file_location

    def clean(self, value):
        value = self.strip_accents(value.replace('\'','').replace('\"','').replace('$','S').replace('/','').replace('#','').replace('?','').replace('!','').replace(':', '').replace('>', '').replace('<', '').replace('*', '').replace('|', '').replace('.', ''))
        return value

    def search(self, track, album, artists):
        artist = artists[0]
        new_track = self.clean(track)
        new_album = self.clean(album)
        new_artist = self.clean(artist)
        query = self.clean(new_track + ' ' + new_artist + ' audio').replace('  ', '+').replace(' ' , '+').replace('&', '%26')
        try:
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        except UnicodeEncodeError as e:
            print('invalid name... skipping')
            return
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        video_id = video_ids[0]
        return video_id

    def get_video(self, track, album, artist, video_id):
        new_artist = self.clean(artist)
        new_album = self.clean(album)
        new_track = self.clean(track)
        artistExists = os.path.isdir('/home/files/Music/{0}'.format(new_artist))
        albumExists = os.path.isdir('/home/files/Music/{0}/{1}'.format(new_artist, new_album))
        trackExists = os.path.isfile('/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track))
        if trackExists:
            print('skipped repeat...')
            return None
        if not artistExists:
            os.system('mkdir \"/home/files/Music/{0}\"; mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
        else:
            if not albumExists:
                os.system('mkdir \"/home/files/Music/{0}/{1}\"'.format(new_artist, new_album))
        file_location = '/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track)
        #os.system("/home/files/.local/bin/yt-dlp -f \"ba\" -x --audio-format mp3 https://www.youtube.com/watch?v={0} -o \"{1}\"".format(video_id, file_location))
        os.system("/home/files/.local/bin/yt-dlp -f \"ba\" -x --audio-format mp3 {0} -o \"{1}\"".format(video_id, file_location))
        return file_location

    def download_track(self, id_):
        query = ['https://open.spotify.com/track/{0}'.format(id_)]
        song_obj = parse_query(
            query,
            'mp3',
            False,
            False,
            'musixmatch',
            4,
            None
        )[0]
        track = song_obj.song_name
        album = song_obj.album_name
        artist = song_obj.contributing_artists[0]
        release_date = song_obj.album_release
        track_num = song_obj.track_number # disc_number
        cover_art = song_obj.album_cover_url
        path = self.get_video(track, album, artist, song_obj.youtube_link)
        if path != None:
            self.tag_file(path, track, album, artist, release_date, track_num, cover_art)
        return path

    def download_album(self, id_):
        query = ['https://open.spotify.com/album/{0}'.format(id_)]
        _song_obj = parse_query(
            query,
            'mp3',
            False,
            False,
            'musixmatch',
            4,
            None
        )
        for song_obj in _song_obj:
            track = song_obj.song_name
            album = song_obj.album_name
            artist = song_obj.contributing_artists[0]
            release_date = song_obj.album_release
            track_num = song_obj.track_number # disc_number
            cover_art = song_obj.album_cover_url
            path = self.get_video(track, album, artist, song_obj.youtube_link)
            if path != None:
                self.tag_file(path, track, album, artist, release_date, track_num, cover_art)

    def download_artist(self, id_):
        query = ['https://open.spotify.com/artist/{0}'.format(id_)]
        _song_obj = parse_query(
            query,
            'mp3',
            False,
            False,
            'musixmatch',
            4,
            None
        )
        for song_obj in _song_obj:
            try:
                track = song_obj.song_name
            except AttributeError:
                continue
            album = song_obj.album_name
            artist = song_obj.contributing_artists[0]
            release_date = song_obj.album_release
            track_num = song_obj.track_number # disc_number
            cover_art = song_obj.album_cover_url
            path = self.get_video(track, album, artist, song_obj.youtube_link)
            if path != None:
                self.tag_file(path, track, album, artist, release_date, track_num, cover_art)

    def download_track_manual(self, spotify_url, youtube_url):
        id_ = spotify_url[spotify_url.find('track/')+6:]

        query = [spotify_url]
        song_obj = parse_query(
            query,
            'mp3',
            False,
            False,
            'musixmatch',
            4,
            None
        )

        track = song_obj.song_name
        album = song_obj.album_name
        artist = song_obj.contributing_artists[0]
        release_date = song_obj.album_release
        track_num = song_obj.track_number # disc_number
        cover_art = song_obj.album_cover_url

        new_track = self.clean(track)
        new_album = self.clean(album)
        new_artist = self.clean(artist)

        filePath = '/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track)
        trackExists = os.path.isfile(filePath)
        if trackExists:
            os.system('rm \"{0}\"'.format(filePath))

        path = self.get_video(track, album, artist, youtube_url[youtube_url.find('v=')+2:])
        self.tag_file(path, track, album, artist, release_date, track_num, cover_art)

    def playlist_loop(self, playlist, playlist_id):
        for song in playlist:
            print(song['track']['name'])
            album = song['track']['album']['name']
            songs = self.client.songs(filter_str=song['track']['name'], exact=1)
            print(songs)
            found = False
            for temp in songs['song']:
                if temp['album']['name'] == album:
                    found = True
                    self.client.playlist_add_song(playlist_id, temp['id'], 1)
                    break
            if not found:
                href = song['track']['href']
                path = self.download_track(href[href.find('tracks/')+7:])
                if path == None:
                    print('Error')
                    continue
                songs = self.client.songs(filter_str=song['track']['name'], exact=1)
                while len(songs['song']) == 0:
                    result = self.client.catalog_file(path, 'add', self.catalog_id)
                    songs = self.client.songs(filter_str=song['track']['name'], exact=1)
                for temp in songs['song']:
                    if temp['album']['name'] == album:
                        found = True
                        self.client.playlist_add_song(playlist_id, temp['id'], 1)

    def download_playlist(self, spotify_url, playlist_name):
        playlist_id = self.client.playlist_create(playlist_name, 'private')['id']
        id_ = spotify_url[spotify_url.find('playlist/')+9:]
        r = requests.get('https://api.spotify.com/v1/playlists/{0}'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        text = json.loads(r.text)
        playlist = text['tracks']['items']
        self.playlist_loop(playlist, playlist_id)
        _next = text['tracks']['next']
        while _next != None:
            r = requests.get(_next, headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {token}'.format(token=self.access_token),
            })
            text = json.loads(r.text)
            playlist = text['items']
            _next = text['next']
            self.playlist_loop(playlist, playlist_id)

    def search_song(self, query, exact_):
        songs = self.client.songs(filter_str=query, exact=exact_)
        return songs

    def replace_song(self, track, album, artist, id_):
        file_path = '/home/files/Music/{0}/{1}/{2}.mp3'.format(self.clean(artist), self.clean(album), self.clean(track))
        trackExists = os.path.isfile(file_path)
        print(file_path)
        if trackExists:
            try:
                copy_file = eyed3.load(file_path)
            except Exception as e:
                print('couldn\'t load file to set tags')
                return
            title = copy_file.tag.title
            album = copy_file.tag.album
            artist = copy_file.tag.artist
            release_date = copy_file.tag.release_date
            track_num = copy_file.tag.track_num
            image_data = ''
            if title == '':
                return

            try:
                image_data = copy_file.tag.images[0].image_data
            except IndexError:
                print('could not load any cover art')

            os.system('rm \"{0}\"'.format(file_path))

            path = self.get_video(track, album, artist, id_)
            if image_data != '':
                self.tag_file(path, title, album, artist, release_date, track_num, img_data=image_data)
            else:
                try:
                    audiofile = eyed3.load(file_location)
                except Exception as e:
                    print('couldn\'t load file to set tags')
                    return
                audiofile.tag.title = title
                audiofile.tag.album = album
                audiofile.tag.artist = artist
                audiofile.tag.release_date = release_date
                audiofile.tag.recording_date = release_date
                audiofile.tag.track_num = track_num
                audiofile.tag.genre = ''
                if image_data != '':
                    audiofile.tag.images.set(ImageFrame.FRONT_COVER, image_data, 'image/jpeg')

                audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
