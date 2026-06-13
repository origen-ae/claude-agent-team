---
name: claude-agent-team
description: Use when setting up a multi-agent team workflow in Claude Code — scaffolds 7 agents (PM, architect, frontend, backend, QA, reviewer, librarian), an 8-stage serial flow with human approval gates, a document system (PRD/SPEC/TEST-PLAN/ADR/RUNBOOK), and an auto-generated STATUS dashboard. Triggers on requests like "set up an agent team", "multi-agent dev workflow", or "agent team for my project".
---

# Claude Agent Team

Scaffold a complete serial multi-agent development team into the current project: 7 agents, an 8-stage workflow with human approval gates, a shared document system, and an auto-generated progress dashboard.

## When to use

Use when the user wants to set up a structured, multi-agent development team in their project — phrases like "set up an agent team", "give me a multi-agent dev workflow", "scaffold the PM/architect/frontend/backend/QA team", or "agent team for my project".

## What it sets up

- **7 agents** in `.claude/agents/`: `pm`, `architect`, `frontend`, `backend`, `qa`, `reviewer`, `librarian`
- **8-stage serial flow** with 3 human approval gates (PRD, SPEC, deploy)
- **Document system** in `docs/`: PRD / SPEC / TEST-PLAN / ADR / RUNBOOK, with ID pairing (PRD-008 → SPEC-008 → TEST-PLAN-008)
- **Auto-generated dashboard**: `STATUS.md` + `status.html` built by `scripts/build_status.py`, refreshed by a PostToolUse hook
- **2 bundled skills**: `doc-conventions`, `playwright-testing`
- **Playwright E2E** config + conventions

See `references/` for the full design: `workflow.md`, `roles.md`, `document-system.md`, `scenarios.md`, `faq.md`.

## Scaffolding procedure

1. **Confirm the target project root.** Default to the current working directory; confirm with the user if ambiguous.
2. **Copy `assets/` into the project root**, preserving structure (`.claude/`, `docs/`, `scripts/`, `tests/`, `CLAUDE.md`, `playwright.config.ts`). **Do not overwrite** existing files — list any conflicts and ask the user how to proceed.
3. **Do not fill the `CLAUDE.md` placeholders** (tech stack / core modules / code dirs) yet — they are filled in step 5.
4. **Tell the user to install dependencies:**
   - `pip install -r scripts/requirements.txt`
   - (optional E2E) `npm install -D @playwright/test @axe-core/playwright && npx playwright install --with-deps chromium`
5. **Bootstrap project baseline:** have the `architect` agent browse `src/` and generate `docs/spec/SPEC-000-current-state.md`, then backfill the `CLAUDE.md` placeholders (tech stack, core modules, code dirs).
6. **First run:** `python scripts/build_index.py && python scripts/build_status.py`, then open `STATUS.md` / `status.html`.
7. **Verify:** `/agents` lists the 7 agents; test the `librarian` ("retrieve the project current state" → returns SPEC-000). Point the user to `references/workflow.md` to run their first requirement through the 8 stages.

## Requirements

- Claude Code with agent teams enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, set in the scaffolded `.claude/settings.json`)
- Python 3 for the dashboard scripts
- A POSIX shell for the PostToolUse hook (macOS/Linux/git-bash/WSL on Windows)
- Node + Playwright only if you use the E2E layer
