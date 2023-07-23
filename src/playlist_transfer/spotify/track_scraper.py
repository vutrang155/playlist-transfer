from __future__ import annotations
from collections.abc import Mapping

from playlist_transfer.spotify.types import * 
from playlist_transfer.request_retriever import IRequestRetriever, RetrieveContext, RetrieveStrategy

from bs4 import BeautifulSoup
import requests
import re
from typing import Optional, List

class RequestRetriever(IRequestRetriever):
    def execute(self, url:str) -> Optional[HtmlDoc]:
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        headers = {
                'user-agent' : USER_AGENT
                }

        result:requests.Response = requests.get(url, headers=headers) 
        if result.status_code != 200:
            # TODO: Log
            return None 
        return HtmlDoc(result.text)

class SpotifyTrackHtmlDocParser(IHtmlDocParser[Track]):
    def from_html(self, input: HtmlDoc) -> Optional[Track]:
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
        htmldoc_parser = SpotifyTrackHtmlDocParser()
        self.__context = RetrieveContext(strategy, request_retriever, htmldoc_parser)

    def execute(self, track_id: List[SpotifyTrackId]) -> Mapping[SpotifyTrackId, Track]:
        return self.__context.retrieve(track_id)
