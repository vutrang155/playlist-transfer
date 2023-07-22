from bs4 import BeautifulSoup

from playlist_transfer.pipeline import Pipe
from playlist_transfer.tracks_retriever import IRequestRetriever, RetrieveStrategy, TracksRetriever
from playlist_transfer.types import *

from typing import Optional, List

class PlaylistTracksExtractor(Pipe[HtmlDoc, PlaylistTrackIds]):
    def process(self, input: HtmlDoc) -> PlaylistTrackIds:
        soup = BeautifulSoup(input, 'html.parser')

        _title = self.__extractTitle(soup)
        if _title == None:
            # TODO: Log 
            pass
        title = str(_title) if _title is not None else ""

        track_ids = self.__extractTracks(soup) 
        return PlaylistTrackIds(title=title, track_ids=track_ids)

    def __extractTitle(self, soup: BeautifulSoup) -> Optional[str]:
        results = soup.find_all("meta", {"property" : "og:title"})

        if len(results) == 0:
            # TODO: Log
            return None
        
        return results[0]['content']

    def __extractTracks(self, soup: BeautifulSoup) -> List[TrackId]:
        track_tags = soup.find_all("meta", {"name": "music:song"})

        if len(track_tags) == 0:
            # TODO: Log
            return [] 

        track_ids = [tag['content'] for tag in track_tags]
        track_ids = [track_id.split("track/")[1] for track_id in track_ids]
        # TODO: Log

        return track_ids

class PlaylistTrackIdsRetriever(Pipe[PlaylistTrackIds, Playlist]):
    def __init__(self, request_retriever:IRequestRetriever, strategy:RetrieveStrategy=RetrieveStrategy.SINGLE_THREAD):
        self.__track_retriever = TracksRetriever(request_retriever, strategy) 

    def process(self, input:PlaylistTrackIds) -> Playlist:
        playlist_title = input['title']
        track_ids = input['track_ids']
        
        _tracks = self.__track_retriever.execute(track_ids)
        tracks = []
        for track_id in input['track_ids']:
            if track_id in _tracks.keys():
                tracks.append(_tracks[track_id])
            
        return Playlist(title=playlist_title, tracks=tracks)
