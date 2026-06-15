# Agent Roles

This team runs a serial delivery flow with a small, fixed set of agents and documents:

- **7 agents**: pm / architect / frontend / backend / qa + reviewer / librarian
- **7 document types**: PRD / SPEC / ADR / TEST-PLAN / RUNBOOK / BACKLOG + STATUS
- **3 scripts**: build_index.py, build_status.py, parse_playwright_report.py
- **Playwright E2E**: UI test automation
- **0 external dependencies**: no database, no Lark, no vector store

The flow has 8 stages and 3 approval gates. Each document carries a numeric ID, and SPEC / TEST-PLAN share the same number as their parent PRD (the ID-pairing rule). The sections below summarize each agent: its responsibility, key outputs, and position in the flow. They do not duplicate the full agent prompts — see the linked definition for the authoritative version.

---

## pm (Product Manager + Progress Summarizer)

Definition: `assets/.claude/agents/pm.md`

The pm wears two hats.

**Identity A — Requirements designer.** When a new request comes in, the pm first asks the librarian whether a similar PRD already exists (to avoid duplication), then digs into the background (target users, the pain point being solved, how success is measured, what is out of scope). Working from the template, the pm produces the **PRD** at `docs/prd/PRD-XXX.md` containing four mandatory blocks: feature definition, prototype design, business flow, and data flow. Critically, the prototype section flags which elements are "must-cover for E2E," so frontend knows where to add `data-testid` and qa knows what to test.

**Identity B — Progress summarizer (event-triggered).** The pm owns the project-wide status board, but is dispatched on demand rather than on a daily schedule the runtime can't provide. Always-on stall/skip detection is mechanical — the dashboard's `⚠️ State warnings` block, surfaced by the orchestrator each turn. The pm is triggered for the deeper work: producing a status summary when the user asks, re-reading the board at gates, and coordinating across agents when a blocker surfaces (e.g. frontend waiting on backend) — escalating urgent blockers to the user.

**Key outputs**: PRD documents; STATUS.md / status.html (script-generated, but the pm is the responsible owner).

**Position in the flow**: Stage 1-2. On creation the PRD stage is `pm-designing`; once written, the pm moves it to `awaiting-prd-approval` and runs build_status.py. The pm must wait for user approval and cannot advance the stage to `architect-designing` themselves. The pm does not write technical solutions (architect's job) or test cases (QA's job), and every acceptance criterion must be testable.

---

## architect (System Architect)

Definition: `assets/.claude/agents/architect.md`

The architect leads the technical design. On the very first run of the agent team, the architect browses `src/` to generate `docs/spec/SPEC-000-current-state.md` (tech stack, core module inventory, frontend/backend directory layout, dependency graph, conventions, obvious tech debt) and fills in the "project current state" placeholders in CLAUDE.md — the code-directory information that frontend.md and backend.md rely on for their permission boundaries.

