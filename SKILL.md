---
name: claude-agent-team
version: 1.3.0
description: Use when setting up a multi-agent team workflow in Claude Code — scaffolds 7 agents (PM, architect, frontend, backend, QA, reviewer, librarian), an 8-stage serial flow with human approval gates and change-size tiers (S/M/L), a document system (PRD/SPEC/TEST-PLAN/ADR/RUNBOOK/BACKLOG), and an auto-generated STATUS dashboard. Triggers on requests like "set up an agent team", "multi-agent dev workflow", or "agent team for my project".
---

# Claude Agent Team

Scaffold a complete serial multi-agent development team into the current project: 7 agents, an 8-stage workflow with human approval gates, a shared document system, and an auto-generated progress dashboard.

## When to use

Use when the user wants to set up a structured, multi-agent development team in their project — phrases like "set up an agent team", "give me a multi-agent dev workflow", "scaffold the PM/architect/frontend/backend/QA team", or "agent team for my project".

## What it sets up

- **7 agents** in `.claude/agents/`: `pm`, `architect`, `frontend`, `backend`, `qa`, `reviewer`, `librarian`
- **8-stage serial flow** with 3 human approval gates (PRD, SPEC, ship)
- **Change-size tiers (S/M/L)** — small changes skip the full flow; only large ones run all 8 stages
- **Document system** in `docs/`: PRD / SPEC / TEST-PLAN / ADR / RUNBOOK + a pm-owned BACKLOG, with ID pairing (PRD-008 → SPEC-008 → TEST-PLAN-008)
- **Auto-generated dashboard**: `STATUS.md` + `status.html` built by `scripts/build_status.py`, refreshed by a PostToolUse hook
- **2 bundled skills**: `doc-conventions`, `playwright-testing`
- **Playwright E2E** config + conventions

See `references/` for the full design: `workflow.md`, `roles.md`, `document-system.md`, `scenarios.md`, `faq.md`.

## Scaffolding procedure

1. **Confirm the target project root.** Default to the current working directory; confirm with the user if ambiguous. Prefer a clean git tree or a dedicated branch, so the install is easy to roll back.
2. **Copy `assets/` into the project root**, preserving structure (`.claude/`, `docs/`, `scripts/`, `tests/`, `CLAUDE.md`, `playwright.config.ts`). Copy brand-new files as-is. For files that **already exist**, do NOT blindly overwrite *or* skip — these two need a structured merge (overwriting loses the user's config; skipping silently disables the whole system):
   - **`.claude/settings.json`**: back up to `settings.json.bak`, then merge key-by-key — set `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, set `teammateMode`, union the `permissions.deny` array (dedupe; keep the user's existing allow/deny), and append our PostToolUse hook to the existing `hooks.PostToolUse` array. Show the user the diff.
   - **`CLAUDE.md`**: back up to `CLAUDE.md.bak`, then append our "Project Collaboration Conventions" content (including the `<!-- claude-agent-team: vX.Y.Z -->` version marker) rather than overwriting.
   - Any other genuine conflict: list it and ask the user how to proceed.
3. **Add generated artifacts to `.gitignore`** (append, don't overwrite): `status.html`, `docs/index.yaml`, `playwright-report.json`, `__pycache__/`. (Only the integration branch commits `STATUS.md`.)
4. **Do not fill the `CLAUDE.md` placeholders** (tech stack / core modules / code dirs) yet — they are filled in the bootstrap step below.
5. **Tell the user to install dependencies:**
   - `pip install -r scripts/requirements.txt`
   - (optional E2E) `npm install -D @playwright/test @axe-core/playwright && npx playwright install --with-deps chromium`
6. **Bootstrap project baseline:** have the `architect` agent browse `src/` and generate `docs/spec/SPEC-000-current-state.md`, then backfill the `CLAUDE.md` placeholders (tech stack, core modules, code dirs).
7. **First run:** `python scripts/build_index.py && python scripts/build_status.py`, then open `STATUS.md` / `status.html`.
8. **Verify:** `/agents` lists the 7 agents; test the `librarian` ("retrieve the project current state" → returns SPEC-000). Point the user to `references/workflow.md` to run their first requirement through the 8 stages.

For a **team on a shared project**, commit `.claude/`, `scripts/`, `docs/_templates/`, and `CLAUDE.md` to the repo so everyone shares one source of truth (don't have each person install separately). See CLAUDE.md → "Multi-Developer Mode".

## Scope

The team delivers a requirement up to **approved, tested, merge-ready code** (terminal stage keyed `deployed`, meaning "done"). Running CI/CD and the actual production deployment stay the user's responsibility — migration/rollback scripts and RUNBOOKs are produced as deliverables but not executed by any stage.

## Requirements

- Claude Code with agent teams enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, set in the scaffolded `.claude/settings.json`); if your version lacks agent teams, the orchestrator falls back to routing each role itself (see CLAUDE.md)
- Python 3 for the dashboard scripts and the PostToolUse hook (the hook is pure Python — works on Windows PowerShell/CMD, macOS, and Linux; no POSIX shell required)
- Node + Playwright only if you use the E2E layer
