import json
from pathlib import Path

from typer.testing import CliRunner

from infratest.cli import app
from infratest.models import Severity
from infratest.results import RunSummary, TestResult as ResultRecord, TestStatus as ResultStatus


runner = CliRunner()


def test_cli_verify_success_passes_context(monkeypatch, tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    captured: dict[str, set[str]] = {}

    def fake_run_verification(config_obj, active_contexts=None):
        captured["contexts"] = set(active_contexts or set())
        return RunSummary(results=[_result(status=ResultStatus.PASS)])

    monkeypatch.setattr("infratest.cli.run_verification", fake_run_verification)

    result = runner.invoke(app, ["verify", str(config), "--context", "public"])

    assert result.exit_code == 0
    assert captured["contexts"] == {"public"}


def test_cli_verify_invalid_config(tmp_path: Path) -> None:
    config = tmp_path / "infra-test.yaml"
    config.write_text("tests: []\n", encoding="utf-8")

    result = runner.invoke(app, ["verify", str(config)])

    assert result.exit_code == 2


def test_cli_json_output_writes_nested_file(monkeypatch, tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    report = tmp_path / "artifacts" / "reports" / "report.json"

    monkeypatch.setattr(
        "infratest.cli.run_verification",
        lambda config_obj, active_contexts=None: RunSummary(
            results=[_result(status=ResultStatus.PASS)]
        ),
    )

    result = runner.invoke(
        app,
        ["verify", str(config), "--output", "json", "--output-path", str(report)],
    )

    assert result.exit_code == 0
    assert report.exists()
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["success"] is True
    assert payload["blocking_failed"] == 0


def test_cli_advisory_failures_do_not_block(monkeypatch, tmp_path: Path) -> None:
    config = _write_config(tmp_path)

    monkeypatch.setattr(
        "infratest.cli.run_verification",
        lambda config_obj, active_contexts=None: RunSummary(
            results=[
                _result(status=ResultStatus.FAIL, severity=Severity.ADVISORY),
            ]
        ),
    )

    result = runner.invoke(app, ["verify", str(config)])

    assert result.exit_code == 0


def _write_config(tmp_path: Path) -> Path:
    config = tmp_path / "infra-test.yaml"
    config.write_text(
        """
tests:
  - name: ok
    type: http
    endpoint: https://example.com/
    expect_status: 200
""".strip(),
        encoding="utf-8",
    )
    return config


def _result(
    *,
    status: ResultStatus,
    severity: Severity = Severity.BLOCKING,
) -> ResultRecord:
    return ResultRecord(
        name="demo",
        test_type="http",
        severity=severity,
        status=status,
        message="ok",
        execution_time_ms=12,
        target="https://example.com/",
        expected="status in [200]",
        actual="status=200; final_url=https://example.com/",
        metadata={},
    )
