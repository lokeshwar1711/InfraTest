import socket

from infratest.models import TCPTestDefinition, TestType as InfraTestType
from infratest.validators.tcp_validator import execute_tcp_test


def test_execute_tcp_test_pass_when_port_is_open(monkeypatch) -> None:
    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "infratest.validators.tcp_validator.socket.create_connection",
        lambda *args, **kwargs: DummySocket(),
    )

    result = execute_tcp_test(
        TCPTestDefinition(
            name="db-port",
            type=InfraTestType.TCP,
            host="db.internal",
            port=5432,
            expect_open=True,
        )
    )

    assert result.status.value == "PASS"
    assert result.message == "TCP connection succeeded"


def test_execute_tcp_test_pass_when_port_is_expected_closed(monkeypatch) -> None:
    def raise_error(*args, **kwargs):
        raise socket.timeout()

    monkeypatch.setattr(
        "infratest.validators.tcp_validator.socket.create_connection",
        raise_error,
    )

    result = execute_tcp_test(
        TCPTestDefinition(
            name="admin-port-closed",
            type=InfraTestType.TCP,
            host="db.internal",
            port=22,
            expect_open=False,
        )
    )

    assert result.status.value == "PASS"
    assert result.actual == "connection timed out"