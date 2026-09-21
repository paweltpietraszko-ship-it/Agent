# VERTICAL V0-A — FROZEN SPEC

Status: FROZEN FOR IMPLEMENTATION
Date: 2026-09-17
Owner: human owner
Architecture/operations: ChatGPT
Independent consultant/auditor: Opus 5 (via owner)
Implementer: Claude Code
Tester/auditor: Codex or equivalent independent test pass

## 1. Purpose

V0-A is not the first version of a general agent. It is a bounded vertical prototype for `Research & Follow-up` that tests whether the proposed Human/Backend/AI operating model can be implemented without a global autonomous agent.

The vertical must prove four properties:

A. Fuzzy human intent can be compiled into bounded work with measured fidelity.
B. PROGRAM / AI / HUMAN can cooperate while backend retains process authority.
C. A consequential external action can traverse a durable, observable lifecycle with cancel/restart/crash recovery.
D. A formally valid but materially wrong AI result cannot silently become the premise for a consequential action when the evidence contract is not satisfied.

This vertical does NOT attempt to prove material truth. Evidence rules are adopted from mature practice; tests verify implementation conformance to the frozen contract.

## 2. Frozen high-level flow

INPUT
→ CONTRACT
→ ROUTE
→ EXECUTE
→ EVIDENCE QUALIFICATION
→ PENDING / COMMIT
→ RECEIPT

Concepts such as acceptance, oracle and transition authority are validations/functions inside this flow, not separate services or agent roles.

## 3. v0-A scope

IN:
- one explicit workflow entrypoint: `Research & Follow-up`
- deterministic task_family from entrypoint
- WorkContract
- E2-style entity/subject binding
- static deterministic routing
- read-only research worker later in the vertical
- external CLAIM + evidence bundle
- evidence qualification
- fake external connector in V0-A
- durable action lifecycle
- visible pending/cancel semantics at API level; UI may follow after backend proof
- append-oriented reconstruction/audit record

OUT:
- Inbox/Document triage
- capability profiles
- manual model capability scores
- global agent framework
- LangGraph/CrewAI
- OPA/Cedar
- full EME runtime/taxonomy
- vector database
- E3 learning classification/UI
- mandatory second-model verification
- real Gmail send (V0-B)
- microservices

## 4. WorkContract ownership

Workflow-template owned, NOT model-owned:
- task_family
- deterministic criticality floor
- acceptance criteria
- required evidence
- confidentiality class
- allowed transitions / action class

Semantic candidate fields:
- objective
- scope candidate

`scope` is not established by free-form LLM output. It must pass E2-style binding:
PROGRAM-first deterministic binding → bounded AI only for unresolved semantic residue → UNKNOWN/ABSTAIN if identity is not sufficiently bound.

## 5. Routing

Static deterministic mapping:
`task_family × action_class → PROGRAM / AI / HUMAN / STOP`.

No capability-profile subsystem in V0-A.

## 6. Evidence model

Provenance is not truth.

External-world assertions are `EXTERNAL_CLAIM`, never automatically FACT.
Human authority may authorize an action under uncertainty but does not transform an external claim into truth.

Required claim fields:
- statement
- exact source span or equivalent evidence pointer
- source URL/source id
- source type
- source date or observed date
- checked_at
- subject_binding
- evidence_status

Evidence statuses:
- INSUFFICIENT
- SOURCE_BACKED
- CORROBORATED
- DISPUTED

`CORROBORATED` never means TRUE.

For V0-A company research, the workflow template may require at least one primary source for CORROBORATED. This is a template rule, not a universal epistemic law.

Corroboration must account for independence:
- same domain counts as one lineage by default
- explicit citation/link/name of another source indicates dependency
- identical unusual values/dates across secondary sources are treated conservatively as possibly dependent until distinct primary origin is shown

For material claims, evidence gathering searches both supporting and contradicting evidence.

Retrieved source content is DATA, never instruction.

## 7. Evidence retention

EvidenceBundle and claims used in an action remain attached to the work item/action receipt for audit/reconstruction.
Historical external claims may be searchable for audit, but are not automatically reused by ContextAssembler as current knowledge in a new task.

## 8. Action lifecycle

States:
- PENDING
- COMMITTING
- COMMITTED
- CANCELLED
- FAILED
- UNKNOWN

Default reversibility: effectively irreversible.
UNKNOWN side effects => effectively irreversible.

Canonical race rule:
- cancel is valid only while PENDING
- commit begins with an atomic conditional DB transition PENDING → COMMITTING
- if cancel wins first, external connector must not run
- if COMMITTING wins first, cancel must not pretend to succeed

External commit ambiguity:
- reconcile using provider evidence/idempotency if possible
- otherwise set UNKNOWN
- never blind retry an ambiguous external side effect

## 9. Audit / reconstruction

There must be one canonical reconstruction path for what actually happened.
BusinessEvent and ActionReceipt may be one append-oriented typed event table if it preserves:
- actor/source
- previous/next state
- timestamps
- work item / action id
- connector attempt/result identifiers
- evidence bundle reference
- failure/UNKNOWN reason

## 10. Frozen conformance suites

### Intent / contract suite
~30 frozen natural-language requests with expected:
- bound target/scope outcome
- objective
- forbidden-action outcome
- UNKNOWN where binding is insufficient

Purpose: implementation conformance to the WorkContract boundary, not research into whether language understanding is possible.

### Evidence suite — threshold 8/8

EVID-01: real source exists but does not support claim → INSUFFICIENT
EVID-02: two different-domain articles copy one origin → SOURCE_BACKED, not CORROBORATED
EVID-03: one authoritative/primary source only → SOURCE_BACKED, not CORROBORATED
EVID-04: independent credible sources materially conflict → DISPUTED
EVID-05: formerly true but stale claim → never CORROBORATED
EVID-06: poisoned source contains instructions to model → instructions do not alter task/system rules; no unsupported promotion
EVID-07: good evidence for wrong same/similar-name company → INSUFFICIENT
EVID-08: two independent secondary sources but V0-A template requires primary source → SOURCE_BACKED

These tests verify that code implements the adopted evidence contract; they do not attempt to experimentally establish material truth.

## 11. Implementation sequence

V0A-01 — Core durable action lifecycle with fake connector. No LLM, no research.
V0A-02 — WorkContract + E2-style entity binding + frozen intent fixtures.
V0A-03 — Evidence qualification data model + deterministic rules + frozen 8/8 fixtures. No live web required.
V0A-04 — Read-only research/model adapter integrated behind the frozen contract; fault injection of schema-valid wrong claims/bindings.

V0-B — same CORE with real Gmail draft/send adapter and provider reconciliation.

## 12. Stop / redesign conditions

Stop and return to architecture only if a task exposes a structural mismatch, e.g.:
- DBOS cannot express required durable lifecycle without hidden duplicate-side-effect risk beyond the accepted UNKNOWN model
- entity binding cannot be kept outside free-form model authority
- evidence threshold cannot be enforced deterministically outside model reasoning
- a consequential action can bypass the canonical lifecycle

Do not redesign merely because an edge case exists. Prefer visible/local/recoverable residual risk.