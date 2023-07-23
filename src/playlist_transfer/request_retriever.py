from typing import TypeVar, Generic, Optional, Mapping, List

from playlist_transfer.pipeline import *
from playlist_transfer.types import *

import concurrent.futures
from abc import ABC, abstractmethod
from enum import Enum

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class IRequestRetriever(Pipe[str, Optional[HtmlDoc]], ABC):
    @abstractmethod
    def process(self, url:str) -> Optional[HtmlDoc]:
        pass

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

class AbstractOutputTransformer(Generic[OutputType], Pipe[Optional[HtmlDoc], Optional[OutputType]]):
    @abstractmethod
    def transform(self, input:HtmlDoc) -> OutputType:
        pass

    def execute(self, input: Optional[HtmlDoc]) -> Optional[OutputType]:
        if input == None:
            return None
        return self.transform(input)

class SingleRequestRetriever(ABC, Generic[UrlParseable, HtmlDocParseable]):
    def __init__(self, request_retriever:IRequestRetriever, parser:IHtmlDocParser[HtmlDocParseable]):
        self.__request_retreiver = request_retriever
        self.__parser = parser

    def execute(self, input: UrlParseable) -> Optional[HtmlDocParseable]:
        url = input.to_url()
        _html_doc:Optional[HtmlDoc] = self.__request_retreiver.process(url)
        if _html_doc == None:
            # TODO: Logging
            return None
        html_doc = HtmlDoc(_html_doc)
        return self.__parser.from_html(html_doc) 

class AbstractRequestRetrieverStrategy(ABC, Generic[InputType, OutputType]):
    def __init__(self, request_retriever:IRequestRetriever, htmldoc_parser:IHtmlDocParser):
        self._single_request_retriever = SingleRequestRetriever(request_retriever, htmldoc_parser) 

    @abstractmethod
    def process(self, track_ids: List[InputType]) -> Mapping[InputType, OutputType]:
        return None 

class SingleThreadRetriever(AbstractRequestRetrieverStrategy, Generic[InputType, OutputType]):
    def process(self, track_ids: List[InputType]) -> Mapping[InputType, OutputType]:
        res:Mapping[InputType, OutputType] = {}
        for track_id in track_ids:
            _track = self._single_request_retriever.execute(track_id)
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
            future_to_url = {executor.submit(self._single_request_retriever.execute, track_id): track_id for track_id in track_ids}
            for future in concurrent.futures.as_completed(future_to_url):
                track_id = future_to_url[future]
                _track = future.result()
                if _track == None:
                    continue
                track: OutputType = (_track)
                res[track_id] = track
        return res
