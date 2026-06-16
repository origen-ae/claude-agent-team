# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Semantic Versioning](https://semver.org/).

## [1.11.0] - 2026-06-16

### Fixed
- **Cancelled/superseded progress bar** (P2-9): these stages sit past `deployed` in the order, so the progress bar rendered them 100% green. They now show no completed milestones (the status label already says cancelled/superseded).
- **HTML escaping** (P2-3): the remaining `status.html` interpolations (backlog id/title/source) are now escaped; removed the unused `jinja2` dependency from `requirements.txt` (the scripts use f-strings; `import yaml` was already dropped from build_status).

### Added
- **Archive directory** (P2-8): `docs/_archive/` is skipped by `build_index.py` / `build_status.py` (like `_templates/`) and searched by the librarian only on request — a place to move long-dead docs out of active scans and the growth thresholds without deleting them.
- **Windows CI leg** (P2-5): `validate.yml` now runs on `windows-latest` as well as Ubuntu (job shell pinned to bash so the harness is identical; scripts execute as native Windows Python) — proving the cross-platform claim.

### Changed
- **playwright.config.ts** (P2-4): the hardcoded `webServer` (`npm run dev` / `:3000`) is commented out with guidance; the architect fills it from the project's real start command/port at bootstrap, or it stays off for non-web projects. `baseURL` is overridable via `BASE_URL`.
- **librarian** (P2-2): on sparse/weak matches it must say so explicitly ("not authoritative") rather than implying a clean miss — a false "no duplicate PRD found" is high-stakes.
- **document-system.md** (P2-10): documents that ADR/RUNBOOK `stage` is informational (never on the board) and the `docs/_archive/` convention.

## [1.10.0] - 2026-06-16

### Added
- **"Cost & Context Budget" guidance** in CLAUDE.md (P1-18). Documents how cost scales with tier ceremony, the rationale for keeping `architect` on **opus** (highest-leverage artifact — **not** downgraded; tunable to sonnet only for routine CRUD SPECs), context-thrift practices (section/summary reads, anchor-based handoffs, reliance on prompt caching for the repeated PRD/SPEC reads within a feature), and a **stop rule** — escalate to the user if a requirement exceeds ~12 agent invocations or a fix/gate loop repeats 3+ times without converging.

### Note
- The audit's suggestion to default `architect` to sonnet was **declined** — architecture is the highest-leverage step; opus stays the default. The cost concern is addressed via tier right-sizing, context thrift, and the stop rule instead.

## [1.9.0] - 2026-06-16

