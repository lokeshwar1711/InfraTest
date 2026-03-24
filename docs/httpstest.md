# InfraTest — First Test Architecture (HTTP Validation Engine)

## 📌 Purpose

This document defines the architecture of the **first executable capability** of InfraTest.

The objective is to validate the InfraTest execution model through a minimal but meaningful infrastructure test.

---

# 🎯 Objective of First Test

The first supported validation:

> Verify that a deployed HTTP endpoint responds as expected after infrastructure provisioning.

This represents the smallest valuable infrastructure behavior check.

---

# 🧠 Why HTTP Validation First

Nearly all infrastructure deployments expose HTTP-based services:

* Application Load Balancers
* API Gateway endpoints
* ECS services
* Kubernetes ingress
* internal service endpoints

Failures frequently occur despite successful provisioning.

---

## Common Failure Scenarios

* incorrect security groups
* failing health checks
* routing misconfiguration
* DNS propagation delays
* service startup failure
* blocked ports

Terraform deployment success does not detect these issues.

---

# 🧭 Position in Deployment Pipeline

```
Terraform Apply
        ↓
InfraTest HTTP Validation
        ↓
Application Deployment
```

InfraTest becomes a deployment confidence gate.

---

# 🧱 Architectural Overview

```
CLI Command
     ↓
Configuration Loader
     ↓
Model Validation
     ↓
Execution Engine
     ↓
HTTP Runner
     ↓
Result Aggregation
     ↓
Terminal Output
```

Each component remains independently extensible.

---

# ⚙️ Execution Lifecycle

## Step 1 — CLI Invocation

User executes:

```
infratest verify infra-test.yaml
```

CLI responsibilities:

* load configuration path
* initiate execution engine
* manage exit codes

---

## Step 2 — Configuration Loading

YAML configuration parsed into structured data.

Example:

```yaml
tests:
  - name: api-health
    type: http
    endpoint: https://api.example.com/health
    expect_status: 200
    timeout: 5
```

---

## Step 3 — Schema Validation

Configuration validated via Pydantic models.

Ensures:

* required fields exist
* correct types
* early failure detection

Invalid configuration must fail before execution.

---

## Step 4 — Test Dispatching

Execution engine routes tests based on type.

Example:

```
type=http → HTTP Runner
```

Future extensibility:

```
aws_rds
tcp
dns
iam
```

---

# 🌐 HTTP Runner Architecture

Core responsibility:

Validate endpoint behavior.

---

## Execution Steps

### 1. Connection Attempt

HTTP request initiated using httpx client.

Parameters:

* endpoint URL
* timeout
* HTTP method

---

### 2. Response Capture

System records:

* status code
* latency
* connection errors

---

### 3. Assertion Evaluation

Validation logic:

```
response.status_code == expected_status
```

Failure categories:

* timeout
* DNS failure
* connection refused
* unexpected status

---

### 4. Result Generation

Structured result object created.

Example:

```
TestResult(
    name="api-health",
    success=True,
    message="200 OK"
)
```

---

# 📊 Result Aggregation

Execution engine collects all results.

Responsibilities:

* summarize outcomes
* determine global success
* prepare output layer

---

# 🎨 Output Rendering

Rich-based renderer produces readable output.

Example:

```
Running Infra Tests...

✔ api-health ........ PASS
✖ auth-service ...... FAIL
```

---

# 🚦 Exit Code Behavior

Critical for automation.

| Result         | Exit Code |
| -------------- | --------- |
| All tests pass | 0         |
| Any test fails | 1         |

Allows CI systems to halt deployment automatically.

---

# 🔄 Retry Strategy (Future)

Initial version executes single attempt.

Future enhancements:

* retry policies
* backoff strategy
* warmup delays

Not included in V1.

---

# ⚡ Performance Considerations

V1 executes sequentially.

Future:

* async parallel tests
* connection pooling
* grouped execution

---

# 🔐 Security Considerations

HTTP validation:

* performs outbound requests only
* stores no payload data
* requires no elevated permissions

Safe default execution model.

---

# 🚫 Explicit Non-Goals

First test will NOT include:

* authentication handling
* AWS API validation
* SSL certificate inspection
* traffic simulation
* load testing

Scope intentionally minimal.

---

# ✅ Definition of Success

First test architecture succeeds when:

* CLI runs reliably
* endpoint validation executes
* failures detected automatically
* CI pipelines react correctly

---

# 🧭 Evolution Path

HTTP validation enables future layers:

1. TCP validation
2. DNS verification
3. AWS resource assertions
4. IAM behavior checks
5. Infrastructure regression testing

The HTTP test forms the foundational execution engine.

---

# 📌 Foundational Principle

> Infrastructure correctness begins with verifying real behavior, not configuration state.

InfraTest validates reality.
