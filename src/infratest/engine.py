"""Verification engine orchestration."""

from __future__ import annotations

from time import sleep

from infratest.models import (
    AWSIAMTestDefinition,
    HTTPTestDefinition,
    InfraTestConfig,
    TCPTestDefinition,
)
from infratest.results import RunSummary, TestResult, TestStatus
from infratest.validators.aws_iam_validator import execute_aws_iam_test
from infratest.validators.tcp_validator import execute_tcp_test
from infratest.validators.http_validator import execute_http_test


def run_verification(
    config: InfraTestConfig, active_contexts: set[str] | None = None
) -> RunSummary:
    """Run all configured validations and return aggregated results."""
    results = []
    normalized_contexts = {context.casefold() for context in active_contexts or set()}

    for test in config.tests:
        context_result = _validate_execution_contexts(test, normalized_contexts)
        if context_result is not None:
            results.append(context_result)
            continue

        if test.start_delay > 0:
            sleep(test.start_delay)

        results.append(_execute_with_retries(test))

    return RunSummary(results=results)


def _execute_with_retries(
    test: HTTPTestDefinition | TCPTestDefinition | AWSIAMTestDefinition,
) -> TestResult:
    attempts = test.retries + 1
    last_result: TestResult | None = None

    for attempt in range(1, attempts + 1):
        result = _dispatch_test(test)
        result.metadata["attempt"] = attempt
        result.metadata["max_attempts"] = attempts
        if result.status is TestStatus.PASS:
            return result

        last_result = result
        if attempt < attempts and test.retry_interval > 0:
            sleep(test.retry_interval)

    assert last_result is not None
    return last_result


def _dispatch_test(
    test: HTTPTestDefinition | TCPTestDefinition | AWSIAMTestDefinition,
) -> TestResult:
    if isinstance(test, HTTPTestDefinition):
        return execute_http_test(test)
    if isinstance(test, TCPTestDefinition):
        return execute_tcp_test(test)
    return execute_aws_iam_test(test)


def _validate_execution_contexts(
    test: HTTPTestDefinition | TCPTestDefinition | AWSIAMTestDefinition,
    active_contexts: set[str],
) -> TestResult | None:
    required_contexts = set(test.execution_contexts or [])
    if not required_contexts:
        return None

    if required_contexts.isdisjoint(active_contexts):
        active_value = ", ".join(sorted(active_contexts)) if active_contexts else "none"
        required_value = ", ".join(sorted(required_contexts))
        return TestResult(
            name=test.name,
            test_type=test.type.value,
            severity=test.severity,
            status=TestStatus.FAIL,
            message="execution context mismatch",
            execution_time_ms=0,
            target=_describe_target(test),
            expected=f"any of: {required_value}",
            actual=f"active contexts: {active_value}",
            metadata={"error_type": "execution_context_mismatch"},
        )

    return None


def _describe_target(
    test: HTTPTestDefinition | TCPTestDefinition | AWSIAMTestDefinition,
) -> str:
    if isinstance(test, HTTPTestDefinition):
        return str(test.endpoint)
    if isinstance(test, TCPTestDefinition):
        return f"{test.host}:{test.port}"
    return f"{test.service}.{test.operation}"
