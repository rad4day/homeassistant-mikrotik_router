"""Fixtures for Mikrotik Router tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in all tests."""
    yield


class MockMikrotikAPI:
    """Minimal MikrotikAPI mock that dispatches query() calls by path/command."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.error = ""
        self.disable_health = False
        self.client_traffic_last_run = None

    def connect(self):
        return True

    def disconnect(self):
        pass

    def query(self, path, command=None, args=None):
        key = (path, command) if command else path
        return self.responses.get(key, [])
