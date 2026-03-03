# InfraTest — Execution Model & User Flow

## 📌 Purpose of This Document

This document defines **how InfraTest works conceptually and operationally**.

It answers the core questions:

* Where does InfraTest run?
* How does it interact with cloud infrastructure?
* How is it used inside deployment pipelines?
* What problem does it practically solve?
* What is the realistic V1 scope?

This serves as the foundational reference for development.

---

# 🚧 Problem Recap

Infrastructure provisioning success does **not** guarantee infrastructure correctness.

Typical workflow today:

```
terraform plan
terraform apply ✅
deployment assumed safe
```

However, real failures still occur:

* Services unreachable
* Incorrect networking rules
* Broken health checks
* Misconfigured IAM permissions
* Public exposure of internal resources
* DNS or routing failures

Infrastructure validation is mostly manual.

InfraTest introduces automated verification **after deployment**.

---

# 🎯 Core Idea

InfraTest acts as a:

> **Post-Deployment Infrastructure Validation Layer**

It verifies whether deployed infrastructure behaves according to expectations before application deployment proceeds.

---

# 🧭 Where InfraTest Runs

InfraTest runs **inside the user's execution environment**.

### Supported Execution Locations

* CI/CD runners (GitHub Actions, GitLab CI, Jenkins)
* Developer machines
* Build containers
* Automation runners

InfraTest **does NOT host or provision infrastructure**.

It operates using existing credentials already available to deployment pipelines.

---

## Execution Model

```
Customer Pipeline Environment
        │
        ├── Terraform Apply
        │
        └── InfraTest CLI
                │
                ▼
        AWS APIs + Network Checks
```

InfraTest uses:

* existing AWS credentials
* AWS SDK/API calls
* live connectivity validation

No external account delegation required.

---

# ⚙️ High-Level Deployment Flow

## Current Industry Workflow

```
Code Commit
    ↓
Terraform Apply
    ↓
Application Deployment
```

## Workflow With InfraTest

```
Code Commit
    ↓
Terraform Apply
    ↓
InfraTest Validation ✅
    ↓
Application Deployment
```

InfraTest becomes a deployment safety gate.

---

# 👤 User Workflow

## Step 1 — Install InfraTest

Example:

```
brew install infratest
```

or

```
pip install infratest
```

---

## Step 2 — Define Infrastructure Expectations

User creates:

`infra-test.yaml`

Example:

```yaml
tests:

  - name: api-health
    type: http
    endpoint: https://api.company.com/health
    expect_status: 200

  - name: rds-private
    type: aws_rds
    identifier: prod-db
    public_access: false

  - name: alb-connectivity
    type: tcp
    host: internal-alb.amazonaws.com
    port: 443
```

This file represents **expected infrastructure behavior**.

---

## Step 3 — Integrate Into Pipeline

Example CI step:

```yaml
- name: Deploy Infrastructure
  run: terraform apply -auto-approve

- name: Validate Infrastructure
  run: infratest run infra-test.yaml
```

---

## Step 4 — Execution Output

Example result:

```
Running Infrastructure Tests...

✔ api-health ........ PASS
✔ rds-private ....... PASS
✖ alb-connectivity .. FAIL

Reason:
Inbound traffic blocked by security group.

Deployment halted.
```

Pipeline stops automatically on failure.

---

# 🔍 What InfraTest Actually Validates

InfraTest performs three categories of checks.

---

## 1. Cloud State Validation

Queries cloud provider APIs.

Example:

* resource configuration
* accessibility flags
* deployment attributes

Example validation:

```
RDS.PubliclyAccessible == false
```

---

## 2. Network Connectivity Validation

Performs live connection attempts:

* TCP connectivity
* HTTP requests
* endpoint reachability
* port validation

Equivalent to automated smoke testing.

---

## 3. Behavioral Validation

Validates runtime expectations:

* health endpoints respond
* services reachable internally
* DNS resolution works

Focus is behavior, not configuration alone.

---

# 🚫 Non-Goals (V1)

InfraTest will NOT attempt:

* full AWS infrastructure simulation
* cost optimization analysis
* compliance auditing
* monitoring replacement
* chaos engineering
* multi-cloud orchestration

V1 scope remains intentionally narrow.

---

# 🧠 Design Philosophy

InfraTest follows these principles:

* Infrastructure should be tested like software
* Deployment success ≠ operational success
* Validation must be automated
* CI/CD integration must be trivial
* Developer workflow first
* Zero mandatory human interaction

---

# 🏗️ Conceptual Architecture

```
                +------------------+
                |  InfraTest CLI   |
                +------------------+
                          |
          -----------------------------------
          |                |               |
          ▼                ▼               ▼
     AWS SDK Calls   Network Checks   HTTP Validators
          |
          ▼
   Infrastructure State
```

The CLI acts as a lightweight execution engine.

---

# 🔐 Security Model

InfraTest:

* Uses existing IAM credentials
* Requires read-level permissions for validation
* Executes inside customer-controlled environments
* Does not persist infrastructure data externally

---

# 📈 Long-Term Evolution (Future)

Possible extensions:

* Hosted execution runners
* Test history tracking
* Deployment confidence scoring
* Infrastructure regression testing
* Drift detection
* Dashboard visualization

These are explicitly **post-V1 goals**.

---

# ✅ V1 Success Definition

InfraTest V1 succeeds if:

* A DevOps engineer can install it in minutes
* A pipeline can fail when infra behaves incorrectly
* Manual post-deploy verification reduces significantly

---

# 📌 Summary

InfraTest introduces a missing capability in modern infrastructure delivery:

> Automated validation of deployed infrastructure behavior.

Infrastructure should not only deploy successfully —
it should **prove correctness automatically**.

---
