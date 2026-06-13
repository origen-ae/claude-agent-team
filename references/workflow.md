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
Deploy
   ↓
PM rolls up progress → STATUS.md / status.html
```

Three human approval gates: PRD approval, technical-solution approval, and pre-deploy approval.

### Core Configuration

- **7 agents**: pm / architect / frontend / backend / qa + reviewer / librarian
- **6 document types**: PRD / SPEC / ADR / TEST-PLAN / RUNBOOK + STATUS
- **3 scripts**: build_index.py, build_status.py, parse_playwright_report.py
- **Playwright E2E**: UI test automation
- **0 external dependencies**: no database, no Lark, no vector store

### Key Design Points

- **ID pairing**: a single requirement runs through several documents under the same number (PRD-008 / SPEC-008 / TEST-PLAN-008 / tests/e2e/PRD-008.spec.ts).
- **STATUS auto-generation**: agents only update the `stage` field in each document's frontmatter; the script scans them and generates STATUS.md and status.html.
- **PM is the central hub**: all progress rolls up to the PM, who maintains the global view for you.
- **Two test rounds**: round 1 plus a re-test, each recorded in the TEST-PLAN document.

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
   ↓ 🛑 User approves deployment
8. deployed         - mark as complete
```

### Mandatory Human Approval Gates

- **🛑 Stage 2 → 3**: user approves the PRD (are the features, prototype, and flow all acceptable?)
- **🛑 Stage 3 → 4**: user approves the SPEC (is the technical solution OK?)
- **🛑 Stage 7 → 8**: user approves deployment (is it ready to go live?)

At these gates, the agent stops and waits; it never advances on its own.

### Cross-Agent Collaboration Rules

Communicate directly via SendMessage, without routing through the lead:

- frontend is unclear about an API → contact backend
- frontend/backend find a requirement ambiguous → contact pm
- implementation hits a design gap → stop the task and contact architect
- qa finds a requirement is untestable → contact pm
- qa finds an implementation bug → SendMessage the responsible dev

### Mandatory Actions After Completing a Stage

After completing its own stage, every agent **must**:

1. Update the `stage` field in the corresponding document's frontmatter.
2. Run `python scripts/build_status.py` to rebuild STATUS.md.
3. Notify the next stage's agent (or the pm, for approval) via SendMessage.

## Stage Enumeration

The full set of `stage` values in document frontmatter:

```
stage: pending | pm-designing | awaiting-prd-approval | architect-designing | awaiting-spec-approval | developing | testing-round1 | fixing | testing-round2 | awaiting-deploy-approval | deployed | cancelled
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
| `awaiting-deploy-approval` | Awaiting user approval of deployment | qa (when the re-test passes) |
| `deployed` | Deployed | pm (marked after deployment) |
| `cancelled` | Cancelled | pm (when the user decides not to proceed) |

**Key rule**: once a document is marked `awaiting-*-approval`, it must wait for user approval; the agent cannot advance on its own.

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
