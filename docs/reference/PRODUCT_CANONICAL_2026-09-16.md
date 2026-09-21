# PRODUCT_CANONICAL_CURRENT

**Status:** CURRENT PRODUCT CANONICAL — pre-implementation  
**Purpose:** single product-level source of truth for the boutique customer-operated agent architecture.

This document supersedes `ASSISTANT_0_BASELINE.md` for implementation decisions. Earlier baselines, rejected-concept files, audits and discussion notes remain audit history.

## 0. Active documents

Only these documents are active for implementation:

1. `PRODUCT_CANONICAL_CURRENT.md` — product architecture, security boundary and implementation philosophy.
2. `RIDGEWAY_CANONICAL_CURRENT.md` — Customer 01 business environment and acceptance contract.
3. `GHL_SPIKE_CURRENT.md` — current empirical integration experiment.

Do not implement from older patch/baseline/audit files unless one of the active documents explicitly references them as evidence.

---

## 1. Product thesis

We are building a **boutique, customer-operated hybrid operational system** in which the unit of agency is the whole work system:

**human + deterministic process/backend + tools/solvers + bounded AI workers**

The product is not designed around a single autonomous LLM that owns a long process end-to-end.

Frozen working principle:

> **Global orchestration + local intelligence.**

The deterministic/customer-controlled process layer owns global state, process continuity and transition authority. AI is used for bounded local work where semantic capability is useful. Human judgment is invoked only where the system lacks a sufficient oracle, a material policy decision is required, or the consequence cannot safely be delegated.

This architecture is intended for small companies that want useful AI without unnecessarily exposing internal data, workflow or process know-how to model providers.

The product is not:
- a universal personal assistant,
- a generic AI employee,
- a mass-market SaaS that we operate for customers,
- a prompt wrapper,
- a system that claims deterministic or infallible AI.

The commercial direction is:

**shared product core + customer-specific configuration/integration + paid implementation/support/audit**

not:

**rewrite a new product for every customer**

and not:

**sell 10,000 identical copies and operate all customer agents centrally**.

Revenue is expected primarily from implementation, adaptation, support, process maintenance and later audits/upgrades, while the runtime remains customer-operated.

---

## 2. Reliability objective

The presence of an AI model means the whole system cannot honestly be described as 100% deterministic.

Frozen objective:

> **Maximum reasonable diligence, bounded failure impact and explicit residual uncertainty — not absolute reliability.**

The threat model assumes **model error, not model malice**.

Typical risks:
- semantic mistake,
- premature closure,
- unsupported inference,
- scope inflation,
- entity/source confusion,
- structurally valid but semantically wrong value,
- repeated known formatting/representation mistakes.

We do not build a “lie detector” for the model.

Where deterministic enforcement is possible, use it.  
Where semantic truth cannot be determined mechanically, keep uncertainty explicit and use evidence/oracle/HITL as appropriate.

---

## 3. Confidentiality thesis

Two different assets must be protected:

1. **customer data / identity**
2. **customer process know-how**

Pseudonymization protects the first only partially. It does not by itself protect the second.

Frozen principle:

> **Data is minimized and pseudonymized before model exposure. Business process logic remains in the customer-controlled backend.**

Another frozen principle:

> **API access is not a security boundary. Assume outbound calls to an external model provider may be correlated over time.**

Therefore security must be achieved primarily by controlling **what never leaves the customer-controlled environment**, not by relying on a provider channel alone.

---

## 4. Ownership boundary

Persistent customer-controlled components own:

- workflow state,
- process order,
- business rules,
- thresholds,
- permissions,
- transition logic,
- canonical decisions/policies,
- receipts/audit,
- mapping between real identities and aliases,
- recovery state,
- mechanically checkable completion conditions,
- known mechanical model-error patterns.

The AI model does **not** own these.

The model is a replaceable semantic component.

Frozen summary:

> **Backend knows the company process. Model knows only the current semantic problem.**

---

## 4.1 Global coherence and local model work

Empirical working assumption from the coding workflow:

> **An LLM can make locally reasonable decisions and still fail the global process.**

This is a distinct failure class from hallucination or schema error.

Examples:
- each local edit is defensible, but architecture drifts;
- a local fix weakens a global invariant;
- a model changes the interpretation of the objective over a long run;
- the model reaches a locally plausible `DONE` while the real global goal is unmet.

Therefore:
- AI workers may solve local semantic problems;
- AI workers do not own the global objective;
- AI workers do not decide authoritative process completion;
- the process kernel preserves prior decisions, invariants, state and legal transitions;
- global coherence is evaluated at the system/process level, not inferred from local success.

The architectural question is always:

