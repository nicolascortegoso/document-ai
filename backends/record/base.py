from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from backends.record.models import DocumentRecord


class DuplicateExternalIdError(Exception):
    """Raised by register() when a record already exists for external_id."""


class RecordNotFoundError(Exception):
    """Raised when no record exists for the given document_id or external_id."""


class RecordStore(ABC):
    """Abstract base for record store implementations.

    A sync ledger between an external document management system and this
    system's own processing state — not a primary document store. status
    and pipeline_name are both opaque str; this store has no knowledge of
    which pipelines exist or what status vocabulary each one uses.
    """

    @abstractmethod
    def register(self, external_id: str, checksum: str) -> DocumentRecord:
        """Create a new record, minting a fresh document_id.

        Raises DuplicateExternalIdError if a record already exists for
        external_id — not an upsert.
        """

    @abstractmethod
    def get(self, document_id: UUID) -> DocumentRecord:
        """Raises RecordNotFoundError if no record exists for document_id."""

    @abstractmethod
    def get_by_external_id(self, external_id: str) -> DocumentRecord:
        """Raises RecordNotFoundError if no record exists for external_id."""

    @abstractmethod
    def exists_by_external_id(self, external_id: str) -> bool:
        """Returns whether a record exists for external_id."""

    @abstractmethod
    def update_checksum(self, document_id: UUID, checksum: str) -> None:
        """Raises RecordNotFoundError if document_id has no record."""

    @abstractmethod
    def update_pipeline_status(
        self, document_id: UUID, pipeline_name: str, status: str
    ) -> None:
        """Targeted update — does not require reading and rewriting the
        whole record.

        Raises RecordNotFoundError if document_id has no record.
        """

    @abstractmethod
    def delete(self, document_id: UUID) -> None:
        """Remove a record by document_id. Idempotent — does not raise if
        document_id has no record.
        """
