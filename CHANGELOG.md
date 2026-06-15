# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Semantic Versioning](https://semver.org/).

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
