"""Execution result models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from infratest.models import Severity


class TestStatus(str, Enum):
    """Verification status for a single check."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(slots=True)
class TestResult:
    """Result of executing one test definition."""

    name: str
    test_type: str
    severity: Severity
    status: TestStatus
    message: str
    execution_time_ms: int
    target: str
    expected: str | None
    actual: str | None
    metadata: dict[str, Any]

    @property
    def blocks_deployment(self) -> bool:
        return self.status is TestStatus.FAIL and self.severity is Severity.BLOCKING


@dataclass(slots=True)
class RunSummary:
    """Aggregated run output."""

    results: list[TestResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.status is TestStatus.PASS)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def blocking_failed(self) -> int:
        return sum(1 for result in self.results if result.blocks_deployment)

    @property
    def advisory_failed(self) -> int:
        return sum(
            1
            for result in self.results
            if result.status is TestStatus.FAIL and not result.blocks_deployment
        )

    @property
    def success(self) -> bool:
        return self.blocking_failed == 0
