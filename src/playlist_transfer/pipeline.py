from __future__ import annotations  # For posponing annotation

from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

from playlist_transfer.exceptions import PipelineException

In = TypeVar("In")
Out = TypeVar("Out")
NewOut = TypeVar("NewOut")

class Pipe(ABC, Generic[In, Out]):
    @abstractmethod
    def process(self, input: In) -> Out:
        pass

class ValueOrError(Pipe[Optional[Out], Out], Generic[Out]):
    def __init__(self, msg):
        self.msg = msg

    def process(self, input: Optional[Out]) -> Out:
        if input == None:
            raise PipelineException(self.msg) 
        res: Out = input
        return res

class Pipeline(ABC, Generic[In, Out]):
    def __init__(self, current_pipe: Pipe[In, Out]):
        self.current_pipe = current_pipe

    def add(self, pipe: Pipe[Out, NewOut]) -> Pipeline[In, NewOut]:
        InnerIn = TypeVar("InnerIn")
        InnerOut = TypeVar("InnerOut")
        InnerNewOut = TypeVar("InnerNewOut")
        class NewPipe(Pipe[InnerIn, InnerNewOut]):
            def __init__(self,
                         current_pipe: Pipe[InnerIn, InnerOut],
                         new_pipe: Pipe[InnerOut, InnerNewOut]):
                self.current_pipe = current_pipe
                self.new_pipe = new_pipe

            def process(self, input: InnerIn) -> InnerNewOut:
                return self.new_pipe.process(self.current_pipe.process(input))

        return Pipeline(NewPipe(current_pipe=self.current_pipe, new_pipe=pipe))

    def execute(self, input: In) -> Out:
        return self.current_pipe.process(input)
