# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Semantic Versioning](https://semver.org/).

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
