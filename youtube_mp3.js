const YoutubeMP3 = require("youtube-mp3-downloader");

let id = process.argv[2]
let fileName = process.argv[3]

var ytmp3 = new YoutubeMP3({
    "ffmpegPath": "/usr/bin/ffmpeg",        // FFmpeg binary location
    "outputPath": "/home/files/Music/",    // Output file location (default: the home directory)
    "youtubeVideoQuality": "highestaudio",  // Desired video quality (default: highestaudio)
    "progressTimeout": 2000,                // Interval in ms for the progress reports (default: 1000)
    "allowWebm": false                      // Enable download from WebM sources (default: false)
});

//Download video and save as MP3 file
ytmp3.download(id, fileName);

ytmp3.on("error", function(error) {
    console.log(error);
});
