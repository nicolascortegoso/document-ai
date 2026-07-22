from __future__ import annotations

from uuid import UUID, uuid4

from backends.record.base import (
    DuplicateExternalIdError,
    RecordNotFoundError,
    RecordStore,
)
from backends.record.models import DocumentRecord


class InMemoryRecordStore(RecordStore):
    """Dict-backed, in-process. Not thread-safe, not persisted across
    restarts — for testing and local development only.
    """

    def __init__(self) -> None:
        self._records: dict[UUID, DocumentRecord] = {}
        self._external_id_index: dict[str, UUID] = {}

    def register(self, external_id: str, checksum: str) -> DocumentRecord:
        if external_id in self._external_id_index:
            raise DuplicateExternalIdError(
                f"A record already exists for external_id {external_id!r}."
            )
        document_id = uuid4()
        record = DocumentRecord(
            document_id=document_id, external_id=external_id, checksum=checksum
        )
        self._records[document_id] = record
        self._external_id_index[external_id] = document_id
        return record

    def get(self, document_id: UUID) -> DocumentRecord:
        try:
            return self._records[document_id]
        except KeyError:
            raise RecordNotFoundError(
                f"No record found for document_id {document_id!r}."
            ) from None

    def get_by_external_id(self, external_id: str) -> DocumentRecord:
        try:
            document_id = self._external_id_index[external_id]
        except KeyError:
            raise RecordNotFoundError(
                f"No record found for external_id {external_id!r}."
            ) from None
        return self._records[document_id]

    def exists_by_external_id(self, external_id: str) -> bool:
        return external_id in self._external_id_index

    def update_checksum(self, document_id: UUID, checksum: str) -> None:
        record = self.get(document_id)
        record.checksum = checksum

    def update_pipeline_status(
        self, document_id: UUID, pipeline_name: str, status: str
    ) -> None:
        record = self.get(document_id)
        record.pipeline_statuses[pipeline_name] = status

    def delete(self, document_id: UUID) -> None:
        record = self._records.pop(document_id, None)
        if record is not None:
            self._external_id_index.pop(record.external_id, None)
