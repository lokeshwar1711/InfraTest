"""Verification engine orchestration."""

from __future__ import annotations

import httpx

from infratest.models import InfraTestConfig, TestType
from infratest.results import RunSummary
from infratest.validators.http_validator import execute_http_test


def run_verification(config: InfraTestConfig) -> RunSummary:
    """Run all configured validations and return aggregated results."""
    results = []

    with httpx.Client(follow_redirects=True) as client:
        for test in config.tests:
            if test.type is TestType.HTTP:
                result = execute_http_test(test, client)
                results.append(result)

    return RunSummary(results=results)
