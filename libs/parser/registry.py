from __future__ import annotations

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.base import BasePageExtractionStrategy
from libs.parser.postprocessor.base import Postprocessor
from libs.parser.postprocessor.implementations.default import DefaultPostprocessor

_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


class ParserPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority
    for the same FileType, or when a strategy declares a priority outside the
    documented [1, 100] range. Indicates a misconfiguration that must be
    resolved before any documents are processed.
    """


class NoStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy survives MIME filtering and
    can_handle inspection. Under normal operation this should never occur — it
    signals that DefaultPageExtractionStrategy was omitted from the registered
    strategy list.
    """


class ParserRegistry:
    """Dispatches a page to the highest-priority matching extraction strategy,
    then passes the extracted text through the configured Postprocessor.

    Accepts a list of strategies and a Postprocessor as constructor arguments.
    Unlike ProfilerRegistry, this registry does not detect the MIME type
    itself — mime_type is passed in by the caller, since it's already known
    from the profiling stage that runs before parsing.

    Startup validation:
        Raises ParserPriorityConflictError if any two strategies share the
        same get_priority() value for the same FileType, or if any strategy
        declares a priority outside [1, 100].

    Dispatch flow:
        1. Filter candidates to those whose supported_mime_types includes mime_type
        2. Call can_handle on each candidate, using the given page_profile
        3. Sort surviving candidates by get_priority() descending, dispatch to winner
        4. Pass the winner's extracted text through the configured Postprocessor
    """

    def __init__(
        self,
        strategies: list[BasePageExtractionStrategy],
        postprocessor: Postprocessor | None = None,
    ) -> None:
        self._strategies = strategies
        self._postprocessor = postprocessor or DefaultPostprocessor()
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[tuple[FileType, int], type[BasePageExtractionStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
                raise ParserPriorityConflictError(
                    f"{type(strategy).__name__} declares priority {priority}, "
                    f"outside the allowed range [{_MIN_PRIORITY}, {_MAX_PRIORITY}]."
                )
            for mime_type in strategy.supported_mime_types:
                key = (mime_type, priority)
                if key in seen:
                    raise ParserPriorityConflictError(
                        f"Priority conflict: {type(strategy).__name__} and "
                        f"{seen[key].__name__} both declare priority {priority} "
                        f"for {mime_type!r}."
                    )
                seen[key] = type(strategy)

    def parse_page(
        self, file_bytes: bytes, mime_type: FileType, page_profile: PageProfile
    ) -> str:
        candidates = [
            s for s in self._strategies if mime_type in s.supported_mime_types
        ]
        survivors = [s for s in candidates if s.can_handle(page_profile)]

        if not survivors:
            raise NoStrategyFoundError(
                f"No extraction strategy found for MIME type {mime_type!r}. "
                "Ensure DefaultPageExtractionStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        extracted = winner.extract(file_bytes, page_profile)
        return self._postprocessor.process(extracted)
