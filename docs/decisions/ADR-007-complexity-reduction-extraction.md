# ADR-007: Cognitive Complexity Reduction via Helper Extraction

**Date:** 2026-03-21
**Status:** Accepted

## Context

SonarCloud flagged 14 functions exceeding the ≤15 cognitive complexity threshold. The worst offender, `async_process_host()`, had a complexity of 136. These functions were inherited from upstream and had grown organically over time. The complexity made them difficult to test, review, and modify safely.

## Decision

Reduce complexity by extracting focused helper methods from large functions. Each helper handles one responsibility and is independently testable. The extraction follows these principles:

1. **Pure extraction** — no behavioral changes. The original call sequence and mutation patterns are preserved exactly.
2. **Naming convention** — private helpers prefixed with `_` for internal-only methods, no prefix for cross-module helpers (e.g., `copy_attrs`).
3. **Return values over mutation** — where possible, helpers return values rather than mutating state (e.g., `_merge_capsman_hosts()` returns a `detected` dict).
4. **Class constants for data** — large inline lists (SFP monitor vals, copper monitor vals, PoE vals, host defaults) extracted to class-level constants.
5. **Static methods for pure logic** — functions that don't need `self` are `@staticmethod` (e.g., `_add_traffic_bytes`).

### Functions Refactored

| Function | Before | After | Helpers Extracted |
|----------|--------|-------|-------------------|
| `async_process_host()` | 136 | ~10 | 11 helpers |
| `_async_update_data()` | 65 | ~15 | 2 helpers + loop tables |
| `process_accounting()` | 48 | ~10 | 4 helpers |
| `get_interface()` | 27 | ~10 | 1 helper + 3 class constants |
| `_skip_sensor()` | 23 | ~5 | 4 predicate functions |
| `extra_state_attributes` | 21 | ~5 | Reuse `copy_attrs` |
| `from_entry_bool()` | 18 | ~8 | `_traverse_entry` + frozensets |

## Alternatives Considered

1. **Splitting coordinator.py into modules** — Higher impact, higher risk. Would require changing import paths across the codebase. Better done as a separate initiative.
2. **Inlining complex conditions** — Would reduce measured complexity but not actual cognitive load. Rejected as cosmetic.
3. **Rewriting with different data structures** — Would change behavior and risk regressions. Out of scope for a complexity-only PR.

## Consequences

- **Positive:** Each function is now independently testable. 58 new tests cover extracted helpers. SonarCloud cognitive complexity gates should pass.
- **Positive:** Future modifications to host processing, accounting, or interface monitoring can target specific helpers without understanding the full function.
- **Trade-off:** More methods means more indirection. Developers must follow the call chain through helpers. Mitigated by clear naming and docstrings.
- **Constraint:** Future extractions should follow the same pattern — pure extraction, no behavioral changes, with tests for each new helper.
