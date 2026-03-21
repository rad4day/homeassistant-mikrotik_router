# ADR-003: Ruff Replaces Black+flake8

**Date:** 2026-03-20
**Status:** Accepted

## Context

The codebase used Black for formatting and flake8 for linting — two separate tools with separate configs. The HA ecosystem and modern Python projects are converging on Ruff, which provides both formatting and linting in a single tool with significantly faster execution.

CI was also using unpinned tool versions, and pre-commit hooks referenced Black+flake8.

## Decision

Replace Black and flake8 with Ruff for both linting and formatting. Use Ruff's default rules (which include pyflakes F-rules and pycodestyle E-rules that flake8 was checking).

Implementation:
- CI (`ci.yml`) uses `ruff check` and `ruff format --check`
- `requirements_dev.txt` includes `ruff` for local development
- `.devcontainer/devcontainer.json` installs the Ruff VS Code extension
- Pre-commit hooks updated to reference `ruff` instead of `black`+`flake8`

## Alternatives Considered

**1. Keep Black+flake8**
Rejected — two tools to maintain, slower CI, diverging from HA ecosystem norms.

**2. Use Black+Ruff (Ruff for linting only)**
Rejected — Ruff's formatter is Black-compatible and eliminates the need for Black entirely.

## Consequences

- Single tool for lint+format reduces CI time and developer cognitive load
- 43 unused imports (F401) and 1 type comparison (E721) found and fixed during migration
- 4 files reformatted (minor whitespace differences from Black)
- `pyproject.toml` with Ruff config is a future enhancement (currently uses defaults)
