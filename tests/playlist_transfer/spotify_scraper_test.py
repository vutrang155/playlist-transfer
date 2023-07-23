from playlist_transfer.pipeline import Pipeline
from playlist_transfer.spotify.types import *
from playlist_transfer.spotify.playlist_scraper import *
from playlist_transfer.spotify.track_scraper import *

from playlist_transfer.types import *

def test_can_parse_title():
    expected_title = "jazzy ketchup"
    expected_track_ids:List[SpotifyTrackId] = [
            SpotifyTrackId("2Syy6iCju7lcPLesnbEwnV"),
            SpotifyTrackId("2iUrcZcAuVIahQD0dg9HLe"),
            SpotifyTrackId("1HEGcv63IZ7TPncpVKdVdN"),
            SpotifyTrackId("5O4qjToldZVIOHF8U3O2bD"),
            SpotifyTrackId("7HqMu6Oa7jLQVDUuWiy6v2"),
            SpotifyTrackId("7JtcCde09fsajDNHmPFrX7"),
            SpotifyTrackId("1jji1sWxZOo7eWnXifT7yP"),
            SpotifyTrackId("4DE2IwQUZMrEqCZ95D1iIk"),
            SpotifyTrackId("4JeFHVGKqWd7C0XVzxAXO5"),
            SpotifyTrackId("5F8rPLt2c52p0SK7kiH26b"),
            SpotifyTrackId("5Fpbw9DCdROeT1JtJWi7lR"),
            SpotifyTrackId("6yKkA8HzwWTZ5taIMaG4Nm"),
            SpotifyTrackId("7rcfs2bBj5mNyiJbBIQ7cc"),
            SpotifyTrackId("0F845nujLVqCb0XMZCh5Pc"),
            SpotifyTrackId("3O7WAvCq2hW9QLgXo5NcH5"),
            SpotifyTrackId("392OK8Qdmos0wNDrduiwy0"),
            SpotifyTrackId("5oq7NF2AjuMbfDMWdmFSbE"),
            SpotifyTrackId("4G3EKvGtqcUSZqPQIWJFxd"),
            SpotifyTrackId("6dNsu5wbiD8keAWts8INjU"),
            SpotifyTrackId("7yzM0pEseQUpb6BMViOPEA"),
            SpotifyTrackId("18MdkWVDeTH1KbCwavftec"),
            SpotifyTrackId("4yKTDPH6iRBHmA44AipmIk"),
            SpotifyTrackId("6qqK0oeBRapZn8f9hJJENw"),
            SpotifyTrackId("7gHRVNiuL66Z6fE6DwZaFT"),
            SpotifyTrackId("273VxALm722DRN4PNujOF8"),
            SpotifyTrackId("6QlkHjQmo2YncQN5MQXgPZ"),
            SpotifyTrackId("1cpANF6zMBoFoxkoIjZHjv"),
            SpotifyTrackId("5XPTuQXrCc8UPDExxVa4vh"),
            SpotifyTrackId("0E8q2Fx2XuzXCO2NSAppkR"),
            SpotifyTrackId("58yFroDNbzHpYzvicaC0de")]
    expected = SpotifyPlaylist(title=str(expected_title), track_ids=expected_track_ids)

    f = open("tests/ressources/playlist_1.html")
    input = HtmlDoc(f.read())

    actual = SpotifyPlaylistHtmlDocParser().from_html(input)
    assert expected == actual 

def test_can_parse_one_track():
    expected_title = "The Two Lonely People"
    expected_artist = "Bill Evans"
    expected_duration = 370
    expected = Track(title=expected_title, artist=expected_artist, duration=expected_duration)

    f = open("tests/ressources/tracks/track_1.html")
    input = HtmlDoc(f.read())

    actual = SpotifyTrackHtmlDocParser().from_html(input) 
    assert expected == actual

def test_can_parse_tracks_single_thread():
    expected = {'title': 'jazzy ketchup', 'tracks': [{'artist': 'Bill Evans', 'duration': 370, 'title': 'The Two Lonely People'}, {'artist': 'Chet Baker', 'duration' : 424, 'title': 'Autumn Leaves'}, {'artist': 'John Coltrane, Johnny Hartman', 'duration': 294, 'title': 'My One And Only Love'}]}
    class MockRequestRetriever(IRequestRetriever):
        def process(self, url:str) -> Optional[HtmlDoc]:
            if url == "https://open.spotify.com/track/2Syy6iCju7lcPLesnbEwnV":
                f = open("tests/ressources/tracks/track_1.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.com/track/2iUrcZcAuVIahQD0dg9HLe":
                f = open("tests/ressources/tracks/track_2.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.com/track/1HEGcv63IZ7TPncpVKdVdN":
                f = open("tests/ressources/tracks/track_3.html")
                return HtmlDoc(f.read())
            else:
                return None

    f = open("tests/ressources/playlist_1.html")
    playlist_doc = HtmlDoc(f.read())
    mock_request_retriever = MockRequestRetriever()
    playlist = Pipeline(SpotifyHtmlDocParser()).add(SpotifyPlaylistToPlaylist(mock_request_retriever)).execute(playlist_doc) 

    assert expected == playlist

def test_can_parse_tracks_multi_thread():
    expected = {'title': 'jazzy ketchup', 'tracks': [{'artist': 'Bill Evans', 'duration': 370, 'title': 'The Two Lonely People'}, {'artist': 'Chet Baker', 'duration' : 424, 'title': 'Autumn Leaves'}, {'artist': 'John Coltrane, Johnny Hartman', 'duration': 294, 'title': 'My One And Only Love'}]}
    class MockRequestRetriever(IRequestRetriever):
        def process(self, url:str) -> Optional[HtmlDoc]:
            if url == "https://open.spotify.com/track/2Syy6iCju7lcPLesnbEwnV":
                f = open("tests/ressources/tracks/track_1.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.com/track/2iUrcZcAuVIahQD0dg9HLe":
                f = open("tests/ressources/tracks/track_2.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.com/track/1HEGcv63IZ7TPncpVKdVdN":
                f = open("tests/ressources/tracks/track_3.html")
                return HtmlDoc(f.read())
            else:
                return None

    f = open("tests/ressources/playlist_1.html")
    playlist_doc = HtmlDoc(f.read())
    mock_request_retriever = MockRequestRetriever()
    playlist = Pipeline(SpotifyHtmlDocParser()).add(SpotifyPlaylistToPlaylist(mock_request_retriever, RetrieveStrategy.MULTI_THREAD)).execute(playlist_doc) 
    assert expected == playlist
