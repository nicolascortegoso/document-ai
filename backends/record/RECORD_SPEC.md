[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Record Paradigm

## Overview

Abstracts a sync ledger between an external document management system
(e.g. paperless-ngx) and this system's own processing state — not a
primary document store. `InMemoryRecordStore` ships as the default.

`status` and `pipeline_name` are both opaque `str`, not enums. Each
pipeline defines and interprets its own status values.

## Interface Contract

### `RecordStore` ABC

| Method | Signature | Description |
|---|---|---|
| `register` | `(external_id: str, checksum: str) -> DocumentRecord` | Create a new record, minting a fresh `document_id`. Raises `DuplicateExternalIdError` if a record already exists for `external_id`. |
| `get` | `(document_id: UUID) -> DocumentRecord` | Raises `RecordNotFoundError` if no record exists for `document_id`. |
| `get_by_external_id` | `(external_id: str) -> DocumentRecord` | Raises `RecordNotFoundError` if no record exists for `external_id`. |
| `exists_by_external_id` | `(external_id: str) -> bool` | Returns whether a record exists for `external_id`. |
| `update_checksum` | `(document_id: UUID, checksum: str) -> None` | Raises `RecordNotFoundError` if `document_id` has no record. |
| `update_pipeline_status` | `(document_id: UUID, pipeline_name: str, status: str) -> None` | Raises `RecordNotFoundError` if `document_id` has no record. |
| `delete` | `(document_id: UUID) -> None` | Idempotent — does not raise if `document_id` has no record. |

Querying by status (e.g. "all documents where `ingestion` failed") is
deferred, not part of this release.

`DuplicateExternalIdError` and `RecordNotFoundError` are both defined
alongside the ABC in `base.py`.

### `DocumentRecord`

Defined in `backends/record/models.py`.

| Field | Type | Description |
|---|---|---|
| `document_id` | `UUID` | Minted by `register()`. |
| `external_id` | `str` | The paperless-ngx (or equivalent) document id. |
| `checksum` | `str` | Opaque hash value. |
| `pipeline_statuses` | `dict[str, str]` | Keyed by pipeline name. |

## `InMemoryRecordStore`

Dict-backed, in-process. Not thread-safe, not persisted across restarts —
for testing and local development only.

## Folder Structure

```
backends/
└── record/
    ├── __init__.py
    ├── base.py                # RecordStore ABC, DuplicateExternalIdError, RecordNotFoundError
    ├── models.py               # DocumentRecord
    └── implementations/
        ├── __init__.py
        └── memory.py            # InMemoryRecordStore
```