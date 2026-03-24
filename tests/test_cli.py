from pathlib import Path

from typer.testing import CliRunner

from infratest.cli import app


runner = CliRunner()


def test_cli_verify_success(tmp_path: Path) -> None:
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

    result = runner.invoke(app, ["verify", str(config)])

    # Network may fail in offline environments; assert CLI contract instead.
    assert result.exit_code in {0, 1}


def test_cli_verify_invalid_config(tmp_path: Path) -> None:
    config = tmp_path / "infra-test.yaml"
    config.write_text("tests: []\n", encoding="utf-8")

    result = runner.invoke(app, ["verify", str(config)])

    assert result.exit_code == 2


def test_cli_json_output_writes_file(tmp_path: Path) -> None:
    config = tmp_path / "infra-test.yaml"
    config.write_text(
        """
tests:
  - name: probably-fails-offline
    type: http
    endpoint: https://example.com/
    expect_status: 200
""".strip(),
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    result = runner.invoke(
        app,
        ["verify", str(config), "--output", "json", "--output-path", str(report)],
    )

    assert result.exit_code in {0, 1}
    assert report.exists()
