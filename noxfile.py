"""Nox sessions for cross-inertia."""

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True
nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHON_VERSIONS, name="tests", tags=["tests"])
def tests(session: nox.Session) -> None:
    """Run unit tests."""
    session.install(
        "pytest", "pytest-cov", "pytest-django", "fastapi", "httpx", "jinja2", "django"
    )
    # Install in editable mode so coverage can track the source
    session.install("-e", ".")
    session.run(
        "python",
        "-m",
        "pytest",
        "tests/",
        "--ignore=tests/e2e/",
        "-v",
        "--cov=src/cross_inertia",
        "--cov-report=xml",
        "--cov-report=term",
    )


@nox.session(python=["3.14"], name="e2e")
def e2e_tests(session: nox.Session) -> None:
    """Run E2E tests with Playwright (requires frontend build).

    To build the frontend first:
        cd examples/fastapi && bun install && bun run build
    """
    from pathlib import Path

    # Check if frontend is built
    build_dir = Path("examples/fastapi/static/build")
    if not build_dir.exists() or not list(build_dir.glob("*")):
        session.error(
            "Frontend not built! Please build it first:\n"
            "  cd examples/fastapi\n"
            "  bun install\n"
            "  bun run build\n"
            "\nOr with npm:\n"
            "  npm install && npm run build"
        )

    session.install(".")
    session.install(
        "pytest",
        "pytest-playwright",
        "playwright",
        "fastapi",
        "httpx",
        "uvicorn",
        "itsdangerous",
        "jinja2",
    )

    # Install Playwright browsers
    session.run("python", "-m", "playwright", "install", "--with-deps", "chromium")
    session.run(
        "python",
        "-m",
        "pytest",
        "tests/e2e/",
        "-v",
    )


@nox.session(python=["3.14"], name="lint")
def lint(session: nox.Session) -> None:
    """Run linting with ruff."""
    session.install("ruff")
    session.run("python", "-m", "ruff", "check", ".")
    session.run("python", "-m", "ruff", "format", "--check", ".")


@nox.session(python=["3.14"], name="format")
def format_code(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("python", "-m", "ruff", "format", ".")
    session.run("python", "-m", "ruff", "check", "--fix", ".")


@nox.session(python=["3.14"], name="typecheck")
def typecheck(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.install(".", "mypy", "fastapi", "httpx")
    session.run("python", "-m", "mypy", "src/", "--ignore-missing-imports")
