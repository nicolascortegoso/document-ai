from __future__ import annotations

from uuid import uuid4

from common.models.entry import Entry


def test_entry_roundtrip() -> None:
    document_id = uuid4()
    entry = Entry(document_id=document_id)

    restored = Entry.from_dict(entry.to_dict())

    assert restored == entry
    assert restored.document_id == document_id


def test_entry_id_is_auto_generated_and_unique() -> None:
    document_id = uuid4()
    entry_a = Entry(document_id=document_id)
    entry_b = Entry(document_id=document_id)

    assert entry_a.id != entry_b.id