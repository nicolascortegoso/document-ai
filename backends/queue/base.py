from __future__ import annotations

from abc import ABC, abstractmethod

from backends.queue.models import JobHandle


class Queue(ABC):
    @abstractmethod
    def dispatch(self, job_name: str, *args: object, **kwargs: object) -> JobHandle:
        """Enqueue the named job for execution and return immediately with
        a handle. Never blocks.

        Jobs are referenced by name, not by direct function reference —
        each implementation is responsible for resolving a name to the
        callable that runs it.
        """