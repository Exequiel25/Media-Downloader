import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import threading
import concurrent.futures

MAX_WORKERS = 16  # Número máximo de hilos para descargar canciones


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
        # Si es una playlist de youtube
        if query.startswith("https://www.youtube.com/playlist") or query.startswith("https://youtu.be/playlist"):
            youtube_results = self.search_youtube_playlist(query)
            results.extend(youtube_results)
        # Si es una url de youtube
        elif query.startswith("https://youtu.be/") or query.startswith("https://www.youtube.com/"):
            youtube_results = self.search_youtube_url(query)
            results.extend(youtube_results)
        # Si hay Spotify disponible, busca también en Spotify y agrega resultados
        elif self.spotify_api:
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

    def download_multiple_songs(self, song_list, save_path, progress_hook, max_workers=MAX_WORKERS):
        """
        Descarga varias canciones en paralelo usando un pool de hilos.
        song_list: lista de dicts con keys 'title', 'artist', 'format'
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for song in song_list:
                futures.append(executor.submit(
                    self.download_song,
                    song["title"],
                    song["artist"],
                    save_path,
                    progress_hook,
                    song["format"]
                ))
            concurrent.futures.wait(futures)

    def search_youtube_url(self, url):
        """Obtiene metadatos de un video de YouTube por URL."""
        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            result = {
                'artist': info.get('uploader', ''),
                'title': info.get('title', ''),
                'cover_url': info.get('thumbnail', ''),
                'youtube_url': url
            }
            self.model.fetch_youtube_metadata(result)
            return [result]
        except Exception as e:
            print(f"Error obteniendo metadatos de YouTube: {e}")
            return []

    def search_youtube_playlist(self, playlist_url, max_workers=MAX_WORKERS):
        """Obtiene metadatos de todos los videos de una playlist de YouTube en paralelo y los agrega al modelo."""
        ydl_opts = {'quiet': True, 'skip_download': True,
                    'ignoreerrors': True}  # <-- agregado ignoreerrors
        results = []
        seen = set()
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                entries = info.get('entries', [])

                def process_entry(entry):
                    if entry is None:
                        return  # <-- ignora entradas nulas (errores)
                    key = (entry.get('title', '').lower(),
                           entry.get('uploader', '').lower())
                    if key in seen:
                        return
                    seen.add(key)
                    result = {
                        'artist': entry.get('uploader', ''),
                        'title': entry.get('title', ''),
                        'cover_url': entry.get('thumbnail', ''),
                        'youtube_url': entry.get('webpage_url', '')
                    }
                    results.append(result)
                    self.model.fetch_youtube_metadata(result)

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    executor.map(process_entry, entries)
            return results
        except Exception as e:
            print(f"Error obteniendo playlist: {e}")
            return []

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
