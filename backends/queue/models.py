from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"


class JobHandle(ABC):
    """Generic wrapper standing in for whatever async handle the underlying
    Queue implementation returns (e.g. Celery's AsyncResult), so nothing
    above backends/queue/ ever imports a task-queue-specific type.

    Abstract rather than a plain dataclass: a production implementation's
    handle needs to actively query a live job (e.g. polling a real
    AsyncResult), not just report a value fixed at construction time.
    """

    @property
    @abstractmethod
    def status(self) -> JobStatus:
        """Current job status."""

    @property
    @abstractmethod
    def result(self) -> Any | None:
        """The job's return value once available; None before completion."""

    @abstractmethod
    def wait(self, timeout: float | None = None) -> None:
        """Block until the job completes or the timeout elapses."""