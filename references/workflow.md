# Agent Team Serial Workflow Reference

This reference describes the strictly serial, eight-stage delivery flow used by the agent team, the three mandatory human approval gates, the complete `stage` enumeration, the cross-agent collaboration rules, the mandatory post-stage actions, and a summary of what the scaffold sets up on first run.

## Overview

### Flow Model

```
User submits a requirement
   ↓
PM design: features, prototype, business flow, data-flow diagram
   ↓ 🛑 User approval
Architect designs the technical solution
   ↓ 🛑 User approval
frontend // backend develop in parallel (with self-testing)
   ↓
QA round 1 (including Playwright E2E)
   ↓
QA re-test (automated regression + fix verification)
   ↓ 🛑 User approval
Done — approved & ready to merge/ship
   ↓
PM rolls up progress → STATUS.md / status.html
```

Three human approval gates: PRD approval, technical-solution approval, and ship approval (code ready to merge/ship).

### Core Configuration

- **7 agents**: pm / architect / frontend / backend / qa + reviewer / librarian
- **7 document types**: PRD / SPEC / TEST-PLAN / ADR / RUNBOOK / BACKLOG + STATUS
- **3 scripts**: build_index.py, build_status.py, parse_playwright_report.py
- **Playwright E2E**: UI test automation
- **0 external dependencies**: no database, no Lark, no vector store

### Key Design Points

- **ID pairing**: a single requirement runs through several documents under the same number (PRD-008 / SPEC-008 / TEST-PLAN-008 / tests/e2e/PRD-008.spec.ts).
- **STATUS auto-generation**: agents only update the `stage` field in each document's frontmatter; the script scans them and generates STATUS.md and status.html.
- **PM owns the progress view, on demand**: progress rolls up to the PM, but the PM is event-triggered (no daily cron). The always-on stall/skip detection is mechanical — the dashboard's `⚠️ State warnings` block — and the orchestrator surfaces it each turn; the PM is dispatched for the deeper coordination (status reports, chasing blockers).
- **Two test rounds**: round 1 plus a re-test, each recorded in the TEST-PLAN document.

## Change-size Tiers (pick the flow that fits)

Not every change runs the full 8 stages. Classify the work first:

| Tier | Typical change | Flow | Docs |
|---|---|---|---|
| **S — small** | bug fix, copy/style tweak, single-file logic change, config | dev edits directly → run existing tests → reviewer → done | none |
| **M — medium** | single feature extension, backend change with no API-contract change, one new interaction | pm writes a short note → dev implements → qa smoke test | optional light PRD (no SPEC) |
| **L — large** | new page/module, cross-layer or API change, DB schema change, affects multiple agents | the full 8-stage flow below, all 3 gates active | full PRD + SPEC + TEST-PLAN |

The agent classifies the tier first; **S never needs pm or architect**. The 8-stage flow below applies in full to **L**; **M** uses a trimmed version; **S** skips it. (S-tier still requires the existing test suite to pass, plus a unit test when core logic changes.)

## New Features Go Through pm (not generic brainstorming)

When the user starts a new feature, the orchestrator dispatches the **pm** agent first — not a generic brainstorming/planning skill, whose terminal state would bypass the PRD → SPEC → approval flow. pm owns requirement shaping (with its own lightweight brainstorming for L-tier work) and ends by writing a PRD. This follows the precedence rule **user instructions > skill triggers**.

## Development Flow (strictly serial, 8 stages)

```
1. pending          - requirement registered
   ↓
2. pm-designing     - pm writes the PRD (features, prototype, business flow, data flow)
   ↓ 🛑 User approves the PRD
3. architect-designing - architect writes the SPEC (including API, data model, task breakdown)
   ↓ 🛑 User approves the technical solution
4. developing       - frontend // backend implement in parallel + self-test
   ↓
5. testing-round1   - qa runs the tests (including Playwright E2E)
   ↓
6. fixing           - dev fixes issues found in round 1 (if any)
   ↓
7. testing-round2   - qa runs automated regression + fix verification
   ↓ 🛑 User approves shipping (code ready to merge/ship)
8. deployed         - Done — approved & ready to merge/ship
```

### Mandatory Human Approval Gates

- **🛑 Stage 2 → 3**: user approves the PRD (are the features, prototype, and flow all acceptable?)
- **🛑 Stage 3 → 4**: user approves the SPEC (is the technical solution OK?)
- **🛑 Stage 7 → 8**: user approves shipping (code ready to merge/ship)

At these gates, the agent stops and waits; it never advances on its own.

**Scope**: the team delivers approved, tested, merge-ready code. Running CI/CD and the actual production deploy stay the user's responsibility — migration/rollback scripts and the RUNBOOK are produced but not executed by any stage.

### Approval Gates Are Loops, Not One-Way Doors

A gate is a loop, not a one-way door. When you give feedback, the orchestrator (main Claude) routes it **back to the same agent** that produced the artifact; that agent revises and re-submits, repeating until you explicitly approve. The orchestrator must not absorb the feedback itself, skip ahead, or reassign the work to another agent.

```
Agent artifact → 🛑 review → "approved" → next stage
                          └→ "change X" → back to the SAME agent → revise → re-submit (loop)
```

### Cross-Agent Collaboration Rules

Communicate directly via SendMessage, without routing through the lead:

- frontend is unclear about an API → contact backend
- frontend/backend find a requirement ambiguous → contact pm
- implementation hits a design gap → stop the task and contact architect
- qa finds a requirement is untestable → contact pm
- qa finds an implementation bug → SendMessage the responsible dev

