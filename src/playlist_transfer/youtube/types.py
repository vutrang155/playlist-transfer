
from typing import NewType, NotRequired, TypedDict


SearchTitle = NewType("SearchTitle", str)
VideoTitle = NewType("VideoTitle", str)
VideoId = NewType("VideoId", str)

class YoutubeVideo(TypedDict):
    id: VideoId
    title: NotRequired[VideoTitle]


