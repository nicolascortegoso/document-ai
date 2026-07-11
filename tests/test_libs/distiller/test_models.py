from __future__ import annotations

from uuid import uuid4

from common.models.entry import Entry
from libs.distiller.models import GlossaryEntry


def test_glossary_entry_roundtrip_with_aliases() -> None:
    entry = GlossaryEntry(
        document_id=uuid4(),
        term="compressor",
        pages=[1, 3, 5],
        confidence=0.82,
        aliases=["compressor unit", "GPA"],
    )

    restored = GlossaryEntry.from_dict(entry.to_dict())

    assert restored == entry
    assert restored.aliases == ["compressor unit", "GPA"]


def test_glossary_entry_aliases_defaults_to_empty_list() -> None:
    entry = GlossaryEntry(
        document_id=uuid4(),
        term="turbine",
        pages=[2],
        confidence=0.5,
    )

    assert entry.aliases == []

    restored = GlossaryEntry.from_dict(entry.to_dict())
    assert restored.aliases == []


def test_glossary_entry_is_also_an_entry() -> None:
    entry = GlossaryEntry(
        document_id=uuid4(), term="valve", pages=[1], confidence=0.9
    )

    assert isinstance(entry, Entry)