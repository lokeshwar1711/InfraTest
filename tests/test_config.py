from pathlib import Path

import pytest

from infratest.config import load_config
from infratest.exceptions import ConfigLoadError


def test_load_config_success(tmp_path: Path) -> None:
    config_file = tmp_path / "infra-test.yaml"
    config_file.write_text(
        """
tests:
  - name: health-check
    type: http
    endpoint: https://example.com/health
    expect_status: 200
""".strip(),
        encoding="utf-8",
    )

    loaded = load_config(config_file)

    assert len(loaded.tests) == 1
    assert loaded.tests[0].name == "health-check"


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