For a regular task, after receiving an approved PRD the architect consults the librarian, reads the PRD (focusing on business flow, data flow, and prototype), draws the system architecture diagram (Mermaid), designs the API contract shared by frontend and backend (each endpoint's method, path, request, response, error codes, with concrete JSON examples), designs any new data models, and breaks the work into implementation tasks labeled frontend / backend / joint with explicit dependencies and estimates. Decisions with two or three competing options are recorded as ADRs.

**Key outputs**: **SPEC** at `docs/spec/SPEC-XXX.md` (XXX matches the parent PRD); **ADR** at `docs/adr/ADR-XXX.md` (independently numbered, only for significant decisions).

**Position in the flow**: Stage 3 (leads). The architect marks the SPEC stage `architect-designing`, then `awaiting-spec-approval`, and must wait for user approval before development starts. The architect does not write code-level detail (dev's job) and must provide alternative comparisons for any technical choice.

---

## frontend (Frontend Developer)

Definition: `assets/.claude/agents/frontend.md`

Implements UI components, pages, state management, and frontend tests. After receiving an approved SPEC, the frontend developer asks the librarian for the relevant PRD (prototype, UI sketches, E2E key-point annotations) and SPEC (API design), and — if it is the first to start — marks the PRD stage `developing`. Before coding it confirms the state-management, component-reuse, and error-handling strategy. While coding, **key interactive elements must get a `data-testid`** (every PRD-flagged "E2E key point" is mandatory), every user-input path must handle the loading / error / empty / success states, and accessibility is enforced (contrast ratio >= 4.5:1, keyboard reachability, ARIA labels). After coding it runs lint, typecheck, and component tests, then spawns the reviewer subagent. When done it notifies qa via SendMessage; once both frontend and backend are done, it adds `frontend-done: true` to the PRD frontmatter and runs build_status.

`data-testid` naming follows `{page}-{element-type}-{purpose}`, e.g. `checkout-btn-submit`, `cart-input-coupon`, `order-list-item`.

**Key outputs**: frontend code, component tests, and stable `data-testid` hooks for qa's E2E tests.

**Position in the flow**: Stage 4 (leads, in parallel with backend). The frontend developer does not touch backend code, does not hardcode business rules (business lives in the backend), and must not bypass type checking or omit `data-testid`.

---

## backend (Backend Developer)

Definition: `assets/.claude/agents/backend.md`

Implements APIs, business logic, data persistence, and performance work. After receiving an approved SPEC, the backend developer asks the librarian for the PRD (business flow, data flow) and SPEC (API design, data model), and — if it is the first to start — marks the PRD stage `developing`. Before coding it confirms transaction boundaries, error handling, idempotency, and performance impact. Database changes must ship with migration + rollback scripts. The API must strictly match the SPEC contract (method/path/fields/error codes), business logic must follow the SPEC's business flow, key operations must be idempotent, errors must use the project's unified error codes, and sensitive operations must be audited. Core business logic needs >= 80% unit-test coverage, every state-transition path needs a test, and bug fixes start with a reproduction test. After coding it spawns the reviewer subagent, notifies frontend that the API is available, and once both sides are done adds `backend-done: true` to the PRD frontmatter and runs build_status.

**Key outputs**: backend code, unit/integration (and where needed load) tests, database migrations + rollbacks.

**Position in the flow**: Stage 4 (leads, in parallel with frontend). The backend developer does not touch frontend code, does not invent APIs outside the SPEC, does not hardcode status strings (use enums), and does not read other services' databases directly.

---

## qa (QA Engineer)

Definition: `assets/.claude/agents/qa.md`

Owns test-case design, round-1 testing, fixing follow-up, retest, and E2E automation (via the playwright-testing skill). qa engages early — it can start designing test cases as soon as the SPEC is done, without waiting for development to finish.

**Round 1 (Stage 5):** qa consults the librarian, sets the PRD stage to `testing-round1`, creates the **TEST-PLAN** at `docs/test-plan/TEST-PLAN-XXX.md` (XXX matches the PRD), and designs a test **pyramid** from the SPEC and PRD: a wide fast base of **API contract-conformance tests** (the front/back seam — shape, status, error codes match the SPEC, run before E2E) plus unit tests, then integration tests from PRD acceptance criteria and SPEC business flows, negative tests from the SPEC's "Security & abuse cases", and a thin top of Playwright E2E for critical user paths (mandatory but few). Boundary-value tests come from the API design, and SPEC §9 performance targets become budgets the tests assert/record. E2E files live at `tests/e2e/PRD-XXX.spec.ts` with a JSDoc header linking the document IDs:

```typescript
/**
 * @prd PRD-008 user points deduction
 * @spec SPEC-008
 * @test-plan TEST-PLAN-008
 */
```

qa runs the tests, does manual exploratory testing for the corners E2E misses, and returns only the failing cases and error info (not the full log). If anything fails, it moves the stage to `fixing` and notifies the dev; if everything passes, it moves to `awaiting-deploy-approval` and notifies the pm.

**Wait for fix (Stage 6):** no proactive action; the dev pings qa via SendMessage once the fix is done.

**Retest (Stage 7):** qa sets the stage to `testing-round2`, runs the full Playwright regression, focuses on the previously failing cases (verifying the fix and checking for new bugs), updates the "retest results" section, and either moves to `awaiting-deploy-approval` or back to `fixing` to loop again.

**Key outputs**: TEST-PLAN documents (including round-1 and retest result sections), Playwright E2E specs, and the test metrics rollup feeding STATUS.

**Position in the flow**: Stages 5-7 (leads). Requirement-level issues go to the pm, technical-design gaps go to the architect.

---

## reviewer (Code Review subagent)

Definition: `assets/.claude/agents/reviewer.md`

A senior code-review specialist invoked proactively by a dev after finishing a task. It reviews quality, security, performance, maintainability, and SPEC conformance — read-only, it finds issues but does not fix them (the fix goes back to the original author). On invocation it runs `git diff`, focuses on the changed files, and starts reviewing immediately; for frontend code it pays special attention to `data-testid` completeness and accessibility, and for backend code to SPEC conformance, error-code correctness, and idempotency.

The review checklist covers naming clarity, duplicated code, complete error handling, exposed secrets/tokens, input validation, test coverage, performance issues (N+1, missing indexes, large objects), security issues (SQL injection, XSS, CSRF, authorization bypass), conformance to the linked SPEC's API contract and business rules, and whether the frontend provides `data-testid` for the PRD-flagged E2E key points. Feedback is grouped as Critical (must fix), Warning (should fix), and Suggestion (may fix). Each issue gets a concrete fix suggestion; it skips what lint already reports and trivial style nits, and simply says "no significant issues" when there are none rather than inventing problems.

**Key outputs**: a structured code-review report.

**Position in the flow**: Stage 4, invoked when a dev completes a task.

---

## librarian (Document Retrieval subagent)

Definition: `assets/.claude/agents/librarian.md`

The team's retrieval assistant. It searches efficiently and returns only summaries plus paths — never full documents. On a retrieval request it first checks `docs/index.yaml` for candidates; if there is no index or it is insufficient, it falls back to grep/glob over the title/summary/tags in `docs/*/*.md` and the file contents. It reads the top-5 candidates, extracts the relevant sections, and returns a concise result.

The return format lists highly relevant items (suggested for full loading) with ID, title, path, current stage, a 2-3 sentence summary, and a one-line reason for relevance; moderately relevant items get a one-line note; and a closing suggestion tells the main agent which documents to load fully and which to keep as reference.

**Key outputs**: a ranked, summarized retrieval result with document paths.

**Position in the flow**: spans the entire flow as every agent's retrieval helper. Strict rules: never return full documents (the main agent reads them itself), no more than 5 highly relevant items, say "not found" plainly when nothing matches, flag broken references (related links pointing to a nonexistent ID), and by default exclude documents in the `cancelled` state unless the main agent explicitly asks for history.
