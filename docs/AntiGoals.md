# InfraTest — Anti Goals

## Purpose

This document defines what InfraTest must intentionally avoid building during its early stages.

Startups and side projects rarely fail because of lack of ideas.
They fail because of uncontrolled expansion and premature complexity.

InfraTest must remain focused on solving one core problem:

Preventing unsafe infrastructure deployments by verifying real infrastructure behavior.

Anything that distracts from this goal is considered an anti-goal.

This document exists to protect development focus for both humans and AI agents working on InfraTest.

If future development proposals conflict with this document, the proposal should be rejected or postponed.

---

## Core Principle

InfraTest is not trying to solve all infrastructure problems.

InfraTest solves only one problem:

"Does this infrastructure actually work before deployment?"

Every feature must directly increase deployment confidence.

If it does not, it does not belong in early InfraTest.

---

## Anti Goal 1 — Building a Dashboard Too Early

InfraTest must not start with a web UI or dashboard.

Dashboards create the illusion of progress without delivering real value.

Early users care about one thing only:

Does my deployment fail safely?

A CLI providing pass or fail validation is sufficient for MVP.

Dashboards introduce unnecessary complexity including:

* authentication systems
* backend services
* hosting costs
* state management
* UI maintenance

No dashboard should be built until InfraTest is already preventing real failures in production environments.

---

## Anti Goal 2 — Becoming Another Terraform Wrapper

InfraTest must never attempt to replace Terraform or act as an orchestration layer.

Terraform already solves infrastructure creation.

InfraTest exists after provisioning succeeds.

InfraTest validates behavior, not resource definition.

Avoid features such as:

* infrastructure provisioning
* deployment orchestration
* state manipulation
* Terraform execution management

InfraTest observes infrastructure.
It does not create infrastructure.

---

## Anti Goal 3 — Policy or Compliance Engine

InfraTest is not a policy enforcement system.

Tools already exist for static validation and compliance checking.

InfraTest must avoid:

* policy-as-code systems
* rule engines
* governance workflows
* compliance reporting frameworks

Configuration correctness is not the same as behavioral correctness.

InfraTest validates runtime reality, not configuration intent.

---

## Anti Goal 4 — Creating a Complex Custom DSL

Creating a proprietary configuration language or scripting DSL early will significantly reduce adoption.

Engineers do not want to learn another syntax to verify infrastructure.

Acceptable in V1:

* a small, explicit YAML file (`infra-test.yaml`)

Avoid introducing:

* rule scripting languages
* custom parser ecosystems
* complex declarative abstractions that require domain training

InfraTest should move toward lower configuration over time,
but V1 keeps YAML simple and practical.

---

## Anti Goal 5 — Multi-Cloud Support in Early Phases

Supporting multiple cloud providers too early dramatically increases complexity.

Each provider introduces different networking, IAM, and service behavior models.

InfraTest must initially support only:

AWS.

Depth of validation is more valuable than breadth of compatibility.

Multi-cloud support may be considered only after strong validation success in one ecosystem.

---

## Anti Goal 6 — Kubernetes-First Development

Kubernetes introduces exponential complexity.

Although Kubernetes is important, starting there risks turning InfraTest into cluster tooling rather than infrastructure verification.

InfraTest should first validate foundational infrastructure:

* networking
* IAM permissions
* service reachability
* cloud dependencies

Kubernetes validation should come later.

---

## Anti Goal 7 — AI or Agent Automation Before Product Value

AI agents should not define product direction.

Automation amplifies clarity but cannot replace product-market validation.

Avoid early development of:

* autonomous infrastructure agents
* AI-driven remediation
* intelligent self-healing systems
* automated decision engines

InfraTest must first prove that its core verification delivers value.

Intelligence comes after usefulness.

---

## Anti Goal 8 — Enterprise Features Too Early

Enterprise workflows must not be implemented during MVP stages.

Avoid building:

* RBAC systems
* organization management
* audit portals
* enterprise integrations
* billing platforms
* permission hierarchies

Enterprise features should follow proven adoption, not precede it.

---

## Anti Goal 9 — Persistent Backend Services

InfraTest must initially operate as a standalone executable.

Avoid introducing:

* centralized servers
* hosted APIs
* databases
* telemetry storage systems
* always-running agents

A simple executable lowers adoption friction and increases trust.

---

## Anti Goal 10 — Solving Every Infrastructure Problem

InfraTest is not:

* observability tooling
* monitoring software
* deployment automation
* incident management
* configuration management
* platform engineering replacement

Scope expansion is the greatest risk to InfraTest’s success.

InfraTest focuses only on infrastructure readiness verification.

---

## Decision Filter

Before implementing any feature, ask:

1. Does this prevent a broken deployment?
2. Does this increase infrastructure confidence?
3. Would an engineer immediately understand its value?
4. Can this run inside CI/CD without additional systems?

If the answer to any question is no, the feature should be postponed.

---

## Long-Term Reminder

The goal of InfraTest is not feature richness.

The goal is trust.

Engineers should eventually feel comfortable saying:

"If InfraTest passes, deployment is safe."

Anything that weakens this clarity must be avoided.
