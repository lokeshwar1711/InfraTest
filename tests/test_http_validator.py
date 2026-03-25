import httpx

from infratest.engine import run_verification
from infratest.models import (
    HTTPTestDefinition,
    InfraTestConfig,
    Severity,
    TestType as CheckType,
)
from infratest.validators.http_validator import execute_http_test


def test_execute_http_test_pass_with_header_and_json_assertions(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, *, follow_redirects, verify):
            assert follow_redirects is True
            assert verify is True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, headers=None, timeout=5.0):
            assert method == "GET"
            assert timeout == 5.0
            request = httpx.Request(method, "https://api.example.com/health")
            return httpx.Response(
                200,
                headers={"x-env": "prod"},
                json={"status": "healthy", "details": {"ready": True}},
                request=request,
            )

    monkeypatch.setattr("infratest.validators.http_validator.httpx.Client", FakeClient)

    test = HTTPTestDefinition(
        name="api-health",
        type=CheckType.HTTP,
        endpoint="https://api.example.com/health",
        expect_status=[200, 204],
        body_contains="health",
        expected_headers={"x-env": "prod"},
        expect_body_json={"details": {"ready": True}},
    )

    result = execute_http_test(test)

    assert result.status.value == "PASS"
    assert result.actual == "status=200; final_url=https://api.example.com/health"


def test_execute_http_test_fail_by_status(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, *, follow_redirects, verify):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, headers=None, timeout=5.0):
            return httpx.Response(
                503,
                text="unavailable",
                request=httpx.Request(method, url),
            )

    monkeypatch.setattr("infratest.validators.http_validator.httpx.Client", FakeClient)

    test = HTTPTestDefinition(
        name="api-health",
        type=CheckType.HTTP,
        endpoint="https://api.example.com/health",
        expect_status=200,
    )

    result = execute_http_test(test)

    assert result.status.value == "FAIL"
    assert result.message == "expected status 200, got 503"


def test_execute_http_test_fail_when_final_url_mismatches(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, *, follow_redirects, verify):
            assert follow_redirects is True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, headers=None, timeout=5.0):
            return httpx.Response(
                200,
                text="healthy",
                request=httpx.Request(method, "https://api.example.com/redirected"),
            )

    monkeypatch.setattr("infratest.validators.http_validator.httpx.Client", FakeClient)

    test = HTTPTestDefinition(
        name="redirect-check",
        type=CheckType.HTTP,
        endpoint="https://api.example.com/start",
        expect_status=200,
        expected_final_url="https://api.example.com/final",
    )

    result = execute_http_test(test)

    assert result.status.value == "FAIL"
    assert "expected final URL" in result.message


def test_run_verification_retries_until_success(monkeypatch) -> None:
    config = InfraTestConfig(
        tests=[
            HTTPTestDefinition(
                name="check-one",
                type=CheckType.HTTP,
                endpoint="https://svc.example.com/one",
                expect_status=200,
                retries=1,
            ),
        ]
    )
    attempts = {"count": 0}

    def fake_execute_http_test(test):
        attempts["count"] += 1
        status = "FAIL" if attempts["count"] == 1 else "PASS"
        return _http_result(test.name, status=status)

    monkeypatch.setattr("infratest.engine.execute_http_test", fake_execute_http_test)

    summary = run_verification(config)

    assert summary.total == 1
    assert summary.passed == 1
    assert summary.failed == 0
    assert attempts["count"] == 2


def test_run_verification_respects_execution_contexts() -> None:
    config = InfraTestConfig(
        tests=[
            HTTPTestDefinition(
                name="private-only",
                type=CheckType.HTTP,
                endpoint="https://svc.example.com/private",
                expect_status=200,
                execution_contexts=["private-runner"],
                severity=Severity.BLOCKING,
            )
        ]
    )

    summary = run_verification(config, active_contexts={"public"})

    assert summary.failed == 1
    assert summary.blocking_failed == 1
    assert summary.results[0].message == "execution context mismatch"


def test_run_verification_advisory_failure_does_not_block() -> None:
    summary = run_verification(
        InfraTestConfig(
            tests=[
                HTTPTestDefinition(
                    name="advisory-check",
                    type=CheckType.HTTP,
                    endpoint="https://svc.example.com/advisory",
                    expect_status=200,
                    severity=Severity.ADVISORY,
                    execution_contexts=["private"],
                )
            ]
        ),
        active_contexts={"public"},
    )

    assert summary.failed == 1
    assert summary.advisory_failed == 1
    assert summary.success is True


def _http_result(name: str, *, status: str) -> object:
    from infratest.results import TestResult, TestStatus

    return TestResult(
        name=name,
        test_type="http",
        severity=Severity.BLOCKING,
        status=TestStatus(status),
        message=status.lower(),
        execution_time_ms=10,
        target="https://svc.example.com",
        expected="status in [200]",
        actual="status=200; final_url=https://svc.example.com",
        metadata={},
    )
