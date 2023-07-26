from playlist_transfer.exceptions import PipelineException
from playlist_transfer.pipeline import Pipeline, ValueOrError
from playlist_transfer.request_retriever import RequestRetriever, RetrieveAndParse, RetrieveStrategy
from playlist_transfer.spotify.playlist_scraper import SpotifyPlaylistResponseParser, SpotifyPlaylistToPlaylist
from playlist_transfer.spotify.types import SpotifyPlaylist
from playlist_transfer.types import Playlist, Track

import sys
import re

from playlist_transfer.youtube.video_loader import SearchOrder, ToYoutubeSearchTitles, YoutubeTrackRetriever, YoutubeVideoRetriever

def print_playlist(playlist: Playlist):
    print(f"Title: {playlist['title']}")
    
    def minute_converter(seconds:int): 
        min, sec = divmod(seconds, 60)
        return '%d:%02d' % (min, sec)
    def track_str(i, track:Track):
        return f"{i}.\t{track['title']} - {track['artist']} - {minute_converter(track['duration'])}" 

    for (i, track) in enumerate(playlist['tracks']):
        print("\t" + track_str(i, track))
        
def spotify_playlist(args=sys.argv):
    if len(args) < 2:
        print("Usage : spotify-playlist [playlist_url]")
        return

    if re.search("https://open.spotify.com/playlist/", args[1]) == None:
        print("Must be a playlist")
        return
    
    url = args[1]
    request_retriever = RequestRetriever()
    spotify_parser = SpotifyPlaylistResponseParser()

    try:
        pipeline = Pipeline(RetrieveAndParse(request_retriever, spotify_parser))
        pipeline = pipeline.add(ValueOrError[SpotifyPlaylist](f"Cannot retrieve playlist from {url}"))
        pipeline = pipeline.add(SpotifyPlaylistToPlaylist(request_retriever, RetrieveStrategy.MULTI_THREAD))
        pipeline = pipeline.add(ToYoutubeSearchTitles())
        pipeline = pipeline.add(YoutubeVideoRetriever(RetrieveStrategy.MULTI_THREAD, SearchOrder.RELEVANCE))
        result = pipeline.execute(url)
        print(result)
    except PipelineException as e:
        print(e.msg)
