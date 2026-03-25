"""TCP connectivity validation module."""

from __future__ import annotations

import socket
from time import perf_counter

from infratest.models import TCPTestDefinition
from infratest.results import TestResult, TestStatus


def execute_tcp_test(test: TCPTestDefinition) -> TestResult:
    """Execute one TCP connectivity test."""
    start = perf_counter()
    status = TestStatus.FAIL
    message = "unknown error"
    actual = "no connection attempt"
    metadata: dict[str, str] = {}

    try:
        with socket.create_connection((test.host, test.port), timeout=test.timeout):
            actual = "connection opened"
            if test.expect_open:
                status = TestStatus.PASS
                message = "TCP connection succeeded"
            else:
                message = "expected port to be closed, but connection succeeded"
    except socket.timeout:
        actual = "connection timed out"
        metadata = {"error_type": "timeout"}
        if not test.expect_open:
            status = TestStatus.PASS
            message = "TCP connection remained closed"
        else:
            message = "connection timed out"
    except OSError as exc:
        actual = str(exc)
        metadata = {"error_type": "connect_error"}
        if not test.expect_open:
            status = TestStatus.PASS
            message = "TCP connection remained closed"
        else:
            message = f"connection error: {exc}"

    elapsed_ms = int((perf_counter() - start) * 1000)
    expectation = "port open" if test.expect_open else "port closed"

    return TestResult(
        name=test.name,
        test_type=test.type.value,
        severity=test.severity,
        status=status,
        message=message,
        execution_time_ms=elapsed_ms,
        target=f"{test.host}:{test.port}",
        expected=expectation,
        actual=actual,
        metadata=metadata,
    )