import requests

def search_songs(song_name, artist_name=None):
    base_url = "https://api.example.com/search/songs"
    params = {"song": song_name}
    if artist_name:
        params["artist"] = artist_name
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def search_videos(video_name, director_name=None, actor_name=None):
    base_url = "https://api.example.com/search/videos"
    params = {"video": video_name}
    if director_name:
        params["director"] = director_name
    if actor_name:
        params["actor"] = actor_name
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def search_by_url(url):
    base_url = "https://api.example.com/search/url"
    params = {"url": url}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()