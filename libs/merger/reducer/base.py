from abc import ABC, abstractmethod

from libs.merger.reducer.models import ReducerInput


class Reducer(ABC):
    @abstractmethod
    def reduce(self, reducer_input: ReducerInput) -> str:
        """Combine reducer_input.texts into a single reduced string.

        Does not carry a "never raises" contract — a failure here feeds
        directly into the next reduction level as one of its own inputs,
        so it should propagate rather than be silently absorbed.
        """
