# ADR-005: Lock Context Managers Replace Manual acquire/release

**Date:** 2026-03-20
**Status:** Accepted

## Context

`mikrotikapi.py` used manual `self.lock.acquire()` / `self.lock.release()` calls in `connect()`, `query()`, `execute()`, and `run_script()`. The `run_script()` method had a critical deadlock bug: the `release()` call was inside a `try` block but not in a `finally` clause. Any exception during script execution would leave the lock permanently acquired, causing all subsequent API calls to hang indefinitely.

This was a production-impacting bug — once triggered, the integration would stop updating and require an HA restart.

## Decision

Replace all manual `self.lock.acquire()` / `self.lock.release()` pairs with `with self.lock:` context manager blocks. This guarantees lock release regardless of how the block exits (normal return, exception, or early return).

Applied to all four methods in `MikrotikAPI`:
- `connect()` — protects connection establishment
- `query()` — protects read operations
- `execute()` — protects write operations
- `run_script()` — protects script execution (the original deadlock site)

## Alternatives Considered

**1. Add `finally` clauses to existing acquire/release pattern**
Rejected — `with self.lock:` is strictly superior: shorter, impossible to get wrong, and the Pythonic idiom. Manual acquire/release with finally is more code for the same guarantee.

**2. Remove locking entirely (rely on HA's single-threaded executor)**
Rejected — while HA runs most executor jobs sequentially, there's no guarantee against concurrent access from platform actions (switch toggles) and coordinator updates. The lock is a correct safety measure.

## Consequences

- Deadlock in `run_script()` is permanently fixed — lock is always released
- All four API methods use identical locking pattern
- No behavioral change for non-error paths
- Regression test added: verifies lock is released after `run_script()` raises an exception
