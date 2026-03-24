import httpx

from infratest.engine import run_verification
from infratest.models import HTTPTestDefinition, InfraTestConfig, TestType as CheckType
from infratest.validators.http_validator import execute_http_test


def test_execute_http_test_pass() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(200, text="healthy")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        test = HTTPTestDefinition(
            name="api-health",
            type=CheckType.HTTP,
            endpoint="https://api.example.com/health",
            expect_status=200,
            body_contains="health",
        )

        result = execute_http_test(test, client)

    assert result.status.value == "PASS"
    assert result.actual_status == 200


def test_execute_http_test_fail_by_status() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        test = HTTPTestDefinition(
            name="api-health",
            type=CheckType.HTTP,
            endpoint="https://api.example.com/health",
            expect_status=200,
        )

        result = execute_http_test(test, client)

    assert result.status.value == "FAIL"
    assert result.actual_status == 503


def test_run_verification_aggregates_results(monkeypatch) -> None:
    config = InfraTestConfig(
        tests=[
            HTTPTestDefinition(
                name="check-one",
                type=CheckType.HTTP,
                endpoint="https://svc.example.com/one",
                expect_status=200,
            ),
            HTTPTestDefinition(
                name="check-two",
                type=CheckType.HTTP,
                endpoint="https://svc.example.com/two",
                expect_status=200,
            ),
        ]
    )

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.calls = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, headers=None, timeout=5.0):
            self.calls += 1
            if "one" in url:
                return httpx.Response(200, request=httpx.Request(method, url), text="ok")
            return httpx.Response(500, request=httpx.Request(method, url), text="bad")

    monkeypatch.setattr("infratest.engine.httpx.Client", FakeClient)

    summary = run_verification(config)

    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.success is False
