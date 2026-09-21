# AGENT — PRODUCT GOAL AND ROADMAP

**Status:** CURRENT PRODUCT DIRECTION (2026-09-21). Product and portfolio goals, not a change to the technical acceptance of V0A-01.
**Owner:** human project owner. **Architecture/operational coordination:** ChatGPT. **Implementation:** Claude Code. **Independent technical testing:** Codex/equivalent; Opus available for bounded consultation through the owner.

## 1. Why this product exists

Build a **demonstrable, customer-configurable AI workflow agent** that the owner can show in an English-language Upwork portfolio as evidence of the ability to design, deliver, test and adapt useful business automation with AI coding tools.

**Personal success criterion:** obtaining even a few paid freelance assignments would be a meaningful success. No revenue, number of clients, or hiring outcome is guaranteed by building the product. We optimize for a complete and credible portfolio and practical deployment capability, not for creating a large platform or pursuing hypothetical scale.

Our customer-facing promise is **a useful completed business workflow under the customer's control**. The architecture (human + deterministic backend + bounded AI) is a means to deliver that outcome, not the item sold on its own.

Provisional English positioning:
> AI workflow automation that keeps your business in control. Your data, your rules, your approvals.

Avoid absolute claims such as “never leaks secrets”, “zero disclosure”, “fully secure”, “anonymous”, “infallible”, or “AI cannot make mistakes”.

## 2. Product identity and boundaries

Agent is a **shared workflow core + customer-specific configuration + adapters** for small-business operational workflows. It is not a Ridgeway-only application, a general autonomous employee, a multi-agent research platform, or a framework developed before use cases demand one.

Ridgeway is a fictional **reference configuration**, not the product architecture. No fixed Ridgeway company names, schema, fields, approval roles, CRM provider or business policy may be embedded as universal core invariants.

A client's configuration may define its workflow template, data schema/field mapping, target systems, source/evidence requirements, approval authority, allowed actions, timing and language preferences. Build only configuration mechanisms exercised by actual demo scenarios; don't invent a generic DSL or plugin platform upfront.

The preferred delivery model is customer-operated: the client controls deployment, credentials, data, provider selection, and permissions. An implementation may use local/self-hosted or approved cloud components according to customer requirements. Do not imply that all workflows must be local or that external providers never receive data.

ADOPT → CONFIGURE → WRITE: compare a mature tool or integration before building a replacement. Preserve the frozen V0A-01 DBOS fit test; its result may justify DBOS for this lifecycle, but not a universal mandate for future engagements.

## 3. Differentiator: controlled disclosure, not an unprovable “no secrets stolen” guarantee

The risk we address: firms can unknowingly allow assistants or third-party models access to CRM transactions, prices, customer identities, sales strategy and internal process know-how merely to carry out bounded tasks.

An external model call is **not automatically publication on the open internet**. It can nonetheless disclose data to a separate provider under its actual settings, terms, retention, access and security controls. We must make this transfer explicit and minimize it. Do not assert that any particular provider uses, retains or trains on customer data without verifying the customer's exact configuration and contract.

Implementation requirements for the eventual demo:
- customer-side process authority, credentials, state and permission checks; model output is candidate data;
- smallest task-local packet to an approved model; avoid dumping full CRM, price lists, customer history or entire internal workflows;
- pseudonymization where the task permits; recognize that some operations genuinely require identities;
- visible outbound-data manifest/log **with sensitive payloads redacted** showing provider, data categories, purpose, approval and timing; test against the actual outbound packet at the boundary;
- user-visible approval before consequential external actions where the action template requires it;
- source-bound external claims and evidence qualification before material decisions; human authorization is not proof of factual truth;
- canonical receipt/recovery trail and explicit UNKNOWN if an external effect cannot be established;
- ordinary access control, secrets management, encryption and retention design remain required; do not present packet minimization alone as complete cybersecurity.

**Demonstrable claim:** “For the tested scenarios, the Agent sends only the allowed task-local fields to the configured provider and retains workflow authority in the customer-controlled backend.” Evidence: captured/redacted outbound manifest, fixture-based boundary tests, inspection of code/configuration. Do not extrapolate to a zero-leak guarantee.

## 4. MVP the customer can actually understand

A user can submit a company-related operational request and see a complete **lead/CRM research-and-follow-up workflow**:
request/intake → identify the correct firm/contact → permitted CRM read and bounded research → qualify evidence → propose an actionable draft → human review where required → perform or cancel one external action → show outcome and reconstruction receipt.

