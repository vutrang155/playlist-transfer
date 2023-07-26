
# class YoutubeJsonResponseDecoder(json.JSONDecoder):
#     def __init__(self, *args, **kwargs):
#         json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
# 
#     def object_hook(self, dct):
#         return YoutubeResponseConverter.convert(dct)
#             
# 
# def test_youtube_decoder():
#     expected = YoutubeVideo(id=VideoId("wgXfou15I28"), title=VideoTitle("The Two Lonely People"))
#     f = open("tests/ressources/youtube_response.json")
#     actual = json.load(f, cls=YoutubeJsonResponseDecoder)
#     assert expected == actual
