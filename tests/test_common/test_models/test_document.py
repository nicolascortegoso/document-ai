from __future__ import annotations

from common.enums import FileType
from common.models.document import DocumentProfile, PageProfile


def test_document_profile_roundtrip_with_no_capabilities() -> None:
    profile = DocumentProfile(
        mime_type=FileType.PLAIN_TEXT,
        page_count=1,
        pages=[
            PageProfile(
                page_number=1,
                has_text=True,
                has_images=False,
                has_tables=False,
                languages=["ru", "en"],
            )
        ],
    )

    restored = DocumentProfile.from_dict(profile.to_dict())

    assert restored == profile


def test_page_profile_capability_api() -> None:
    page = PageProfile(
        page_number=1, has_text=True, has_images=False, has_tables=False
    )

    assert page.has(dict) is False
    assert page.get(dict) is None

    marker = {"example": "capability"}
    page.add(marker)

    assert page.has(dict) is True
    assert page.get(dict) is marker


def test_unknown_capability_is_skipped_not_fatal_on_deserialize() -> None:
    data = {
        "page_number": 1,
        "has_text": True,
        "has_images": False,
        "has_tables": False,
        "languages": [],
        "capabilities": {"SomeUnregisteredCapability": {"foo": "bar"}},
    }

    # Should not raise, even though "SomeUnregisteredCapability" was never
    # registered via @register_capability.
    restored = PageProfile.from_dict(data)

    assert restored.page_number == 1
    assert restored._capabilities == {}