# Amperfy + Apple Shortcuts
Python script that communicates with Apple's Shortcuts to add songs to a private music server running on the Subsonic API.
Includes crontab script to be run every minute to update Subsonic database.

## Link to Apple Shortcut
* [Download Songs](https://www.icloud.com/shortcuts/e503330f5aa8441f9388c2307c1fc3ef)
* [Replace Songs](https://www.icloud.com/shortcuts/6a06697f3a64492fb989b743ee49b1c4)
* [Sync Spotify Playlist](https://www.icloud.com/shortcuts/3e824c46de07487d8558a48ddea61018)

## Dependencies
### Python
* urllib
* subsonic
* dotenv
* eyed3
* spotdl
* pytube
* yt-dlp 

## TODO
* Allow replacement of .mp4 files with same tags and custom selected YouTube links
