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

| ID | Title | Source | Priority | Prerequisite | Status |
|---|---|---|---|---|---|
| BACKLOG-001 | _(example)_ Bulk CSV export for reports | PRD-001 §Non-goals | P2 | reporting API stable | open |

## Conventions

- **id**: `BACKLOG-NNN`, never reused.
- **Source**: where it came from (e.g. `PRD-001 §Non-goals`, a user request, a retro).
- **Priority**: P0–P3.
- **Status**: `open` | `in-progress` | `done` | `superseded` (note which PRD/BACKLOG superseded it).
- pm sweeps unimplemented P2/P3 items here after a PRD deploys, and updates statuses when a new PRD incidentally resolves an item.
