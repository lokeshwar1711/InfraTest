"""InfraTest CLI entrypoint."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from infratest.config import load_config
from infratest.engine import run_verification
from infratest.exceptions import ConfigLoadError, InfraTestError
from infratest.reporting import render_console, write_json_report


class ExitCode(int, Enum):
    """CLI exit code contract."""

    VERIFIED = 0
    VALIDATION_FAILED = 1
    EXECUTION_ERROR = 2


class OutputMode(str, Enum):
    """Supported output modes for CLI runs."""

    CONSOLE = "console"
    JSON = "json"
    BOTH = "both"


app = typer.Typer(
    help="InfraTest validates deployed infrastructure behavior before deployment.",
    add_completion=False,
)
console = Console()


@app.callback()
def main() -> None:
    """InfraTest command group."""


@app.command()
def verify(
    config_path: Path = typer.Argument(
        ...,
        help="Path to infra-test.yaml configuration file.",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    output: OutputMode = typer.Option(
        OutputMode.CONSOLE,
        "--output",
        help="Output format: console, json, or both.",
        case_sensitive=False,
    ),
    output_path: Path = typer.Option(
        Path("infratest-report.json"),
        "--output-path",
        help="Path for JSON report output.",
    ),
) -> None:
    """Verify infrastructure behavior using YAML-defined tests."""
    try:
        config = load_config(config_path)
        summary = run_verification(config)

        if output in {OutputMode.CONSOLE, OutputMode.BOTH}:
            render_console(summary, console=console)

        if output in {OutputMode.JSON, OutputMode.BOTH}:
            report_file = write_json_report(summary, output_path)
            if output != OutputMode.JSON:
                console.print(f"\n[dim]JSON report written to {report_file}[/dim]")

        raise typer.Exit(
            ExitCode.VERIFIED if summary.success else ExitCode.VALIDATION_FAILED
        )
    except ConfigLoadError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(ExitCode.EXECUTION_ERROR) from exc
    except InfraTestError as exc:
        console.print(f"[bold red]Execution error:[/bold red] {exc}")
        raise typer.Exit(ExitCode.EXECUTION_ERROR) from exc
    except typer.Exit:
        raise
    except Exception as exc:  # pragma: no cover
        console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        raise typer.Exit(ExitCode.EXECUTION_ERROR) from exc


if __name__ == "__main__":
    app()
