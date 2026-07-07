from __future__ import annotations

from common.models.document import DocumentProfile
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.base import BaseIngestionPipeline


class IngestionPipeline(BaseIngestionPipeline):
    """Concrete ingestion pipeline, composing libs/ domain logic behind the
    BaseIngestionPipeline contract.
    """

    def __init__(self, profiler_registry: ProfilerRegistry) -> None:
        self._profiler_registry = profiler_registry

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        return self._profiler_registry.profile(file_bytes)