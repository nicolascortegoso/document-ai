from __future__ import annotations

import pytest

from backends.queue.implementations.dummy import DummyQueue, UnknownJobError
from backends.queue.models import JobStatus


def test_dispatch_runs_job_synchronously_and_returns_success() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    queue = DummyQueue(jobs={"add": add})

    handle = queue.dispatch("add", 2, 3)

    assert handle.status == JobStatus.SUCCESS
    assert handle.result == 5


def test_dispatch_passes_kwargs_through_to_the_job() -> None:
    def greet(name: str, *, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    queue = DummyQueue(jobs={"greet": greet})

    handle = queue.dispatch("greet", "world", greeting="Hi")

    assert handle.result == "Hi, world!"


def test_dispatch_returns_failure_status_when_job_raises() -> None:
    def boom() -> None:
        raise RuntimeError("something went wrong")

    queue = DummyQueue(jobs={"boom": boom})

    handle = queue.dispatch("boom")

    assert handle.status == JobStatus.FAILURE
    assert handle.result is None


def test_dispatch_raises_unknown_job_error_for_unregistered_name() -> None:
    queue = DummyQueue(jobs={})

    with pytest.raises(UnknownJobError):
        queue.dispatch("does_not_exist")


def test_wait_on_an_already_complete_handle_is_a_no_op() -> None:
    queue = DummyQueue(jobs={"noop": lambda: "done"})

    handle = queue.dispatch("noop")

    # Should not raise or block, regardless of timeout value.
    assert handle.wait() is None
    assert handle.wait(timeout=5.0) is None