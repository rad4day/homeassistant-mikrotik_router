"""Tests for update.py pure functions — version list generation."""

from packaging.version import Version

from custom_components.mikrotik_router.update import (
    generate_version_list,
    decrement_version,
)


# ---------------------------------------------------------------------------
# decrement_version
# ---------------------------------------------------------------------------


class TestDecrementVersion:
    def test_decrement_patch(self):
        """7.16.2 → 7.16.1"""
        result = decrement_version(Version("7.16.2"), Version("7.0"))
        assert result == Version("7.16.1")

    def test_decrement_patch_to_zero(self):
        """7.16.1 → 7.16.0"""
        result = decrement_version(Version("7.16.1"), Version("7.0"))
        assert result == Version("7.16.0")

    def test_decrement_rolls_minor(self):
        """7.16.0 → 7.15.999 (rolls minor when patch is 0)."""
        result = decrement_version(Version("7.16.0"), Version("7.0"))
        assert result == Version("7.15.999")

    def test_decrement_rolls_major(self):
        """7.0.0 → 6.999.999 (rolls major when minor is 0)."""
        result = decrement_version(Version("7.0.0"), Version("6.0"))
        assert result == Version("6.999.999")


# ---------------------------------------------------------------------------
# generate_version_list
# ---------------------------------------------------------------------------


class TestGenerateVersionList:
    def test_same_version(self):
        """Same start and end → single entry."""
        result = generate_version_list("7.16.0", "7.16.0")
        assert result == ["7.16.0"]

    def test_patch_range(self):
        """Short patch range generates correct list in reverse order."""
        result = generate_version_list("7.16.0", "7.16.2")
        assert result == ["7.16.2", "7.16.1", "7.16.0"]

    def test_start_included(self):
        """Start version is included in the list."""
        result = generate_version_list("7.16.1", "7.16.2")
        assert "7.16.1" in result
        assert "7.16.2" in result

    def test_reverse_order(self):
        """Versions are returned newest-first."""
        result = generate_version_list("7.16.0", "7.16.3")
        versions = [Version(v) for v in result]
        assert versions == sorted(versions, reverse=True)