> **If this worker is locally wrong or locally optimal in the wrong direction, what prevents the error from propagating globally?**

---

## 4.2 Human role

Human is not the default reviewer of every AI output.

Human enters the process when:
- no sufficient external/mechanical oracle exists;
- a material ambiguity remains;
- a policy/business-value trade-off must be decided;
- an irreversible/high-impact action requires human authority;
- the human is the only practical oracle for a property not yet formalized.

A human checkpoint is invalid if the human does not receive enough evidence to make a real judgment.

Avoid:
- review theater,
- `APPROVE` clicks without real evaluability,
- fixed checkpoints such as “every N steps” without material reason,
- model-confidence thresholds as a proxy for truth.

The objective is not maximum human oversight. It is **minimum necessary human cognitive work while preserving acceptable quality and risk bounds**.

---

## 5. Model context policy

The backend is persistent. Model context should be **task-local and ephemeral by default**.

The model receives only the minimum context required for the current semantic operation.

External model calls must not receive the full workflow merely because it is convenient.

Examples of suitable model work:
- parse an unstructured message into a defined schema,
- classify a document/value,
- extract candidate facts,
- compare bounded evidence,
- research a bounded question,
- produce a bounded analytical result.

Unsuitable delegation:
- “run our whole onboarding process” when the process can remain in backend state/rules,
- expose the entire internal decision tree to let the model decide the next step,
- use persistent provider-side context as the canonical company memory.

A model may receive a local task definition or output schema needed to perform its semantic operation. This does not authorize exposure of the surrounding proprietary workflow.

---

## 6. Pseudonymization and minimization

For business data sent to an external AI provider:

1. minimize fields first;
2. pseudonymize identifiers using the existing customer-side pseudonymizer;
3. send only the task-local semantic packet;
4. keep the real-identity mapping inside the customer-controlled environment;
5. depseudonymize only after the structured result returns.

Task-local / short-lived aliases are preferred when stable cross-call identity is not required.

Stable aliases must not be used merely for convenience if they create unnecessary cross-call linkability.

Pseudonymization is not presented as anonymization and does not prove that correlation is impossible.

---

## 7. Semantic packet

External AI interaction should use a bounded **semantic packet** rather than general company context.

A packet should contain only what the operation needs, for example:

- task-local alias(es),
- bounded source text/evidence,
- exact semantic question,
- output schema,
- evidence/source references needed for the result.

It should not contain:
- unrelated customer records,
- full workflow definitions,
- internal process maps,
- thresholds not required for this semantic question,
- canonical policy history unrelated to the operation.

Packet schemas are customer/task-specific configuration and must be auditable.

---

## 8. Structured candidate output

Model output is treated as **candidate data**, not canonical truth.

Preferred flow:

`customer data/state`
→ `backend selects semantic operation`
→ `minimization + pseudonymization`
→ `semantic packet`
→ `model`
→ `structured candidate output`
→ `mechanical backend validation`
→ `evidence/oracle/HITL where semantic truth remains open`
→ `state/action`

Structured output may be JSON or an equivalent typed object.

Backend may mechanically validate, where applicable:

- schema,
- IDs/aliases,
- enum/domain membership,
- units/representation,
- permissions,
- task scope,
- source/evidence references,
- state transition,
- compare-and-set,
- duplicate/reconciliation state,
- mechanically enumerable completion.

A structurally valid output can still be semantically wrong.

Therefore:

> **Structured output reduces the blast radius of hallucination; it does not turn a model answer into truth.**

---

## 9. Deterministic backend boundary

The deterministic backend is intentionally literal.

Use it for:
- state,
- permissions,
- IDs,
- versions,
- receipts,
- allowlists,
- exact transitions,
- exact approved actions,
- representation domains,
- resource limits,
- duplicate/recovery checks,
- mechanically definable task coverage.

Do not ask it to decide open-ended semantic truth.

Do not create separate “gates” as architectural components for every new failure. Prefer one backend/state machine with explicit invariants.

---

## 10. Completion

For finite tasks whose required items can be frozen, authoritative completion belongs to the system state, not to a model sentence such as “done”.

The expected item set comes from frozen task/backend state, never from the model's own description of what it thinks the task contained.

Each required item must end in an allowed state such as:
- valid committed value,
- UNKNOWN with reason,
- CONFLICT with evidence,
- another explicitly frozen terminal state.

This checks **accounting/coverage**, not semantic truth.

Open-ended research/analysis is different. When several materially plausible versions survive the evidence, the correct result may be a bounded set of evidence-backed alternatives for the human decision-maker rather than an arbitrary model choice.

---

