from __future__ import annotations

from libs.chunker.splitter.implementations.default import DefaultSplitter


def test_returns_zero_for_non_positive_position() -> None:
    splitter = DefaultSplitter()

    assert splitter.find_split("hello world", 0) == 0
    assert splitter.find_split("hello world", -5) == 0


def test_returns_text_length_for_position_at_or_beyond_end() -> None:
    splitter = DefaultSplitter()
    text = "hello world"

    assert splitter.find_split(text, len(text)) == len(text)
    assert splitter.find_split(text, len(text) + 100) == len(text)


def test_returns_position_unchanged_when_already_at_a_boundary() -> None:
    splitter = DefaultSplitter()
    text = "hello world foo"
    #        0123456789012345
    #             ^ position 5 is the space itself, right after "hello"

    # Should NOT search further back and find an earlier boundary — position
    # is already a valid split point.
    assert splitter.find_split(text, 5) == 5
    # Position immediately after a space is also already a valid boundary.
    assert splitter.find_split(text, 6) == 6


def test_prefers_nearest_whitespace_at_or_before_position() -> None:
    splitter = DefaultSplitter()
    text = "hello world foo"
    #        0123456789012345
    #                  ^ position 13, inside "foo" — nearest space before is at index 11

    result = splitter.find_split(text, 13)

    assert result == 12  # just after the space at index 11
    assert text[:result] == "hello world "


def test_falls_back_to_forward_search_when_no_space_before_position() -> None:
    splitter = DefaultSplitter()
    text = "helloworld foo"
    #       0123456789012345
    #             ^ position 5, no space before it — nearest space after is at index 10

    result = splitter.find_split(text, 5)

    assert result == 10


def test_returns_position_unchanged_when_no_whitespace_anywhere() -> None:
    splitter = DefaultSplitter()
    text = "oneverylongunbrokentoken"

    result = splitter.find_split(text, 10)

    assert result == 10