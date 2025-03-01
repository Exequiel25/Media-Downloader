import yt_dlp
from youtube_search import YoutubeSearch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TRCK, TCON, TPUB, error
import urllib.request
import os
import re


class MusicDownloaderModel:
    def __init__(self, spotify_client_id, spotify_client_secret):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret))

    def clean_title(self, title):
        title = re.sub(r'\(.*?\)|\[.*?\]', '', title)
        title = re.sub(
            r'(?i)official (video|lyrics|audio|music video)', '', title)
        title = re.sub(r'(?i)lyric video', '', title)
        title = re.sub(r'[^a-zA-Z0-9 \-]', '', title)
        return title.strip()

    def custom_title(self, s):
        return ' '.join(word[0].upper() + word[1:].lower() if word else '' for word in s.split())

    def get_best_youtube_url(self, song, artist, duration):
        search_query = f"{artist} - {song}"
        results = YoutubeSearch(search_query, max_results=5).to_dict()
        best_url = None
        min_diff = float('inf')

        for result in results:
            video_duration = result.get('duration', "0:00")
            video_seconds = sum(
                int(x) * 60 ** i for i, x in enumerate(reversed(video_duration.split(':'))))
            diff = abs(video_seconds - duration)
            if diff < min_diff:
                min_diff = diff
                best_url = f"https://www.youtube.com{result['url_suffix']}"

        return best_url

    def download_song(self, song, artist, save_path, progress_hook):
        results = self.spotify.search(
            q=f"track:{song} artist:{artist}", type="track", limit=1)
        if not results['tracks']['items']:
            raise ValueError(
                f"No se encontró la canción en Spotify: {song} - {artist}")

        track = results['tracks']['items'][0]
        correct_title = self.custom_title(track['name'])
        correct_artist = self.custom_title(track['artists'][0]['name'])
        album = track['album']['name']
        album_artist = track['album']['artists'][0]['name']
        release_year = track['album']['release_date'].split("-")[0]
        track_number = track['track_number']
        genre = ', '.join(track['album'].get('genres', [])) or "Unknown"
        publisher = track['album'].get('label', 'Unknown')
        duration = track['duration_ms'] // 1000
        album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        video_url = self.get_best_youtube_url(
            correct_title, correct_artist, duration)
        if not video_url:
            raise ValueError(
                f"No se encontró un video adecuado para: {correct_title} - {correct_artist}")

        filename = f"{correct_artist} - {correct_title}"
        filename = self.clean_title(filename)
        filepath = os.path.join(save_path, filename)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filepath,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)

        filepath += ".mp3"
        if os.path.exists(filepath) and album_cover_url:
            cover_filename = os.path.join(save_path, "cover.jpg")
            urllib.request.urlretrieve(album_cover_url, cover_filename)

            audio = MP3(filepath, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            with open(cover_filename, 'rb') as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=0,
                    desc='Cover',
                    data=img.read()
                ))

            audio.tags.add(TIT2(encoding=3, text=correct_title))
            audio.tags.add(
                TPE1(encoding=3, text=[a['name'] for a in track['artists']]))
            audio.tags.add(TPE2(encoding=3, text=album_artist))
            audio.tags.add(TALB(encoding=3, text=album))
            audio.tags.add(TDRC(encoding=3, text=release_year))
            audio.tags.add(TRCK(encoding=3, text=str(track_number)))
            audio.tags.add(TCON(encoding=3, text=genre))
            audio.tags.add(TPUB(encoding=3, text=publisher))

            audio.save(v2_version=3)
            os.remove(cover_filename)
