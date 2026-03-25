# InfraTest — System Architecture V1

## Purpose

This document describes the current executable architecture in the repository.

The design goal is still simplicity, but the architecture now reflects the features that actually ship: HTTP checks, TCP checks, AWS runtime IAM checks, retry policy, and execution-context awareness.

## Runtime Shape

InfraTest remains a local or pipeline-run CLI.

Execution flow:

1. CLI loads YAML configuration
2. CLI receives active execution contexts from repeated `--context` flags
3. Pydantic validates discriminated test definitions
4. Engine enforces context requirements and retry policy
5. Test-specific validator executes the live check
6. Reporting layer emits console and optional JSON output
7. CLI exits with a deployment-gating code

## Layers

### CLI Layer

Responsibilities:

- parse command-line arguments
- accept `--context` labels for the current run
- load configuration
- invoke the engine
- render output and exit codes

### Configuration Layer

Responsibilities:

- parse YAML
- enforce strict schema validation
- reject logically inconsistent checks

Examples of rejected combinations:

- `HEAD` with `body_contains`
- `expected_final_url` when redirects are disabled
- `expected_error_codes` on a positive AWS access assertion

### Engine Layer

Responsibilities:

- sequential orchestration
- start-delay handling
- retry handling
- execution-context enforcement
- summary aggregation

The engine is intentionally synchronous for now because deployment-gate trust is more important than early parallelism.

### Validator Layer

Current validators:

- `http_validator`
- `tcp_validator`
- `aws_iam_validator`

Each validator:

- accepts one typed test definition
- executes a live check
- never raises expected infra failures into the CLI path
- returns a structured `TestResult`

### Reporting Layer

Outputs:

- rich console table
- stable JSON summary

Results include:

- test type
- severity
- target
- expected value
- actual value
- execution time
- structured metadata

## Execution Context Model

This is the most important addition for product correctness.

Tests may declare `execution_contexts`, for example:

- `public`
- `private-runner`
- `vpn`
- `local`
- `aws`

The CLI provides active contexts for the run. If none of a test's required contexts are active, InfraTest records an explicit failure instead of pretending the check was meaningful.

This keeps private-network and credential-scoped assertions honest.

## Severity Model

Every test is either:

- `blocking`
- `advisory`

Blocking failures produce exit code `1`.

Advisory failures are visible in reports but do not block deployment when all blocking checks pass.

## AWS Runtime IAM Model

AWS checks execute real boto3 operations with the credentials already present in the environment.

This is important because InfraTest is verifying runtime behavior, not policy text.

The current repository supports:

- positive assertions: the operation must succeed
- negative assertions: the operation must fail with an expected access-denied code

## JSON Reporting Model

JSON output is now part of the stable execution path rather than a later enhancement.

The writer creates parent directories as needed and returns a controlled execution error if the report cannot be written.

## Current Limitations

Still intentionally missing:

- distributed execution
- hosted control plane
- auto-discovery from Terraform or cloud metadata
- multi-cloud provider abstractions
- parallel execution

These remain future architecture work, not current repository concerns.

## Sellable-Service Direction

The technically clean next step is to split the system into:

- customer-run execution plane
- separate control plane

That lets a future service schedule checks from the correct network zones without weakening trust in the result.
