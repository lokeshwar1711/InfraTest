"""HTTP validation module for V1."""

from __future__ import annotations

from time import perf_counter

import httpx

from infratest.models import HTTPTestDefinition
from infratest.results import TestResult, TestStatus


def execute_http_test(test: HTTPTestDefinition, client: httpx.Client) -> TestResult:
    """Execute one HTTP test and return a structured result."""
    start = perf_counter()
    status = TestStatus.FAIL
    message = "unknown error"
    actual_status: int | None = None
    metadata: dict[str, str] = {}

    try:
        response = client.request(
            method=test.method.value,
            url=str(test.endpoint),
            headers=test.headers,
            timeout=test.timeout,
        )
        actual_status = response.status_code

        if response.status_code != test.expect_status:
            message = (
                f"expected status {test.expect_status}, "
                f"got {response.status_code}"
            )
        elif test.body_contains and test.body_contains not in response.text:
            message = f"response body does not contain: {test.body_contains!r}"
        else:
            status = TestStatus.PASS
            message = f"{response.status_code} {response.reason_phrase}".strip()

        metadata = {
            "http_version": response.http_version,
            "final_url": str(response.url),
        }
    except httpx.ConnectTimeout:
        message = "connection timed out"
        metadata = {"error_type": "timeout"}
    except httpx.ReadTimeout:
        message = "response timed out"
        metadata = {"error_type": "timeout"}
    except httpx.ConnectError as exc:
        message = f"connection error: {exc}"
        metadata = {"error_type": "connect_error"}
    except httpx.HTTPError as exc:
        message = f"http error: {exc}"
        metadata = {"error_type": "http_error"}

    elapsed_ms = int((perf_counter() - start) * 1000)

    return TestResult(
        name=test.name,
        status=status,
        message=message,
        execution_time_ms=elapsed_ms,
        expected_status=test.expect_status,
        actual_status=actual_status,
        endpoint=str(test.endpoint),
        metadata=metadata,
    )
