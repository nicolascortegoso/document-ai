from abc import ABC, abstractmethod


class Splitter(ABC):
    @abstractmethod
    def find_split(self, text: str, position: int) -> int:
        """Given a desired split position, return the actual position to cut at.

        Implementations may adjust the position to align with a natural boundary
        (e.g. sentence end, paragraph break). The returned position must be in
        the range [0, len(text)]. Never raises.
        """