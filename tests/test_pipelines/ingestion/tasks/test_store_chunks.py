from __future__ import annotations

from uuid import UUID, uuid4

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from backends.vector.implementations.memory import InMemoryVectorStore
from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.indexed import IndexedChunk
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
from libs.indexer.implementations.batch import BatchIndexer
from libs.indexer.registry import IndexerRegistry
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.registry import ParserRegistry
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.implementations.ingestion import IngestionPipeline
from pipelines.ingestion.tasks.chunk import make_chunk_document_job
from pipelines.ingestion.tasks.index_chunks import make_index_chunks_job
from pipelines.ingestion.tasks.parse import make_parse_document_job
from pipelines.ingestion.tasks.profile import make_profile_document_job
from pipelines.ingestion.tasks.store_chunks import make_store_chunks_job


def _indexed_chunk_dict(
    document_id: str | None = None, chunk_id: str | None = None
) -> dict:
    chunk = DocumentChunk(
        content="hello world",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )
    if chunk_id is not None:
        chunk.id = UUID(chunk_id)
    if document_id is not None:
        chunk.document_id = UUID(document_id)
    indexed = IndexedChunk(chunk=chunk, embedding=[0.1, 0.2, 0.3])
    return indexed.to_dict()


def test_job_returns_stored_ids_not_full_indexed_chunks() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    data = _indexed_chunk_dict()

    result = job([data])

    assert result == [data["chunk"]["id"]]


def test_job_actually_stores_the_embedding_in_the_vector_store() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    data = _indexed_chunk_dict()

    job([data])

    stored = vector_store.get(UUID(data["chunk"]["id"]))
    assert stored.embedding == [0.1, 0.2, 0.3]


def test_job_stores_document_id_and_mime_type_as_metadata() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    document_id = str(uuid4())
    data = _indexed_chunk_dict(document_id=document_id)

    job([data])

    stored = vector_store.get(UUID(data["chunk"]["id"]))
    assert stored.metadata == {"document_id": document_id, "mime_type": "text/plain"}


def test_job_stores_none_document_id_when_chunk_has_none() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    data = _indexed_chunk_dict(document_id=None)

    job([data])

    stored = vector_store.get(UUID(data["chunk"]["id"]))
    assert stored.metadata["document_id"] is None


def test_job_handles_multiple_chunks_and_returns_all_their_ids() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    data_a = _indexed_chunk_dict(chunk_id=str(uuid4()))
    data_b = _indexed_chunk_dict(chunk_id=str(uuid4()))

    result = job([data_a, data_b])

    assert set(result) == {data_a["chunk"]["id"], data_b["chunk"]["id"]}
    assert vector_store.exists(UUID(data_a["chunk"]["id"])) is True
    assert vector_store.exists(UUID(data_b["chunk"]["id"])) is True


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    vector_store = InMemoryVectorStore(collection_name="chunks")
    job = make_store_chunks_job(vector_store)
    queue = DummyQueue(jobs={"store_chunks": job})
    data = _indexed_chunk_dict()

    handle = queue.dispatch("store_chunks", [data])

    assert handle.status == JobStatus.SUCCESS
    assert handle.result == [data["chunk"]["id"]]


def test_full_chain_profile_parse_chunk_index_store() -> None:
    # The realistic flow: profile -> parse -> chunk -> index_chunks ->
    # store_chunks, each dispatch feeding its (serialized) result into the
    # next, ending in a real (if in-memory) vector store.
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    indexer_registry = IndexerRegistry([BatchIndexer()])
    pipeline = IngestionPipeline(
        profiler_registry, parser_registry, chunker_registry, indexer_registry
    )
    vector_store = InMemoryVectorStore(collection_name="chunks")
    file_bytes = "Привет, мир! Это тестовый документ.".encode("utf-8")

    queue = DummyQueue(
        jobs={
            "profile_document": make_profile_document_job(pipeline),
            "parse_document": make_parse_document_job(pipeline),
            "chunk_document": make_chunk_document_job(pipeline),
            "index_chunks": make_index_chunks_job(pipeline),
            "store_chunks": make_store_chunks_job(vector_store),
        }
    )

    profile_handle = queue.dispatch("profile_document", file_bytes)
    assert profile_handle.status == JobStatus.SUCCESS

    parse_handle = queue.dispatch("parse_document", file_bytes, profile_handle.result)
    assert parse_handle.status == JobStatus.SUCCESS

    chunk_handle = queue.dispatch(
        "chunk_document", profile_handle.result, parse_handle.result
    )
    assert chunk_handle.status == JobStatus.SUCCESS

    index_handle = queue.dispatch("index_chunks", chunk_handle.result)
    assert index_handle.status == JobStatus.SUCCESS

    store_handle = queue.dispatch("store_chunks", index_handle.result)
    assert store_handle.status == JobStatus.SUCCESS

    stored_id = UUID(store_handle.result[0])
    assert vector_store.exists(stored_id) is True
    assert chunk_handle.result[0]["id"] == str(stored_id)
