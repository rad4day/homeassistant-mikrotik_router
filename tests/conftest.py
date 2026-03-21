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
        self._accounting_enabled = False
        self._local_traffic_enabled = False
        self._snapshot_time_diff = 0

    def connect(self):
        return True

    def disconnect(self):
        pass

    def query(self, path, command=None, args=None):
        key = (path, command) if command else path
        return self.responses.get(key, [])

    def execute(self, path, command, param=None, value=None, options=None):
        pass

    def set_value(self, path, param, value, mod_param, mod_value):
        return True

    def is_accounting_and_local_traffic_enabled(self):
        return self._accounting_enabled, self._local_traffic_enabled

    def take_client_traffic_snapshot(self, accounting):
        return self._snapshot_time_diff
