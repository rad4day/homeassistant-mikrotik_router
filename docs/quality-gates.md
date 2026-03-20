# Quality Gates

## CI Tooling

| Gate | Tool | Status |
|------|------|--------|
| Format | Black | Migrate to Ruff (tracked) |
| Lint | flake8 | Migrate to Ruff (tracked) |
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

## Pre-commit Hooks

gitleaks, black, flake8, bandit, trailing-whitespace, end-of-file-fixer, check-yaml, no-commit-to-branch (master)

## Pre-PR Checklist

1. `pytest tests/ -v` — all green
2. `/simplify` on changed code
3. Silent-failure-hunter on changed files
4. Code review agent
5. README/info.md updated if behaviour changed
6. Branch up to date, working tree clean
7. PR targets jnctech fork
