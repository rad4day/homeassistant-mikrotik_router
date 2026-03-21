# Quality Gates

## CI Tooling

| Gate | Tool | Status |
|------|------|--------|
| Format | Ruff | Active |
| Lint | Ruff | Active |
| Security | Bandit + gitleaks | Active |
| Tests | pytest + pytest-homeassistant-custom-component | Active |
| Coverage | Codecov + SonarCloud | Active |
| HACS | hassfest + hacs/action | Active |

## SonarCloud

- **Project:** `jnctech_homeassistant-mikrotik_router`
- **Org:** `jnctech-homeassistant-mikrotik-router`

### Quality Targets (non-negotiable)

| Metric | Target |
|--------|--------|
| Reliability | Grade A |
| Security | Grade A |
| Maintainability | Grade A |
| Cognitive complexity | ≤15 per function |
| New code coverage | ≥80% |
| Duplication | <3% (new code) |

### Exclusions (see `sonar-project.properties`)
- **Coverage:** platform wiring files, pure data descriptors, const, exceptions
- **CPD:** `sensor_types.py`, `coordinator.py`, `tests/` (intentional structural repetition)

## Local Development (Devcontainer)

1. Open the repo in VS Code
2. When prompted, select **Reopen in Container** (or use the command palette: `Dev Containers: Reopen in Container`)
3. The container installs all deps from `requirements_dev.txt` automatically
4. Run tests: `pytest tests/ -v --tb=short`
5. Run with coverage: `pytest -v --cov=custom_components/mikrotik_router --cov-report=term-missing`
6. Lint: `ruff check custom_components/mikrotik_router tests`
7. Format: `ruff format custom_components/mikrotik_router tests`

## Pre-commit Hooks

gitleaks, ruff, bandit, trailing-whitespace, end-of-file-fixer, check-yaml, no-commit-to-branch (master)

## Pre-PR Checklist

1. `pytest tests/ -v` — all green
2. `/simplify` on changed code
3. Silent-failure-hunter on changed files
4. Code review agent
5. **Docs audit:**
   - README/info.md version and feature list match code
   - CHANGE-REGISTER.md has CR entry for this branch
   - ISSUES.md statuses updated for resolved/progressed issues
   - ADR created if decision changes data format, entity identity, API contract, or migration
   - architecture.md updated if new patterns or structural changes introduced
6. Branch up to date, working tree clean
7. PR targets jnctech fork
