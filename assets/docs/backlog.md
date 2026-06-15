---
id: BACKLOG
title: Backlog
type: backlog
owner: pm
updated: 2026-02-11
summary: Running list of deferred and planned work items (BACKLOG-NNN).
---

# Backlog

Deferred and planned work, owned by pm. Each item has a stable `BACKLOG-NNN` id that PRD "Non-goals" can reference. This is a single running file — it is **not** stage-tracked and does not appear on the STATUS dashboard.

| ID | Title | Priority | Source | Status |
|---|---|---|---|---|
| BACKLOG-001 | _(example)_ Bulk CSV export for reports | P2 | PRD-001 §Non-goals | open |

## Conventions

- **id**: `BACKLOG-NNN`, never reused.
- **Priority**: P0–P2.
- **Source**: where it came from (e.g. `PRD-001 §Non-goals`, a user request, a retro).
- **Status**: `open` | `in-progress` | `done` | `wontfix` | `superseded` (note which PRD superseded it).
- pm sweeps unimplemented items here after a PRD deploys, and updates statuses when a new PRD incidentally resolves an item.
