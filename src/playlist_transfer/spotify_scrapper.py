from bs4 import BeautifulSoup

from playlist_transfer.pipeline import Pipe

from typing import NewType, Optional, List, TypedDict

HtmlDoc = NewType("HtmlDoc", str)
Url = NewType("Url", str)
PlaylistTrackUrls = TypedDict('PlaylistTrackUrls', {'title':str, 'track_ids': List[Url]})

class PlaylistTracksExtractor(Pipe[HtmlDoc, PlaylistTrackUrls]):
    def process(self, input: HtmlDoc) -> PlaylistTrackUrls:
        return self.__process(input)

    def __process(self, input:HtmlDoc) -> PlaylistTrackUrls:
        soup = BeautifulSoup(input, 'html.parser')

        _title = self.__extractTitle(soup)
        if _title == None:
            # TODO: Log 
            pass
        title = str(_title) if _title is not None else ""

        track_ids = self.__extractTracks(soup) 
        return PlaylistTrackUrls(title=title, track_ids=track_ids)

    def __extractTitle(self, soup: BeautifulSoup) -> Optional[str]:
        results = soup.find_all("meta", {"property" : "og:title"})

        if len(results) == 0:
            # TODO: Log
            return None
        
        return results[0]['content']

    def __extractTracks(self, soup: BeautifulSoup) -> List[Url]:
        track_tags = soup.find_all("meta", {"name": "music:song"})

        if len(track_tags) == 0:
            # TODO: Log
            return [] 

        track_urls = [tag['content'] for tag in track_tags]
        track_ids = [url.split("track/")[1] for url in track_urls]
        # TODO: Log

        return track_ids
