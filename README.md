# Amperfy + Apple Shortcuts
Python script that communicates with Apple's Shortcuts to add songs to a private music server.
Includes crontab script to be run every minute to update Ampache database.

## Link to Apple Shortcut
https://www.icloud.com/shortcuts/e503330f5aa8441f9388c2307c1fc3ef

## Dependencies
1. Python
* urllib
* ampache
* dotenv
* eyed3

2. NodeJS
* youtube-mp3-downloader

## TODO
* Add support for ID3 tag additions for albums/songs with unsupported ASCII characters + emojis
