# Python Pytest 9.x

Use this file when a Python project uses pytest. It assumes `SKILL.md` and `python-unit-testing.md` have already supplied the general and Python-specific testing rules. This file only adds pytest 9.x mechanics, using pytest 9.0.0 documentation as the baseline.

## Configuration And Discovery

Read project configuration before choosing commands or file locations. Pytest settings commonly live in `pyproject.toml`, `pytest.ini`, `tox.ini`, or `setup.cfg`.

Respect configured discovery such as `testpaths`, `python_files`, `python_classes`, and `python_functions`. If no config exists, pytest's common convention is `test_*.py` or `*_test.py` files with `test_*` functions.

Use focused commands first, then broaden:

```bash
pytest tests/path/test_module.py::test_specific_behavior
pytest tests/path/test_module.py -q
pytest -k "specific behavior expression"
pytest -m "unit and not slow"
pytest -q
```

Prefer existing project wrappers such as `tox`, `nox`, `make`, `uv`, `hatch`, `poetry`, or CI commands when present.

## Plain Assert And Approx

Use plain `assert` so pytest can introspect failures.

Bad:

```python
def test_discount_applies_percentage():
    assert calculate_total(100, discount_percent=20)
```

Good:

```python
def test_discount_applies_percentage():
    assert calculate_total(100, discount_percent=20) == 80
```

Use `pytest.approx` for floating-point values:

```python
import pytest


def test_tax_rate():
    assert calculate_tax(19.99, rate=0.0825) == pytest.approx(1.649175)
```

## Raises And Exception Groups

Use `pytest.raises` instead of broad `try`/`except`.

Bad:

```python
def test_parse_port_rejects_non_numeric_value():
    try:
        parse_port("abc")
    except Exception:
        assert True
```

Good:

```python
import pytest


def test_parse_port_rejects_non_numeric_value():
    with pytest.raises(ValueError, match="port"):
        parse_port("abc")
```

In pytest 9.x, use `check=` when the exception object itself needs validation:

```python
def test_parse_error_includes_error_code():
    with pytest.raises(ParseError, match="invalid", check=lambda exc: exc.code == "E_PARSE"):
        parse_config("invalid")
```

For exception groups, use pytest's exception-group helpers when the target Python version supports them:

```python
def test_batch_validation_groups_errors():
    with pytest.RaisesGroup(ValueError, match="batch"):
        validate_batch([{"email": ""}])
```

## Parametrize

Use `pytest.mark.parametrize` for compact variants of the same behavior. Use `ids=` when failure names would otherwise be unclear.

Good:

```python
import pytest


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" ada ", "ada"),
        ("ADA", "ada"),
        ("Ada Lovelace", "ada lovelace"),
    ],
    ids=["trim", "lowercase", "preserve-space"],
)
def test_normalize_username(raw, expected):
    assert normalize_username(raw) == expected
```

Bad:

```python
@pytest.mark.parametrize("payload", [None, {}, {"email": "bad"}])
def test_create_user_errors(payload):
    assert create_user(payload) is None
```

The bad version combines materially different cases behind one weak assertion.

## Fixtures

Use pytest fixtures for named reusable setup, not to hide scenario details.

Good:

```python
import pytest


@pytest.fixture
def fake_user_repo():
    return FakeUserRepository()


def test_register_user_saves_new_user(fake_user_repo):
    service = RegistrationService(fake_user_repo)

    user = service.register("ada@example.com")

    assert fake_user_repo.find_by_email("ada@example.com") == user
```

Bad:

```python
def test_register_user_saves_new_user(big_test_context):
    assert big_test_context.service.register(big_test_context.email)
```

Pytest fixture specifics:

- Prefer function scope by default.
- Use broader scopes only for immutable, expensive setup that cannot leak state.
- Use `yield` fixtures when teardown is needed.
- Use `autouse=True` sparingly; invisible setup should be obvious and genuinely universal in that scope.
- Keep `conftest.py` fixtures local to the subtree that needs them.

## Built-In Isolation Fixtures

Use pytest's built-in fixtures instead of manual global mutation.

`tmp_path`:

```python
def test_export_writes_json(tmp_path):
    output = tmp_path / "report.json"

    export_report({"total": 3}, output)

    assert output.read_text(encoding="utf-8") == '{"total": 3}'
```

`monkeypatch`:

```python
def test_config_reads_timeout_from_environment(monkeypatch):
    monkeypatch.setenv("APP_TIMEOUT_SECONDS", "30")

    assert load_timeout() == 30
```

```python
def test_config_uses_default_when_timeout_missing(monkeypatch):
    monkeypatch.delenv("APP_TIMEOUT_SECONDS", raising=False)

    assert load_timeout() == 10
```

Use `monkeypatch.context()` for risky or short-lived patches, especially around standard-library objects or objects pytest may use internally.

## Capturing Logs, Output, And Warnings

Use `caplog` for log assertions:

```python
import logging


def test_retry_logs_warning(caplog):
    caplog.set_level(logging.WARNING)

    retry_once(failing_operation)

    assert "retrying" in caplog.text
```

Use `capsys` for Python-level stdout/stderr and `capfd` for file-descriptor-level output:

```python
def test_cli_prints_summary(capsys):
    run_summary_command(["--count", "2"])

    captured = capsys.readouterr()
    assert "Processed 2 items" in captured.out
    assert captured.err == ""
```

Use `pytest.warns`, `pytest.deprecated_call`, or `recwarn` for warnings:

```python
import pytest


def test_old_name_warns_before_delegating():
    with pytest.warns(DeprecationWarning, match="old_name"):
        assert old_name("Ada") == "ada"
```

## Markers, Skip, And Xfail

Use existing markers consistently. Register custom markers in project configuration when strict marker checking is enabled.

Use `skip` only for legitimate environment limitations. Use `xfail` only for a known unresolved defect or unsupported behavior, with a specific reason. Do not use either to hide a failure that should be fixed.

## Pytest-Mock And Async Plugins

If the project uses `pytest-mock`, use its `mocker` fixture consistently:

```python
def test_send_report_sends_email(mocker, user):
    send_email = mocker.patch("app.reports.send_email", autospec=True)

    send_report(user, "body")

    send_email.assert_called_once_with(user.email, "Monthly report", "body")
```

Do not add `pytest-mock` only to avoid importing `unittest.mock`.

For async tests, use the async plugin and mode already configured by the project, such as `pytest-asyncio` if present. Do not introduce an async plugin without approval.

## Pytest Checklist

- Pytest is actually the project runner.
- Discovery, markers, and commands follow project config.
- Fixtures are narrow, named after meaning, and correctly scoped.
- Built-in pytest fixtures replace manual process-global mutation.
- Focused pytest commands were run or the blocker was reported.
