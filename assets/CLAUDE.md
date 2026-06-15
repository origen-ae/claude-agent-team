# Project Collaboration Conventions

<!-- claude-agent-team: v1.7.0 — do not remove; upgrades use this to detect the installed version -->

## Project Status (filled in by the architect after first launch)

> **Important**: Every agent, when it picks up a task, must:
> 1. First look at the src/ directory to understand the current state of the project
> 2. Extend new features on top of existing patterns; do not reinvent
> 3. Legacy modules are not required to be backfilled with PRD/SPEC; new work and refactors follow these conventions

- **Tech stack**: (to be filled in by the architect in SPEC-000)
- **Core modules**: (to be filled in by the architect in SPEC-000)
- **Code directories**: (to be filled in by the architect in SPEC-000, e.g. src/frontend, src/backend)

## Agent Team

| Role | Main responsibilities | Key deliverables |
|---|---|---|
| pm | Requirements design + progress aggregation (dual role) | PRD + STATUS maintenance |
| architect | Technical design, architecture decisions | SPEC, ADR |
| frontend | Frontend implementation | Code + component tests |
| backend | Backend implementation | Code + unit tests + API |
| qa | Test design and execution (round 1 + retest) | TEST-PLAN, E2E tests |
| reviewer | Code review (subagent) | Review report |
| librarian | Document retrieval (subagent) | Retrieval results |

Enabling agent teams: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is already set in `.claude/settings.json`.

**Fallback when agent teams / SendMessage are unavailable.** This is an experimental feature; on a Claude Code version that lacks it, inter-agent `SendMessage` won't work and the flow would otherwise stall silently. In that case the **orchestrator (main Claude) acts as the router**: it invokes each role with the Task/subagent tool, reads that agent's output itself, and dispatches the next stage manually instead of relying on agent-to-agent messages. The `stage` field in frontmatter remains the source of truth either way, so the document flow is identical — only the handoff mechanism changes. If handoffs seem to vanish, assume the feature is off and switch to router mode.

### New Features Go Through pm (not generic brainstorming)

When the user starts a new feature, dispatch the **pm** agent first. Do **not** trigger a generic brainstorming/planning skill (e.g. `superpowers:brainstorming`) for feature work — its terminal state writes a plan that bypasses the PRD → SPEC → approval flow. The pm owns requirement shaping (it has its own lightweight brainstorming for L-tier work) and ends by writing a PRD. (User instructions outrank skill triggers.)

## Change-size Tiers (pick the flow that fits)

Not every change needs the full 8 stages. Classify the work first, then pick the flow:

| Tier | Typical change | Flow | Docs |
|---|---|---|---|
| **S — small** | bug fix, copy/style tweak, single-file logic change, config | dev edits directly → run existing tests → reviewer → done | none |
| **M — medium** | single feature extension, backend change with no API-contract change, one new interaction | pm writes a short note → dev implements → qa smoke test | optional light PRD (no SPEC) |
| **L — large** | new page/module, cross-layer or API change, DB schema change, affects multiple agents | full 8-stage flow below, all 3 approval gates active | full PRD + SPEC + TEST-PLAN |

Rule of thumb: only one file's internals change, no API change → **S**; an API changes but not the schema, ≤ 2 files → **M**; DB schema changes / a new API route / multiple subsystems touched → **L**.

**Who classifies, and when.** The **orchestrator (main Claude) classifies at intake**, before dispatching any agent — this is the one decision that precedes the pm-first rule. When in doubt, classify **up** (the cost of an unnecessary PRD is small; the cost of a skipped gate on a schema change is large).

