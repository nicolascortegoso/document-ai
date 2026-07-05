from __future__ import annotations

CAPABILITY_REGISTRY: dict[str, type] = {}


def register_capability(cls: type) -> type:
    """Decorator for registering capability dataclasses (e.g. a future
    ScanProfile, TabularProfile) so PageProfile.from_dict can reconstruct
    them from serialized data.

    Empty for now — plain text has no capabilities to attach. When a new
    format needs one, define the dataclass (in common/models/, or in an
    external client package) and decorate it:

        @register_capability
        @dataclass
        class ScanProfile:
            scan_format: ScanFormat = ScanFormat.UNKNOWN
            ...
    """
    CAPABILITY_REGISTRY[cls.__name__] = cls
    return cls