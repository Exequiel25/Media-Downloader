class Song:
    def __init__(self, title, artist, url, youtube_url=None):
        self.title = title
        self.artist = artist
        self.url = url  # Puede ser Spotify, etc.
        self.youtube_url = youtube_url  # Enlace real de YouTube

    def __repr__(self):
        return f"Song(title={self.title}, artist={self.artist}, url={self.url}, youtube_url={self.youtube_url})"


class MediaManager:
    def __init__(self):
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)

    def find_song(self, title=None, artist=None):
        results = []
        for song in self.songs:
            if (title and title.lower() in song.title.lower()) or (artist and artist.lower() in song.artist.lower()):
                results.append(song)
        return results

    def search(self, query):
        results = []
        for song in self.songs:
            if (query.lower() in song.title.lower() or
                query.lower() in song.artist.lower() or
                    query.lower() in song.url.lower()):
                results.append({'type': 'song', 'title': song.title,
                               'artist': song.artist, 'url': song.url,
                                'youtube_url': song.youtube_url})
        return results

    def search_by_artist_title(self, artist, title):
        results = []
        for song in self.songs:
            if artist.lower() in song.artist.lower() and title.lower() in song.title.lower():
                results.append({'type': 'song', 'title': song.title,
                               'artist': song.artist, 'url': song.url,
                                'youtube_url': song.youtube_url})
        return results

    def get_song(self, title, artist):
        for song in self.songs:
            if title.lower() in song.title.lower() and artist.lower() in song.artist.lower():
                return {
                    'title': song.title,
                    'artist': song.artist,
                    'youtube_url': song.youtube_url
                }
        return None

    def clear_media(self):
        self.songs.clear()

    def fetch_spotify_metadata(self, spotify_api, query):
        results = []
        search_results = spotify_api.search(q=query, type='track', limit=5)
        for item in search_results['tracks']['items']:
            title = item['name']
            artist = item['artists'][0]['name']
            url = item['external_urls']['spotify']
            # Obtener la imagen del álbum
            cover_url = item['album']['images'][0]['url'] if item['album']['images'] else None
            song = Song(title, artist, url)
            self.add_song(song)
            results.append({
                'type': 'song',
                'title': title,
                'artist': artist,
                'url': url,
                'cover_url': cover_url
            })
        return results
