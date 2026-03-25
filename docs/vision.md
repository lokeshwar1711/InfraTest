# InfraTest — Execution Model & User Flow

## What This Repository Represents

InfraTest is currently a customer-run execution engine.

It runs inside a developer machine, CI runner, build container, or customer-controlled automation environment and performs live infrastructure verification from that location.

## Current Operating Model

InfraTest is used after provisioning and before application rollout:

```text
terraform apply
infratest verify infra-test.yaml --context private-runner
application deployment
```

The `--context` flag is not cosmetic. It declares where the check is actually running from, which is required for private-network and credential-scoped assertions to mean anything.

## What Users Can Verify Today

### HTTP

- public and private endpoints
- redirect behavior
- final destination URL
- expected headers
- expected JSON body subset
- retry and warmup behavior

### TCP

- service ports that must be reachable
- ports that must stay closed from a given context

### AWS Runtime IAM

- real AWS client calls using environment credentials
- positive allow checks
- negative deny checks with expected AWS error codes

## Practical User Flow

1. Provision infrastructure
2. Choose the runner or agent that represents the required network context
3. Provide the active context labels to the CLI
4. Run InfraTest with a declarative YAML file
5. Gate deployment on blocking failures

## Why This Matters For A Sellable Service

The hard product problem is not only check execution. It is trustworthy execution from the correct place.

That is why the likely service shape is:

- a control plane for configuration, history, and orchestration
- customer-run execution nodes in public, VPN, VPC, or workload-local contexts

This repository is the execution-plane foundation for that model.

## What This Repository Does Not Claim Yet

It does not yet provide:

- hosted dashboards
- centralized scheduling
- agent fleet management
- automatic infrastructure intent discovery
- private-network reachability from hosted infrastructure you do not control

Those should come later, on top of a trusted execution model.
