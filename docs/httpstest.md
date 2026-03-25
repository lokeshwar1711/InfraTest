# InfraTest — HTTP Validation Architecture

## Purpose

This document describes the current HTTP validator behavior in the repository.

The original prototype proved basic status-code checks. The current implementation adds the controls needed for deployment-gate trust.

## What The HTTP Validator Does Now

The HTTP validator can assert:

- one or more allowed status codes
- redirect-following behavior
- expected final URL after redirects
- expected response headers
- plain-text body containment
- JSON body subset matching
- retry policy and warmup delay
- execution-context requirements
- advisory vs blocking severity

## Why These Controls Matter

Simple `GET` plus `200` checks create false confidence in real infrastructure.

Examples:

- a broken endpoint redirects to a generic landing page
- a service returns `200` before its JSON payload is ready
- a load balancer responds before the expected application version is actually serving traffic
- a private endpoint is tested from a public runner and the result is misinterpreted

InfraTest therefore treats HTTP validation as behavioral verification, not just reachability.

## Execution Lifecycle

### 1. Context Validation

Before any request is sent, the engine checks whether the test's required `execution_contexts` match the active `--context` values supplied on the CLI.

If the run context is wrong, InfraTest records a failed result immediately.

### 2. Optional Warmup Delay

If `start_delay` is configured, InfraTest waits before the first attempt.

This is useful for systems that are expected to become healthy shortly after provisioning.

### 3. Request Execution

InfraTest creates an HTTP client using the test's redirect and TLS settings and performs the request with the configured method, headers, and timeout.

### 4. Assertion Evaluation

InfraTest evaluates the response in this order:

1. status code is allowed
2. final URL matches when configured
3. expected headers match
4. body contains required text when configured
5. JSON body contains the expected subset when configured

### 5. Retry Policy

If an attempt fails and retries are configured, InfraTest waits for `retry_interval` and tries again until the configured attempt count is exhausted.

### 6. Result Reporting

The validator returns a structured result with:

- test name
- type
- severity
- target
- expected summary
- actual summary
- execution time
- metadata such as final URL and redirect count

## Configuration Example

```yaml
tests:
  - name: api-health
    type: http
    endpoint: https://api.example.com/health
    expect_status: [200, 204]
    expected_headers:
      x-env: prod
    expect_body_json:
      status: healthy
      details:
        ready: true
    follow_redirects: true
    expected_final_url: https://api.example.com/health
    retries: 2
    retry_interval: 3
    start_delay: 5
    execution_contexts: [private-runner]
    severity: blocking
```

## Current Constraints

Still intentionally limited:

- methods are `GET` and `HEAD`
- TLS control is a boolean toggle, not a full certificate bundle workflow
- execution is synchronous

Those constraints are acceptable for the current repository stage because the key deployment-trust gaps are already addressed.
