from __future__ import annotations

from uuid import uuid4

import pytest

from backends.record.base import (
    DuplicateExternalIdError,
    RecordNotFoundError,
)
from backends.record.implementations.memory import InMemoryRecordStore


def _store() -> InMemoryRecordStore:
    return InMemoryRecordStore()


def test_register_creates_a_new_record_with_a_fresh_document_id() -> None:
    store = _store()

    record = store.register(external_id="paperless-123", checksum="abc")

    assert record.external_id == "paperless-123"
    assert record.checksum == "abc"
    assert record.pipeline_statuses == {}
    assert record.document_id is not None


def test_register_raises_on_duplicate_external_id() -> None:
    store = _store()
    store.register(external_id="paperless-123", checksum="abc")

    with pytest.raises(DuplicateExternalIdError):
        store.register(external_id="paperless-123", checksum="def")


def test_get_returns_the_registered_record() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    record = store.get(registered.document_id)

    assert record == registered


def test_get_raises_record_not_found_for_missing_document_id() -> None:
    store = _store()

    with pytest.raises(RecordNotFoundError):
        store.get(uuid4())


def test_get_by_external_id_returns_the_registered_record() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    record = store.get_by_external_id("paperless-123")

    assert record == registered


def test_get_by_external_id_raises_record_not_found_for_missing_id() -> None:
    store = _store()

    with pytest.raises(RecordNotFoundError):
        store.get_by_external_id("does-not-exist")


def test_exists_by_external_id_reflects_stored_state() -> None:
    store = _store()

    assert store.exists_by_external_id("paperless-123") is False
    store.register(external_id="paperless-123", checksum="abc")
    assert store.exists_by_external_id("paperless-123") is True


def test_update_checksum_changes_the_stored_value() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    store.update_checksum(registered.document_id, "new-checksum")

    record = store.get(registered.document_id)
    assert record.checksum == "new-checksum"


def test_update_checksum_raises_record_not_found_for_missing_document_id() -> None:
    store = _store()

    with pytest.raises(RecordNotFoundError):
        store.update_checksum(uuid4(), "checksum")


def test_update_pipeline_status_sets_a_new_pipeline_status() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    store.update_pipeline_status(registered.document_id, "ingestion", "success")

    record = store.get(registered.document_id)
    assert record.pipeline_statuses == {"ingestion": "success"}


def test_update_pipeline_status_overwrites_an_existing_status() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")
    store.update_pipeline_status(registered.document_id, "ingestion", "running")

    store.update_pipeline_status(registered.document_id, "ingestion", "success")

    record = store.get(registered.document_id)
    assert record.pipeline_statuses == {"ingestion": "success"}


def test_update_pipeline_status_for_different_pipelines_does_not_clobber() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    store.update_pipeline_status(registered.document_id, "ingestion", "success")
    store.update_pipeline_status(registered.document_id, "summarization", "running")

    record = store.get(registered.document_id)
    assert record.pipeline_statuses == {
        "ingestion": "success",
        "summarization": "running",
    }


def test_update_pipeline_status_raises_record_not_found_for_missing_document_id() -> None:
    store = _store()

    with pytest.raises(RecordNotFoundError):
        store.update_pipeline_status(uuid4(), "ingestion", "success")


def test_delete_removes_the_record() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    store.delete(registered.document_id)

    with pytest.raises(RecordNotFoundError):
        store.get(registered.document_id)


def test_delete_is_idempotent() -> None:
    store = _store()

    store.delete(uuid4())  # should not raise


def test_delete_cleans_up_the_external_id_index() -> None:
    store = _store()
    registered = store.register(external_id="paperless-123", checksum="abc")

    store.delete(registered.document_id)

    assert store.exists_by_external_id("paperless-123") is False
    # Re-registering the same external_id after delete must succeed —
    # confirms the index was actually cleaned up, not left dangling.
    new_record = store.register(external_id="paperless-123", checksum="xyz")
    assert new_record.document_id != registered.document_id
