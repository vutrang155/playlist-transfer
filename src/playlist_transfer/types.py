from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, TypedDict, List, NewType 

Url = NewType("Url", str)
class ToUrl(ABC):
    @abstractmethod
    def to_url(self) -> Url:
        pass
UrlParseable = TypeVar('UrlParseable', bound=ToUrl)

HtmlDoc = NewType("HtmlDoc", str)
HtmlDocParseable = TypeVar("HtmlDocParseable")
class IHtmlDocParser(ABC, Generic[HtmlDocParseable]):
    @abstractmethod
    def from_html(self, doc: HtmlDoc) -> Optional[HtmlDocParseable]: 
        pass

class SpotifyTrackId(str, ToUrl):
    def to_url(self) -> Url | None:
        return Url("https://open.spotify.con/track/" + self.__str__())

class SpotifyPlaylist(TypedDict):
    title:str
    track_ids: List[SpotifyTrackId]

class Track(TypedDict):
    title:str
    artist:str
    duration:int

class Playlist(TypedDict):
    title:str
    tracks:List[Track]
