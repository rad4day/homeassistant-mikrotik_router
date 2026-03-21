# ADR-002: New Device Discovery Without Log Spam

**Date:** 2026-03-20
**Status:** Proposed

## Context

New network devices discovered by the MikroTik router (e.g. a phone joining WiFi) do not appear as HA entities until HA is restarted. The `update_sensors` dispatcher signal was designed to trigger `_run_entity_setup_loop()` which iterates entity descriptions and adds missing entities.

In v2.3.6, re-enabling the dispatcher caused thousands of "does not generate unique IDs" log errors every 30 seconds because `_check_entity_exists()` doesn't guard against re-adding entities that already exist in `platform.entities`. The dispatcher was disabled in v2.3.8 to stop the log spam.

## Decision

**Not yet decided.** Two approaches are under evaluation:

### Option A: Track known UIDs in coordinator
- Maintain `self._known_uids[data_path]` as a set per data path
- Only fire `async_dispatcher_send("update_sensors")` when new UIDs appear that weren't in the previous set
- Pros: minimal changes, dispatcher only fires when needed
- Cons: adds state tracking to coordinator

### Option B: Fix `_check_entity_exists()` to be idempotent
- Guard against re-adding entities already present in `platform.entities`
- Pros: fixes the root cause, dispatcher can fire freely
- Cons: touches HA entity registration logic, needs careful testing

## Alternatives Considered

**Keep dispatcher disabled (current state)**
Acceptable as a workaround but means new devices require HA restart. Not ideal for a network monitoring integration.

## Consequences

- Tracked as ISS-260320-new-device-discovery
- Whichever option is chosen needs integration tests verifying entity creation without log errors
