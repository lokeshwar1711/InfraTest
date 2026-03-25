# InfraTest

InfraTest is a CLI verification engine for post-deployment infrastructure checks.

It is designed to answer one operational question before application rollout:

> Does this environment behave the way we expect from the network location and credentials we are actually using?

## What Ships Today

InfraTest currently supports three executable check types:

- HTTP checks with redirect control, retries, warmup delay, header assertions, JSON body subset assertions, and final URL assertions
- TCP connectivity checks for open or closed ports
- AWS runtime IAM checks by executing real boto3 client operations

Each test can also declare:

- `severity`: `blocking` or `advisory`
- `execution_contexts`: labels such as `public`, `private-runner`, `vpn`, `local`, or `aws`
- retry policy: `retries`, `retry_interval`, `start_delay`

InfraTest uses those contexts to avoid a common false-confidence trap: a check from the wrong network location is not treated as valid evidence.

## Why Execution Contexts Matter

If you want to prove an internal service is reachable only from a private network, the check must run from a private network. A public runner proving success or failure does not answer that question.

InfraTest keeps this explicit:

```bash
infratest verify infra-test.yaml --context private-runner
```

If a test requires a context that is not active, InfraTest fails the test with an explicit execution-context mismatch.

## Install

```bash
pip install -e .[dev]
```

## Quick Start

Run the sample suite in the repository:

```bash
infratest verify infra-test.yaml --context public --output both --output-path artifacts/infratest/report.json
```

Exit codes:

- `0`: all blocking checks passed, or only advisory checks failed
- `1`: one or more blocking checks failed
- `2`: InfraTest configuration or execution error

## Example Configuration

```yaml
tests:
        - name: docs-home
                type: http
                endpoint: https://example.com/
                expect_status: [200]
                follow_redirects: true
                retries: 2
                retry_interval: 2
                expected_final_url: https://example.com/
                execution_contexts: [public]

        - name: docs-https-port
                type: tcp
                host: example.com
                port: 443
                expect_open: true
                execution_contexts: [public]

        - name: caller-identity
                type: aws_iam
                service: sts
                operation: get_caller_identity
                region: us-east-1
                expect_access: true
                execution_contexts: [aws]
                severity: advisory
```

## Check Types

### HTTP

Supported fields:

- `endpoint`
- `expect_status`: single status code or list of allowed codes
- `method`: `GET` or `HEAD`
- `headers`
- `body_contains`
- `expect_body_json`
- `expected_headers`
- `follow_redirects`
- `expected_final_url`
- `tls_verify`
- `timeout`
- `retries`
- `retry_interval`
- `start_delay`
- `severity`
- `execution_contexts`

### TCP

Supported fields:

- `host`
- `port`
- `expect_open`
- `timeout`
- `retries`
- `retry_interval`
- `start_delay`
- `severity`
- `execution_contexts`

### AWS IAM

Supported fields:

- `service`
- `operation`
- `region`
- `parameters`
- `expect_access`
- `expected_error_codes`
- `timeout`
- `retries`
- `retry_interval`
- `start_delay`
- `severity`
- `execution_contexts`

Example negative runtime access check:

```yaml
tests:
        - name: prod-bucket-must-be-denied
                type: aws_iam
                service: s3
                operation: head_bucket
                parameters:
                        Bucket: prod-secret-bucket
                expect_access: false
                expected_error_codes: [AccessDenied]
                execution_contexts: [aws]
```

## Local Development

The repository now includes:

- deterministic unit tests for HTTP, TCP, AWS IAM, CLI, and config behavior
- local smoke-test assets under `examples/`
- a manual test runbook in [docs/COMMAND_RUNBOOK.md](docs/COMMAND_RUNBOOK.md)

Run the full automated suite:

```bash
pytest
```

## Current Positioning

InfraTest is ready to act as a customer-run verification engine in CI or controlled environments.

It is not yet a hosted SaaS control plane. The technically credible path to selling it as a service is:

- customer-run execution agents or runners inside the right network zones
- a separate control plane for history, reporting, orchestration, and team workflows

That separation is important because private-network validation is only meaningful when execution happens from the correct vantage point.

## Current Scope Boundaries

InfraTest is not currently:

- a monitoring platform
- a hosted dashboard product
- a Terraform wrapper
- a policy or compliance engine
- a multi-cloud governance layer

It is a deployment-readiness verification engine.
