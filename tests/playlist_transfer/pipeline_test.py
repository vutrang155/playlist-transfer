from playlist_transfer import pipeline

class ToString(pipeline.Pipe[int, str]):
    def process(self, input: int) -> str:
        return str(input)

class AddSpaces(pipeline.Pipe[str, str]):
    def process(self, input: str) -> str:
        return " ".join(input)

def test_with_one_pipe():
    expected = "1234"
    input = 1234
    actual = pipeline.Pipeline(ToString()).execute(input)
    assert expected == actual 

def test_with_two_pipes():
    expected = "1 2 3 4"
    input = 1234
    actual = pipeline.Pipeline(ToString()).add(AddSpaces()).execute(input)
    assert expected == actual 
