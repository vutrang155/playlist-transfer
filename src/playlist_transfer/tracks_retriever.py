from __future__ import annotations
from collections.abc import Mapping

from playlist_transfer.types import * 
from playlist_transfer.pipeline import Pipe, Pipeline

from bs4 import BeautifulSoup

import concurrent.futures

import requests

from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import Optional, List

class RetrieveStrategy(Enum):
    SINGLE_THREAD = 0
    MULTI_THREAD = 1

class IRequestRetriever(ABC):
    @abstractmethod
    def process(self, url:str) -> Optional[HtmlDoc]:
        pass

class RequestRetriever(IRequestRetriever):
    def process(self, url:str) -> Optional[HtmlDoc]:
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        headers = {
                'user-agent' : USER_AGENT
                }

        result:requests.Response = requests.get(url, headers=headers) 
        if result.status_code != 200:
            # TODO: Log
            return None 
        return HtmlDoc(result.text)

class RetrieveContext:
    def __init__(self, strategy: RetrieveStrategy, request_retriever: IRequestRetriever):
        self.strategy = strategy
        self.request_retriever = request_retriever

    def retrieve(self, url: List[TrackId]) -> Mapping[TrackId, Track]:
        retriever  = SingleThreadRetriever(self.request_retriever) if self.strategy == RetrieveStrategy.SINGLE_THREAD else MultiThreadRetriever(self.request_retriever) 
        return retriever.process(url)

class OneTrackExtractor(Pipe[Optional[HtmlDoc], Optional[Track]]):
    def process(self, _input: Optional[HtmlDoc]) -> Optional[Track]:
        if _input == None:
            return None

        input = HtmlDoc(_input)
        soup = BeautifulSoup(input, "html.parser")

        _title = soup.find_all("meta", {"property":"og:title"})
        title = ""
        if len(_title) == 0:
            # TODO: Log
            pass
        else:
            title = _title[0]['content']

        _artist = self.__extract_artist(soup)
        artist = str(_artist) if _artist != None else ""

        _duration = soup.find_all("meta", {"name":"music:duration"})
        duration = 0
        if len(_duration) == 0:
            # TODO: Log
            pass
        else:
            duration = int(_duration[0]['content'], 0)

        return Track(title=title, artist=artist, duration=duration)

    def __extract_artist(self, soup) -> Optional[str]:
        title = soup.title.string
        PATTERN = r"- song and lyrics by (.*) \| Spotify"
        r = re.search(PATTERN, title)

        if r == None:
            # TODO: Log
            return None 
        else:
            return r.group(1)

class OneTrackRetriever(Pipe[TrackId, Optional[HtmlDoc]]):
    def __init__(self, request_retriever: IRequestRetriever):
        self.__request_retriever = request_retriever

    def process(self, input: TrackId) -> Optional[HtmlDoc]:
        url = "https://open.spotify.con/track/" + input
        return self.__request_retriever.process(url)
    
class AbstractTrackRetrieverStrategy(ABC):

    def __init__(self, request_retriever:IRequestRetriever):
        self._request_retriever = request_retriever

    @abstractmethod
    def process(self, track_ids: List[TrackId]) -> Mapping[TrackId, Track]:
        return None 

class SingleThreadRetriever(AbstractTrackRetrieverStrategy):
    def process(self, track_ids: List[TrackId]) -> Mapping[TrackId, Track]:
        res:Mapping[TrackId, Track] = {}
        retriever = Pipeline(OneTrackRetriever(self._request_retriever)).add(OneTrackExtractor())
        for track_id in track_ids:
            _track = retriever.execute(track_id)
            if _track == None:
                continue
            track = Track(_track)
            res[track_id] = track
        return res

class MultiThreadRetriever(AbstractTrackRetrieverStrategy):
    def process(self, track_ids: List[TrackId]) -> Mapping[TrackId, Track]:
        res:Mapping[TrackId, Track] = {}
        retriever = Pipeline(OneTrackRetriever(self._request_retriever)).add(OneTrackExtractor())

        # Thread Pool with worker = user's thread * 3 
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(retriever.execute, track_id): track_id for track_id in track_ids}
            for future in concurrent.futures.as_completed(future_to_url):
                track_id = future_to_url[future]
                _track = future.result()
                if _track == None:
                    continue
                track = Track(_track)
                res[track_id] = track

        return res

class TracksRetriever:
    def __init__(self, request_retriever: IRequestRetriever, strategy = RetrieveStrategy.SINGLE_THREAD):
        self.__context = RetrieveContext(strategy, request_retriever)

    def execute(self, url: List[TrackId]) -> Mapping[TrackId, Track]:
        return self.__context.retrieve(url)
