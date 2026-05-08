# Python Unit Testing

Use this file whenever the code under test is Python. It assumes `SKILL.md` has already provided the general unit-testing rules; add only Python-specific guidance here. If the project uses pytest, also read `python-pytest.md`.

## Local Python Context

Before editing Python tests, inspect the closest relevant files:

- `pyproject.toml`, `setup.cfg`, `tox.ini`, `noxfile.py`, `hatch.toml`, `poetry.lock`, `uv.lock`, or CI config for commands and Python versions.
- Existing tests, `conftest.py`, factories, fixtures, and helper modules for import style and layout.
- Package boundaries, `__init__.py` files, and source layout such as `src/` vs flat packages.

Prefer normal package imports. Do not add `sys.path` mutations unless the project already relies on them or packaging is broken and the user accepts that workaround.

## Python-Specific Unit Subjects

In addition to the universal subjects in `SKILL.md`, Python unit tests often need focused coverage for:

- Dataclass defaults, validation hooks, equality, ordering, and serialization helpers.
- Context managers: enter behavior, exit cleanup, and exception handling.
- Decorators: wrapped function behavior and preserved metadata when relevant.
- Generators and iterators: yielded sequence, early termination, and cleanup.
- Async functions and async context managers.
- Module-level configuration, caches, registries, and lazy initialization.
- Exception types and message fragments that callers rely on.

## Python Testability Hazards

Watch for Python-specific patterns that make otherwise good unit tests brittle:

- Import-time network calls, filesystem writes, environment reads, background threads, or global client construction.
- Mutable default arguments that leak state between calls.
- Module-level caches, registries, and singletons with no reset path.
- Functions that read `datetime.now()`, `random`, `os.environ`, or the current working directory deep inside logic that could accept those values from its caller.
- Dynamic attributes that make unspec'd mocks hide misspellings or invalid calls.

When changing production code for testability, prefer changes that reduce these Python hazards for real callers too.

## Patching Rule

Patch the name looked up by the code under test.

Production code:

```python
# app/reports.py
from app.mailer import send_email


def send_report(user, body):
    send_email(user.email, "Monthly report", body)
```

Bad:

```python
from unittest.mock import patch


def test_send_report_sends_email(user):
    with patch("app.mailer.send_email") as send_email:
        send_report(user, "body")

    send_email.assert_called_once()
```

Good:

```python
from unittest.mock import patch


def test_send_report_sends_email_to_user(user):
    with patch("app.reports.send_email", autospec=True) as send_email:
        send_report(user, "body")

    send_email.assert_called_once_with(user.email, "Monthly report", "body")
```

`send_report` uses `app.reports.send_email`, so that is the name the test patches.

## Mock Specs

When using `unittest.mock`, prefer mocks that constrain the API:

```python
from unittest.mock import create_autospec


def test_service_closes_client():
    client = create_autospec(ApiClient, instance=True)
    service = SyncService(client)

    service.close()

    client.close.assert_called_once_with()
```

Avoid bare `Mock()` or `MagicMock()` for real collaborators unless the API is intentionally dynamic. Unspec'd mocks can hide misspelled attributes and invalid calls.

## Deterministic Time

Prefer injectable time over patching global time:

```python
from datetime import datetime


def is_expired(expires_at, *, now=None):
    now = now or datetime.now()
    return expires_at <= now
```

```python
def test_is_expired_when_expiry_is_in_past():
    assert is_expired(
        datetime(2026, 1, 1, 11, 59),
        now=datetime(2026, 1, 1, 12, 0),
    )
```

Patch `datetime` only when changing the production seam would be unjustified or too invasive.

## Fakes For Python Collaborators

Use hand-written fakes when they make domain behavior clearer than mocks:

```python
class FakeUserRepository:
    def __init__(self):
        self.users_by_email = {}

    def find_by_email(self, email):
        return self.users_by_email.get(email)

    def save(self, user):
        self.users_by_email[user.email] = user
        return user
```

This is better than a chain of mocks when the repository's in-memory behavior is small and meaningful.

## Environment And Process State

Treat these as process-global and restore them with the runner's cleanup tools:

- `os.environ`
- current working directory
- `sys.path`, `sys.modules`, and import caches
- locale, timezone, warnings filters, logging config
- module-level caches, registries, and singletons

Do not mutate them directly without automatic cleanup.

## Async Python

Use the async test support already configured by the project. For unit tests:

- Await the unit directly.
- Replace async clients with async fakes or `AsyncMock` objects that use a spec when representing a real API.
- Avoid real sleeps; inject awaitable collaborators or fake clocks.
- Assert task scheduling only when scheduling is the contract.

## Python Checklist

- Imports use the project's normal package layout.
- Patches target the lookup name used by the unit.
- Real API mocks use `spec`, `spec_set`, `autospec`, `create_autospec`, or `AsyncMock` with a spec.
- Process-global state is restored by test tooling.
- Production seams are useful design improvements, not test-only access points.
