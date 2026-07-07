from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pipelines.ingestion.base import BaseIngestionPipeline


def make_profile_document_job(
    pipeline: BaseIngestionPipeline,
) -> Callable[[bytes], dict[str, Any]]:
    """Build the plain, framework-free job function for the
    "profile_document" job.

    Dependency injection happens here, at job-registry construction time —
    not inside the returned callable itself, which stays a plain function
    of (file_bytes,) -> dict, safe to hand to any Queue implementation.
    """

    def profile_document(file_bytes: bytes) -> dict[str, Any]:
        result = pipeline.profile(file_bytes)
        return result.to_dict()

    return profile_document