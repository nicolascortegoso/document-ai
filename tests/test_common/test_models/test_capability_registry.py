from __future__ import annotations

from dataclasses import dataclass

from common.models.document import PageProfile
from common.models.capability_registry import CAPABILITY_REGISTRY, register_capability


def test_register_capability_adds_to_registry_by_class_name() -> None:
    @register_capability
    @dataclass
    class _ExampleCapability:
        value: str

    try:
        assert CAPABILITY_REGISTRY["_ExampleCapability"] is _ExampleCapability
    finally:
        del CAPABILITY_REGISTRY["_ExampleCapability"]


def test_registered_capability_round_trips_through_page_profile() -> None:
    @register_capability
    @dataclass
    class _ExampleCapability:
        value: str

    try:
        page = PageProfile(
            page_number=1, has_text=True, has_images=False, has_tables=False
        )
        page.add(_ExampleCapability(value="hello"))

        restored = PageProfile.from_dict(page.to_dict())

        assert restored.get(_ExampleCapability) == _ExampleCapability(value="hello")
    finally:
        del CAPABILITY_REGISTRY["_ExampleCapability"]