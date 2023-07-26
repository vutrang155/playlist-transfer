from typing import Dict, TypeVar, Generic, Optional, Mapping, List

from playlist_transfer.pipeline import *
from playlist_transfer.types import *

import concurrent.futures
from abc import ABC, abstractmethod
from enum import Enum
import requests

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class IRequestRetriever(Pipe[InputType, Response], ABC, Generic[InputType]):
    @abstractmethod
    def process(self, url:InputType) -> Optional[Response]:
        pass

class RequestRetriever(IRequestRetriever[Url]):
    def __init__(self):
        self.__default_headers:Dict[str, str] = dict()

    def with_default_header(self, key:str, val:str): 
        self.__default_headers[key] = val

    def process(self, url:str) -> Optional[Response]:
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        headers = self.__default_headers
        headers["user-agent"] = USER_AGENT

        result:requests.Response = requests.get(url, headers=headers) 
        if result.status_code != 200:
            # TODO: Log
            return None 
        return TextResponse(result.text)

class AbstractSingleRequestRetriever(Pipe[InputType, Optional[ResponseParseable]], ABC, Generic[InputType, ResponseParseable]):
    def __init__(self, request_retriever:IRequestRetriever, parser:IResponseParser[ResponseParseable]):
        self._request_retreiver = request_retriever
        self._parser = parser

    @abstractmethod
    def process(self, input:InputType) -> Optional[ResponseParseable]:
        pass

class UrlRetrieveAndParse(AbstractSingleRequestRetriever[UrlParseable, ResponseParseable], Generic[UrlParseable, ResponseParseable]):
    def process(self, input: UrlParseable) -> Optional[ResponseParseable]:
        url = input.to_url() 
        _response = self._request_retreiver.process(url)

        if _response == None:
            # TODO: Logging
            return None
        html_doc = _response
        return self._parser.from_response(html_doc) 

class RetrieveAndParse(AbstractSingleRequestRetriever[InputType, ResponseParseable], Generic[InputType, ResponseParseable]):
    def process(self, input: InputType) -> Optional[ResponseParseable]:
        _response = self._request_retreiver.process(input)
        if _response == None:
            # TODO: Logging
            return None
        html_doc = _response
        return self._parser.from_response(html_doc) 

class RetrieveStrategy(Enum):
    SINGLE_THREAD = 0
    MULTI_THREAD = 1

class RetrieveContext(Generic[InputType, ResponseParseable]):
    def __init__(self, single_request_retriever:AbstractSingleRequestRetriever[InputType, ResponseParseable], strategy:RetrieveStrategy=RetrieveStrategy.SINGLE_THREAD):
        self.__strategy = strategy
        self.__single_request_retriever = single_request_retriever

    def retrieve(self, url: List[InputType]) -> Mapping[InputType, ResponseParseable]:
        retriever  = SingleThreadRetriever(self.__single_request_retriever) if self.__strategy == RetrieveStrategy.SINGLE_THREAD else MultiThreadRetriever(self.__single_request_retriever) 
        return retriever.process(url)

class AbstractRequestRetrieverStrategy(ABC, Generic[InputType, OutputType]):
    def __init__(self, single_request_retriever:AbstractSingleRequestRetriever[InputType, OutputType]):
        self._single_request_retriever = single_request_retriever 

    @abstractmethod
    def process(self, keys: List[InputType]) -> Mapping[InputType, OutputType]:
        return None 

class SingleThreadRetriever(AbstractRequestRetrieverStrategy, Generic[InputType, OutputType]):
    def process(self, keys: List[InputType]) -> Mapping[InputType, OutputType]:
        res:Mapping[InputType, OutputType] = {}
        for key in keys:
            _val = self._single_request_retriever.process(key)
            if _val == None:
                continue
            val: OutputType = _val
            res[key] = val 
        return res

class MultiThreadRetriever(AbstractRequestRetrieverStrategy, Generic[OutputType]):
    def process(self, keys: List[InputType]) -> Mapping[InputType, OutputType]:
        res:Mapping[InputType, OutputType] = {}
        # Thread Pool with worker = user's thread * 3 
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(self._single_request_retriever.process, key): key for key in keys}
            for future in concurrent.futures.as_completed(future_to_url):
                key = future_to_url[future]
                _val = future.result()
                if _val == None:
                    continue
                val: OutputType = (_val)
                res[key] = val
        return res
