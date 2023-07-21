from playlist_transfer.spotify_scrapper import * 

def test_can_parse_title():
    expected_title = "jazzy ketchup"
    expected_track_ids:List[Url] = [
            Url("2Syy6iCju7lcPLesnbEwnV"),
            Url("2iUrcZcAuVIahQD0dg9HLe"),
            Url("1HEGcv63IZ7TPncpVKdVdN"),
            Url("5O4qjToldZVIOHF8U3O2bD"),
            Url("7HqMu6Oa7jLQVDUuWiy6v2"),
            Url("7JtcCde09fsajDNHmPFrX7"),
            Url("1jji1sWxZOo7eWnXifT7yP"),
            Url("4DE2IwQUZMrEqCZ95D1iIk"),
            Url("4JeFHVGKqWd7C0XVzxAXO5"),
            Url("5F8rPLt2c52p0SK7kiH26b"),
            Url("5Fpbw9DCdROeT1JtJWi7lR"),
            Url("6yKkA8HzwWTZ5taIMaG4Nm"),
            Url("7rcfs2bBj5mNyiJbBIQ7cc"),
            Url("0F845nujLVqCb0XMZCh5Pc"),
            Url("3O7WAvCq2hW9QLgXo5NcH5"),
            Url("392OK8Qdmos0wNDrduiwy0"),
            Url("5oq7NF2AjuMbfDMWdmFSbE"),
            Url("4G3EKvGtqcUSZqPQIWJFxd"),
            Url("6dNsu5wbiD8keAWts8INjU"),
            Url("7yzM0pEseQUpb6BMViOPEA"),
            Url("18MdkWVDeTH1KbCwavftec"),
            Url("4yKTDPH6iRBHmA44AipmIk"),
            Url("6qqK0oeBRapZn8f9hJJENw"),
            Url("7gHRVNiuL66Z6fE6DwZaFT"),
            Url("273VxALm722DRN4PNujOF8"),
            Url("6QlkHjQmo2YncQN5MQXgPZ"),
            Url("1cpANF6zMBoFoxkoIjZHjv"),
            Url("5XPTuQXrCc8UPDExxVa4vh"),
            Url("0E8q2Fx2XuzXCO2NSAppkR"),
            Url("58yFroDNbzHpYzvicaC0de")]
    expected = PlaylistTrackUrls(title=str(expected_title), track_ids=expected_track_ids)

    f = open("tests/ressources/playlist_1.html")
    input = HtmlDoc(f.read())

    parser = PlaylistTracksExtractor()
    actual = parser.process(input)

    assert expected == actual 
