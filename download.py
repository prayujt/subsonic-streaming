#!/usr/bin/env python3
import urllib.request
import re
import sys
import os
import time
import requests
import json
import unicodedata

import eyed3
from eyed3.id3.frames import ImageFrame
import libsonic
from ytmusicapi import YTMusic
import yt_dlp

yt_music = YTMusic()

def simplify_query(value):
    characters = ['(', '[', '{', '-', ')', ']', '}', '!', '.']
    for character in characters:
        value = value.replace(character, '')
    value = value.replace(':', ' ')
    return value

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
            .encode('ascii', 'ignore')\
            .decode("utf-8")
    return str(text)

def clean(value):
    value = strip_accents(value.replace('\'','').replace('\"','').replace('$','S').replace('/','').replace('#','').replace('?','').replace('!','').replace(':', '').replace('>', '').replace('<', '').replace('*', '').replace('|', '').replace('.', ''))
    return value

def find_yt_music_url(track_name, album_name):
    res = yt_music.search(track_name + ' ' + album_name, filter='songs')
    return 'https://music.youtube.com/watch?v={0}'.format(res[0]['videoId'])
    # encoded_url = urllib.parse.urlencode({ 'url': sp_url })
    # res = requests.get('https://api.song.link/v1-alpha.1/links?{0}'.format(encoded_url))
    # val = json.loads(res.text)
    # return val['linksByPlatform']['youtubeMusic']['url']