## 11. Human decision versus reusable policy

A one-off human decision is not automatically a reusable rule.

Distinguish:
- `CASE_DECISION` — exact case only,
- `POLICY_RULE` — explicitly approved as reusable.

Model interpretation, repeated behavior or one-off approval cannot silently promote a case into policy.

---

## 11.1 Learning path: how the system may improve

The system may learn recurring correct behavior, but **learning means controlled transfer of responsibility**, not silent self-modification of policy by an LLM.

A human-resolved or externally resolved case may be stored as a learning event containing:
- task/work-item identity,
- problem signature,
- evidence available at decision time,
- AI candidate,
- human/oracle decision,
- final authoritative outcome,
- reason for correction/approval where available,
- later observed outcome where available.

Classify learning events into:

- `SEMANTIC_ONE_OFF` — no safe generalization yet;
- `REPEATABLE_MECHANICAL_PATTERN` — candidate for validator, invariant, regression test or deterministic rule;
- `BUSINESS_POLICY_CANDIDATE` — reusable only after explicit owner approval;
- `SEMANTIC_PRECEDENT` — useful as an example/retrieval aid, but not authorization;
- `GLOBAL_PROCESS_DEFECT` — requires process redesign, not a local rule.

A human-trigger may be removed for a class of cases only when one of these becomes true:

1. a deterministic rule/oracle can decide the class;
2. an explicitly owner-approved policy covers the class;
3. a separately accepted bounded semantic mechanism has an external acceptance oracle showing that routine human review is no longer required for that class.

Do not invent arbitrary promotion counts such as “3 approvals = rule”.

Allowed learning effects:
- regression cases,
- mechanical validators,
- retrieval of prior examples,
- policy proposals,
- improved bounded prompts/context,
- reduced human escalation after formal promotion.

Not allowed automatically:
- permission changes,
- source-policy changes,
- CEO-authorization changes,
- identity-binding relaxation,
- promotion of one correction into policy,
- treating repeated model agreement as truth.

Frozen summary:

> **The system learns by moving proven classes of work from HUMAN → AI/PROGRAM, not by letting the model rewrite the process.**

---

## 12. Backend Error Pattern Registry

The backend may maintain a local registry of **mechanically confirmed recurring model errors**.

Purpose:
- avoid paying repeatedly for the same detectable technical mistake,
- reduce repeat failures,
- build empirical model/task knowledge without teaching the model customer workflow.

A registry entry should be scoped, for example, by:
- model/provider/version,
- task family,
- mechanical signature,
- configured handling,
- evidence/occurrence count,
- status: active/retired.

Examples of eligible patterns:
- percentage returned as `42` when frozen representation is fraction `[0,1]`,
- invalid enum,
- missing required evidence reference,
- wrong date representation,
- repeated schema violation.

Not eligible as automatic backend truth:
- “healthcare is suspicious” because one prior industry classification was wrong,
- semantic rules inferred from a single correction,
- a new business policy invented from model behavior.

A detected failure first becomes a regression case. It becomes an active registry pattern only when the pattern is mechanically definable and deliberately approved/configured.

Exact registry schema and per-pattern actions remain implementation details until the first real patterns are observed.

---

## 13. Memory

Canonical process/business memory remains customer-controlled.

Do not use external model memory as canonical company truth.

Canonical memory may contain:
- decisions,
- constraints,
- policies,
- evidence references,
- status/supersession,
- user confirmation.

Model inference must not automatically become canonical policy.

The memory system should provide only the minimum relevant task-local material to a model call; it should not dump the full company memory into the model context.

---

## 14. Evaluators and extra models

Do not use model committees or majority voting as default safety.

Do not add an evaluator merely because a semantic risk exists.

If a concrete high-value semantic step justifies an evaluator:
- it is read-only,
- has bounded inputs,
- receives the original request when scope fidelity matters,
- has a different job from the primary model,
- is not a source of truth,
- its existence must justify its cost/complexity empirically.

---

## 15. Model/provider routing

External AI is an **optional semantic accelerator, not the runtime owner**.

Preference order:

1. deterministic/local backend operation where semantics are unnecessary;
2. existing local/open-source component when it solves the task adequately;
3. model call only where semantic capability is actually needed.

The exact use of local versus external models is **not yet frozen** and will be selected by capability/cost/security evidence.

Changing model provider must not require rewriting customer workflow logic.

---

## 16. Implementation philosophy

We are building a **pilot-grade / reference implementation**, not a cardboard MVP.

The first system must show whether an evolvable product can be built with AI assistance.

Implementation preference:

> **adopt → configure → write**

Use existing mature components before custom code.

But:

> **minimum custom code + minimum components**

