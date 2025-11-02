"""Nox sessions for cross-inertia."""

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = True
nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHON_VERSIONS, name="tests", tags=["tests"])
def tests(session: nox.Session) -> None:
    """Run unit tests."""
    session.install(".")
    session.install("pytest", "pytest-cov", "fastapi", "httpx", "jinja2")
    session.run(
        "pytest",
        "tests/",
        "--ignore=tests/e2e/",
        "-v",
        "--cov=src",
        "--cov-append",
        "--cov-report=xml",
        "--cov-report=term",
    )


@nox.session(python=["3.14"], name="e2e")
def e2e_tests(session: nox.Session) -> None:
    """Run E2E tests with Playwright (local only - requires frontend build)."""
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
    session.run("playwright", "install", "--with-deps", "chromium")
    session.run(
        "pytest",
        "tests/e2e/",
        "-v",
    )


@nox.session(python=["3.14"], name="lint")
def lint(session: nox.Session) -> None:
    """Run linting with ruff."""
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=["3.14"], name="format")
def format_code(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", ".")
    session.run("ruff", "check", "--fix", ".")


@nox.session(python=["3.14"], name="typecheck")
def typecheck(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.install(".", "mypy", "fastapi", "httpx")
    session.run("mypy", "src/", "--ignore-missing-imports")
