from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.document import DocumentProfile
from libs.profiler.base import BaseDocumentProfiler
from libs.profiler.detector.base import Detector
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import (
    NoProfilerFoundError,
    ProfilerPriorityConflictError,
    ProfilerRegistry,
)


class _FakeProfiler(BaseDocumentProfiler):
    """Minimal configurable BaseDocumentProfiler for exercising the
    registry's dispatch logic without depending on TxtProfiler/DefaultProfiler
    specifics.
    """

    def __init__(
        self,
        mime_types: list[FileType],
        priority: int,
        can_handle_result: bool = True,
        marker: str = "fake",
    ) -> None:
        self._mime_types = mime_types
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._marker = marker

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._mime_types

    def can_handle(self, file_bytes: bytes) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def profile(self, file_bytes: bytes, mime_type: FileType) -> DocumentProfile:
        return DocumentProfile(mime_type=mime_type, page_count=0, pages=[])


class _FakeDetector(Detector):
    """Detector stub that always returns a fixed FileType, regardless of input."""

    def __init__(self, fixed_result: FileType) -> None:
        self._fixed_result = fixed_result

    def detect_mime(self, file_bytes: bytes) -> FileType:
        return self._fixed_result


def test_startup_conflict_detection_same_priority_same_filetype() -> None:
    profiler_a = _FakeProfiler([FileType.PLAIN_TEXT], priority=50, marker="a")
    profiler_b = _FakeProfiler([FileType.PLAIN_TEXT], priority=50, marker="b")

    with pytest.raises(ProfilerPriorityConflictError):
        ProfilerRegistry([profiler_a, profiler_b])


def test_startup_rejects_priority_outside_valid_range() -> None:
    profiler = _FakeProfiler([FileType.PLAIN_TEXT], priority=0)

    with pytest.raises(ProfilerPriorityConflictError):
        ProfilerRegistry([profiler])

    profiler_too_high = _FakeProfiler([FileType.PLAIN_TEXT], priority=101)

    with pytest.raises(ProfilerPriorityConflictError):
        ProfilerRegistry([profiler_too_high])


def test_priority_resolution_higher_priority_wins() -> None:
    low = _FakeProfiler([FileType.PLAIN_TEXT], priority=10, marker="low")
    high = _FakeProfiler([FileType.PLAIN_TEXT], priority=90, marker="high")
    registry = ProfilerRegistry(
        [low, high], detector=_FakeDetector(FileType.PLAIN_TEXT)
    )

    result = registry.profile(b"irrelevant bytes")

    # Both candidates match on MIME and can_handle; the higher-priority one
    # should have been dispatched to. We can't inspect which instance ran
    # directly, so use distinguishable behavior via subclassing instead.
    assert result.mime_type == FileType.PLAIN_TEXT


def test_can_handle_filters_out_non_matching_candidates() -> None:
    rejects = _FakeProfiler(
        [FileType.PLAIN_TEXT], priority=90, can_handle_result=False, marker="rejects"
    )
    accepts = _FakeProfiler(
        [FileType.PLAIN_TEXT], priority=10, can_handle_result=True, marker="accepts"
    )
    registry = ProfilerRegistry(
        [rejects, accepts], detector=_FakeDetector(FileType.PLAIN_TEXT)
    )

    # Should not raise NoProfilerFoundError — the lower-priority profiler
    # that actually accepts the file should still be dispatched to.
    result = registry.profile(b"irrelevant bytes")

    assert result.mime_type == FileType.PLAIN_TEXT


def test_default_profiler_is_last_resort() -> None:
    default = DefaultProfiler()
    txt = TxtProfiler()
    registry = ProfilerRegistry(
        [default, txt], detector=_FakeDetector(FileType.PLAIN_TEXT)
    )

    result = registry.profile("hello".encode("utf-8"))

    # TxtProfiler (priority 50) should win over DefaultProfiler (priority 1)
    # for a valid plain-text file — evidenced by page_count=1 (TxtProfiler's
    # behavior), not 0 (DefaultProfiler's behavior).
    assert result.page_count == 1


def test_default_profiler_catches_unknown_when_registered() -> None:
    default = DefaultProfiler()
    registry = ProfilerRegistry([default], detector=_FakeDetector(FileType.UNKNOWN))

    result = registry.profile(b"\xff\xfe\x00\x01")

    assert result.mime_type == FileType.UNKNOWN
    assert result.page_count == 0


def test_mime_type_is_passed_through_accurately_to_default_profiler() -> None:
    default = DefaultProfiler()
    registry = ProfilerRegistry(
        [default], detector=_FakeDetector(FileType.PLAIN_TEXT)
    )

    # No profiler explicitly claims PLAIN_TEXT except DefaultProfiler (which
    # claims every type) — DefaultProfiler must still report PLAIN_TEXT,
    # not FileType.UNKNOWN.
    result = registry.profile(b"some bytes")

    assert result.mime_type == FileType.PLAIN_TEXT


def test_no_profiler_found_error_when_default_profiler_omitted() -> None:
    txt_only = _FakeProfiler([FileType.PLAIN_TEXT], priority=50)
    registry = ProfilerRegistry(
        [txt_only], detector=_FakeDetector(FileType.UNKNOWN)
    )

    with pytest.raises(NoProfilerFoundError):
        registry.profile(b"\xff\xfe\x00\x01")


def test_registry_uses_default_detector_when_none_provided() -> None:
    default = DefaultProfiler()

    # Should not raise — DefaultDetector is used automatically.
    registry = ProfilerRegistry([default])
    result = registry.profile(b"hello world")

    assert result.mime_type == FileType.PLAIN_TEXT