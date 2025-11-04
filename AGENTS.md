# Cross-Inertia Development Guidelines

This file contains guidelines and conventions for AI coding agents working on the Cross-Inertia project.

For human developers, see the main [README.md](./README.md) and [documentation](https://inertia.patrick.wtf).

## Release Process

When creating a release, add a `RELEASE.md` file to your PR with this format:

```markdown
---
release type: patch|minor|major
---

Release notes go here.

- List your changes
- Can be multiple lines
```

### Release Types
- **patch**: Bug fixes, documentation (0.1.0 → 0.1.1)
- **minor**: New features, backwards compatible (0.1.0 → 0.2.0)
- **major**: Breaking changes (0.1.0 → 1.0.0)

### Example

```markdown
---
release type: minor
---

Add lazy props evaluation support

- Implement lazy prop wrapper
- Only evaluate when needed
- Add documentation and tests
```

The autopub workflow will automatically:
1. Update version in pyproject.toml
2. Create GitHub release
3. Publish to PyPI
4. Update CHANGELOG.md
5. Remove RELEASE.md

See `docs/RELEASING.md` for full details.

## Code Style

- **Linting**: Run `nox -s lint` before committing
- **Type Checking**: Run `nox -s typecheck` to verify types
- **Formatting**: Use `nox -s format` to auto-format code
- **Tests**: Run `nox -s tests-3.14` for unit tests

## Testing

- **Unit Tests**: `nox -s tests-3.14`
- **E2E Tests**: `nox -s e2e-3.14` (requires frontend build)
- **Coverage**: Maintain 70%+ coverage
- **All Python Versions**: CI tests on 3.10-3.14

## Commit Messages

Use conventional commit style:
- `feat: Add new feature`
- `fix: Fix bug in X`
- `docs: Update documentation`
- `test: Add test for Y`
- `refactor: Refactor Z`

## Documentation

- **Live site**: https://inertia.patrick.wtf
- Update docs in `docs/src/content/docs/` for new features
- Run `cd docs && bun run dev` to preview locally at http://localhost:4321
- Documentation deploys automatically via Cloudflare Pages on push to main

## CI/CD

- **Tests**: Automatically run on all PRs
- **Lint**: Checks code quality and types
- **Release**: Triggered by RELEASE.md in merged PRs

## Project Structure

```
src/inertia/          # Main package code
tests/                # Unit tests
tests/e2e/           # End-to-end tests
examples/fastapi/    # Example application
docs/                # Starlight documentation
```

## Dependencies

- **Python**: 3.10+
- **FastAPI**: Primary framework support
- **lia**: Framework abstraction layer
- **Vite**: Frontend build tool
- **Inertia.js**: v2.0+ (client-side adapters)

## Helpful Commands

```bash
# Development
nox -s tests-3.14        # Run unit tests
nox -s lint              # Check code quality
nox -s typecheck         # Check types
nox -s format            # Auto-format code

# Documentation
cd docs && bun run dev   # Start docs server at http://localhost:4321

# E2E (requires frontend build)
cd examples/fastapi && bun run build
nox -s e2e-3.14
```

## Important Links

- **Documentation**: https://inertia.patrick.wtf
- **PyPI**: https://pypi.org/project/cross-inertia/
- **GitHub**: https://github.com/patrick91/cross-inertia
- **Issues**: https://github.com/patrick91/cross-inertia/issues
