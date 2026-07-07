from __future__ import annotations

from collections.abc import Callable
from typing import Any

from backends.queue.base import Queue
from backends.queue.models import JobHandle, JobStatus


class UnknownJobError(Exception):
    """Raised when dispatch() is called with a job_name that isn't present
    in the job registry DummyQueue was constructed with.
    """


class _ImmediateJobHandle(JobHandle):
    """JobHandle for a job that has already finished executing by the time
    it's constructed. DummyQueue runs jobs synchronously, so there's no
    pending state to represent — status and result are fixed at construction.
    """

    def __init__(self, status: JobStatus, result: Any | None) -> None:
        self._status = status
        self._result = result

    @property
    def status(self) -> JobStatus:
        return self._status

    @property
    def result(self) -> Any | None:
        return self._result

    def wait(self, timeout: float | None = None) -> None:
        # Already complete — nothing to wait for.
        return None


class DummyQueue(Queue):
    """Executes the named job synchronously, in the calling process, the
    moment dispatch() is called.

    Not for production use — no retries, no process isolation, no
    persistence across restarts.
    """

    def __init__(self, jobs: dict[str, Callable[..., Any]]) -> None:
        self._jobs = jobs

    def dispatch(self, job_name: str, *args: object, **kwargs: object) -> JobHandle:
        try:
            job = self._jobs[job_name]
        except KeyError:
            raise UnknownJobError(
                f"No job registered under the name {job_name!r}."
            ) from None

        try:
            result = job(*args, **kwargs)
        except Exception:
            return _ImmediateJobHandle(status=JobStatus.FAILURE, result=None)
        return _ImmediateJobHandle(status=JobStatus.SUCCESS, result=result)