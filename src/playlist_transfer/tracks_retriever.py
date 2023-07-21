from __future__ import annotations

from playlist_transfer.types import * 

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List

class RetrieveStrategy(Enum):
    SINGLE_THREAD = 0
    MULTI_THREAD = 1

class RetrieveContext:
    def __init__(self, strategy: RetrieveStrategy):
        self.strategy = strategy

    def retrieve(self, url: List[TrackId]) -> Optional[List[Track]]:
        retriever  = __SingleThreadRetriever() if self.strategy == RetrieveStrategy.SINGLE_THREAD else __MultiThreadRetriever() 
        return retriever.process(url)

class __ITrackRetrieverStrategy(ABC):
    @abstractmethod
    def process(self, url: List[TrackId]) -> Optional[List[Track]]:
        return None 

class __SingleThreadRetriever(__ITrackRetrieverStrategy):
    def process(self, url: List[TrackId]) -> Optional[List[Track]]:
        return None

class __MultiThreadRetriever(__ITrackRetrieverStrategy):
    def process(self, url: List[TrackId]) -> Optional[List[Track]]:
        return None

class TracksRetriever:
    def __init__(self, strategy = RetrieveStrategy.SINGLE_THREAD):
        self.__context = RetrieveContext(strategy)

    def execute(self, url: List[TrackId]) -> Optional[List[Track]]:
        return self.__context.retrieve(url)
