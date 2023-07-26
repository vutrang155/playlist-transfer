from abc import ABC, abstractmethod
from typing import Generic, Hashable, Optional, TypeVar, TypedDict, List, NewType 

Url = NewType("Url", str)
class ToUrl(ABC):
    @abstractmethod
    def to_url(self) -> Url:
        pass
UrlParseable = TypeVar("UrlParseable", bound=ToUrl)

TextResponse = NewType("TextResponse", str)
DictResponse = NewType("DictResponse", dict)
Response = TextResponse | DictResponse
ResponseParseable = TypeVar("ResponseParseable")
class IResponseParser(ABC, Generic[ResponseParseable]):
    @abstractmethod
    def from_response(self, doc: Response) -> Optional[ResponseParseable]: 
        pass

JsonParseable = TypeVar("JsonParseable")
class IJsonParser(IResponseParser[JsonParseable], ABC, Generic[JsonParseable]):
    @abstractmethod
    def from_response(self, doc: Response) -> Optional[JsonParseable]: 
        pass

HtmlDocParseable = TypeVar("HtmlDocParseable")
class IHtmlDocParser(IResponseParser[HtmlDocParseable], ABC, Generic[HtmlDocParseable]):
    @abstractmethod
    def from_response(self, doc: Response) -> Optional[HtmlDocParseable]: 
        pass

class Track(TypedDict):
    title:str
    artist:str
    duration:int

class Playlist(TypedDict):
    title:str
    tracks:List[Track]