**Fallback**: if the experimental agent-teams feature (and SendMessage) is unavailable, the orchestrator (main Claude) acts as router — it invokes each role itself and dispatches the next stage manually. The frontmatter `stage` field remains the source of truth.

### Mandatory Actions After Completing a Stage

After completing its own stage, every agent **must**:

1. Update the `stage` field in the corresponding document's frontmatter.
2. Run `python scripts/build_status.py` to rebuild STATUS.md.
3. Notify the next stage's agent (or the pm, for approval) via SendMessage.

## Stage Enumeration

The full set of `stage` values in document frontmatter:

```
stage: pending | pm-designing | awaiting-prd-approval | architect-designing | awaiting-spec-approval | developing | testing-round1 | fixing | testing-round2 | awaiting-deploy-approval | deployed | superseded | cancelled
```

| stage | Meaning | Who may set this state |
|---|---|---|
| `pending` | Requirement registered, not yet started | pm (at creation) |
| `pm-designing` | PM is designing | pm |
| `awaiting-prd-approval` | Awaiting user approval of the PRD | pm (on completion) |
| `architect-designing` | Architect is designing | architect |
| `awaiting-spec-approval` | Awaiting user approval of the technical solution | architect (on completion) |
| `developing` | In development | frontend or backend (on start) |
| `testing-round1` | Round 1 testing in progress | qa |
| `fixing` | Fixes in progress | qa (when failures are found) |
| `testing-round2` | Re-test in progress | qa |
| `awaiting-deploy-approval` | Awaiting ship approval | qa (when the re-test passes) |
| `deployed` | Done — approved & ready to merge/ship | pm (marked after ship approval) |
| `superseded` | 🔁 Replaced by a later PRD | architect (when a new PRD refactors it) |
| `cancelled` | Cancelled | pm (when the user decides not to proceed) |

**Key rule**: once a document is marked `awaiting-*-approval`, it must wait for user approval; the agent cannot advance on its own.

## Multi-Developer Mode (optional)

For teams, run one feature branch per person; the branch name is the owner identity. The full protocol lives in **assets/CLAUDE.md "Multi-Developer Mode"** — see there for details. Key points:

- Before branching, claim document ids on the **integration branch** with `python scripts/next_id.py <type>` (it scans files plus index reservations), then write the doc on your `feature/<name>` branch.
- Generated files are gitignored: `status.html` and `docs/index.yaml` are not committed; `STATUS.md` is committed **only on the integration branch** (feature branches don't commit it).
- SPEC-000 is reconciled on the integration branch after merge.

## What the Scaffold Sets Up / First Run

Run these steps in order. After each step completes, report the result before moving on to the next.

### Step 1: Create directories

```bash
mkdir -p .claude/agents
mkdir -p .claude/skills/doc-conventions
mkdir -p .claude/skills/playwright-testing
mkdir -p docs/prd docs/spec docs/adr docs/test-plan docs/runbook docs/_templates
mkdir -p scripts
mkdir -p tests/e2e/pages tests/e2e/fixtures
touch docs/prd/.gitkeep docs/spec/.gitkeep docs/adr/.gitkeep
touch docs/test-plan/.gitkeep docs/runbook/.gitkeep
touch tests/e2e/.gitkeep
```

### Step 2: Create configuration

Follow the "CLAUDE.md" and "settings.json" sections.

### Step 3: Create the 7 agents

Create them per the "Agent Definitions" section:
- pm.md, architect.md, frontend.md, backend.md, qa.md
- reviewer.md, librarian.md

### Step 4: Create the 2 skills

- `.claude/skills/doc-conventions/SKILL.md`
- `.claude/skills/playwright-testing/SKILL.md`

### Step 5: Create the 5 document templates

Create them per the "Document Templates" section.

### Step 6: Create the scripts

Create them per the "Scripts" section:
- requirements.txt
- build_index.py
- build_status.py
- parse_playwright_report.py

Install dependencies:

```bash
pip install -r scripts/requirements.txt
```

### Step 7: Install Playwright

```bash
npm install -D @playwright/test @axe-core/playwright
npx playwright install --with-deps chromium
```

Create `playwright.config.ts` (per the "Playwright Configuration" section).

### Step 8: Create initial documents

- `docs/README.md`
- `docs/adr/ADR-000-adr-conventions.md`

### Step 9: Have the architect generate the project's current state

In Claude Code:

```
Have the architect browse the src/ directory to understand the project's
tech stack and core modules, then generate docs/spec/SPEC-000-current-state.md.
When done, fill in the placeholders in the "Project Current State" section at
the top of CLAUDE.md (tech stack, core modules, code directory layout).
```

### Step 10: Run the scripts for the first time

```bash
python scripts/build_index.py
python scripts/build_status.py
```

Open `STATUS.md` and `status.html` to check that they display correctly (at this point only ADR-000 and SPEC-000 exist).

### Step 11: Verify the agents

```
/agents
```

You should see 7 agents.

Test the librarian:

```
Have the librarian search for "project current state"
```

It should return SPEC-000.

### Step 12: Run the first real requirement

A full end-to-end test:

```
Start the agent team and, following CLAUDE.md, strictly run the 8-stage flow
to implement a real requirement.

Requirement description: [the feature you want to build]

Flow:
1. pm writes the PRD (including features, prototype, business flow, data flow) → wait for my approval
2. architect writes the SPEC → wait for my approval
3. frontend // backend implement in parallel → each spawns a reviewer
4. qa writes the TEST-PLAN and Playwright E2E, then runs round 1
5. if anything fails, dev fixes it
6. qa re-tests
7. wait for my approval to deploy

After every stage switch you must run build_status.py so the dashboard updates.
At the key gates, wait for my approval; do not advance automatically.
```
