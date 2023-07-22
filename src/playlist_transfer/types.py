from typing import TypedDict, List, NewType

HtmlDoc = NewType("HtmlDoc", str)
TrackId = NewType("TrackId", str)

Track = TypedDict('Track', {'title': str, 'artist': str, 'duration':int})
Playlist = TypedDict('Playlist', {'title':str, 'tracks': List[Track]})
PlaylistTrackIds = TypedDict('PlaylistTrackIds', {'title':str, 'track_ids': List[TrackId]})

