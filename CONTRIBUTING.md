# Contributing to Cross-Inertia

Thank you for your interest in contributing to Cross-Inertia! We welcome contributions of all kinds.

## Quick Links

- 📚 [Documentation](https://inertia.patrick.wtf)
- 🐛 [Issues](https://github.com/patrick91/cross-inertia/issues)
- 🌟 [Good First Issues](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- 🗺️ [Roadmap](./ROADMAP.md)

## Getting Started

### Prerequisites

- **Python 3.10+** (we test on 3.10-3.14)
- **uv** - Fast Python package installer ([install guide](https://docs.astral.sh/uv/))
- **Git**
- **Bun or Node.js** (for E2E tests and docs)

### Clone the Repository

```bash
git clone https://github.com/patrick91/cross-inertia.git
cd cross-inertia
```

### Set Up Development Environment

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Install nox for running tests
uv pip install nox
```

### Run Tests

```bash
# Run unit tests (Python 3.14)
nox -s tests-3.14

# Run all unit tests across Python versions
nox -t tests

# Run linting
nox -s lint

# Run type checking
nox -s typecheck

# Format code
nox -s format
```

### Run the Example App

```bash
# Terminal 1: Build frontend
cd examples/fastapi
bun install  # or: npm install
bun run build  # or: npm run build

# Terminal 2: Run FastAPI
cd examples/fastapi
uvicorn main:app --reload

# Visit http://localhost:8000
```

For development with hot reload:

```bash
# Terminal 1: Vite dev server
cd examples/fastapi
bun run dev

# Terminal 2: FastAPI
uvicorn main:app --reload
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, documented code
- Add type hints (required)
- Follow existing code style
- Add tests for new features
- Update documentation if needed

### 3. Run Tests Locally

```bash
# Format code
nox -s format

# Check linting
nox -s lint

# Run tests
nox -s tests-3.14

# Check types
nox -s typecheck
```

### 4. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add lazy props evaluation"
git commit -m "fix: handle None in asset version comparison"
git commit -m "docs: update installation guide"
```

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub:
1. Go to https://github.com/patrick91/cross-inertia
2. Click "Pull requests" → "New pull request"
3. Select your branch
4. Fill in the PR description
5. Submit!

## Code Style

### Formatting and Linting

We use **ruff** for both formatting and linting:

```bash
# Auto-format code
nox -s format

# Check for issues
nox -s lint
```

### Type Hints

All code must have type hints:

```python
# Good ✅
def render(component: str, props: dict[str, Any]) -> Response:
    return Response(...)

# Bad ❌
def render(component, props):
    return Response(...)
```

### Documentation

- Add docstrings to public functions and classes
- Update documentation in `docs/src/content/docs/` for new features
- Include examples in docstrings

```python
def lazy(func: Callable[[], T]) -> LazyProp[T]:
    """Wrap a function to defer evaluation until needed.
    
    Args:
        func: Function that returns the prop value
        
    Returns:
        LazyProp wrapper that evaluates on access
        
    Example:
        ```python
        @app.get("/users")
        def users(inertia: InertiaDep):
            return inertia.render("Users", {
                "users": lazy(lambda: get_all_users()),
            })
        ```
    """
    return LazyProp(func)
```

## Testing

### Unit Tests

```bash
# Run all unit tests
nox -s tests-3.14

# Run specific test file
uv run pytest tests/test_protocol.py -v

# Run specific test
uv run pytest tests/test_protocol.py::TestInertiaProtocol::test_detects_inertia_request -v
```

### E2E Tests

E2E tests require the frontend to be built:

```bash
# Build frontend first
cd examples/fastapi
bun run build

# Run E2E tests
cd ../..
nox -s e2e-3.14
```

### Test Coverage

We aim for 70%+ coverage:

```bash
# Run tests with coverage
nox -s tests-3.14

# Coverage report is shown in terminal
# Coverage XML is saved to coverage.xml
```

### Writing Tests

- Use pytest fixtures from `tests/conftest.py`
- Test both success and error cases
- Use descriptive test names

```python
def test_renders_component_with_props(client: TestClient):
    """Test that components render with props correctly."""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "TestComponent"
    assert data["props"]["message"] == "Hello, World!"
```

## Documentation

### Building Documentation Locally

```bash
cd docs
bun install
bun run dev

# Visit http://localhost:4321
```

### Documentation Structure

```
docs/src/content/docs/
├── getting-started/     # Installation, quick start
├── guides/             # Feature guides
└── reference/          # API reference
```

### Adding Documentation

1. Create a `.md` or `.mdx` file in `docs/src/content/docs/`
2. Add frontmatter:
   ```yaml
   ---
   title: Page Title
   description: Page description for SEO
   ---
   ```
3. Write content in Markdown
4. Preview locally with `bun run dev`

## Areas to Contribute

### 🌟 Good First Issues

Great for newcomers! Check out issues labeled [`good first issue`](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22):

- Error bags support
- Prefetching support
- Documentation improvements
- Example applications

### 🔥 High Priority

See [`high-priority`](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3Ahigh-priority) label:

- Page object fields
- Import refactoring
- PyPI publishing improvements

### 🚀 Framework Support

Help us support more Python web frameworks:

- **Flask** - Similar to FastAPI, good starting point
- **Django** - Large ecosystem, high demand
- **Sanic** - Async framework
- See [Framework Support Issues](https://github.com/patrick91/cross-inertia/issues?q=is%3Aissue+is%3Aopen+label%3Aframework-support)

### 📚 Documentation

- Write tutorials and guides
- Add more code examples
- Improve API documentation
- Create video tutorials

### 🧪 Testing

- Improve test coverage
- Add E2E test scenarios
- Performance benchmarks
- Browser compatibility testing

## Releasing

Releases are automated via autopub. To trigger a release:

1. Create your PR with changes
2. Add a `RELEASE.md` file:
   ```markdown
   ---
   release type: patch
   ---
   
   Brief description of changes
   
   - List your changes here
   ```
3. Merge to main → automatic release!

See [docs/RELEASING.md](./docs/RELEASING.md) for details.

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** - Treat everyone with respect
- **Be collaborative** - Work together constructively
- **Be inclusive** - Welcome newcomers and diverse perspectives
- **Be professional** - Keep discussions focused and productive

### Unacceptable Behavior

- Harassment, discrimination, or hate speech
- Personal attacks or insults
- Trolling or inflammatory comments
- Publishing others' private information

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report issues to: patrick.arminio@gmail.com

## Getting Help

- 💬 **Questions?** [Open a discussion](https://github.com/patrick91/cross-inertia/discussions)
- 🐛 **Bug?** [Open an issue](https://github.com/patrick91/cross-inertia/issues/new)
- 📚 **Docs:** https://inertia.patrick.wtf
- 🗺️ **Roadmap:** [ROADMAP.md](./ROADMAP.md)

## Project Structure

```
cross-inertia/
├── src/inertia/          # Main package code
│   ├── __init__.py       # Public API
│   ├── _core.py          # Core Inertia implementation
│   └── middleware.py     # Shared data middleware
├── tests/                # Unit tests
│   ├── conftest.py       # Test fixtures
│   ├── test_*.py         # Unit tests
│   └── e2e/             # End-to-end tests
├── examples/fastapi/     # Example application
├── docs/                 # Starlight documentation
├── noxfile.py           # Test automation
└── pyproject.toml       # Package configuration
```

## Resources

- [Inertia.js Documentation](https://inertiajs.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [lia Framework Abstraction](https://github.com/patrick91/lia)
- [Vite Documentation](https://vitejs.dev/)

## Recognition

Contributors will be:
- Listed in release notes
- Added to GitHub contributors
- Mentioned in documentation (for significant contributions)

Thank you for contributing to Cross-Inertia! 🎉
