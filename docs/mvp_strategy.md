# InfraTest — MVP Strategy

## Purpose

This document defines the execution strategy for building the first usable version of InfraTest.

The goal of the MVP is NOT completeness.

The goal is to deliver measurable infrastructure confidence as quickly as possible.

This document constrains development scope to prevent over-engineering.

---

# MVP Definition

InfraTest MVP is:

> A CLI tool that verifies infrastructure readiness after deployment and prevents unsafe application releases.

InfraTest must answer:

"Is this environment safe to deploy into?"

---

# Non-Goals (Critical)

The MVP must NOT include:

- SaaS dashboards
- Web UI
- Multi-cloud support
- Plugin systems
- Custom DSLs
- AI automation
- Complex configuration
- Kubernetes-native orchestration
- Enterprise workflows

If a feature does not directly increase deployment confidence, it must be rejected.

---

# Target User

Primary User:

Platform Engineers / DevOps Engineers who:

- Use Terraform
- Deploy to AWS
- Maintain staging or production environments
- Experience post-deployment infrastructure failures

---

# MVP Workflow

Expected usage:

terraform apply
|
infratest verify


Output:

Environment Ready ✅
or
Deployment Unsafe ❌



InfraTest integrates naturally into CI/CD pipelines.

---

# MVP Success Criteria

The MVP succeeds if:

- A team detects at least one real infrastructure issue before deployment
- InfraTest runs inside CI pipelines
- Engineers trust InfraTest output
- Setup time is under 5 minutes

---

# Supported Platform (Phase 1)

Cloud Provider:
- AWS ONLY

Infrastructure Sources:
- Terraform Outputs
- Environment Metadata
- Runtime Connectivity Checks

Avoid abstraction layers early.

Depth over breadth.

---

# Core Validation Categories

InfraTest MVP implements only the following validations.

---

## 1. Service Reachability Validation

Goal:
Verify externally or internally exposed services respond correctly.

Examples:
- Load balancer reachable
- DNS resolves
- HTTP endpoint responds
- Port accessibility

Checks:
- DNS resolution
- TCP connectivity
- HTTP status validation

---

## 2. Network Connectivity Validation

Goal:
Confirm services can communicate as expected.

Examples:
- App → Database connectivity
- Service → Internal API reachability

Checks:
- Port access
- Route validation
- Security group behavior
- Internal DNS resolution

---

## 3. Runtime IAM Permission Validation

Goal:
Verify permissions work during execution.

Examples:
- EC2 accessing S3
- Service role accessing secrets
- Application accessing queues

Method:
Real authentication attempt instead of policy inspection.

---

## 4. Dependency Availability Validation

Goal:
Ensure required infrastructure dependencies are usable.

Examples:
- Database reachable
- Cache reachable
- Message queue accessible

---

# Expected CLI Output

Example:

InfraTest Verification Report

DNS Resolution ✅ PASS
Load Balancer Reachability ✅ PASS
Service Connectivity ❌ FAIL
IAM Runtime Access ✅ PASS

Environment Score: 75%
Deployment Blocked


Output must be human-readable first.

Machine-readable output comes later.

---

# Architecture Overview

Terraform Outputs
↓
InfraTest CLI
↓
Validation Engine
↓
Check Modules
↓
Pass / Fail Result

InfraTest must run without persistent services.

---

# Configuration Philosophy

Configuration must be minimal.

Preferred approach:

infratest verify --auto-discover


InfraTest should infer expectations whenever possible.

Manual configuration is last resort.

---

# Development Phases

---

## Phase 0 — Bootstrap

Goals:
- CLI skeleton
- Command parsing
- Logging system
- Result reporting

Deliverable:
Working CLI executable.

---

## Phase 1 — First Validation

Implement:
- HTTP reachability check

Goal:
Catch real failures quickly.

Ship immediately after working.

---

## Phase 2 — Connectivity Checks

Add:
- TCP connectivity validation
- Internal service access tests

Goal:
Detect networking issues.

---

## Phase 3 — IAM Runtime Checks

Add:
- AWS credential execution tests

Goal:
Differentiate InfraTest from existing tools.

---

## Phase 4 — CI Integration

Support:
- Exit codes
- JSON output
- Pipeline blocking

InfraTest becomes deployment gate.

---

# Explicit Anti-Scope Rules

Reject features involving:

- dashboards
- authentication systems
- user accounts
- hosted backend
- metrics storage
- visualization

InfraTest is a verification engine first.

---

# MVP Completion Definition

MVP is complete when:

- InfraTest blocks a broken deployment in real usage
- At least one external team can run it successfully
- CI integration works reliably

Do not expand scope before this point.

---

# Post-MVP Direction (Preview Only)

After validation:

Possible expansions:

- Environment scoring
- Continuous verification
- Drift detection
- Kubernetes validation
- Hosted SaaS layer

These are NOT MVP concerns.

---

# Guiding Principle

InfraTest should make engineers feel:

"I trust this environment."

Every feature must move toward that outcome.
