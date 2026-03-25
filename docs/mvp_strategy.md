# InfraTest — MVP Strategy

## Current MVP Shape

InfraTest MVP is now a working CLI verification engine with three executable check families:

- HTTP behavior checks
- TCP reachability checks
- AWS runtime IAM checks

The MVP input remains an explicit YAML file. The product value is still the same: block unsafe deployments after provisioning and before application rollout.

## What The MVP Must Prove

The MVP is successful only if teams can trust it as a deployment gate.

That means the following are more important than feature count:

- deterministic exit codes
- low false-positive rates
- clear failure messages
- verification from the correct execution context

## What Changed In Scope

InfraTest now explicitly models execution context. This matters because a check from the wrong network zone creates false confidence.

Examples:

- a public runner cannot prove an internal load balancer works
- a developer laptop cannot prove a VPC-only database is reachable from an ECS task
- AWS IAM behavior checks only mean something when the command runs under the real workload credentials

The MVP therefore treats context as first-class input, not documentation.

## Supported Capabilities In This Repository

### HTTP

- exact or multi-status assertions
- retry policy and warmup delay
- redirect control
- final URL assertions
- expected header assertions
- JSON body subset assertions
- advisory vs blocking severity

### TCP

- open-port validation
- closed-port validation
- retry policy and warmup delay
- advisory vs blocking severity

### AWS Runtime IAM

- executes real boto3 client operations
- supports positive and negative access expectations
- supports expected AWS error-code matching
- uses runtime credentials already available in the environment

## MVP Commercialization Threshold

This repository is credible as a customer-run execution engine.

It is not yet a hosted SaaS product.

To sell it safely as a service, the next architectural layer should be:

- control plane for configuration, history, and team workflows
- customer-run agents or runners inside the right network boundaries
- context-aware scheduling so checks run from the right vantage point

Without that separation, private-network validation claims are weak.

## Immediate KPIs

- first-run setup under 10 minutes
- fully deterministic test suite in CI
- blocking failures stop deployment reliably
- advisory failures remain visible without stopping deployment
- at least one real infrastructure issue caught before rollout

## Short-Term Roadmap

### Phase 1

- stabilize the current HTTP, TCP, and AWS validators in real pilot environments
- capture real failure examples and reduce false positives

### Phase 2

- add more AWS runtime checks for common services
- add better negative-path network assertions
- add richer response assertions where customers need them

### Phase 3

- add control-plane concepts without weakening the customer-run execution model

## Anti-Scope Still Applies

The MVP must still avoid:

- dashboards before execution trust is earned
- policy-engine sprawl
- generic workflow orchestration
- hosted execution that cannot reach private customer networks

## Guiding Principle

InfraTest should make an engineer comfortable saying:

> This environment was verified from the right place, with the right credentials, against the right behaviors.
