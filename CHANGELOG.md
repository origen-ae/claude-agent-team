# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses [Semantic Versioning](https://semver.org/).

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
