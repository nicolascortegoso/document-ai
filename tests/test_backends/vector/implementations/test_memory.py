from __future__ import annotations

from uuid import uuid4

import pytest

from backends.vector.base import VectorNotFoundError
from backends.vector.implementations.memory import InMemoryVectorStore


def _store() -> InMemoryVectorStore:
    return InMemoryVectorStore(collection_name="test")


def test_upsert_then_get_returns_the_stored_record() -> None:
    store = _store()
    id_ = uuid4()

    store.upsert(id_, [1.0, 0.0, 0.0], metadata={"kind": "chunk"})
    record = store.get(id_)

    assert record.id == id_
    assert record.embedding == [1.0, 0.0, 0.0]
    assert record.metadata == {"kind": "chunk"}


def test_get_raises_vector_not_found_error_for_missing_id() -> None:
    store = _store()

    with pytest.raises(VectorNotFoundError):
        store.get(uuid4())


def test_exists_reflects_stored_state() -> None:
    store = _store()
    id_ = uuid4()

    assert store.exists(id_) is False
    store.upsert(id_, [1.0, 0.0])
    assert store.exists(id_) is True


def test_delete_is_idempotent() -> None:
    store = _store()
    id_ = uuid4()
    store.upsert(id_, [1.0, 0.0])

    store.delete(id_)
    assert store.exists(id_) is False

    store.delete(id_)  # should not raise


def test_upsert_overwrites_existing_record() -> None:
    store = _store()
    id_ = uuid4()

    store.upsert(id_, [1.0, 0.0], metadata={"v": 1})
    store.upsert(id_, [0.0, 1.0], metadata={"v": 2})

    record = store.get(id_)
    assert record.embedding == [0.0, 1.0]
    assert record.metadata == {"v": 2}


def test_search_returns_results_sorted_by_score_descending() -> None:
    store = _store()
    id_close = uuid4()
    id_far = uuid4()
    id_exact = uuid4()

    store.upsert(id_exact, [1.0, 0.0])
    store.upsert(id_close, [0.9, 0.1])
    store.upsert(id_far, [0.0, 1.0])

    results = store.search(query_vector=[1.0, 0.0], top_k=10)

    assert [r.id for r in results] == [id_exact, id_close, id_far]
    assert results[0].score > results[1].score > results[2].score


def test_search_respects_top_k() -> None:
    store = _store()
    for _ in range(5):
        store.upsert(uuid4(), [1.0, 0.0])

    results = store.search(query_vector=[1.0, 0.0], top_k=2)

    assert len(results) == 2


def test_search_identical_vector_scores_close_to_one() -> None:
    store = _store()
    id_ = uuid4()
    store.upsert(id_, [1.0, 2.0, 3.0])

    results = store.search(query_vector=[1.0, 2.0, 3.0], top_k=1)

    assert results[0].score == pytest.approx(1.0)


def test_search_orthogonal_vector_scores_near_zero() -> None:
    store = _store()
    id_ = uuid4()
    store.upsert(id_, [1.0, 0.0])

    results = store.search(query_vector=[0.0, 1.0], top_k=1)

    assert results[0].score == pytest.approx(0.0)


def test_search_filters_by_metadata() -> None:
    store = _store()
    id_a = uuid4()
    id_b = uuid4()
    store.upsert(id_a, [1.0, 0.0], metadata={"document_id": "doc-a"})
    store.upsert(id_b, [1.0, 0.0], metadata={"document_id": "doc-b"})

    results = store.search(
        query_vector=[1.0, 0.0], top_k=10, filters={"document_id": "doc-a"}
    )

    assert [r.id for r in results] == [id_a]


def test_search_with_no_filters_includes_everything() -> None:
    store = _store()
    store.upsert(uuid4(), [1.0, 0.0], metadata={"document_id": "doc-a"})
    store.upsert(uuid4(), [1.0, 0.0], metadata=None)

    results = store.search(query_vector=[1.0, 0.0], top_k=10, filters=None)

    assert len(results) == 2


def test_search_excludes_records_with_no_metadata_when_filtering() -> None:
    store = _store()
    id_with_metadata = uuid4()
    id_without_metadata = uuid4()
    store.upsert(id_with_metadata, [1.0, 0.0], metadata={"document_id": "doc-a"})
    store.upsert(id_without_metadata, [1.0, 0.0], metadata=None)

    results = store.search(
        query_vector=[1.0, 0.0], top_k=10, filters={"document_id": "doc-a"}
    )

    assert [r.id for r in results] == [id_with_metadata]


def test_search_top_k_zero_or_negative_returns_empty_list() -> None:
    store = _store()
    store.upsert(uuid4(), [1.0, 0.0])

    assert store.search(query_vector=[1.0, 0.0], top_k=0) == []
    assert store.search(query_vector=[1.0, 0.0], top_k=-5) == []


def test_search_on_empty_store_returns_empty_list() -> None:
    store = _store()

    assert store.search(query_vector=[1.0, 0.0], top_k=10) == []


def test_search_zero_vector_scores_zero_without_raising() -> None:
    store = _store()
    id_ = uuid4()
    store.upsert(id_, [0.0, 0.0, 0.0])

    results = store.search(query_vector=[1.0, 0.0, 0.0], top_k=1)

    assert results[0].score == 0.0
