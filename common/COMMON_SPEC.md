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
```

Unpaginated formats (e.g. `.txt`) are modeled as one synthetic page
(`page_count=1`, `page_number=1`).

### Serialization

`to_dict()` / `from_dict()` on both classes. Capabilities serialize under a
`"capabilities"` key, keyed by class name; unknown capability names are
skipped on deserialization, not fatal.

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