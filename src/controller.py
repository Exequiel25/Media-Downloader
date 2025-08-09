import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class MusicDownloaderController:
    def __init__(self, model, client_id=None, client_secret=None):
        self.model = model
        self.spotify_api = None
        if client_id and client_secret:
            self.authenticate_spotify(client_id, client_secret)

    def authenticate_spotify(self, client_id, client_secret):
        credentials = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret)
        self.spotify_api = spotipy.Spotify(
            client_credentials_manager=credentials)

    def search(self, query):
        # Busca localmente
        results = self.model.search(query)
        # Si hay Spotify disponible, busca también en Spotify y agrega resultados
        if self.spotify_api:
            spotify_results = self.model.fetch_spotify_metadata(
                self.spotify_api, query)
            results.extend(spotify_results)
        return results

    def search_by_artist_title(self, artist, title):
        results = self.model.search_by_artist_title(artist, title)
        # También busca en Spotify si está disponible
        if self.spotify_api:
            spotify_query = f"{artist} {title}"
            spotify_results = self.model.fetch_spotify_metadata(
                self.spotify_api, spotify_query)
            results.extend(spotify_results)
        return results

    def download_song(self, song_title, artist, save_path, progress_hook, format_selected):
        if format_selected == "mp3":
            self.download_audio(song_title, artist, save_path, progress_hook)
        elif format_selected == "mp4":
            self.download_video(song_title, artist, save_path, progress_hook)

    def download_audio(self, song_title, artist, save_path, progress_hook):
        song_obj = None
        # Busca el objeto Song en la lista
        for s in self.model.songs:
            if song_title.lower() in s.title.lower() and artist.lower() in s.artist.lower():
                song_obj = s
                break
        song = self.model.get_song(song_title, artist)
        if not song:
            raise ValueError("Song not found.")
        url = song.get('youtube_url')
        if not url:
            url = self.get_youtube_url(song_title, artist)
            if not url:
                raise ValueError("No YouTube URL found for this song.")
            # Guarda el enlace en el objeto Song
            if song_obj:
                song_obj.youtube_url = url

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_video(self, video_title, artist, save_path, progress_hook):
        video_obj = None
        for v in self.model.songs:
            if video_title.lower() in v.title.lower() and artist.lower() in v.artist.lower():
                video_obj = v
                break
        video = self.model.get_song(video_title, artist)
        if not video:
            raise ValueError("Video not found.")
        url = video.get('youtube_url')
        if not url:
            url = self.get_youtube_url(video_title, artist)
            if not url:
                raise ValueError("No YouTube URL found for this video.")
            if video_obj:
                video_obj.youtube_url = url

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"[ERROR] yt_dlp falló: {e}")

    def get_youtube_url(self, title, artist):
        query = f"ytsearch1:{artist} {title}"
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'default_search': 'auto',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                # Puede venir como dict o lista
                entries = info.get('entries') if isinstance(
                    info, dict) else info
                if entries and len(entries) > 0:
                    entry = entries[0]
                    # Intenta obtener el enlace de varias formas
                    if 'webpage_url' in entry:
                        return entry['webpage_url']
                    elif 'url' in entry and entry['url'].startswith('http'):
                        return entry['url']
                    elif 'id' in entry:
                        return f"https://www.youtube.com/watch?v={entry['id']}"
        except Exception as e:
            print(f"Error buscando en YouTube: {e}")
        return None
