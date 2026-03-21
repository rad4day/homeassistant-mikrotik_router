# ADR-004: Blocking I/O Wrapped with async_add_executor_job

**Date:** 2026-03-20
**Status:** Accepted

## Context

The MikroTik integration used `librouteros` (a synchronous library) for all API communication. Several platform modules (`switch.py`, `button.py`, `update.py`, `config_flow.py`) called synchronous API methods directly from async HA callbacks (`async_turn_on`, `async_press`, `async_install`, `async_step_user`). This violated HA's async architecture rules and caused the event loop to block during network I/O, freezing the HA UI for the duration of each API call.

The coordinator's `_async_update_data` already ran blocking API calls via `async_add_executor_job`, but action-triggered calls (switches, buttons, updates) did not.

## Decision

Wrap all synchronous `librouteros` API calls (`api.query`, `api.execute`, `api.run_script`, `api.set_value`, `api.connect`) in `self.hass.async_add_executor_job()` when called from async context. Specifically:

- `switch.py`: All `async_turn_on`/`async_turn_off` methods delegate `set_value`/`execute` to executor
- `button.py`: `async_press` delegates `run_script` to executor
- `update.py`: `async_install` delegates `execute` to executor for both RouterOS and RouterBOARD updates
- `config_flow.py`: `async_step_user` delegates `api.connect()` to executor

The coordinator's existing pattern of `await self.hass.async_add_executor_job(self.get_*)` is the model — platform actions now follow the same pattern.

## Alternatives Considered

**1. Migrate to an async MikroTik library**
Rejected — no mature async RouterOS library exists. `librouteros` is the standard and is well-maintained. The wrapping approach is the HA-recommended pattern for sync libraries.

**2. Run all API calls through the coordinator**
Rejected — action calls (toggle switch, press button) need immediate execution, not deferred to the next coordinator update cycle. The coordinator pattern is for polling, not imperative actions.

## Consequences

- HA UI no longer freezes during switch toggles, button presses, or firmware updates
- All blocking I/O is confined to the executor thread pool
- Dead synchronous `turn_on`/`turn_off` stubs in `switch.py` were removed (they were unreachable)
- Pattern is consistent: if it touches `self.api.*`, it runs in executor when called from async
