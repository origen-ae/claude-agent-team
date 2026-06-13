---
id: ADR-000
title: ADR conventions
type: adr
stage: deployed
owner: architect
created: 2026-05-15
updated: 2026-05-15
summary: Conventions for how architecture decisions are recorded in the project
related: []
---

# ADR conventions

## TL;DR

Every non-trivial technical decision is recorded in its own standalone ADR, covering context, alternatives, decision, and consequences.

## Status

accepted

## 1. Context

As the project grows in complexity, technical decisions need to be traceable, reviewable, and inheritable.

## 2. Alternatives

### Option A: Free-form notes
- Pro: low barrier to entry
- Con: inconsistent format, hard to index, easy to lose

### Option B: Standardized ADR + git
- Pro: diffable, referenceable, indexable, shares the same lifecycle as the code
- Con: slightly more formal

### Option C: Write it into the SPEC
- Pro: context stays in one place
- Con: the decision gets buried in implementation details

## 3. Decision

**Adopt Option B**: every non-trivial technical decision must have its own standalone ADR.

## 4. Consequences

### Positive
- Decisions are traceable
- New members quickly understand how the architecture evolved
- Prevents "circling back to an already-rejected option"

### Negative
- Slightly more work for the architect

## 5. Implementation

- ADRs live in `docs/adr/`
- File name: `ADR-XXX-<topic>.md`
- Use the `docs/_templates/TEMPLATE-ADR.md` template
- Once an ADR is accepted, its content is no longer modified; changes go through a new ADR
