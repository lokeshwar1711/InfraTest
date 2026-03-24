# InfraTest — Infrastructure Validation After Deployment

## 🚧 Problem

Modern infrastructure is provisioned using Infrastructure as Code tools such as Terraform, CloudFormation, or Pulumi.

A typical deployment pipeline looks like:

```
terraform plan
terraform apply
application deployment
```

If infrastructure provisioning succeeds, teams usually assume the environment is ready.

However, **successful deployment does not guarantee functional infrastructure**.

Common real-world failures still occur:

* Services are unreachable despite successful deployment
* Security groups block required traffic
* Load balancer health checks fail
* DNS resolution is incorrect
* Internal services become publicly accessible
* IAM permissions do not behave as expected

These issues are often discovered **late**, during application deployment or production usage.

Today, infrastructure correctness is mostly verified through:

* manual validation
* ad-hoc scripts
* tribal knowledge
* post-failure debugging

Software systems have automated tests.

Infrastructure largely does not.

---

## 🎯 Vision

InfraTest aims to introduce a missing layer in modern delivery pipelines:

> **Automated Infrastructure Testing after deployment.**

Similar to how unit tests validate application behavior,
InfraTest validates **deployed infrastructure behavior**.

The goal is simple:

```
Provision Infrastructure
        ↓
Validate Infrastructure ✅
        ↓
Deploy Applications Safely
```

---

## ✅ What InfraTest Does (V1)

InfraTest runs automated assertions against live infrastructure immediately after deployment.

Initial focus:

* Endpoint reachability checks
* Internal vs public accessibility validation
* Port connectivity verification
* DNS resolution validation
* Health endpoint verification

Example:

```yaml
tests:
  - name: api-health
    type: http
    endpoint: https://api.example.com/health
    expect_status: 200

  - name: database-private
    type: connectivity
    host: db.internal
    public_access: false
```

InfraTest executes these checks and returns:

```
PASS ✅
or
FAIL ❌
```

allowing CI/CD pipelines to stop unsafe deployments early.

---

## 🧩 Where It Fits

Typical CI/CD workflow:

```
Terraform Apply
        ↓
InfraTest Verify
        ↓
Application Deployment
```

InfraTest acts as a **post-deployment infrastructure validation layer**.

---

## 👤 Who This Is For

* DevOps Engineers
* Platform Engineers
* SRE Teams
* Startup engineering teams managing AWS infrastructure
* Teams using Terraform-based deployments

Especially useful where infrastructure validation is currently manual.

---

## 🚫 Non-Goals (V1)

InfraTest is **not**:

* a cloud cost optimization platform
* a security compliance scanner
* a chaos engineering framework
* a monitoring system
* a multi-cloud governance platform

The focus is intentionally narrow:

> Validate that deployed infrastructure behaves as expected.

---

## ⚙️ Design Principles

* Simple installation
* CI/CD friendly
* Declarative testing
* Cloud-account minimal permissions
* Fast feedback after deployment
* Developer-first workflow

---

## 🚀 Current Status

✅ MVP implemented (HTTP validation engine, YAML-driven CLI, CI exit-code contract).

Initial work focuses on defining:

* core validation model
* execution engine
* pipeline integration workflow

---

## 🛠️ Quick Start

### 1) Install

```bash
pip install -e .
```

### 2) Run Verification

```bash
infratest verify infra-test.yaml
```

### 3) CI-Friendly JSON Report

```bash
infratest verify infra-test.yaml --output both --output-path infratest-report.json
```

Exit code contract:

* `0` = all checks passed
* `1` = one or more checks failed
* `2` = InfraTest execution/configuration error

---

## 🧪 Example YAML

```yaml
tests:
        - name: api-health
                type: http
                endpoint: https://api.example.com/health
                expect_status: 200
                method: GET
                timeout: 5
```

---

## 🗺️ Roadmap (Early Thoughts)

* [ ] Basic connectivity assertions
* [ ] HTTP health validation
* [ ] DNS checks
* [ ] CI/CD integration
* [ ] Terraform workflow examples
* [ ] AWS-first support

---

## 💡 Why Now?

Infrastructure complexity continues to grow, while deployment velocity increases.

Automated infrastructure validation helps teams ship faster with confidence by catching environmental failures before they reach production.

---

## 📌 Philosophy

Infrastructure should be **tested**, not trusted.

---
