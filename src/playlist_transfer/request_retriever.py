from typing import TypeVar, Generic, Optional, Mapping, List

from playlist_transfer.pipeline import *
from playlist_transfer.types import *

import concurrent.futures
from abc import ABC, abstractmethod
from enum import Enum
import requests

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class IRequestRetriever(Pipe[Url, Optional[HtmlDoc]], ABC):
    @abstractmethod
    def process(self, url:Url) -> Optional[HtmlDoc]:
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

class RetrieveAndParse(Generic[UrlParseable, HtmlDocParseable], Pipe[UrlParseable, Optional[HtmlDocParseable]]):
    def __init__(self, request_retriever:IRequestRetriever, parser:IHtmlDocParser[HtmlDocParseable]):
        self.__request_retreiver = request_retriever
        self.__parser = parser

    def process(self, url_parseable: UrlParseable) -> Optional[HtmlDocParseable]:
        url = url_parseable.to_url()
        _html_doc:Optional[HtmlDoc] = self.__request_retreiver.process(url)
        if _html_doc == None:
            # TODO: Logging
            return None
        html_doc = HtmlDoc(_html_doc)
        return self.__parser.from_html(html_doc) 

class RetrieveStrategy(Enum):
    SINGLE_THREAD = 0
    MULTI_THREAD = 1

class RetrieveContext(Generic[InputType, HtmlDocParseable]):
    def __init__(self, strategy: RetrieveStrategy, request_retriever: IRequestRetriever, htmldoc_parser: IHtmlDocParser[HtmlDocParseable]):
        self.strategy = strategy
        self.request_retriever = request_retriever
        self.htmldoc_parser = htmldoc_parser

    def retrieve(self, url: List[InputType]) -> Mapping[InputType, HtmlDocParseable]:
        retriever  = SingleThreadRetriever(self.request_retriever, self.htmldoc_parser) if self.strategy == RetrieveStrategy.SINGLE_THREAD else MultiThreadRetriever(self.request_retriever, self.htmldoc_parser) 
        return retriever.process(url)

class AbstractRequestRetrieverStrategy(ABC, Generic[InputType, OutputType]):
    def __init__(self, request_retriever:IRequestRetriever, htmldoc_parser:IHtmlDocParser):
        self._single_request_retriever = RetrieveAndParse(request_retriever, htmldoc_parser) 

    @abstractmethod
    def process(self, track_ids: List[InputType]) -> Mapping[InputType, OutputType]:
        return None 

class SingleThreadRetriever(AbstractRequestRetrieverStrategy, Generic[InputType, OutputType]):
    def process(self, track_ids: List[InputType]) -> Mapping[InputType, OutputType]:
        res:Mapping[InputType, OutputType] = {}
        for track_id in track_ids:
            _track = self._single_request_retriever.process(track_id)
            if _track == None:
                continue
            track: OutputType = _track
            res[track_id] = track
        return res

class MultiThreadRetriever(AbstractRequestRetrieverStrategy, Generic[InputType, OutputType]):
    def process(self, track_ids: List[InputType]) -> Mapping[InputType, OutputType]:
        res:Mapping[InputType, OutputType] = {}
        # Thread Pool with worker = user's thread * 3 
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(self._single_request_retriever.process, track_id): track_id for track_id in track_ids}
            for future in concurrent.futures.as_completed(future_to_url):
                track_id = future_to_url[future]
                _track = future.result()
                if _track == None:
                    continue
                track: OutputType = (_track)
                res[track_id] = track
        return res