**Escalation is mandatory and the boundary is not one-way.** If an S or M change turns out, mid-flight, to touch a DB schema, add or change an API route, or reach into a second subsystem, the agent **must stop, re-classify up, and re-enter the flow at the matching gate** (don't finish it as S just because it started as S). The **reviewer is the backstop**: if a review of an S/M change shows an API-contract or schema change, the reviewer flags `tier-escalation` and the change does not merge until it has gone through the right gate.

**S-tier testing**: the existing suite must still pass; if you touch core logic (shared utilities, data processing, common components), add a unit test covering the change.

The 8-stage flow below applies in full to **L**. **M** uses a trimmed version: a short PRD and **one** lightweight checkpoint — the user OKs the short note before dev starts — but no formal SPEC and no separate ship gate. **S** skips the flow entirely.

## Development Flow (strictly serial, 8 stages)

```
1. Pending          - Requirement registered
   ↓
2. PM designing     - pm writes the PRD (features, prototype, business flow, data flow)
   ↓ 🛑 User approves the PRD
3. Architect designing - architect writes the SPEC (including API, data model, task breakdown)
   ↓ 🛑 User approves the technical design
4. Developing       - frontend // backend implement in parallel + self-test
   ↓
5. Testing round 1  - qa runs tests (including Playwright E2E)
   ↓
6. Fixing           - dev fixes issues found in round 1 (if any)
   ↓
7. Testing round 2  - qa runs automated regression + verifies fixes
   ↓ 🛑 User approves shipping
8. Done             - Approved & ready to merge/ship (see "Scope boundary" below)
```

### Scope boundary (what "Done" means)

This team takes a requirement from idea to **approved, tested, merge-ready code**. The terminal stage is still keyed `deployed` in frontmatter (for backward compatibility), but it means **"done — approved and ready to ship"**, *not* "running in production".

**Out of scope — these stay yours:** running CI/CD, building artifacts, deploying to environments (dev/staging/prod), database migration execution, monitoring/alerting, and production rollback. The `backend`'s migration + rollback scripts and the `RUNBOOK` are produced as deliverables but are **not executed** by any stage. If you want a release gate, wire your own CI to run the test suite on the PR and treat a green run as part of the ship approval.

### Mandatory Human Approval Gates

- **🛑 Stage 2 → 3**: User approves the PRD (are the features, prototype, and flow all OK?)
- **🛑 Stage 3 → 4**: User approves the SPEC (is the technical design OK?)
- **🛑 Stage 7 → 8**: User approves shipping (is the code ready to merge/ship?)

At these gates the agent stops and waits; it does not advance automatically.

**The agent must not silently end its turn while waiting.** When it reaches a gate (or has to wait on another agent), it states plainly what it is waiting for and what it needs from you, in the same turn — so a wait is never indistinguishable from an abandoned task.

**Approval is recorded, not just spoken.** When you approve, the responsible agent sets `approved-by: <your name or "user">` in the document frontmatter before advancing. This makes the gate auditable on the board.

### Definition of Ready / Definition of Done (gate checklists)

The agent presenting a gate states which items are met; the user uses them to approve deliberately rather than rubber-stamp a 200-line document.

**DoR — before pm moves a PRD to `awaiting-prd-approval`:**
- [ ] Target user, pain point, and success metric are stated
- [ ] Every acceptance criterion is testable
- [ ] Every Non-goal has a matching `BACKLOG-NNN` entry
- [ ] Prototype flags the E2E key points

**DoD — before the ship gate (`awaiting-deploy-approval`):**
- [ ] Every PRD acceptance criterion maps to a passing test
- [ ] `python scripts/check_state.py` reports no errors
- [ ] TEST-PLAN round-2 results are filled in and green
- [ ] Reviewer raised no unresolved Critical findings
- [ ] Backend: migration + rollback scripts present (if schema changed)
- [ ] Security: for auth/money/PII features, the SPEC's "Security & abuse cases" are addressed and have negative tests; any new dependency is noted for supply-chain scanning
- [ ] SPEC-000 update is queued (architect applies it once shipped)

### Approval Gates Are Loops, Not One-Way Doors

When you give feedback at a gate, the orchestrator (main Claude) **must route it back to the same agent** that produced the artifact; that agent revises and re-submits, and this repeats until you explicitly approve ("looks good" / "approved"). The orchestrator must **not** absorb the feedback itself, jump ahead to the next stage, or hand the work to a different agent.

```
Agent artifact (PRD / SPEC / ADR)
    ↓
🛑 User review
    ├── "approved"      → advance to the next stage
    └── "change X ..."  → route back to the SAME agent → revise → re-submit (loop)
```

### Cross-agent Collaboration Rules

Communicate directly via SendMessage, without routing through the lead:

- frontend finds the API unclear → ask backend
- frontend/backend find the requirement ambiguous → ask pm
- a design gap is hit during implementation → stop the task and ask architect
- qa finds a requirement is untestable → ask pm
- qa finds an implementation bug → SendMessage the corresponding dev

### Mandatory Actions After a Stage Completes

After an agent finishes its stage task, it **must**:

1. Update the stage field in the frontmatter of the corresponding document
2. Confirm STATUS refreshed — the PostToolUse hook reruns `scripts/refresh_status.py` automatically on any `docs/**/*.md` edit; only run `python scripts/build_status.py` by hand if the hook didn't fire
3. Notify the agent for the next stage via SendMessage (or pm, for approval)

**Stage 4 → 5 handoff (the parallel-dev join).** frontend and backend run in parallel, so neither may unilaterally hand off to qa. Rules:
- The dev who finishes **first** sets its own `frontend-done: true` / `backend-done: true` flag and notifies the other — it does **not** advance the stage or call qa.
- The dev who finishes **second** verifies both flags are true, sets the PRD stage to `testing-round1`, and only then notifies qa.
- qa does not start round 1 until **both** flags are true. If only one is set, qa pings the missing dev rather than testing a half-built feature.

**Additional action at `deployed` (= done):** the architect updates `docs/spec/SPEC-000-current-state.md` — append new APIs, data model changes, and module updates introduced by this PRD. SPEC-000 is the single source of truth for the overall system architecture and must stay current. (In multi-developer mode this happens on the **integration branch after merge**, not on each feature branch — see "Multi-Developer Mode".)

### Progress health is event-triggered, not scheduled

Agents are event-driven — nothing runs "once a day," so don't rely on a patrolling agent to notice stalls. Instead:
- **Always-on detection is mechanical**: `build_status.py` renders a `⚠️ State warnings` block (stalled requirements, stages past their artifacts) and `check_state.py` asserts the same invariants as a gate. These run on every doc edit via the hook.
- **The orchestrator (main Claude)** is present every turn and should surface any State-warnings to the user rather than letting them sit silently.
- **pm (Hat B)** is the progress *owner* but is dispatched on demand — for status reports, gate summaries, and chasing down blockers — not as a standing daemon.

## Document System

### 7 Document Types

| Type | Prefix | Directory | Who writes it | Requirement link |
|---|---|---|---|---|
| Product requirement | PRD | docs/prd/ | pm | One-to-one |
| Technical spec | SPEC | docs/spec/ | architect | One-to-one (paired numbering) |
| Test plan | TEST-PLAN | docs/test-plan/ | qa | One-to-one (paired numbering) |
| Architecture decision | ADR | docs/adr/ | architect | Independent numbering, major decisions only |
| Runbook | RUNBOOK | docs/runbook/ | dev | Independent numbering, production modules |
| Backlog | BACKLOG | docs/backlog.md | pm | Running list of deferred work (not stage-tracked) |
| Global progress | STATUS | root STATUS.md | Auto-generated by script | Aggregates all requirements |

The backlog is a single running file (`docs/backlog.md`), owned by pm. Each item gets a stable `BACKLOG-NNN` id. PRD "Non-goals" reference these ids; pm sweeps unimplemented P2/P3 items into the backlog after a PRD deploys, and checks the backlog when a PRD enters development for items it will incidentally resolve or supersede.

**ID pairing rule**: a single requirement runs through multiple documents, **using the same number**:

```
The requirement "user points deduction" maps to:
  PRD-008.md       ← produced by pm
  SPEC-008.md      ← produced by architect
  TEST-PLAN-008.md ← produced by qa
  tests/e2e/PRD-008.spec.ts  ← E2E written by qa
```

ADR and RUNBOOK use independent numbering (e.g. ADR-001, RUNBOOK-001) and can be referenced by multiple requirements.

### A PRD Must Contain 4 Sections

The PRD written by PM is a comprehensive document:

1. **Feature definition**: user stories, acceptance criteria, feature list
2. **Prototype design**: UI sketches (ASCII or Figma links)
3. **Business flow**: Mermaid flowchart
4. **Data flow**: Mermaid flowchart LR (nodes are data, edges are transformations)

For simple features some sections may be "not applicable," but state explicitly "this feature has no complex business flow."

### A SPEC Must Contain

The SPEC written by the architect comprehensively contains:

- Technical design overview
- Architecture diagram (Mermaid)
- API design (shared by frontend and backend)
- Data model (if there are new tables)
- Technical implementation of the business flow
- Implementation task breakdown (including the frontend/backend split)
- Risks and mitigations

### Frontmatter (the stage field is key)

Every document must have:

```yaml
---
id: PRD-008              # globally unique
title: User Points Deduction
type: prd                # prd | spec | adr | test-plan | runbook
stage: pm-designing      # ⭐ current stage; the STATUS script aggregates on this
owner: pm
created: 2026-05-10
updated: 2026-05-15
summary: One-line summary (< 100 chars)
---
```

Optional: `related`, `tags`, `module`, `priority`, `cancelled-reason`, `supersedes`, `superseded-by`, `approved-by`.

`approved-by` records who signed off at a gate (set by the responsible agent when the user approves) — keeps the approval auditable.

Cross-PRD supersession fields:
- `supersedes: [PRD-003, PRD-005]` — add to the **new** PRD that replaces earlier ones
- `superseded-by: PRD-008` — add to the **old** PRD being replaced, together with `stage: superseded`

### stage Enum (8 stages + special)

| stage value | Meaning | Currently responsible |
|---|---|---|
| `pending` | Pending | - |
| `pm-designing` | PM designing | pm |
| `awaiting-prd-approval` | Awaiting user approval of the PRD | user |
| `architect-designing` | Architect designing | architect |
| `awaiting-spec-approval` | Awaiting user approval of the technical design | user |
| `developing` | Developing | frontend + backend |
| `testing-round1` | Testing round 1 | qa |
| `fixing` | Fixing | frontend/backend |
| `testing-round2` | Testing round 2 | qa |
| `awaiting-deploy-approval` | Awaiting user approval of deployment | user |
| `deployed` | Deployed ✅ | - |
| `cancelled` | Cancelled ❌ | - |
| `superseded` | Replaced by a later PRD 🔁 | architect (set on old PRD when new PRD refactors it) |

### Must-do Before Writing a Document

1. Ask librarian to search for existing documents on the same topic
2. Take the largest existing ID of the same type, +1
3. Pick a template from `docs/_templates/`
4. **After writing, you must update the stage field and run build_status.py**

### Modification Rules

- Modifying body content requires updating the `updated` field
- Major changes to approved/active documents must follow a process similar to creating a new one
- Do not delete documents; archive via the `cancelled` state
- IDs are not reused

## Document Growth Strategy

The current default is "Phase A" (flat). It evolves naturally afterward based on document volume:

| Doc count | Mode | Trigger | Upgrade action |
|---|---|---|---|
| 0-20 | Flat + auto index | Current | - |
| 20-50 | + tags + related | librarian retrieval is inaccurate | Populate extended fields |
| 50-100 | Split into subdirectories by module | A single directory has too many files | Configure the module field |
| 100+ | Upgrade to the full system | Continued growth | See the v1.1 advanced guide |

A separate trigger, independent of doc *count*, is **SPEC-000 size**: because every architect run reads it, a single oversized baseline strains the context window even with few documents. When the dashboard warns SPEC-000 is large (~40 KB), the architect compacts it (it's a current-state snapshot, not a changelog) or splits it per-domain (`SPEC-000-api` / `SPEC-000-data-model` / `SPEC-000-modules`).

## Tool Permissions

All agents are denied by default:

- `Read(.env*)`, `Read(**/.git/**)`, `Write(.git/**)`
- `Bash(rm -rf*)`, `Bash(git push --force*)`

Role permission boundaries:

- **pm/architect**: write only docs/, do not modify src/
- **frontend**: write the frontend code directory and tests/, do not modify backend code
- **backend**: write the backend code directory, tests/, and migrations/, do not modify frontend code
- **qa**: write tests/, may read all code
- **reviewer/librarian**: read-only (subagents)

(The specific frontend/backend directories are pinned down by the architect in SPEC-000, who also updates the "Code directories" field at the top of CLAUDE.md)

### Mechanized frontend/backend boundary

The frontend↔backend split is not just prose — it's enforced by a **PreToolUse hook** (`scripts/guard_paths.py`) that reads the calling agent (`agent_type`) and blocks an Edit/Write that crosses the boundary defined in **`.claude/agent-team-boundaries.json`**. The architect fills that file's globs during the bootstrap step (same time as SPEC-000 / "Code directories"):

```json
{
  "frontend": { "deny_write": ["src/backend/**", "migrations/**"] },
  "backend":  { "deny_write": ["src/frontend/**"] }
}
```

- The guard **fails open** by design: if the agent identity is unavailable, the boundaries file is missing, or a `deny_write` list is empty, nothing is blocked. It is defense-in-depth on top of the prose rules, not a replacement.
- **Monorepo / full-stack layouts** (no clean front/back directory split, e.g. Next.js app dir, tRPC): leave the relevant `deny_write` lists **empty** to disable enforcement, and rely on the prose rules + review. Don't invent a split that doesn't exist.
- The guard relies on Claude Code populating `agent_type` for subagent tool calls (experimental agent-teams behaviour); if that's absent it is simply inert.

## Git Commit Convention

```
<type>(<agent>): <description>

type: feat | fix | docs | refactor | test | chore
agent: pm | architect | frontend | backend | qa

Examples:
docs(pm): add PRD-008 user points deduction
feat(backend): implement points API (SPEC-008, TASK-001)
test(qa): add PRD-008 E2E tests
```

For every commit that involves a document stage change, **you must also run build_status.py and commit the updated STATUS.md along with it**.

## Multi-Developer Mode (optional)

When several people work the **same project**, each running their own agent team in their own environment, the single-user flow needs extra coordination — otherwise generated files, ID numbers, and the SPEC-000 baseline all collide at merge time. Run one feature branch per person; the branch name is that person's identity.

### Setup: `.claude/` is committed, shared truth (not per-person installs)

Scaffold **once**, commit the whole `.claude/` directory (agents, skills, `settings.json`, `CLAUDE.md`) plus `scripts/` and `docs/_templates/` to the repo, and have everyone pull it. Do **not** have each person `/plugin install` independently — that drifts agent definitions, the process contract, and scripts across environments so the "same" project behaves differently per person. The committed copy is the source of truth; upgrade it in one PR.

Each environment still needs `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and a Claude Code version that supports agent teams (else see the router fallback above).

### Generated files are build artifacts — don't commit them from feature branches

`status.html` and `docs/index.yaml` are pure derived output; **gitignore them** (see the `.gitignore` snippet in README). `STATUS.md` may be committed for GitHub viewing, but **only the integration branch regenerates and commits it** — feature branches let the hook refresh it locally but must not commit it (it's a guaranteed merge conflict otherwise). Treat all three as regenerable: `python scripts/build_index.py && python scripts/build_status.py`.

### Claim ID numbers on the shared branch before branching

"Highest ID + 1" is computed locally, so two people will pick the same `PRD-009` on separate branches and collide on merge. Protocol:

1. On the integration branch, run `python scripts/next_id.py prd` (also `spec` / `backlog` / `adr`) to get the next free number — it scans both files and `docs/index.yaml` reservations.
2. Reserve it: add a stub entry to `docs/index.yaml` and push to the integration branch.
3. Branch off and write the real document with that number.

This applies to PRD/SPEC/TEST-PLAN ids **and** to `BACKLOG-NNN` entries (backlog.md is a shared single file — coordinate additions the same way).

### Cross-branch invisibility — sync before you design

An architect's cross-PRD impact analysis only sees documents **on the current branch**; another person's in-flight PRD on an unmerged branch is invisible. Before pm writes a PRD or architect writes a SPEC, **rebase/merge from the integration branch** so you see what's already merged, and check the `docs/index.yaml` reservations for in-flight numbers. If two active PRDs touch the same module/API/table, serialize them or have the architects add an explicit integration task — don't let them merge blind.

### SPEC-000 is reconciled on the integration branch only

The living architecture doc is a magnet for concurrent appends. Feature branches do **not** edit SPEC-000. After a PRD merges, a designated architect updates SPEC-000 **on the integration branch** to fold in that PRD's API/data-model/module changes. This keeps one authoritative baseline instead of N divergent ones.

### Approval gates map onto PRs (but keep the early gates)

PR review can serve as the **ship** gate (merging = ship approval). But the PRD and SPEC gates happen *before* implementation for a reason (catching a bad design before code is written), so prefer to still get PRD/SPEC sign-off in-session (or via stacked PRs) rather than collapsing all three into one final PR review. Record sign-off with `approved-by` either way.

### Memory is local — durable knowledge goes in committed docs

`memory: project` is per-environment and is **not** shared across teammates; don't rely on it as team truth. Anything the whole team must know (architecture decisions, conventions, fragile modules) belongs in committed documents — ADRs, SPEC-000, this CLAUDE.md — not in agent memory.

## Context Management

- Finding documents → use librarian, do not grep yourself
- Running tests / extensive searches → spawn a subagent
- Context exceeds 70% → `/compact`

## Common Commands

```bash
# Rebuild the document index
python scripts/build_index.py

# Rebuild the STATUS board (the PostToolUse hook also does this automatically)
python scripts/build_status.py

# Check intended state vs. evidence (use as a pre-ship gate / in CI; exit 1 on errors)
python scripts/check_state.py

# Allocate the next free document id (multi-dev: run on the integration branch)
python scripts/next_id.py prd

# Run Playwright E2E
npx playwright test

# Run E2E for a single PRD only
npx playwright test tests/e2e/PRD-008.spec.ts
```
