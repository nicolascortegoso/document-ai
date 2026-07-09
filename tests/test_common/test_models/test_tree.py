from __future__ import annotations

from uuid import uuid4

import pytest

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.tree import DocumentTree, InvalidTreeNodeError, SummaryNode


def _chunk(page: int, content: str = "text") -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=page, page_end=page),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )


def test_empty_children_raises_invalid_tree_node_error() -> None:
    with pytest.raises(InvalidTreeNodeError):
        SummaryNode(content="summary", children=[], level=0)


def test_source_reference_with_chunk_children_spans_first_to_last() -> None:
    node = SummaryNode(
        content="summary",
        children=[_chunk(1), _chunk(2), _chunk(3)],
        level=0,
    )

    assert node.source_reference == SourceReference(page_start=1, page_end=3)


def test_source_reference_recurses_through_summary_node_children() -> None:
    # Two-level tree: leaf SummaryNodes wrap chunks, root wraps those.
    left = SummaryNode(content="left", children=[_chunk(1), _chunk(2)], level=1)
    right = SummaryNode(content="right", children=[_chunk(3), _chunk(4)], level=1)
    root = SummaryNode(content="root", children=[left, right], level=0)

    # No explicit tree-walking needed — root.source_reference reads
    # children[0]/children[-1].source_reference, which recurses naturally
    # since left/right are themselves SummaryNodes with their own computed
    # source_reference.
    assert root.source_reference == SourceReference(page_start=1, page_end=4)


def test_summary_node_roundtrip_with_chunk_children() -> None:
    node = SummaryNode(
        content="summary",
        children=[_chunk(1, "a"), _chunk(2, "b")],
        level=0,
    )

    restored = SummaryNode.from_dict(node.to_dict())

    assert restored == node
    assert all(isinstance(c, DocumentChunk) for c in restored.children)


def test_summary_node_roundtrip_with_summary_node_children() -> None:
    left = SummaryNode(content="left", children=[_chunk(1)], level=1)
    right = SummaryNode(content="right", children=[_chunk(2)], level=1)
    root = SummaryNode(content="root", children=[left, right], level=0)

    restored = SummaryNode.from_dict(root.to_dict())

    assert restored == root
    assert all(isinstance(c, SummaryNode) for c in restored.children)
    assert all(isinstance(gc, DocumentChunk) for c in restored.children for gc in c.children)


def test_document_tree_roundtrip_with_document_id() -> None:
    document_id = uuid4()
    tree = DocumentTree(
        root=SummaryNode(content="root", children=[_chunk(1)], level=0),
        mime_type=FileType.PLAIN_TEXT,
        document_id=document_id,
    )

    restored = DocumentTree.from_dict(tree.to_dict())

    assert restored == tree
    assert restored.document_id == document_id


def test_document_tree_document_id_defaults_to_none() -> None:
    tree = DocumentTree(
        root=SummaryNode(content="root", children=[_chunk(1)], level=0),
        mime_type=FileType.PLAIN_TEXT,
    )

    restored = DocumentTree.from_dict(tree.to_dict())

    assert restored.document_id is None