is better than “maximum number of open-source dependencies”.

Do not add a large framework when a small explicit implementation is safer and clearer.

Do not pre-build infrastructure for hypothetical future customers.

Useful build metrics:
- custom production LOC,
- number of custom modules,
- number of direct dependencies/components,
- amount of Customer-01-specific code in the shared core,
- code added per new customer/task family,
- operational complexity introduced by each component.

These metrics are diagnostics, not arbitrary LOC quotas.

---

## 17. Runtime/framework

The earlier assumption that LangGraph OSS is the frozen v0 workflow/runtime is **reopened** by the newer process-kernel architecture.

Do not select a runtime first and then force the process into it.

Current rule:

> **Freeze the process contract and required runtime properties first; select the smallest runtime that implements them.**

Possible implementation classes include:
- plain application code + database/state machine,
- durable workflow runtime,
- BPM/workflow engine where visual/process representation materially helps,
- LangGraph only inside a bounded semantic subworkflow where it demonstrably adds value.

Do not build our own orchestration framework in advance.

Do not adopt a framework merely because the product uses AI.

---

## 18. Customer-operated deployment

Frozen:
- customer owns/controls runtime,
- customer controls data and credentials,
- customer chooses model providers,
- customer controls persistent state/memory,
- cloud is allowed,
- product is not local-only,
- we do not require our own hosted control/data plane.

We provide:
- software,
- implementation/configuration,
- updates,
- support,
- later audits and process evolution.

---

## 19. Security claim boundary

Do not market the product as:
- “AI never sees any company information,”
- “anonymous,”
- “100% deterministic,”
- “guaranteed safe,”
- “incapable of error.”

Defensible target claim:

> **Customer process logic and persistent operational state remain customer-controlled. External models receive only the minimum pseudonymized task-local context required for the current semantic operation.**

This claim must be backed by outbound-context tests and architecture inspection, not by provider promises alone.

---

## 20. Acceptance direction for confidentiality

Before pilot admission, tests/audit must demonstrate at least:

- business records are minimized before external model calls;
- real identities are pseudonymized where the task does not require them;
- alias mapping stays customer-side;
- full workflow/process logic is not included in external model packets;
- unrelated company memory/state is not dumped into model context;
- stable aliases are not reused unnecessarily;
- model output cannot directly mutate canonical state without backend handling;
- structured candidate output is mechanically checked where rules exist;
- known mechanical error patterns can become regression tests/registry entries without creating semantic policy.

This does not prove that no information can ever be inferred. It proves the intended disclosure boundary is being enforced.

---

## 21. Current product experiment

Customer 01 / Ridgeway is the reference implementation.

Success is not “the demo works”.

The main experiment is now:

> **Can the proven human-centered coding pattern — global process outside the model, local model work, external/mechanical or human oracles — produce measurable advantage in ordinary operational work?**

We want evidence that:
- useful work can be decomposed among PROGRAM / AI / HUMAN;
- global state and transition authority remain outside the LLM;
- bounded AI improves semantic work where classical software alone is insufficient;
- human review is used only where it adds a real oracle/judgment;
- repeated human interventions can safely become regression/rules/policy proposals;
- human cognitive work decreases over time without weakening quality;
- process logic remains customer-controlled;
- model context can stay minimal/task-local;
- errors have bounded impact;
- open-source components keep custom code manageable;
- the system can be extended without rewriting the core.

Primary product metric:

> **How much human cognitive work was safely removed from the process?**

Supporting measures include:
- correctness,
- human intervention count,
- human review time,
- false success,
- unresolved cases,
- errors passed,
- cases completed without human,
- cases escalated to a human who could not actually assess them.

For relevant task families compare, where practical:
- human alone,
- human + ordinary AI copilot,
- classic software/automation,
- hybrid process: backend + bounded AI + human only where required.

Only a later, materially different Customer 02 can test whether the shared core is truly reusable.

---

## 22. Current open items

Not frozen yet:

- exact local/external model routing;
- exact semantic packet schemas per task family;
- exact pseudonymizer integration interface for this product;
- exact Error Pattern Registry schema/actions;
- exact governance and evidential threshold for promoting learning events;
- exact operational acceptance-oracle design for semantic task families;
- exact customer-facing confidentiality metrics/report;
- exact support/pricing model;
- workflow/runtime choice for the process kernel;
- which open-source components beyond the existing pseudonymizer are actually necessary.

These must be resolved from implementation/test evidence, not speculative architecture.

Do not confuse absence of metaphysical semantic certainty with absence of an operational oracle. A business process may define sufficient evidence for action while still carrying explicit residual uncertainty.