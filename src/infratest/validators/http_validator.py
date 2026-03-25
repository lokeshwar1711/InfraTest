"""HTTP validation module for V1."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any

import httpx

from infratest.models import HTTPTestDefinition
from infratest.results import TestResult, TestStatus


def execute_http_test(test: HTTPTestDefinition) -> TestResult:
    """Execute one HTTP test and return a structured result."""
    start = perf_counter()
    status = TestStatus.FAIL
    message = "unknown error"
    metadata: dict[str, str] = {}
    actual: str | None = None

    try:
        with httpx.Client(
            follow_redirects=test.follow_redirects,
            verify=test.tls_verify,
        ) as client:
            response = client.request(
                method=test.method.value,
                url=str(test.endpoint),
                headers=test.headers,
                timeout=test.timeout,
            )

        actual = _describe_http_actual(response)

        if response.status_code not in test.expect_status:
            message = (
                f"expected status {', '.join(str(code) for code in test.expect_status)}, "
                f"got {response.status_code}"
            )
        elif test.expected_final_url and str(response.url) != str(test.expected_final_url):
            message = (
                f"expected final URL {test.expected_final_url}, "
                f"got {response.url}"
            )
        elif test.expected_headers and not _headers_match(
            test.expected_headers, response.headers
        ):
            message = "response headers did not match expected values"
        elif test.body_contains and test.body_contains not in response.text:
            message = f"response body does not contain: {test.body_contains!r}"
        elif test.expect_body_json is not None and not _json_body_matches(
            response, test.expect_body_json
        ):
            message = "response JSON body did not match expected subset"
        else:
            status = TestStatus.PASS
            message = f"{response.status_code} {response.reason_phrase}".strip()

        metadata = {
            "http_version": response.http_version,
            "final_url": str(response.url),
            "redirect_count": str(len(response.history)),
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
        test_type=test.type.value,
        severity=test.severity,
        status=status,
        message=message,
        execution_time_ms=elapsed_ms,
        target=str(test.endpoint),
        expected=_describe_http_expectation(test),
        actual=actual,
        metadata=metadata,
    )


def _describe_http_expectation(test: HTTPTestDefinition) -> str:
    expectations = [f"status in {test.expect_status}"]
    if test.expected_final_url is not None:
        expectations.append(f"final_url={test.expected_final_url}")
    if test.expected_headers:
        expectations.append(
            "headers=" + ", ".join(sorted(test.expected_headers.keys()))
        )
    if test.body_contains is not None:
        expectations.append(f"body contains {test.body_contains!r}")
    if test.expect_body_json is not None:
        expectations.append("json subset")
    return "; ".join(expectations)


def _describe_http_actual(response: httpx.Response) -> str:
    return f"status={response.status_code}; final_url={response.url}"


def _headers_match(expected: dict[str, str], actual: httpx.Headers) -> bool:
    for key, value in expected.items():
        if actual.get(key) != value:
            return False
    return True


def _json_body_matches(response: httpx.Response, expected: Any) -> bool:
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return False

    return _is_subset(expected, payload)


def _is_subset(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _is_subset(value, actual[key])
            for key, value in expected.items()
        )

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        return all(any(_is_subset(item, candidate) for candidate in actual) for item in expected)

    return expected == actual
