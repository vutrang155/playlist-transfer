from enum import StrEnum
from typing import List, Optional
from playlist_transfer import request_retriever
from playlist_transfer.pipeline import Pipe
from playlist_transfer.request_retriever import IRequestRetriever, RetrieveAndParse, RetrieveContext, RetrieveStrategy
from playlist_transfer.types import DictResponse, IJsonParser, JsonParseable, Playlist, Response, Track

import googleapiclient.discovery
import googleapiclient.errors
from playlist_transfer.youtube.types import SearchTitle, VideoId, YoutubeVideo
import settings 

class SearchOrder(StrEnum):
    RELEVANCE = "relevance"
    MOST_VIEW = "viewCount"
    DATE = "date"
    TITLE = "title"

class YoutubeResponseConverter:
    @staticmethod
    def convert(dct) -> Optional[YoutubeVideo]:
        if 'items' not in dct:
            return None 

        items = dct['items']
        if items == None or len(items) == 0:
            return None 
        item = items[0]
        if 'id' not in item:
            return None 

        if 'kind' not in item['id'] or 'videoId' not in item['id']:
            return None 

        if item['id']['kind'] != "youtube#video":
            return None 

        video = YoutubeVideo(id=VideoId(item['id']['videoId']))
        if 'snippet' in item:
            snippet = item['snippet']
            if 'title' in snippet:
                video['title'] = snippet['title']
        return video

class YoutubeTrackParser(IJsonParser[YoutubeVideo]):
    def from_response(self, doc: Response) -> Optional[YoutubeVideo]: 
        return YoutubeResponseConverter.convert(doc)

class YoutubeTrackRetriever(IRequestRetriever[SearchTitle]):
    def __init__(self, search_strategy:SearchOrder=SearchOrder.RELEVANCE):
        api_service_name = "youtube"
        api_version = "v3"
        self.__youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=settings.YOUTUBE_API_KEY)
        self.__search_strategy = search_strategy

    def process(self, search_title:SearchTitle) -> Optional[Response]:
        request = self.__youtube.search().list(
            part = "id, snippet",
            order = self.__search_strategy.__str__(),
            q = search_title.__str__(),
            maxResults = 1,
            alt="json",
            prettyPrint=True
        )
        return DictResponse(request.execute())


class ToYoutubeSearchTitles(Pipe[Playlist, List[SearchTitle]]):
    def process(self, playlist:Playlist) -> List[SearchTitle]:
        tracks = playlist['tracks']
        res:List[SearchTitle] = []
        for track in tracks:
            res.append(SearchTitle(str(track['title']) + " " + str(track['artist'])))

        return res 

class YoutubeVideoRetriever(Pipe[List[SearchTitle], List[YoutubeVideo]]):
    def __init__(self, strategy:RetrieveStrategy=RetrieveStrategy.SINGLE_THREAD, search_strategy=SearchOrder.RELEVANCE):
        request_retriever = YoutubeTrackRetriever(search_strategy) 
        resposne_parser = YoutubeTrackParser()
        single_request_retriever = RetrieveAndParse(request_retriever, resposne_parser)
        self.__context = RetrieveContext[SearchTitle, YoutubeVideo](single_request_retriever) 

    def process(self, search_titles : List[SearchTitle]) -> List[YoutubeVideo]:
        responses = self.__context.retrieve(search_titles)
        return list(responses.values())
