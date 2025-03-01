import yt_dlp

# URL of the Bilibili video
# Ask for the URL
video_url = input('Enter the URL of the video: ')

# Options for downloading
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',  # Choose a specific format from the list
    'outtmpl': '%(title)s.%(ext)s',  # Save with the title of the video
}
# Needs ffmpeg to merge the video and audio

# Download the video
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
