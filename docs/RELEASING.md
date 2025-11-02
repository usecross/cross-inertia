# Releasing Cross-Inertia

This guide explains how to release a new version of Cross-Inertia to PyPI.

## Quick Start

1. Create your PR with changes
2. Add a `RELEASE.md` file to the root of the repo
3. PR will be checked by autopub
4. Merge to main → automatic release! 🎉

## RELEASE.md Format

Create a `RELEASE.md` file in your PR with YAML frontmatter:

```markdown
---
release type: patch
---

Brief description of what changed.

- Fix bug in asset version comparison
- Add test coverage
```

### Release Types

- **patch** (0.1.0 → 0.1.1): Bug fixes, documentation
- **minor** (0.1.0 → 0.2.0): New features, backwards compatible  
- **major** (0.1.0 → 1.0.0): Breaking changes

## What Happens Automatically

When your PR is merged to main, autopub will:

1. ✅ Update version in `pyproject.toml`
2. ✅ Create a git tag (e.g., `v0.2.0`)
3. ✅ Create a GitHub Release with your notes
4. ✅ Build the package with `uv build`
5. ✅ Publish to [PyPI](https://pypi.org/project/cross-inertia/)
6. ✅ Update `CHANGELOG.md`
7. ✅ Remove `RELEASE.md`

## Examples

### Bug Fix Release (Patch)

```markdown
---
release type: patch
---

Fix asset version handling for None values

- Handle None values correctly in version comparison
- Add test coverage for edge cases
- Update error messages
```

### New Feature (Minor)

```markdown
---
release type: minor
---

Add lazy props evaluation

This release adds support for lazy props, allowing expensive
computations to be deferred until they're actually needed.

Features:
- Lazy prop wrapper that defers evaluation
- Only evaluated when requested in partial reloads
- Full test coverage and documentation

See #2 for details.
```

### Breaking Change (Major)

```markdown
---
release type: major
---

Refactor imports to inertia.fastapi namespace

**BREAKING CHANGE**: All imports must be updated.

Migration:
- Before: `from inertia import InertiaDep`
- After: `from inertia.fastapi import InertiaDep`

This change enables better multi-framework support.

See #10 for migration guide.
```

## Pre-Release Checklist

Before creating a RELEASE.md:

- [ ] All tests passing on CI
- [ ] Code coverage maintained (71%+)
- [ ] CHANGELOG.md will be auto-updated, but review manually after
- [ ] Breaking changes documented clearly
- [ ] Examples updated if APIs changed

## Testing the Release

You can test the release process locally:

```bash
# Install autopub
uv pip install autopub

# Check if RELEASE.md is valid
autopub check

# See what would be released (doesn't publish)
autopub prepare
autopub build
```

## Troubleshooting

### PR Check Fails

If the autopub check fails on your PR:

1. Check RELEASE.md format matches examples
2. Ensure "Release type:" line is present
3. Make sure file is named exactly `RELEASE.md`
4. Check autopub logs in GitHub Actions

### Release Doesn't Trigger

If merged but no release happened:

1. Check if RELEASE.md was in the PR
2. Verify the release workflow ran on main branch
3. Check workflow logs in GitHub Actions

### PyPI Upload Fails

Publishing requires PyPI trusted publisher setup:

1. Go to PyPI → cross-inertia → Settings → Publishing
2. Ensure GitHub Actions is configured as trusted publisher
3. Repository: `patrick91/cross-inertia`
4. Workflow: `release.yml`

## Version History

Current version: **0.1.0** (initial release)

See [CHANGELOG.md](../CHANGELOG.md) for full history.

## Questions?

See [RELEASE.md.example](../RELEASE.md.example) for more examples.
