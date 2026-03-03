# InfraTest — System Architecture V1

## Purpose

This document defines the internal architecture of InfraTest Version 1.

The goal of this architecture is simplicity, extensibility, and fast iteration.

InfraTest V1 prioritizes development speed and usability over scalability or optimization.

This architecture intentionally avoids distributed systems, backend services, or complex abstractions.

InfraTest must remain a local-first verification engine.

---

## Technology Decision

Primary Language: Python

Reasoning:

* Fast development velocity
* Strong cloud SDK ecosystem
* Excellent AWS integration via boto3
* Easy experimentation
* Lower cognitive overhead for solo development
* Ideal for early-stage validation

Performance is not a concern for MVP.

Execution clarity and iteration speed are higher priorities.

---

## High-Level Architecture

InfraTest operates as a command-line verification engine.

Execution Flow:

User runs InfraTest CLI
→ InfraTest collects environment context
→ Validation engine executes checks
→ Results aggregated
→ Deployment decision returned

No persistent services exist in V1.

---

## System Overview

Architecture Layers:

CLI Layer
Core Engine
Validation Modules
Cloud Providers
Reporting System

Each layer has a single responsibility.

---

## Layer 1 — CLI Layer

Responsibilities:

* command parsing
* argument handling
* execution trigger
* exit code management
* user interaction

Example commands:

infratest verify
infratest verify --auto-discover
infratest verify --output json

Implementation Recommendation:

Use Python argparse or typer.

CLI must remain thin.

Business logic must never exist here.

---

## Layer 2 — Core Engine

This is the heart of InfraTest.

Responsibilities:

* orchestration of validations
* execution lifecycle
* module loading
* timeout handling
* result aggregation

Core Engine Flow:

Initialize runtime
Load validation modules
Execute validations sequentially
Collect results
Compute environment readiness
Return final verdict

The engine does not know cloud-specific logic.

It only coordinates execution.

---

## Layer 3 — Validation Modules

Validation modules perform actual infrastructure checks.

Each validation represents one confidence signal.

Examples:

ReachabilityCheck
NetworkConnectivityCheck
IAMRuntimeCheck
DependencyHealthCheck

Design Rule:

Each validation must be independent.

Validation modules must:

* accept context
* perform check
* return structured result

Expected Output Structure:

status
message
metadata
severity
execution_time

Failures must never crash InfraTest.

Failures must only return failed validation results.

---

## Layer 4 — Cloud Provider Layer

Responsible for interacting with cloud infrastructure.

V1 supports:

AWS only.

Responsibilities:

* resource discovery
* credential usage
* runtime access testing
* metadata retrieval

Implementation:

Use boto3 SDK.

Provider logic must remain isolated so additional providers can be added later without rewriting validation logic.

Validation modules request data through provider interfaces.

They must not directly call cloud SDKs.

---

## Layer 5 — Context Discovery System

InfraTest should automatically discover environment details when possible.

Sources include:

Terraform outputs
Environment variables
AWS metadata APIs
Runtime endpoints

Goal:

Reduce required configuration.

Preferred user experience:

infratest verify --auto-discover

Manual configuration is fallback only.

---

## Layer 6 — Reporting System

Responsible for presenting results.

Outputs:

Human-readable console report
Machine-readable JSON output

Example Console Output:

InfraTest Verification Report

DNS Resolution PASS
Load Balancer Reachability PASS
Service Connectivity FAIL

Environment Score: 75%
Deployment Blocked

Reporting must remain simple and readable.

No visualization systems in V1.

---

## Execution Model

Execution Style:

Synchronous execution.

Parallel execution is intentionally avoided initially to simplify debugging and reliability.

Optimization can occur later.

---

## Error Handling Philosophy

InfraTest must never fail silently.

Rules:

Infrastructure failure → validation failure
InfraTest bug → explicit error message
Cloud timeout → failed validation

InfraTest crashing equals loss of trust.

Stability is mandatory.

---

## Exit Codes

InfraTest integrates with CI/CD through exit codes.

0 → Environment Verified
1 → Validation Failed
2 → InfraTest Execution Error

This enables pipeline gating.

---

## Repository Structure Recommendation

src/

cli/
engine/
validators/
providers/
reporting/
utils/

Example:

src/infratest/
src/infratest/cli
src/infratest/engine
src/infratest/validators
src/infratest/providers/aws
src/infratest/reporting

Clear boundaries prevent architecture drift.

---

## Dependency Philosophy

Dependencies must remain minimal.

Allowed:

boto3
requests
typer or argparse
pydantic (optional)

Avoid heavy frameworks.

InfraTest must remain lightweight.

---

## Observability (Internal Only)

Logging allowed:

info
warning
error

No telemetry collection in V1.

User trust comes before analytics.

---

## Security Principles

InfraTest never stores credentials.

InfraTest uses existing cloud authentication:

AWS CLI credentials
IAM roles
environment credentials

No secret persistence.

---

## Future Compatibility

Architecture must allow:

Parallel execution
Plugin system
Multi-cloud providers
Hosted verification service

But these must not influence V1 complexity.

---

## Architectural Guiding Rule

InfraTest is a verification engine.

Not a platform.
Not a service.
Not an orchestrator.

Every architectural decision must preserve simplicity.

---

## Final Principle

If InfraTest becomes harder to understand than the infrastructure it validates, the architecture has failed.
