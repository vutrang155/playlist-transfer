from typing import TypedDict, List 

Song = TypedDict('Song', {'title': str, 'artist': str, 'album': str, 'duration':str})
Playlist = TypedDict('Playlist', {'title':str, 'songs': List[Song]})