### Added
- **Observability is declared end-to-end** (P1-15) — closing the gap where the flow stopped at `deployed` and the RUNBOOK assumed alert signals nobody produced. The team *declares* what to observe (wiring monitoring stays the user's, per the delivery boundary):
  - **PRD**: success metrics must be **production-observable**; 1-2 are marked `[instrument]` (pm.md + TEMPLATE-PRD).
  - **SPEC**: new "Observability" section (§12) turns each `[instrument]` metric into concrete signals to emit (metric/event/log names + where) and lists alert-worthy conditions; required for production-facing features. Wired into `architect.md` ("A SPEC must contain").
  - **dev**: backend emits the SPEC's declared signals (coding standard).
  - **RUNBOOK**: "Alert Signals" must be non-empty for a production module and reference the SPEC's signal names (not vague descriptions) — making the runbook's "confirm metrics recovered" step actually executable.
  - **DoD** gate item for observability; CLAUDE.md scope boundary now distinguishes **declare** (the team, ships instrumented) vs **wire** (the user's dashboards/alerts). New FAQ Q15.

## [1.8.0] - 2026-06-15

### Added
- **Contract tests guard the front/back API seam** (P1-16): qa now derives **API contract-conformance tests** (request/response shape, status codes, error codes match the SPEC exactly) as a mandatory, run-**early** source — the most dangerous seam, since frontend and backend agree only on the SPEC contract, now fails fast and cheap instead of surfacing in a slow E2E run. Added to `qa.md`, the TEST-PLAN template (new §3.2), `roles.md`, and the DoD.
- **Performance targets become budgets**: the SPEC §9 P95/availability targets are now asserted/recorded by qa (new TEST-PLAN §3.7 "Performance Budget" + DoD item) — "a target nobody checks is not a target".
- **Security/abuse negative tests** wired into the test plan (§3.4), one per SPEC threat (ties P1-14 into the test layer).

### Changed
- **Test pyramid made explicit and right-side-up** (P1-16): qa layers tests as a wide fast base (contract + unit) → integration → a thin top of Playwright E2E for critical paths only. The "two rounds" are reframed everywhere (qa.md, workflow.md, roles.md) as fix-verify cycles, not the only time tests run — every change must pass the suite, which maps onto a CI gate when the user wires one.

## [1.7.0] - 2026-06-15

### Added
- **Security as a first-class concern** (P1-14), at the layers the team controls — security was previously just one bullet in the reviewer checklist:
  - **Design-time threat modeling**: the SPEC template gains a "Security & abuse cases" section (STRIDE-lite — each threat → mitigation → verifying test), REQUIRED when a feature touches auth/authorization, money/balances, PII, file uploads, or untrusted input; otherwise state "Not security-sensitive: <why>". Wired into `architect.md` ("A SPEC must contain").
  - **Reviewer security deep-dive**: a mandatory expanded checklist for sensitive diffs — authorization on every mutation / no IDOR, injection, secrets & PII, money/state integrity (idempotency, no double-spend), and new-dependency supply-chain flags; cross-checked against the SPEC's abuse cases.
  - **DoD gate item** for security (abuse cases addressed + negative tests + new deps noted).
  - **Dependency/supply-chain scanning is the user's CI** (consistent with the delivery boundary): README "Security" section recommends `npm audit` / `pip-audit`, Dependabot/Renovate, and optional CodeQL/semgrep. No dedicated security agent (too heavy for a small team).
  - New FAQ Q14 on security scope.

## [1.6.0] - 2026-06-15

### Changed
- **PM's progress-aggregator hat is now honestly event-triggered** (P1-3). The design previously told the pm to "read STATUS once a day" and called it the "central hub" — but agents are event-driven, with no scheduler, so that role never actually fired. Reframed:
  - Always-on stall/skip detection is **mechanical** — the dashboard's `⚠️ State warnings` block (`build_status.py` / `check_state.py`), added in 1.3.0 — not a patrolling agent.
  - The **orchestrator (main Claude)**, which is present every turn, surfaces those warnings to the user.
  - **pm (Hat B)** is dispatched on demand (status reports, gate summaries, chasing blockers), not as a standing daemon.
  - No 8th agent added — a `delivery-lead` would be just as unscheduled; the fix is honest triggers + the existing mechanical warnings.
- Updated `pm.md`, `references/workflow.md` (dropped "PM is the central hub"), `references/roles.md`, and added a "Progress health is event-triggered" note to CLAUDE.md.

## [1.5.0] - 2026-06-15

### Changed
- **SPEC-000 is a bounded current-state snapshot, not a changelog** (P1-4 audit follow-up / P1-9): the architect now updates entries **in place** (a changed endpoint replaces the old line; a refactored module's paragraph is rewritten) instead of only appending, so SPEC-000's size tracks the *current system* rather than the number of PRDs ever shipped. History stays in the individual PRDs/SPECs.
- The architect reads SPEC-000 **by section** (only the parts a PRD touches) rather than reloading the whole baseline on every design — bounds per-invocation context cost.

### Added
- **SPEC-000 size warning**: `build_status.py` / `check_state.py` warn when the combined `SPEC-000*` baseline exceeds ~40 KB, prompting compaction or a per-domain split.
- **Per-domain split convention**: when SPEC-000 grows too large, split into `SPEC-000-api.md` / `SPEC-000-data-model.md` / `SPEC-000-modules.md` with the main file as a short overview + index. The dashboard/index treat any `SPEC-000*` file as baseline (not a tracked requirement), so the split is transparent.
- "Context limit" documented as a scaling trigger independent of document count (CLAUDE.md, document-system.md).

## [1.4.0] - 2026-06-15

### Added
- **Mechanized frontend/backend boundary** (P1-4): a PreToolUse guard (`scripts/guard_paths.py`) reads the calling agent (`agent_type`) and blocks an Edit/Write that crosses the boundary defined in the new `.claude/agent-team-boundaries.json`. The split is no longer prose-only.
  - **Fails open by design**: if agent identity is unavailable, the boundaries file is missing, or a `deny_write` list is empty, nothing is blocked — it's defense-in-depth on top of the prose rules, never a single point of breakage.
  - Pure-Python and cross-platform; blocks via exit code 2 with a reason.
  - Handles **monorepo / full-stack layouts**: leave `deny_write` empty to disable enforcement where there's no clean split.
  - The architect populates the boundary globs during the bootstrap step (alongside SPEC-000 and the CLAUDE.md "Code directories").

### Changed
- `.claude/settings.json` now registers the PreToolUse path guard in addition to the PostToolUse dashboard refresh; install merges both hook arrays.
- CLAUDE.md "Tool Permissions" documents the mechanized boundary, its fail-open behaviour, and the monorepo escape hatch.

## [1.3.0] - 2026-06-15

A design-audit pass: fixes correctness/honesty bugs found in a holistic review, clarifies the delivery boundary, and hardens multi-developer use.

### Fixed
- **Cross-platform hook**: the PostToolUse hook is now a pure-Python entry point (`scripts/refresh_status.py`) that works on Windows PowerShell/CMD, macOS, and Linux. The old POSIX one-liner (`... 2>/dev/null || true`) silently did nothing on Windows, so the dashboard never refreshed there.
- **Hook path filtering**: removed the non-existent `pathMatcher` hook field (it was silently ignored, firing the rebuild on *every* Edit/Write); the entry point now filters to `docs/**/*.md` itself and also rebuilds the librarian index.
- **Honest progress board**: progress checkmarks are now artifact-driven — a milestone only shows ✅ if the artifact proving it (SPEC, TEST-PLAN) exists; a stage that jumped ahead without its artifact renders ⚠️ instead of a falsely green check.
- **Consistency**: document-type count corrected to **7** (README, roles); "no Lark" naming unified; `superseded` stage and `supersedes`/`superseded-by`/`approved-by` fields propagated to all references; `references/document-system.md` no longer embeds a stale full copy of the doc-conventions skill (now points to the source); duplicate step number in `architect.md` fixed; versions aligned to 1.3.0 (SKILL, FAQ, plugin.json).

### Added
- **State reconciliation** (`scripts/check_state.py`): asserts cross-document invariants (no stage past architecture without a SPEC, no done-without-TEST-PLAN, stalled-item detection) and exits non-zero — usable as a pre-ship gate / in CI. The board surfaces the same warnings in a "⚠️ State warnings" block.
- **ID allocator** (`scripts/next_id.py`): allocates the next free document id from files + index reservations, for collision-free numbering in multi-developer mode.
- **DoR / DoD gate checklists** and an `approved-by` field so gate sign-off is deliberate and auditable; the board now shows each pending item's `summary`.
- **Tier classification ownership + escalation**: the orchestrator classifies S/M/L at intake; mid-flight schema/API/second-subsystem discoveries force an upgrade; the reviewer is the tier-escalation backstop.
- **Parallel-dev join**: explicit `developing → testing-round1` handoff — the second finisher advances the stage; qa waits for both `frontend-done` and `backend-done`.
- **agent-teams fallback**: documented orchestrator-as-router behaviour when the experimental agent-teams feature / SendMessage is unavailable.
- **Uninstall** instructions and an installed-version stamp in the project's CLAUDE.md.

### Changed
- **Delivery boundary clarified**: the terminal state (still keyed `deployed`) now reads as **"Done — approved & merge-ready"**; running CI/CD and the production deploy are explicitly the user's responsibility. Wording updated across CLAUDE.md, README, SKILL, workflow, roles, FAQ.
- **Multi-Developer Mode rewritten**: commit `.claude/` as shared truth (no per-person installs); gitignore `status.html` / `docs/index.yaml` and commit `STATUS.md` only on the integration branch; reserve ids on the integration branch before branching; sync before designing (in-flight branches are invisible to cross-PRD analysis); SPEC-000 reconciled on the integration branch after merge; project memory is local, so shared knowledge goes in committed docs.
- **Install is a structured merge**: `.claude/settings.json` and `CLAUDE.md` are merged key-by-key with a `.bak` backup instead of being overwritten or skipped wholesale.
- CI (`validate.yml`) now actually runs the scripts against the worked example and asserts a non-empty STATUS.
- `build_status.py`: HTML output escapes interpolated titles/summaries; removed an unused import.

## [1.2.0] - 2026-06-15

### Added
- **SPEC-000 living document**: architect must patch SPEC-000 (API inventory, data model, module descriptions) after every deployed PRD; rules enforced in architect agent and doc-conventions skill
- **Backlog enforcement**: PM now writes a `BACKLOG-NNN` entry for every Non-goal before PRD approval; backlog table referenced inline in Non-goals text
- **Cross-PRD supersession**: `supersedes` / `superseded-by` optional frontmatter fields; `superseded` stage with 🔁 emoji; architect marks impacted PRDs as superseded when a new PRD refactors them
- **STATUS backlog summary**: `build_status.py` parses `docs/backlog.md` and renders open P0/P1 items in both STATUS.md and status.html; statuses: `open | in-progress | done | wontfix | superseded`
- `assets/docs/backlog.md` column order aligned with parser: `ID | Title | Priority | Source | Status`

### Changed
- `assets/CLAUDE.md`: added superseded stage, supersedes/superseded-by fields, deployed → update-SPEC-000 rule
- `assets/.claude/agents/architect.md`: cross-PRD impact analysis step + post-deployment SPEC-000 update section
- `assets/.claude/agents/pm.md`: explicit Non-goals → Backlog step (step 6) in PRD workflow
- `assets/docs/_templates/TEMPLATE-PRD.md`: Non-goals section now shows BACKLOG-NNN reference format
- `assets/.claude/skills/doc-conventions/SKILL.md`: superseded stage documented, SPEC-000 living doc rules, cross-PRD supersession rules

## [1.1.0] - 2026-06-15

### Added
- **Change-size tiers (S/M/L)**: small changes skip the full 8-stage flow; only L runs all gates and requires PM + architect
- **BACKLOG doc type**: pm-owned running list of deferred items (`docs/backlog.md`), with stable `BACKLOG-NNN` IDs
- **Multi-developer mode**: feature branches per developer; PR review doubles as approval gates
- **PM-first rule**: new features always route through pm before development begins
- **Approval-loop enforcement**: gates loop back to the same agent for revision until the user explicitly approves

### Changed
- PM agent definition updated to include BACKLOG ownership and S/M/L tier classification
- All agent definitions updated to understand tier routing
- `references/workflow.md`, `roles.md`, `document-system.md`, `faq.md` updated to reflect v1.1 behaviour
- README and SKILL.md updated

## [1.0.0] - 2026-06-13

### Added
- 7 agents: pm, architect, frontend, backend, qa, reviewer, librarian
- 8-stage serial workflow with 3 human approval gates (PRD → SPEC → deploy)
- Document system: PRD, SPEC, TEST-PLAN, ADR, RUNBOOK with ID pairing (`PRD-008 → SPEC-008 → TEST-PLAN-008`)
- Auto-generated STATUS dashboard (`STATUS.md` + `status.html`) via `scripts/build_status.py`
- PostToolUse hook to auto-refresh dashboard on every doc edit
- 2 bundled skills: `doc-conventions`, `playwright-testing`
- Playwright E2E test layer with Page Object conventions
- GitHub Actions CI: Python compilation, JSON validation, frontmatter checks
- Worked example: `examples/loyalty-points-checkout/` (real filled-in docs, not templates)
