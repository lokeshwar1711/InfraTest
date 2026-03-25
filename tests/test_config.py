from pathlib import Path

import pytest

from infratest.config import load_config
from infratest.exceptions import ConfigLoadError
from infratest.models import AWSIAMTestDefinition, HTTPTestDefinition, TCPTestDefinition


def test_load_config_success(tmp_path: Path) -> None:
    config_file = tmp_path / "infra-test.yaml"
    config_file.write_text(
        """
tests:
  - name: health-check
    type: http
    endpoint: https://example.com/health
    expect_status: [200, 204]
  - name: database-port
    type: tcp
    host: db.internal
    port: 5432
    expect_open: true
  - name: identity-check
    type: aws_iam
    service: sts
    operation: get_caller_identity
    expect_access: true
""".strip(),
        encoding="utf-8",
    )

    loaded = load_config(config_file)

    assert len(loaded.tests) == 3
    assert isinstance(loaded.tests[0], HTTPTestDefinition)
    assert loaded.tests[0].expect_status == [200, 204]
    assert isinstance(loaded.tests[1], TCPTestDefinition)
    assert isinstance(loaded.tests[2], AWSIAMTestDefinition)


def test_load_config_duplicate_names(tmp_path: Path) -> None:
    config_file = tmp_path / "infra-test.yaml"
    config_file.write_text(
        """
tests:
  - name: API
    type: http
    endpoint: https://example.com/one
    expect_status: 200
  - name: api
    type: http
    endpoint: https://example.com/two
    expect_status: 200
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigLoadError):
        load_config(config_file)


def test_load_config_empty_file(tmp_path: Path) -> None:
    config_file = tmp_path / "infra-test.yaml"
    config_file.write_text("", encoding="utf-8")

    with pytest.raises(ConfigLoadError):
        load_config(config_file)


def test_load_config_rejects_head_with_body_assertion(tmp_path: Path) -> None:
  config_file = tmp_path / "infra-test.yaml"
  config_file.write_text(
    """
tests:
  - name: invalid-head
  type: http
  endpoint: https://example.com/health
  method: HEAD
  body_contains: healthy
""".strip(),
    encoding="utf-8",
  )

  with pytest.raises(ConfigLoadError):
    load_config(config_file)


def test_load_config_rejects_expected_error_codes_for_positive_access(
  tmp_path: Path,
) -> None:
  config_file = tmp_path / "infra-test.yaml"
  config_file.write_text(
    """
tests:
  - name: invalid-aws-config
  type: aws_iam
  service: s3
  operation: head_bucket
  expect_access: true
  expected_error_codes: [AccessDenied]
""".strip(),
    encoding="utf-8",
  )

  with pytest.raises(ConfigLoadError):
    load_config(config_file)
