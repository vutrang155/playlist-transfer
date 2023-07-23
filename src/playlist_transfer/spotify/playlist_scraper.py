from bs4 import BeautifulSoup

from playlist_transfer.spotify.types import *
from playlist_transfer.spotify.track_scraper import IRequestRetriever, TracksRetriever

from playlist_transfer.pipeline import Pipe
from playlist_transfer.request_retriever import RetrieveStrategy

from typing import Optional, List

class SpotifyPlaylistHtmlDocParser(IHtmlDocParser[SpotifyPlaylist]):
    def from_html(self, input: HtmlDoc) -> Optional[SpotifyPlaylist]:
        soup = BeautifulSoup(input, 'html.parser')
        _title = SpotifyPlaylistHtmlDocParser.__extractTitle(soup)
        if _title == None:
            # TODO: Log 
            pass
        title = str(_title) if _title is not None else ""

        track_ids = SpotifyPlaylistHtmlDocParser.__extractTracks(soup) 
        return SpotifyPlaylist(title=title, track_ids=track_ids)

    @staticmethod
    def __extractTitle(soup: BeautifulSoup) -> Optional[str]:
        results = soup.find_all("meta", {"property" : "og:title"})

        if len(results) == 0:
            # TODO: Log
            return None
        
        return results[0]['content']

    @staticmethod
    def __extractTracks(soup: BeautifulSoup) -> List[SpotifyTrackId]:
        track_tags = soup.find_all("meta", {"name": "music:song"})

        if len(track_tags) == 0:
            # TODO: Log
            return [] 

        track_ids = [tag['content'] for tag in track_tags]
        track_ids = [SpotifyTrackId(track_id.split("track/")[1]) for track_id in track_ids]
        # TODO: Log

        return track_ids

class SpotifyHtmlDocParser(Pipe[HtmlDoc, SpotifyPlaylist]):
    def process(self, input:HtmlDoc) -> Optional[SpotifyPlaylist]:
        return SpotifyPlaylistHtmlDocParser().from_html(input) 

class SpotifyPlaylistToPlaylist(Pipe[SpotifyPlaylist, Playlist]):
    def __init__(self, request_retriever:IRequestRetriever, strategy:RetrieveStrategy=RetrieveStrategy.SINGLE_THREAD):
        self.__track_retriever = TracksRetriever(request_retriever, strategy) 

    def process(self, input:SpotifyPlaylist) -> Playlist:
        playlist_title = input['title']
        track_ids = input['track_ids']
        
        _tracks = self.__track_retriever.execute(track_ids)
        tracks = []
        for track_id in input['track_ids']:
            if track_id in _tracks.keys():
                tracks.append(_tracks[track_id])
            
        return Playlist(title=playlist_title, tracks=tracks)
