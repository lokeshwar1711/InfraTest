"""Configuration and execution models."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class TestType(str, Enum):
    """Supported test types in V1."""

    HTTP = "http"
    TCP = "tcp"
    AWS_IAM = "aws_iam"


class Severity(str, Enum):
    """Controls whether a failed check blocks deployment."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class HttpMethod(str, Enum):
    """Supported HTTP methods in V1."""

    GET = "GET"
    HEAD = "HEAD"


class BaseTestDefinition(BaseModel):
    """Fields shared by every executable InfraTest check."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    type: TestType
    timeout: float = Field(default=5.0, gt=0, le=300)
    start_delay: float = Field(default=0.0, ge=0, le=300)
    retries: int = Field(default=0, ge=0, le=10)
    retry_interval: float = Field(default=0.0, ge=0, le=60)
    severity: Severity = Severity.BLOCKING
    execution_contexts: list[str] | None = Field(default=None, min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be empty")
        return normalized

    @field_validator("execution_contexts")
    @classmethod
    def validate_execution_contexts(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            context = item.strip().casefold()
            if not context:
                raise ValueError("execution contexts must not be empty")
            if context not in seen:
                normalized.append(context)
                seen.add(context)
        return normalized


class HTTPTestDefinition(BaseTestDefinition):
    """User-defined HTTP verification check."""

    type: Literal[TestType.HTTP] = TestType.HTTP
    endpoint: HttpUrl
    expect_status: list[int] = Field(default_factory=lambda: [200], min_length=1)
    method: HttpMethod = HttpMethod.GET
    headers: dict[str, str] | None = None
    body_contains: str | None = Field(default=None, max_length=2000)
    expect_body_json: dict[str, Any] | list[Any] | None = None
    expected_headers: dict[str, str] | None = None
    follow_redirects: bool = True
    expected_final_url: HttpUrl | None = None
    tls_verify: bool = True

    @field_validator("expect_status", mode="before")
    @classmethod
    def validate_expected_status(cls, value: int | list[int]) -> list[int]:
        values = value if isinstance(value, list) else [value]
        if not values:
            raise ValueError("expect_status must contain at least one status code")

        normalized: list[int] = []
        seen: set[int] = set()
        for status_code in values:
            if not isinstance(status_code, int) or not 100 <= status_code <= 599:
                raise ValueError("expect_status entries must be integers between 100 and 599")
            if status_code not in seen:
                normalized.append(status_code)
                seen.add(status_code)
        return normalized

    @field_validator("headers", "expected_headers")
    @classmethod
    def validate_headers(
        cls, value: dict[str, str] | None
    ) -> dict[str, str] | None:
        if value is None:
            return None

        normalized: dict[str, str] = {}
        for key, header_value in value.items():
            clean_key = key.strip()
            if not clean_key:
                raise ValueError("header names must not be empty")
            normalized[clean_key.lower()] = str(header_value)
        return normalized

    @model_validator(mode="after")
    def validate_http_assertions(self) -> "HTTPTestDefinition":
        if self.method is HttpMethod.HEAD and (
            self.body_contains is not None or self.expect_body_json is not None
        ):
            raise ValueError("HEAD requests cannot assert response body content")

        if self.expected_final_url is not None and not self.follow_redirects:
            raise ValueError("expected_final_url requires follow_redirects=true")

        return self


class TCPTestDefinition(BaseTestDefinition):
    """User-defined TCP reachability check."""

    type: Literal[TestType.TCP] = TestType.TCP
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    expect_open: bool = True

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("host must not be empty")
        return normalized


class AWSIAMTestDefinition(BaseTestDefinition):
    """Runtime AWS API execution check for IAM behavior."""

    type: Literal[TestType.AWS_IAM] = TestType.AWS_IAM
    service: str = Field(min_length=1, max_length=100)
    operation: str = Field(min_length=1, max_length=100)
    region: str | None = Field(default=None, min_length=1, max_length=50)
    parameters: dict[str, Any] = Field(default_factory=dict)
    expect_access: bool = True
    expected_error_codes: list[str] | None = Field(default=None, min_length=1)

    @field_validator("service", "operation", "region")
    @classmethod
    def validate_non_empty_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be empty")
        return normalized

    @field_validator("expected_error_codes")
    @classmethod
    def validate_expected_error_codes(
        cls, value: list[str] | None
    ) -> list[str] | None:
        if value is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()
        for code in value:
            clean_code = code.strip()
            if not clean_code:
                raise ValueError("expected error codes must not be empty")
            if clean_code not in seen:
                normalized.append(clean_code)
                seen.add(clean_code)
        return normalized

    @model_validator(mode="after")
    def validate_negative_access_expectations(self) -> "AWSIAMTestDefinition":
        if self.expect_access and self.expected_error_codes:
            raise ValueError(
                "expected_error_codes can only be set when expect_access=false"
            )
        return self


TestDefinition = Annotated[
    HTTPTestDefinition | TCPTestDefinition | AWSIAMTestDefinition,
    Field(discriminator="type"),
]


class InfraTestConfig(BaseModel):
    """Top-level config for an InfraTest run."""

    model_config = ConfigDict(extra="forbid")

    tests: list[TestDefinition] = Field(min_length=1)

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
