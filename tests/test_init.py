"""Tests for Mikrotik Router __init__.py — lifecycle functions."""

from unittest.mock import MagicMock

import pytest

from homeassistant.const import CONF_VERIFY_SSL

from custom_components.mikrotik_router import (
    async_migrate_entry,
    async_remove_config_entry_device,
)
from custom_components.mikrotik_router.const import DEFAULT_VERIFY_SSL


# ---------------------------------------------------------------------------
# async_migrate_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_migrate_entry_v1_to_v2_adds_verify_ssl():
    """Version 1 entry gets CONF_VERIFY_SSL injected and bumped to version 2."""
    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.version = 1
    config_entry.minor_version = 0
    config_entry.data = {"host": "10.0.0.1", "username": "admin"}

    result = await async_migrate_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_called_once()
    call_kwargs = hass.config_entries.async_update_entry.call_args
    new_data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
    assert new_data[CONF_VERIFY_SSL] == DEFAULT_VERIFY_SSL
    assert call_kwargs.kwargs.get("version") or call_kwargs[1].get("version") == 2


@pytest.mark.asyncio
async def test_migrate_entry_v2_is_noop():
    """Version 2 entry is already current — no update call."""
    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.version = 2
    config_entry.minor_version = 0
    config_entry.data = {"host": "10.0.0.1", CONF_VERIFY_SSL: False}

    result = await async_migrate_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_not_called()


@pytest.mark.asyncio
async def test_migrate_entry_preserves_existing_data():
    """Migration preserves all existing config data while adding verify_ssl."""
    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.version = 1
    config_entry.minor_version = 0
    config_entry.data = {
        "host": "10.0.0.1",
        "username": "admin",
        "password": "secret",
    }

    await async_migrate_entry(hass, config_entry)

    call_kwargs = hass.config_entries.async_update_entry.call_args
    new_data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
    assert new_data["host"] == "10.0.0.1"
    assert new_data["username"] == "admin"
    assert new_data["password"] == "secret"
    assert CONF_VERIFY_SSL in new_data


# ---------------------------------------------------------------------------
# async_remove_config_entry_device
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_config_entry_device_returns_true():
    """Device removal always succeeds."""
    hass = MagicMock()
    config_entry = MagicMock()
    device_entry = MagicMock()

    result = await async_remove_config_entry_device(hass, config_entry, device_entry)
    assert result is True
