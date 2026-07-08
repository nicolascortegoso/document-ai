from __future__ import annotations

from libs.chunker.splitter.base import Splitter


class DefaultSplitter(Splitter):
    """Finds the nearest whitespace boundary to the desired split position,
    so a chunk boundary doesn't land in the middle of a word.

    If position already sits at a natural boundary (immediately before or
    after whitespace), it's returned unchanged — searching further back
    would needlessly shrink the window. Otherwise, searches backward from
    position first (keeping chunks at or under their target size), falls
    back to a forward search if no whitespace exists before position, and
    returns position unchanged if the text has no whitespace at all nearby
    (e.g. one long unbroken token).
    """

    def find_split(self, text: str, position: int) -> int:
        if position <= 0:
            return 0
        if position >= len(text):
            return len(text)

        if text[position] == " " or text[position - 1] == " ":
            return position

        backward = text.rfind(" ", 0, position)
        if backward != -1:
            return backward + 1

        forward = text.find(" ", position)
        if forward != -1:
            return forward

        return position