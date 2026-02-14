# Release Plan: v2.2.1 — OptionsFlow HA 2025.12+ Compatibility Fix

## Release Summary

Bugfix release to restore compatibility with Home Assistant 2025.12+ by updating the OptionsFlow implementation to use `OptionsFlowWithConfigEntry`.

---

## Pre-Release Checklist

### 1. Merge the Refined Fix into Master

The branch `claude/fix-hacs-wheel-error-2KYA0` contains the refined fix (`OptionsFlowWithConfigEntry`) and unit tests, but it also includes artifacts that should NOT be in the release (a pre-built zip file, version bump to `0.7.0`).

**Action items:**

- [ ] Cherry-pick the config_flow refinement from `c54b209` onto master (or manually apply the 3-line diff)
- [ ] Cherry-pick the test infrastructure from `c54b209` (test files only)
- [ ] Do NOT merge `04d1283` (version 0.7.0 bump) or `e7240a6` (pre-built zip) — these are testing artifacts

**The actual diff to apply to master's `config_flow.py` is minimal (3 changes):**

```diff
-from homeassistant.config_entries import ConfigFlow, OptionsFlow
+from homeassistant.config_entries import ConfigFlow, OptionsFlowWithConfigEntry

-        return MikrotikControllerOptionsFlowHandler()
+        return MikrotikControllerOptionsFlowHandler(config_entry)

-class MikrotikControllerOptionsFlowHandler(OptionsFlow):
+class MikrotikControllerOptionsFlowHandler(OptionsFlowWithConfigEntry):
     """Handle options."""

     async def async_step_init(self, user_input=None):
         """Manage the options."""
-        self.options = dict(self.config_entry.options)
         return await self.async_step_basic_options(user_input)
```

### 2. Update Version Number

- [ ] Set `version` in `manifest.json` to `"2.2.1"`

### 3. Update Fork-Specific References

The release workflow and release notes generator reference the upstream repo. These need updating for the jnctech fork:

- [ ] **`.github/workflows/release.yml`** — Update hardcoded paths from `homeassistant-mikrotik_router` to match actual repo checkout path (use `${{ github.workspace }}` instead)
- [ ] **`.github/generate_releasenotes.py`** — Change `tomaae/homeassistant-mikrotik_router` to `jnctech/homeassistant-mikrotik_router` (lines 61, 82, 117)
- [ ] **`.github/generate_releasenotes.py`** — Update badge URLs in the `BODY` template (line 28)
- [ ] **`manifest.json`** — Update `documentation` and `issue_tracker` URLs to point to jnctech fork

### 4. Run Tests

- [ ] Run unit tests: `pytest tests/ -v`
- [ ] Verify HACS validation passes (hacs.yml workflow)
- [ ] Verify hassfest validation passes (ci.yml workflow)

### 5. Verify the Fix Manually

- [ ] Install in a HA 2025.12+ instance
- [ ] Open Configure dialog — should load without error
- [ ] Change an option and save — should persist correctly
- [ ] Verify existing sensor data is unaffected

---

## Release Steps

### Step 1: Apply Changes to Master

```bash
# On master branch, apply the refined OptionsFlowWithConfigEntry fix
git checkout master

# Apply the config_flow.py refinement
# (edit config_flow.py with the 3-line change shown above)

# Copy test infrastructure from the branch
git checkout origin/claude/fix-hacs-wheel-error-2KYA0 -- \
  custom_components/__init__.py \
  pytest.ini \
  requirements_test.txt \
  tests/__init__.py \
  tests/conftest.py \
  tests/test_config_flow.py

# Update manifest.json version
# Change "version": "0.0.0" to "version": "2.2.1"

# Commit
git add -A
git commit -m "Prepare v2.2.1 release: OptionsFlowWithConfigEntry fix + tests"
```

### Step 2: Update Release Infrastructure for Fork

```bash
# Update generate_releasenotes.py repo references
# Update release.yml paths
# Update manifest.json URLs
git commit -m "Update release infrastructure for jnctech fork"
```

### Step 3: Tag and Push

```bash
git tag v2.2.1
git push origin master --tags
```

### Step 4: Create GitHub Release

```bash
gh release create v2.2.1 \
  --title "Mikrotik Router v2.2.1" \
  --notes "## Changes

- Fix 500 error on Configure dialog for Home Assistant 2025.12+
- Switch OptionsFlow to OptionsFlowWithConfigEntry for cross-version compatibility
- Remove deprecated CONN_CLASS_LOCAL_POLL import
- Add unit tests for config flow and options flow
- Add .gitignore for __pycache__ exclusion

## Compatibility

- Minimum Home Assistant: 2024.3.0
- Tested with: HA 2025.12+
- RouterOS: v6.43+ / v7.1+"
```

The release workflow will automatically:
1. Create `mikrotik_router.zip` from `custom_components/mikrotik_router/`
2. Attach it to the release
3. Generate formatted release notes (if `generate_releasenotes.py` is updated)

### Step 5: Verify HACS Distribution

- [ ] Confirm the release appears in HACS
- [ ] Confirm `mikrotik_router.zip` is attached to the release
- [ ] Test a fresh HACS install from the release

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `OptionsFlowWithConfigEntry` not available | Very Low | Min HA version is 2024.3.0, class available since 2024.3 |
| Options not persisting | Low | Unit test `test_options_flow_complete` validates this |
| Regression on older HA | Low | `OptionsFlowWithConfigEntry` is backward-compatible to HA 2024.3 |
| Release zip missing | Medium | Verify release.yml paths are correct for fork |

---

## Post-Release

- [ ] Monitor GitHub issues for any regression reports
- [ ] Consider syncing future upstream changes from tomaae
- [ ] Update HACS default repository listing if applicable
