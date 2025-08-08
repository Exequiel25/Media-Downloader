class Song:
    def __init__(self, title, artist, url):
        self.title = title
        self.artist = artist
        self.url = url

    def __repr__(self):
        return f"Song(title={self.title}, artist={self.artist}, url={self.url})"


class Video:
    def __init__(self, title, director, url):
        self.title = title
        self.director = director
        self.url = url

    def __repr__(self):
        return f"Video(title={self.title}, director={self.director}, url={self.url})"


class MediaManager:
    def __init__(self):
        self.songs = []
        self.videos = []

    def add_song(self, song):
        self.songs.append(song)

    def add_video(self, video):
        self.videos.append(video)

    def find_song(self, title=None, artist=None):
        results = []
        for song in self.songs:
            if (title and title.lower() in song.title.lower()) or (artist and artist.lower() in song.artist.lower()):
                results.append(song)
        return results

    def find_video(self, title=None, director=None):
        results = []
        for video in self.videos:
            if (title and title.lower() in video.title.lower()) or (director and director.lower() in video.director.lower()):
                results.append(video)
        return results

    def search(self, query):
        # Busca en canciones y videos por cualquier campo relevante
        results = []
        for song in self.songs:
            if (query.lower() in song.title.lower() or
                query.lower() in song.artist.lower() or
                    query.lower() in song.url.lower()):
                results.append({'type': 'song', 'title': song.title,
                               'artist': song.artist, 'url': song.url})
        for video in self.videos:
            if (query.lower() in video.title.lower() or
                query.lower() in video.director.lower() or
                    query.lower() in video.url.lower()):
                results.append({'type': 'video', 'title': video.title,
                               'director': video.director, 'url': video.url})
        return results

    def search_by_artist_title(self, artist, title):
        # Busca canciones por artista y título
        results = []
        for song in self.songs:
            if artist.lower() in song.artist.lower() and title.lower() in song.title.lower():
                results.append({'type': 'song', 'title': song.title,
                               'artist': song.artist, 'url': song.url})
        return results

    def get_song(self, title, artist):
        for song in self.songs:
            if title.lower() in song.title.lower() and artist.lower() in song.artist.lower():
                return song
        return None

    def get_video(self, title, director):
        for video in self.videos:
            if title.lower() in video.title.lower() and director.lower() in video.director.lower():
                return video
        return None

    def clear_media(self):
        self.songs.clear()
        self.videos.clear()

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
