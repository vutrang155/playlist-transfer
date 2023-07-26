from __future__ import annotations
from collections.abc import Mapping

from playlist_transfer.spotify.types import * 
from playlist_transfer.request_retriever import IRequestRetriever, RetrieveContext, RetrieveStrategy, UrlRetrieveAndParse

from bs4 import BeautifulSoup
import re
from typing import Optional, List

class SpotifyTrackHtmlDocParser(IHtmlDocParser[Track]):
    def from_response(self, input: TextResponse) -> Optional[Track]:
        soup = BeautifulSoup(input, "html.parser")

        _title = soup.find_all("meta", {"property":"og:title"})
        title = ""
        if len(_title) == 0:
            # TODO: Log
            pass
        else:
            title = _title[0]['content']

        _artist = SpotifyTrackHtmlDocParser.__extract_artist(soup)
        artist = str(_artist) if _artist != None else ""

        _duration = soup.find_all("meta", {"name":"music:duration"})
        duration = 0
        if len(_duration) == 0:
            # TODO: Log
            pass
        else:
            duration = int(_duration[0]['content'], 0)

        return Track(title=title, artist=artist, duration=duration)

    @staticmethod
    def __extract_artist(soup) -> Optional[str]:
        title = soup.title.string
        PATTERN = r"- song and lyrics by (.*) \| Spotify"
        r = re.search(PATTERN, title)

        if r == None:
            # TODO: Log
            return None 
        else:
            return r.group(1)

class TracksRetriever:
    def __init__(self, request_retriever: IRequestRetriever, strategy = RetrieveStrategy.SINGLE_THREAD):
        spotify_track_parser = SpotifyTrackHtmlDocParser()
        single_request_retriever = UrlRetrieveAndParse(request_retriever, spotify_track_parser)
        self.__context = RetrieveContext[SpotifyTrackId, Track](single_request_retriever, strategy)

    def execute(self, track_id: List[SpotifyTrackId]) -> Mapping[SpotifyTrackId, Track]:
        return self.__context.retrieve(track_id)