class Downloader:
    def __init__(self, url, port, username, password, music_home, sp_client):
        self.client = libsonic.Connection(url, username, password, port)
        self.music_home = music_home
        self.sp_client = sp_client

    def add_to_playlist(self, playlist_id, song_id):
        playlist = self.client.getPlaylist(playlist_id)['playlist']
        song_ids = []
        if 'entry' in playlist:
            for song in playlist['entry']:
                song_ids.append(song['id']) 
        song_ids.append(song_id)
        self.client.createPlaylist(playlistId=playlist_id, songIds=song_ids)

    def wait_for_sync(self):
        self.client.startScan()
        print('scanning')
        status = self.client.getScanStatus()
        while (status['scanStatus']['scanning'] == True):
            status = self.client.getScanStatus()
        print('finished scanning')
        return

    def tag_file(self, file_location, track, album, artist, release_date, track_num, cover_art=None, img_data=None):
        if os.path.isfile(file_location):
            try:
                audiofile = eyed3.load(file_location)
            except Exception as e:
                print('couldn\'t load file to set tags')
                return
            try:
                audiofile.tag.title = track
            except AttributeError:
                return
            audiofile.tag.album = album
            audiofile.tag.artist = artist
            audiofile.tag.release_date = release_date
            audiofile.tag.track_num = track_num
            audiofile.tag.genre = ''
            if cover_art != None:
                img_data = requests.get(cover_art).content
            audiofile.tag.images.set(ImageFrame.FRONT_COVER, img_data, 'image/jpeg')

            audiofile.tag.save(version=eyed3.id3.ID3_V2_3)

            self.wait_for_sync()

            return file_location

    def search(self, track, album, artists):
        artist = artists[0]
        new_track = clean(track)
        new_album = clean(album)
        new_artist = clean(artist)
        query = clean(new_track + ' ' + new_artist + ' audio').replace('  ', '+').replace(' ' , '+').replace('&', '%26')
        try:
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
        except UnicodeEncodeError as e:
            print('invalid name... skipping')
            return
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        video_id = video_ids[0]
        return video_id

    def get_video(self, track, album, artist, video_link):
        new_track = clean(track)
        new_album = clean(album)
        new_artist = clean(artist)
        artistExists = os.path.isdir('{0}/{1}'.format(self.music_home, new_artist))
        albumExists = os.path.isdir('{0}/{1}/{2}'.format(self.music_home, new_artist, new_album))
        trackExists = os.path.isfile('{0}/{1}/{2}/{3}.mp3'.format(self.music_home, new_artist, new_album, new_track))
        file_location = '{0}/{1}/{2}/{3}.mp3'.format(self.music_home, new_artist, new_album, new_track)
        if trackExists:
            print('skipped repeat...')
            return file_location
        if not artistExists:
            os.mkdir('{0}/{1}'.format(self.music_home, new_artist, new_album))
            os.mkdir('{0}/{1}/{2}'.format(self.music_home, new_artist, new_album))
        else:
            if not albumExists:
                os.mkdir('{0}/{1}/{2}'.format(self.music_home, new_artist, new_album))

        error_code = -1
        if not new_track == '':
            ydl_opts = {
                'format': 'mp3/bestaudio/best',
                'outtmpl': '{0}/{1}/{2}/{3}'.format(self.music_home, new_artist, new_album, new_track),
                'postprocessors': [{  # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download(video_link)

        if error_code == 0:
            return file_location
        else:
            print('invalid characters')
            return None

    def download_track(self, id_):
        metadata = self.sp_client.api_req('/tracks/{0}'.format(id_))

        track = metadata['name']
        album = metadata['album']['name']
        artist = metadata['album']['artists'][0]['name']
        release_date = metadata['album']['release_date']
        track_num = metadata['track_number']
        cover_art = metadata['album']['images'][0]['url']

        yt_url = find_yt_music_url(track, album)

        path = self.get_video(track, album, artist, yt_url)
        if path != None:
            self.tag_file(path, track, album, artist, release_date, track_num, cover_art)
        return path

    def download_album(self, id_):
        next_ = ''
        offset = 0

        while next_ != None:
            tracks = self.sp_client.api_req('/albums/{0}/tracks?limit=50&offset={1}'.format(id_, offset))
            offset += 50
            next_ = tracks['next']
            track_ids = [track['id'] for track in tracks['items']]

            for track_id in track_ids:
                self.download_track(track_id)

    def download_artist(self, id_):
        next_ = ''
        offset = 0

        while next_ != None:
            albums = self.sp_client.api_req('/artists/{0}/albums?limit=50&offset={1}'.format(id_, offset))
            offset += 50
            next_ = albums['next']
            album_ids = [album['id'] for album in albums['items']]

            for album_id in album_ids:
                self.download_album(album_id)

    def download_track_manual(self, spotify_url, youtube_url):
        id_ = spotify_url[spotify_url.find('track/')+6:]

        query = [spotify_url]
        song_obj = sp.spotify_query(query)

        track = song_obj.song_name
        album = song_obj.album_name
        artist = song_obj.contributing_artists[0]
        release_date = song_obj.album_release
        track_num = song_obj.track_number # disc_number
        cover_art = song_obj.album_cover_url

        new_track = clean(track)
        new_album = clean(album)
        new_artist = clean(artist)

        filePath = '/home/files/Music/{0}/{1}/{2}.mp3'.format(new_artist, new_album, new_track)
        trackExists = os.path.isfile(filePath)
        if trackExists:
            os.system('rm \"{0}\"'.format(filePath))

        path = self.get_video(track, album, artist, youtube_url[youtube_url.find('v=')+2:])
        self.tag_file(path, track, album, artist, release_date, track_num, cover_art)

    def playlist_loop(self, playlist, playlist_id):
        for song in playlist:
            print('---------------------')
            if 'track' not in song or 'name' not in song['track'] or song['track']['name'] == '':
                print('Song information missing')
                continue
            print(song['track']['name'])
            album = song['track']['album']['name']
            songs = self.client.search2(simplify_query(song['track']['name']), songCount=2000)['searchResult2']
            found = False
            if not songs == {} and 'song' in songs:
                for temp in songs['song']:
                    if temp['album'] == album and temp['title'] == song['track']['name']:
                        found = True
                        print('adding to playlist')
                        self.add_to_playlist(playlist_id, temp['id'])
                        break
            if not found:
                href = song['track']['href']
                path = self.download_track(href[href.find('tracks/')+7:])
                if path == None:
                    print('Error')
                    continue
                songs = self.client.search2(simplify_query(song['track']['name']))['searchResult2']
                if 'song' not in songs:
                    continue
                while len(songs['song']) == 0:
                    songs = self.client.search2(simplify_query(song['track']['name']))['searchResult2']
                for temp2 in songs['song']:
                    if temp2['album'] == album and temp2['title'] == song['track']['name']:
                        print('adding to playlist')
                        found = True
                        self.add_to_playlist(playlist_id, temp2['id'])
                    
    def download_playlist(self, spotify_url, playlist_name):
        playlist_id = self.client.createPlaylist(name=playlist_name, songIds=[])['playlist']['id']
        id_ = spotify_url[spotify_url.find('playlist/')+9:]

        offset = 0
        next_ = ''
        while next_ != None:
            offset += 50
            playlist = self.sp_client.api_req('/playlists/{0}/tracks?limit=50&offset={1}'.format(id_, offset))
            next_ = playlist['next']
            tracks = playlist['items']
            self.playlist_loop(tracks, playlist_id)

    def search_song(self, query):
        songs = self.client.search2(simplify_query(query))['searchResult2']
        return songs

    def replace_song(self, track, album, artist, id_):
        file_path = '/home/files/Music/{0}/{1}/{2}.mp3'.format(clean(artist), clean(album), clean(track))
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
                audiofile.tag.track_num = track_num
                audiofile.tag.genre = ''
                if image_data != '':
                    audiofile.tag.images.set(ImageFrame.FRONT_COVER, image_data, 'image/jpeg')

                audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
    
    def get_songs_from_playlist(self, spotify_url):
        id_ = spotify_url[spotify_url.find('playlist/')+9:]
        r = requests.get('https://api.spotify.com/v1/playlists/{0}'.format(id_), headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.access_token),
        })
        text = json.loads(r.text)
        playlist = text['tracks']['items']
        self.playlist_download_loop(playlist)
        _next = text['tracks']['next']
        while _next != None:
            r = requests.get(_next, headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {token}'.format(token=self.access_token),
            })
            text = json.loads(r.text)
            playlist = text['items']
            _next = text['next']
            self.playlist_download_loop(playlist)

    def playlist_download_loop(self, playlist):
        for song in playlist:
            try:
                print(song['track']['name'])
            except TypeError:
                continue 
            album = song['track']['album']['name']
            songs = self.client.search2(simplify_query(song['track']['name']))['searchResult2']
            found = False
            if not songs == {} and 'song' in songs:
                for temp in songs['song']:
                    if temp['album'] == album and temp['title'] == song['track']['name']:
                        found = True
                        break
            if not found:
                href = song['track']['href']
                path = self.download_track(href[href.find('tracks/')+7:])
                print(path)

