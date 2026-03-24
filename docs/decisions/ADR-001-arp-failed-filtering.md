# ADR-001: ARP Unreachable-Status Filtering Strategy

**Date:** 2026-03-20
**Status:** Accepted
**Updated:** 2026-03-24 — added `incomplete` status (same semantics as `failed`)

## Context

ARP entries with `status: failed` were causing devices to incorrectly show as "home" in device tracking. The failed status means the router sent an ARP request but received no reply — the device is unreachable. The same applies to `status: incomplete`, which MikroTik uses when an ARP resolution is in progress but no reply has been received. However, ARP entries are also used for bridge-interface resolution in the device tracker coordinator's ping logic.

The initial fix (v2.3.6) filtered failed entries in `get_arp()`, but this broke bridge-interface lookups because the entries were removed from `ds["arp"]` entirely.

## Decision

Filter ARP unreachable-status entries in `async_process_host()` rather than in `get_arp()`. Unreachable entries remain in `ds["arp"]` for bridge-interface resolution but are excluded from the `arp_detected` set used for availability checks.

Specifically:
- `get_arp()` keeps all ARP entries regardless of status
- `async_process_host()` builds an `arp_detected` set excluding entries where `status` is in `{"failed", "incomplete"}`
- Host availability is determined by presence in `arp_detected`, not `ds["arp"]`

## Alternatives Considered

**1. Filter in `get_arp()` with a separate bridge cache**
Rejected — would require duplicating bridge data and keeping two ARP-like structures in sync.

**2. Add a `failed` flag to ARP entries instead of filtering**
Rejected — simpler to filter at the point of use (host processing) than to thread a flag through multiple consumers.

## Consequences

- Bridge-interface resolution continues to work for all hosts including unreachable ones
- Regression tests added to verify the filtering behaviour for both statuses
- Device tracker accurately reflects network reachability
