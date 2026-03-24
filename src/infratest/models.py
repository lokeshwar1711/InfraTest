"""Configuration and execution models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class TestType(str, Enum):
    """Supported test types in V1."""

    HTTP = "http"


class HttpMethod(str, Enum):
    """Supported HTTP methods in V1."""

    GET = "GET"
    HEAD = "HEAD"


class HTTPTestDefinition(BaseModel):
    """User-defined HTTP verification check."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    type: TestType
    endpoint: HttpUrl
    expect_status: int = Field(ge=100, le=599)
    method: HttpMethod = HttpMethod.GET
    timeout: float = Field(default=5.0, gt=0, le=60)
    headers: dict[str, str] | None = None
    body_contains: str | None = Field(default=None, max_length=2000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be empty")
        return normalized


class InfraTestConfig(BaseModel):
    """Top-level config for an InfraTest run."""

    model_config = ConfigDict(extra="forbid")

    tests: list[HTTPTestDefinition] = Field(min_length=1)

    @model_validator(mode="after")
    def ensure_unique_names(self) -> "InfraTestConfig":
        seen: set[str] = set()
        duplicates: set[str] = set()
        for test in self.tests:
            key = test.name.casefold()
            if key in seen:
                duplicates.add(test.name)
            seen.add(key)

        if duplicates:
            values = ", ".join(sorted(duplicates))
            raise ValueError(f"duplicate test names found: {values}")

        return self
