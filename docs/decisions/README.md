# Architecture Decision Records

Lightweight records of key design decisions for mikrotik_router HACS integration.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](ADR-001-arp-failed-filtering.md) | ARP Failed-Status Filtering Strategy | Accepted |
| [ADR-002](ADR-002-dispatcher-new-devices.md) | New Device Discovery Without Log Spam | Proposed |
| [ADR-003](ADR-003-ruff-migration.md) | Ruff Replaces Black+flake8 | Accepted |

## Template

```markdown
# ADR-NNN: Title

**Date:** YYYY-MM-DD
**Status:** Accepted | Superseded by ADR-NNN | Deprecated

## Context
What problem or need prompted this decision?

## Decision
What did we decide, and what are the key design choices?

## Alternatives Considered
What other approaches were evaluated and why were they rejected?

## Consequences
What are the trade-offs, risks, and follow-on constraints?
```

## Notes

- ADRs are **immutable once accepted** — never edit a decision after the fact. If the decision changes, create a new ADR marked "Supersedes ADR-NNN" and update the old one to "Superseded by ADR-NNN".
- ADRs live alongside the code — check `docs/ISSUES.md` for tactical issues that may eventually warrant an ADR.
- For cross-project patterns, see `~/Code/develop/homelab-docs/` (future: extract template there).
