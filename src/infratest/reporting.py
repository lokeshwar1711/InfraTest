"""Console and JSON reporting utilities."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from infratest.exceptions import ReportWriteError
from infratest.results import RunSummary


def render_console(summary: RunSummary, console: Console | None = None) -> None:
    """Render human-readable output in terminal."""
    out = console or Console()

    out.print("\n[bold]InfraTest Verification Report[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Test", style="cyan", overflow="fold")
    table.add_column("Type")
    table.add_column("Severity")
    table.add_column("Status", style="bold")
    table.add_column("Target", overflow="fold")
    table.add_column("Expected")
    table.add_column("Actual")
    table.add_column("Latency")
    table.add_column("Message", overflow="fold")

    for result in summary.results:
        color = "green" if result.status.value == "PASS" else "red"
        table.add_row(
            result.name,
            result.test_type,
            result.severity.value,
            f"[{color}]{result.status.value}[/{color}]",
            result.target,
            result.expected or "-",
            result.actual or "-",
            f"{result.execution_time_ms}ms",
            result.message,
        )

    out.print(table)
    out.print(
        f"\nTotal: {summary.total} | "
        f"Passed: [green]{summary.passed}[/green] | "
        f"Failed: [red]{summary.failed}[/red] | "
        f"Blocking Failures: [red]{summary.blocking_failed}[/red] | "
        f"Advisory Failures: [yellow]{summary.advisory_failed}[/yellow]"
    )
    if summary.success:
        out.print("\n[bold green]Environment Verified[/bold green]")
    else:
        out.print("\n[bold red]Deployment Blocked[/bold red]")


def summary_to_json(summary: RunSummary) -> str:
    """Serialize run summary to stable JSON."""
    payload = {
        "success": summary.success,
        "total": summary.total,
        "passed": summary.passed,
        "failed": summary.failed,
        "results": [
            {
                "name": result.name,
                "type": result.test_type,
                "severity": result.severity.value,
                "status": result.status.value,
                "message": result.message,
                "execution_time_ms": result.execution_time_ms,
                "target": result.target,
                "expected": result.expected,
                "actual": result.actual,
                "metadata": result.metadata,
            }
            for result in summary.results
        ],
        "blocking_failed": summary.blocking_failed,
        "advisory_failed": summary.advisory_failed,
    }
    return json.dumps(payload, indent=2)


def write_json_report(summary: RunSummary, output_path: str | Path) -> Path:
    """Write JSON report to disk and return resolved output path."""
    destination = Path(output_path)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(summary_to_json(summary) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ReportWriteError(f"failed to write JSON report: {exc}") from exc
    return destination.resolve()
