"""Configuration loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from infratest.exceptions import ConfigLoadError
from infratest.models import InfraTestConfig


def load_config(path: str | Path) -> InfraTestConfig:
    """Load and validate InfraTest YAML configuration."""
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigLoadError(f"configuration file not found: {config_path}")

    if config_path.is_dir():
        raise ConfigLoadError(f"configuration path is a directory: {config_path}")

    try:
        raw_data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigLoadError(f"failed to read configuration: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigLoadError(f"invalid YAML: {exc}") from exc

    if raw_data is None:
        raise ConfigLoadError("configuration is empty")

    if not isinstance(raw_data, dict):
        raise ConfigLoadError("configuration root must be a mapping")

    return _validate(raw_data)


def _validate(raw_data: dict[str, Any]) -> InfraTestConfig:
    try:
        return InfraTestConfig.model_validate(raw_data)
    except ValidationError as exc:
        raise ConfigLoadError(f"configuration validation failed: {exc}") from exc
