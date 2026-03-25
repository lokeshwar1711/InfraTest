"""AWS runtime IAM behavior validation module."""

from __future__ import annotations

from time import perf_counter
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from infratest.models import AWSIAMTestDefinition
from infratest.results import TestResult, TestStatus


AUTHZ_ERROR_CODES = {
    "AccessDenied",
    "AccessDeniedException",
    "UnauthorizedOperation",
    "UnrecognizedClientException",
    "InvalidClientTokenId",
    "ExpiredToken",
}


def execute_aws_iam_test(test: AWSIAMTestDefinition) -> TestResult:
    """Execute one AWS API call to validate runtime IAM behavior."""
    start = perf_counter()
    status = TestStatus.FAIL
    message = "unknown error"
    actual: str | None = None
    metadata: dict[str, Any] = {
        "service": test.service,
        "operation": test.operation,
    }

    try:
        session = boto3.Session()
        client = session.client(
            test.service,
            region_name=test.region,
            config=Config(
                connect_timeout=test.timeout,
                read_timeout=test.timeout,
                retries={"max_attempts": 0},
            ),
        )
        operation = getattr(client, test.operation, None)
        if operation is None:
            actual = f"operation {test.operation} not found"
            message = f"unknown boto3 operation: {test.operation}"
        else:
            response = operation(**test.parameters)
            actual = "access granted"
            metadata["response_keys"] = sorted(response.keys())
            if test.expect_access:
                status = TestStatus.PASS
                message = "AWS API call succeeded"
            else:
                message = "expected access to be denied, but AWS API call succeeded"
    except (NoCredentialsError, PartialCredentialsError) as exc:
        actual = "credentials unavailable"
        metadata["error_type"] = "credentials"
        message = f"AWS credentials unavailable: {exc}"
    except ClientError as exc:
        error = exc.response.get("Error", {})
        error_code = error.get("Code", "Unknown")
        error_message = error.get("Message", str(exc))
        actual = error_code
        metadata["error_type"] = "client_error"
        metadata["aws_error_code"] = error_code
        if not test.expect_access and _denial_matches(test, error_code):
            status = TestStatus.PASS
            message = f"AWS API call denied as expected: {error_code}"
        else:
            message = f"AWS API call failed: {error_code}: {error_message}"
    except BotoCoreError as exc:
        actual = exc.__class__.__name__
        metadata["error_type"] = "botocore_error"
        message = f"AWS SDK error: {exc}"

    elapsed_ms = int((perf_counter() - start) * 1000)
    expected = "access granted" if test.expect_access else "access denied"

    return TestResult(
        name=test.name,
        test_type=test.type.value,
        severity=test.severity,
        status=status,
        message=message,
        execution_time_ms=elapsed_ms,
        target=f"{test.service}.{test.operation}",
        expected=expected,
        actual=actual,
        metadata=metadata,
    )


def _denial_matches(test: AWSIAMTestDefinition, error_code: str) -> bool:
    if test.expected_error_codes:
        return error_code in set(test.expected_error_codes)
    return error_code in AUTHZ_ERROR_CODES