---
name: doc-conventions
description: Project documentation conventions. Used by every agent when creating, modifying, or referencing documents.
---

# Project Documentation Conventions

## The 7 Document Types

| Type | Prefix | Directory |
|---|---|---|
| Product requirements | PRD | docs/prd/ |
| Technical specification | SPEC | docs/spec/ |
| Test plan | TEST-PLAN | docs/test-plan/ |
| Architecture decision | ADR | docs/adr/ |
| Incident runbook | RUNBOOK | docs/runbook/ |
| Backlog | BACKLOG | docs/backlog.md (single running file, pm-owned, not stage-tracked) |
| Progress board | STATUS | root-level STATUS.md (script-generated) |

## ID-Pairing Rule

One requirement = one numeric ID, threaded across multiple documents:

```
Requirement number 008 maps to:
  PRD-008.md
  SPEC-008.md
  TEST-PLAN-008.md
  tests/e2e/PRD-008.spec.ts
```

ADR and RUNBOOK are numbered independently.

## Required Frontmatter Fields

```yaml
---
id: <PREFIX>-<3-digit number>
title: Short title
type: prd | spec | adr | test-plan | runbook
stage: pending | pm-designing | awaiting-prd-approval | architect-designing | awaiting-spec-approval | developing | testing-round1 | fixing | testing-round2 | awaiting-deploy-approval | deployed | cancelled
owner: <agent-name>
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: One-sentence summary (< 100 characters)
---
```

## Full Description of the stage Enum

| stage | Meaning | Who may set this state |
|---|---|---|
| `pending` | Awaiting kickoff | pm (at creation) |
| `pm-designing` | PM is designing | pm |
| `awaiting-prd-approval` | Waiting for user to approve the PRD | pm when done |
| `architect-designing` | Architecture design in progress | architect |
| `awaiting-spec-approval` | Waiting for user to approve the technical design | architect when done |
| `developing` | In development | frontend or backend at start |
| `testing-round1` | First test round in progress | qa |
| `fixing` | Fixing in progress | qa (when failures are found) |
| `testing-round2` | Re-test round in progress | qa |
| `awaiting-deploy-approval` | Waiting for user to approve deployment | qa (when the re-test passes) |
| `deployed` | Deployed | marked by pm after deployment |
| `cancelled` | Cancelled | pm (when the user decides not to proceed) |
| `superseded` | Replaced by a later PRD | architect (when a new PRD refactors this one) |

**Key rule**: Once marked `awaiting-*-approval`, you must wait for the user's approval; agents may not advance on their own.

## Required Before Creating a Document

1. Ask the librarian to search whether one already exists
2. Take the largest ID of the same type + 1
3. Copy the template from `docs/_templates/`
4. Fill in the complete frontmatter

## Required After Modifying

1. Update the `updated` field
2. If you changed the stage, run `python scripts/build_status.py`

## Cross-Document References

Use the ID (e.g. `PRD-008`), not natural language. The optional `related` field lists associations:

```yaml
related: [SPEC-008, ADR-005]
```

## SPEC-000 Is a Living Document

`docs/spec/SPEC-000-current-state.md` is **not** a one-time snapshot. The architect must update it after every PRD reaches `deployed`:

- Append new API routes to the API inventory
- Update the data model section for new tables or fields
- Update module descriptions and the dependency diagram if responsibilities shifted

Do not rewrite SPEC-000 from scratch — patch the relevant sections and update the `updated` field.

## Cross-PRD Supersession

When a new PRD refactors or replaces content from an earlier PRD:

- Add `supersedes: [PRD-003]` to the new PRD's frontmatter (optional field)
- Add `superseded-by: PRD-008` and change stage to `superseded` in the old PRD's frontmatter
- The architect notes the impact in the new SPEC's "Links" section

Optional frontmatter fields for cross-PRD tracking:
```yaml
supersedes: [PRD-003, PRD-005]   # this PRD replaces these
superseded-by: PRD-012            # set when this PRD is replaced
```

## Do Not

- Do not delete documents (archive via cancelled or superseded)
- Do not reuse IDs
- Do not write the same content in multiple documents
- Do not write "TBD" (either leave it out, or state explicitly "pending decision by X, expected to be filled in by Y")
