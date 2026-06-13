# Worked Example: Loyalty Points Checkout Discount

This folder is a complete worked example of what the **claude-agent-team** skill produces for a single shipped feature: a loyalty-points checkout discount that lets customers redeem accrued points against their order total.

Everything here is **real output, not a template**. These are the actual artifacts the agent team generated and refined while taking the feature from idea to production. We kept them intact — wording, decisions, open questions, and all — so you can see the genuine shape of the work rather than a sanitized skeleton with placeholder text.

## The documents

The feature is captured in three linked documents, each owned by a different role in the team:

- [Product Requirements](./docs/prd/PRD-001.md) — `PRD-001` — the problem, users, scope, and acceptance criteria.
- [Technical Specification](./docs/spec/SPEC-001.md) — `SPEC-001` — the design, data model, and implementation plan that realizes the PRD.
- [Test Plan](./docs/test-plan/TEST-PLAN-001.md) — `TEST-PLAN-001` — the verification strategy and test cases that prove the spec was built correctly.

## How to read it

The documents are connected by a shared ID, so the chain of intent is traceable end to end:

```
PRD-001  ->  SPEC-001  ->  TEST-PLAN-001
```

Each downstream document references the one before it by ID. A spec always names the PRD it satisfies; a test plan always names the spec it verifies. This 1:1:1 pairing is what lets the team (and you) answer "why does this exist?" and "is this covered?" at a glance.

All three documents reached `stage: deployed`, meaning the feature was specified, built, tested, and shipped. This is the steady state you are aiming for: a fully traced set of artifacts whose stages line up behind a feature that is live in production.
