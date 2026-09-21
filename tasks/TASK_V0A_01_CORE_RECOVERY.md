# TASK V0A-01 — CORE DURABLE ACTION LIFECYCLE

Status: FROZEN FOR IMPLEMENTATION — 2026-09-21 (scope/process adaptation; technical acceptance unchanged)
TASK_ID: TASK_V0A_01_CORE_RECOVERY
BRANCH: task/TASK_V0A_01_CORE_RECOVERY
AUDIT_TIER: CRITICAL
MAX_NEW_FILES: 30
TOTAL_LINES_THRESHOLD: 2500

Parent: VERTICAL V0-A — FROZEN SPEC
Purpose: falsify or validate DBOS + PostgreSQL as the durable runtime for the canonical pending-action lifecycle before any LLM/research code exists.

## Mechanically enforced task scope

TASK_SCOPE:
- app/**
- migrations/**
- tests/**
- alembic.ini
- pyproject.toml
- docker-compose.yml
- V0A01_REPORT.md

Read-only context: `docs/VERTICAL_V0A_FROZEN_SPEC.md`, `docs/PRODUCT_GOAL_AND_ROADMAP.md`, `CLAUDE.md`, `CC_START_HERE.md`, `docs/PROCESS.md`. Do not edit these, the task brief, or anything under `harness/`, `.github/`, `.githooks/`. The implementation is generic and fake-only; Ridgeway is NOT a source of new product requirements.

Branch naming is intentional: the existing brief path is `tasks/TASK_V0A_01_CORE_RECOVERY.md`, so `task/TASK_V0A_01_CORE_RECOVERY` is the matching branch for the current GitHub gate. Initialize bookkeeping with `python harness/task_init.py TASK_V0A_01_CORE_RECOVERY`. Do not create a duplicate brief just to shorten the branch name.

If a necessary implementation file falls outside TASK_SCOPE: STOP the affected change; report the exact missing path, purpose and smallest proposed amendment via `BOARD.md`. Neither CC nor the harness may silently expand the frozen scope. The two numerical limits are capacity/decision tripwires for this new-code task, not a request to create 30 files or 2500 lines. Prefer less code.

## Role

Implementer writes only this bounded spike. Do not add AI, EME, Gmail, search, UI framework, policy engine, agent framework, capability profiles, or generic workflow abstractions.

## Required stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- DBOS Transact Python
- pytest

Use current DBOS datasource APIs rather than legacy transaction APIs where practical.

## Required domain model

### action
Minimum fields:
- id
- work_item_id (may be synthetic UUID in this task)
- state: PENDING | COMMITTING | COMMITTED | CANCELLED | FAILED | UNKNOWN
- execute_after
- action_type (for task: FAKE_EXTERNAL)
- payload_hash
- created_at
- updated_at
- connector_attempt_id nullable
- connector_result_id nullable
- failure_reason nullable
- unknown_reason nullable

### event
One canonical append-oriented reconstruction stream. Minimum:
- id
- action_id
- event_type
- from_state nullable
- to_state nullable
- occurred_at
- metadata JSON

No separate business_event + receipt tables unless a concrete test forces separation.

## Required API surface

Keep it minimal:
- POST /actions — create PENDING fake external action with execute_after and payload
- POST /actions/{id}/cancel — cancel iff state == PENDING
- GET /actions/{id} — inspect canonical state
- GET /actions/{id}/events — reconstruct action history

An internal/start mechanism must ensure DBOS durable workflow exists for each accepted PENDING action.

## Canonical workflow

1. Persist PENDING action and corresponding event.
2. Durably wait until execute_after using DBOS durable sleep.
3. Atomically claim action with conditional transaction `PENDING -> COMMITTING`.
4. If claim fails because action is no longer PENDING, do not call connector.
5. Call fake connector exactly according to scenario.
6. On unambiguous success, persist COMMITTED plus connector result id and event.
7. On unambiguous pre-effect failure, persist FAILED.
8. On ambiguous outcome where external effect may have occurred but local proof is unavailable, persist UNKNOWN and DO NOT blind retry.

## Fake connector

Must be deterministic and injectable. It needs modes sufficient to test:
- SUCCESS: records one external effect and returns stable result id
- FAIL_BEFORE_EFFECT: throws before recording effect
- AMBIGUOUS_AFTER_EFFECT: records external effect, then simulates crash/exception before caller receives durable success proof

The fake external effect must be stored somewhere independently inspectable from the action row so tests can detect duplicates.

Do not "solve" ambiguity by making the fake connector transactionally atomic with the app database; that would erase the real external-API problem we are testing.

## Atomicity requirement

`PENDING -> COMMITTING` must be one conditional DB transaction. Concurrent cancel and commit must have only one canonical winner.

DBOS documentation guarantees exactly-once for tracked database transactions and durable sleep/recovery, but not magical exactly-once semantics for arbitrary external APIs. The implementation must preserve that boundary.

## Mandatory acceptance tests

T01_CREATE_PENDING
Create action. Assert state=PENDING and first event recorded.

T02_CANCEL_BEFORE_DEADLINE
Cancel before execute_after. Assert CANCELLED, connector effect count=0, later workflow wake does not commit.

T03_NORMAL_COMMIT
Let deadline pass. Assert exactly one PENDING->COMMITTING transition, one fake external effect, then COMMITTED with result id.

T04_RESTART_DURING_SLEEP
Start PENDING with future deadline, terminate/restart app/runtime before deadline, then allow deadline. Assert one external effect and COMMITTED.

T05_CANCEL_COMMIT_RACE_CANCEL_WINS
Arrange concurrent cancel/claim with deterministic synchronization so cancel commits first. Assert CANCELLED and zero external effects.

T06_CANCEL_COMMIT_RACE_COMMIT_WINS
Arrange commit claim first. Cancel endpoint must not report success. Exactly one external effect; final COMMITTED for SUCCESS mode.

T07_FAIL_BEFORE_EFFECT
Connector fails before external effect. Assert effect count=0 and final FAILED. No repeated external effect.

T08_AMBIGUOUS_AFTER_EFFECT
Connector records effect then loses acknowledgement/simulates crash ambiguity. After recovery, assert:
- external effect count=1
- action becomes UNKNOWN (unless deterministic reconciliation proves success, but this task's fake ambiguous mode should intentionally withhold such proof)
- workflow never blindly calls connector again
- event history explains why state is UNKNOWN

T09_RESTART_AFTER_COMMIT
After COMMITTED, restart runtime. Assert no additional connector call/effect.

T10_EVENT_RECONSTRUCTION
For CANCELLED, COMMITTED, FAILED, UNKNOWN examples, events are sufficient to reconstruct the canonical transitions and relevant connector attempt/result metadata without consulting application logs.

All 10 tests are contract tests. Passing them does not prove DBOS generally correct; it proves our implementation satisfies this frozen lifecycle contract under the tested failure modes.

## Crash injection

Tests must include controlled process/runtime interruption, not merely Python exceptions, for at least T04 and one commit-boundary scenario if technically feasible in CI/local test harness.

If true process-kill testing is impractical in the first commit, implement deterministic crash checkpoints and document the limitation as a finding; do not silently replace crash semantics with ordinary exception handling.

## Forbidden implementation moves

- no LLM/provider SDK
- no web search
- no Gmail
- no EME tables
- no Redis/RabbitMQ/Celery
- no Temporal/Restate
- no OPA/Cedar
- no LangGraph/CrewAI
- no second model
- no generic plugin architecture
- no production UI
- no retry of AMBIGUOUS_AFTER_EFFECT
- no broad refactor outside task scope

## Deliverables

- runnable FastAPI service
- migrations/schema
- DBOS workflow
- fake connector and deterministic fault injection
- pytest acceptance suite with the 10 named tests
- short `V0A01_REPORT.md` containing:
  - exact commands to run
  - test result
  - observed DBOS limitations
  - any deviation from contract
  - whether result is PASS or FAIL for DBOS fit

## PASS definition

PASS only if all mandatory acceptance tests pass and no ambiguous external side effect can be silently retried into a duplicate.

If implementation can only pass by changing the lifecycle contract, return FAIL with the smallest concrete mismatch. Do not redesign the architecture inside this task.