A working demo must show both a successful path and a contained error/uncertainty path. Use synthetic or consented data; never send unsolicited mail or mutate a real customer's CRM in a public demo. One real adapter (email or CRM) should be introduced after a fake connector proves the action contract. Do not force every potential customer to use Gmail or GHL.

**Portability evidence:** the same core runs in **two visibly different fictional customer configurations** with materially different rules, input fields, authority or workflow variation, without forking/copying core logic. A second case may reveal a justified extension; document and test it rather than claiming universal applicability. The second case must be meaningfully different, not “Ridgeway renamed”.

**Usability:** a simple end-user interface and repeatable setup/deployment instructions. Architecture documents alone do not count as a demonstrable agent.

## 5. Language

**English-first, Polish-ready.** English is mandatory for the demonstrable product interface, setup guide, error messages, portfolio text and narrated or captioned demo. Polish is the second UI locale where feasible; isolate display strings and locale from business logic from the beginning.

User UI language, source language and output language are independent per-work-item concepts. Do not force English source documents or English outputs because the interface is English. The first release can be English-only if full bilingual support would delay a complete product. Never promise perfect multilingual research without appropriate tests.

## 6. Ordered milestones and exit evidence

**M0 — Product contract (THIS DOCUMENT).** Freeze the owner goal, demo workflow, confidentiality claim boundary, customer/core split and English-first direction. No speculative multi-customer framework. Exit: these criteria are referenced by the repo entrypoint/implementer guide.

**M1 — Durable action foundation (V0A-01, current task).** FastAPI/PostgreSQL/DBOS and fake connector: PENDING/cancel/commit/UNKNOWN, restart and race behavior. Exit: 10/10 named implementation-conformance tests and honest report, or a bounded FAIL with concrete evidence. This does not itself constitute a usable product.

**M2 — First end-to-end business outcome.** WorkContract, correct entity binding, read-only research, evidence qualification, bounded AI, human decision, fake action and minimal English interface in one coherent lead/follow-up scenario. Exit: an observer can complete the workflow and see the source, uncertainty, decision and receipt; wrong-company/wrong-source inputs are blocked or escalated. Existing frozen V0-A stages V0A-02/03/04 are components of this milestone, not replacements for it.

**M3 — Practical integration and customer control.** Integrate a selected real mail/CRM adapter with test/sandbox credentials, reconciliation and no blind retry, then demonstrate configuration-owned roles, permissions and outbound-data boundaries. Exit: success and failure demonstrated with authorized test data; outbound packet tests and redacted disclosure view pass; no uncontrolled real-world send.

**M4 — Not sewn to Ridgeway.** Run the unchanged core on a second materially distinct synthetic customer configuration; add only the smallest evidenced extension if a structural incompatibility is found. Exit: comparison of config changes vs code changes, same build and repeatable acceptance for both cases.

**M5 — Portfolio-ready release.** English-first UX, straightforward reproducible installation, short demo film, synthetic fixtures, public-safe screenshots, concise technical case study showing scope, business result, privacy boundary, limitations, tests and the owner's actual role coordinating AI implementation. Exit: a client can understand the result without reading the architecture ledger. Optional Polish UI only after English demo is complete.

**M6 — Freelance validation, not automatic product expansion.** Publish truthful Upwork profile/project material and offer scoped services: automation integration, adapting workflows to client systems, troubleshooting and customer-operated deployments. Observe real inquiries and requests; refine positioning based on demand. Do not add broad functionality solely for imagined clients. A few real paid assignments would meet the owner's personal success aspiration, but the portfolio milestone is within our control whereas client purchases are not.

## 7. Stop / scope controls

- At each milestone ask: does this directly move us toward a customer-understandable, repeatable demo or solve a verified blocker? If not, defer.
- Prefer existing products/adapters over bespoke infrastructure when they satisfy the same contract.
- Do not promote historical Ledger hypotheses or Ridgeway-specific rules into the active architecture.
- Acceptance tests validate **implementation against contract**. They do not experimentally re-establish established principles of epistemology, data protection or workflow engineering.
- No claims of a tested privacy property before actual boundary tests. No claims of a reusable core before the second configuration runs.
- Do not silently turn V0A-01 into a complete product task. Its existing frozen technical spec remains unchanged; this roadmap controls what product outcome must follow.
