"""Execution result models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TestStatus(str, Enum):
    """Verification status for a single check."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(slots=True)
class TestResult:
    """Result of executing one test definition."""

    name: str
    status: TestStatus
    message: str
    execution_time_ms: int
    expected_status: int
    actual_status: int | None
    endpoint: str
    metadata: dict[str, Any]


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
    def success(self) -> bool:
        return self.failed == 0
