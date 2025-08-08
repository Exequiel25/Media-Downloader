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
        song = self.model.get_song(song_title, artist)
        if not song:
            raise ValueError("Song not found.")
        # Simulate download process
        for i in range(101):
            progress_hook({'status': 'downloading',
                          'downloaded_bytes': i, 'total_bytes': 100})
        progress_hook({'status': 'finished'})

    def download_video(self, video_title, director, save_path, progress_hook):
        video = self.model.get_video(video_title, director)
        if not video:
            raise ValueError("Video not found.")
        # Simulate download process
        for i in range(101):
            progress_hook({'status': 'downloading',
                          'downloaded_bytes': i, 'total_bytes': 100})
        progress_hook({'status': 'finished'})
