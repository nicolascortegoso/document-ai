[← README](../README.md)

# `common/` Module Spec

## Purpose

Lowest layer of the monorepo (`common/` → `libs/` → `backends/` →
`pipelines/` → `services/`). Holds data models and vocabulary shared across
every layer.

**Hard constraint:** `common/` must not import from `libs/`, `backends/`,
`pipelines/`, or `services/`.

## Scope

Ships `.txt` processing. Can be extended to support scanned documents,
spreadsheets, DOCX, and other formats without redesigning this layer — see
[Extensibility](#extensibility).

## File Layout

```
common/
  enums.py
  models/
    __init__.py
    document.py
    parsed.py
    chunk.py
    tree.py
    capability_registry.py
```

## `enums.py`

```python
class FileType(str, Enum):
    PLAIN_TEXT = "text/plain"
    UNKNOWN = "unknown"
```

- Values are MIME strings, so `FileType(detected_mime)` works directly
- `UNKNOWN` is the explicit fallback for unclassified files
- New formats are added as new members

## `models/document.py`

### `PageProfile`

```python
@dataclass
class PageProfile:
    page_number: int
    has_text: bool
    has_images: bool
    has_tables: bool
    languages: list[str] = field(default_factory=list)
    _capabilities: dict[type, object] = field(default_factory=dict, repr=False)
```

Core fields must be populatable by every format. Format-specific data (scan,
layout, tabular) attaches via capabilities instead of new fields.

`languages`: a page can have more than one. Empty list = none identified;
index 0 = dominant language when ranked. Nothing in `common/` populates it.

**Capability API:**

| Method | Purpose |
|---|---|
| `add(capability)` | Attach a capability, keyed by type. Chainable. |
| `get(capability_type)` | Retrieve by type, or `None`. |
| `has(capability_type)` | Check presence. |

Stored as `dict[type, object]` rather than fields or a list — type-safe
retrieval, no combinatorial subclassing, and a new capability requires no
change to `PageProfile`.

### `DocumentProfile`

```python
@dataclass
class DocumentProfile:
    mime_type: FileType
    page_count: int
    pages: list[PageProfile] = field(default_factory=list)
    document_id: UUID | None = None
```

Unpaginated formats (e.g. `.txt`) are modeled as one synthetic page
(`page_count=1`, `page_number=1`).

`document_id` is `None` until the document is registered somewhere that
assigns one — nothing in `common/` generates it. Not auto-generated via a
default factory: the ID is expected to come from whoever registers the
document (e.g. a future `DocumentService.register()`, generating it before
profiling even runs) and get threaded through from there, not invented
independently at each stage.

### Serialization

`to_dict()` / `from_dict()` on both classes. Capabilities serialize under a
`"capabilities"` key, keyed by class name; unknown capability names are
skipped on deserialization, not fatal.

## `models/parsed.py`

```python
@dataclass
class ParsedPage:
    page_number: int
    text: str

@dataclass
class ParsedDocument:
    pages: list[ParsedPage]
```

The output of parsing — text extracted per page, keeping page structure
rather than collapsing it into one string. Lives in `common/`, not a
downstream orchestration module, for the same reason `PageProfile`/
`DocumentProfile` do: it's document content, usable by any layer, not
orchestration-internal bookkeeping. Same `to_dict()`/`from_dict()`
convention as `document.py`.

## `models/chunk.py`

```python
@dataclass
class SourceReference:
    page_start: int
    page_end: int

@dataclass
class DocumentChunk:
    content: str
    source_reference: SourceReference
    mime_type: FileType
    strategy: str
    id: UUID = field(default_factory=uuid4)
    document_id: UUID | None = None
```

The output of chunking. `SourceReference` preserves which
page(s) a chunk came from — required for citation-grounded answers.
`mime_type` travels with the chunk (denormalized from `DocumentProfile`) so
a retrieval hit is self-contained without a join back to the document.
`strategy` records which chunking strategy produced it, for debugging and
future strategy comparison. `id` is auto-generated (`default_factory=uuid4`)
since it identifies the chunk itself; `document_id` is not — it's `None`
until threaded in from whoever registers the document, same convention as
`DocumentProfile.document_id`.

## `models/tree.py`

```python
@dataclass
class SummaryNode:
    content: str
    children: list[DocumentChunk | SummaryNode]
    level: int
    id: UUID = field(default_factory=uuid4)

    @property
    def source_reference(self) -> SourceReference:
        return SourceReference(
            page_start=self.children[0].source_reference.page_start,
            page_end=self.children[-1].source_reference.page_end,
        )

@dataclass
class DocumentTree:
    root: SummaryNode
    mime_type: FileType
    document_id: UUID | None = None
```

The output of merging — the inverse of chunking:
`DocumentChunk`s aggregated bottom-up into increasingly general summaries.

**Reuses `DocumentChunk` as the tree's leaf type directly**, rather than
wrapping it — `children: list[DocumentChunk | SummaryNode]` mixes both.
Since both types expose `.source_reference` (one stored, one computed),
`SummaryNode.source_reference` needs no explicit tree-walking: reading
`children[0].source_reference` / `children[-1].source_reference` recurses
naturally through Python's own attribute access, regardless of whether that
child is a leaf or another internal node.

`SummaryNode.content` is always a reduced representation — never a raw
copy of a child's content, including the trivial single-chunk-document
case. `DocumentTree.root` is unconditionally a `SummaryNode`,
never a bare `DocumentChunk`, so nothing downstream needs to branch on the
root's type.

**Defended construction:** `SummaryNode.__post_init__` raises
`InvalidTreeNodeError` if `children` is empty. Splitting the leaf case out
into `DocumentChunk` (which has no `children` field to misuse) removes the
"both chunk and children set" / "neither set" ambiguity a single combined
node type would otherwise need to guard against — there's only one invalid
state left to defend here, not several.

Deliberately **not** validated here: that `children` are in sequential
document order. Whether that ordering matters, and how it's upheld, is a
property of how a given merging strategy groups chunks — a strategy that
clusters by similarity rather than position could legitimately produce a
`SummaryNode` with out-of-order children by design. `common/` shouldn't
bake one strategy's assumption into a model every strategy has to produce;
upholding order, where it matters, is left to whatever constructs the tree.

## `models/capability_registry.py`

```python
CAPABILITY_REGISTRY: dict[str, type] = {}

def register_capability(cls: type) -> type:
    CAPABILITY_REGISTRY[cls.__name__] = cls
    return cls
```

Maps capability class names to types for `PageProfile.from_dict()`. Empty in
this release — plain text has no capabilities.

## Extensibility

- **New capability** (e.g. `ScanProfile`): define the dataclass, decorate
  with `@register_capability`. No change to `document.py`.
- **New format**: handled by a downstream implementation. No change
  to `common/models/` unless it needs a new capability.
- `common/models/` itself only changes if a field proves universal across
  every format and wasn't anticipated.