from playlist_transfer.pipeline import Pipeline
from playlist_transfer.spotify_scraper import *
from playlist_transfer.tracks_retriever import OneTrackExtractor 

from playlist_transfer.types import *

def test_can_parse_title():
    expected_title = "jazzy ketchup"
    expected_track_ids:List[TrackId] = [
            TrackId("2Syy6iCju7lcPLesnbEwnV"),
            TrackId("2iUrcZcAuVIahQD0dg9HLe"),
            TrackId("1HEGcv63IZ7TPncpVKdVdN"),
            TrackId("5O4qjToldZVIOHF8U3O2bD"),
            TrackId("7HqMu6Oa7jLQVDUuWiy6v2"),
            TrackId("7JtcCde09fsajDNHmPFrX7"),
            TrackId("1jji1sWxZOo7eWnXifT7yP"),
            TrackId("4DE2IwQUZMrEqCZ95D1iIk"),
            TrackId("4JeFHVGKqWd7C0XVzxAXO5"),
            TrackId("5F8rPLt2c52p0SK7kiH26b"),
            TrackId("5Fpbw9DCdROeT1JtJWi7lR"),
            TrackId("6yKkA8HzwWTZ5taIMaG4Nm"),
            TrackId("7rcfs2bBj5mNyiJbBIQ7cc"),
            TrackId("0F845nujLVqCb0XMZCh5Pc"),
            TrackId("3O7WAvCq2hW9QLgXo5NcH5"),
            TrackId("392OK8Qdmos0wNDrduiwy0"),
            TrackId("5oq7NF2AjuMbfDMWdmFSbE"),
            TrackId("4G3EKvGtqcUSZqPQIWJFxd"),
            TrackId("6dNsu5wbiD8keAWts8INjU"),
            TrackId("7yzM0pEseQUpb6BMViOPEA"),
            TrackId("18MdkWVDeTH1KbCwavftec"),
            TrackId("4yKTDPH6iRBHmA44AipmIk"),
            TrackId("6qqK0oeBRapZn8f9hJJENw"),
            TrackId("7gHRVNiuL66Z6fE6DwZaFT"),
            TrackId("273VxALm722DRN4PNujOF8"),
            TrackId("6QlkHjQmo2YncQN5MQXgPZ"),
            TrackId("1cpANF6zMBoFoxkoIjZHjv"),
            TrackId("5XPTuQXrCc8UPDExxVa4vh"),
            TrackId("0E8q2Fx2XuzXCO2NSAppkR"),
            TrackId("58yFroDNbzHpYzvicaC0de")]
    expected = PlaylistTrackIds(title=str(expected_title), track_ids=expected_track_ids)

    f = open("tests/ressources/playlist_1.html")
    input = HtmlDoc(f.read())

    parser = PlaylistTracksExtractor()
    actual = parser.process(input)

    assert expected == actual 

def test_can_parse_one_track():
    expected_title = "The Two Lonely People"
    expected_artist = "Bill Evans"
    expected_duration = 370
    expected = Track(title=expected_title, artist=expected_artist, duration=expected_duration)

    f = open("tests/ressources/tracks/track_1.html")
    input = HtmlDoc(f.read())

    parser = OneTrackExtractor()
    actual = parser.process(input)
    assert expected == actual

def test_can_parse_tracks_single_thread():
    expected = {'title': 'jazzy ketchup', 'tracks': [{'artist': 'Bill Evans', 'duration': 370, 'title': 'The Two Lonely People'}, {'artist': 'Chet Baker', 'duration' : 424, 'title': 'Autumn Leaves'}, {'artist': 'John Coltrane, Johnny Hartman', 'duration': 294, 'title': 'My One And Only Love'}]}
    class MockRequestRetriever(IRequestRetriever):
        def process(self, url:str) -> Optional[HtmlDoc]:
            if url == "https://open.spotify.con/track/2Syy6iCju7lcPLesnbEwnV":
                f = open("tests/ressources/tracks/track_1.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.con/track/2iUrcZcAuVIahQD0dg9HLe":
                f = open("tests/ressources/tracks/track_2.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.con/track/1HEGcv63IZ7TPncpVKdVdN":
                f = open("tests/ressources/tracks/track_3.html")
                return HtmlDoc(f.read())
            else:
                return None

    f = open("tests/ressources/playlist_1.html")
    playlist_doc = HtmlDoc(f.read())
    mock_request_retriever = MockRequestRetriever()
    playlist = Pipeline(PlaylistTracksExtractor()).add(PlaylistTrackIdsRetriever(mock_request_retriever)).execute(playlist_doc) 
    assert expected == playlist

def test_can_parse_tracks_multi_thread():
    expected = {'title': 'jazzy ketchup', 'tracks': [{'artist': 'Bill Evans', 'duration': 370, 'title': 'The Two Lonely People'}, {'artist': 'Chet Baker', 'duration' : 424, 'title': 'Autumn Leaves'}, {'artist': 'John Coltrane, Johnny Hartman', 'duration': 294, 'title': 'My One And Only Love'}]}
    class MockRequestRetriever(IRequestRetriever):
        def process(self, url:str) -> Optional[HtmlDoc]:
            if url == "https://open.spotify.con/track/2Syy6iCju7lcPLesnbEwnV":
                f = open("tests/ressources/tracks/track_1.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.con/track/2iUrcZcAuVIahQD0dg9HLe":
                f = open("tests/ressources/tracks/track_2.html")
                return HtmlDoc(f.read())
            elif url == "https://open.spotify.con/track/1HEGcv63IZ7TPncpVKdVdN":
                f = open("tests/ressources/tracks/track_3.html")
                return HtmlDoc(f.read())
            else:
                return None

    f = open("tests/ressources/playlist_1.html")
    playlist_doc = HtmlDoc(f.read())
    mock_request_retriever = MockRequestRetriever()
    playlist = Pipeline(PlaylistTracksExtractor()).add(PlaylistTrackIdsRetriever(mock_request_retriever, RetrieveStrategy.MULTI_THREAD)).execute(playlist_doc) 
    assert expected == playlist
