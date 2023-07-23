from playlist_transfer.types import *

class SpotifyTrackId(str, ToUrl):
    def to_url(self) -> Url | None:
        return Url("https://open.spotify.com/track/" + self.__str__())

class SpotifyPlaylist(TypedDict):
    title:str
    track_ids: List[SpotifyTrackId]

