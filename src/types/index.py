# filepath: music-video-downloader/src/types/index.py
from typing import TypedDict, Union, List

class Song(TypedDict):
    title: str
    artist: str
    url: str

class Video(TypedDict):
    title: str
    director: str
    url: str

SearchResult = Union[Song, Video]

class SearchResults(TypedDict):
    results: List[SearchResult]
    total_results: int
    query: str