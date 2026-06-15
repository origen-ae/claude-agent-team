---
id: TEST-PLAN-XXX
title: <Feature Name> Test Plan
type: test-plan
stage: testing-round1
owner: qa
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: One-line summary — what this test plan covers and the target quality level
related: [PRD-XXX, SPEC-XXX]
---

# <Feature Name> Test Plan

## TL;DR

<!-- 1-3 sentences: test scope, key metrics, testing approach -->

## 1. Links

- **PRD**: PRD-XXX
- **SPEC**: SPEC-XXX

## 2. Test Scope

### In Scope

- 

### Out of Scope

- 

## 3. Test Cases

### 3.1 Unit Tests (owned by dev)

Written by backend/frontend themselves during implementation; QA reviews the coverage.

Expected coverage:
- backend: core business logic ≥ 80%
- frontend: key components 100%

### 3.2 Contract Tests (front/back API seam — run before E2E)

Derived from the SPEC API design. Each endpoint's request/response **shape**, HTTP **status**, and **error codes** must match the SPEC exactly — this is where frontend and backend silently drift apart. Fast, no browser; fail here before spending an E2E run.

| Case ID | Endpoint | Asserts | Expected |
|---|---|---|---|
| CT-001 | POST /api/order/calc | success response shape + fields match SPEC §5.1 | 200, `{code, data:{...}}` schema valid |
| CT-002 | POST /api/order/calc | each SPEC error code is reachable & correct | 400 `POINTS_OVER_LIMIT`, etc. |
| CT-003 | POST /api/order/submit | shape + status + error codes match SPEC | per SPEC §5.2 |

### 3.3 Integration Tests

Derived from the PRD acceptance criteria:

| Case ID | Source | Description | Expected Result |
|---|---|---|---|
| IT-001 | PRD AC1 | User can redeem 100 points for a 1-dollar discount | Order total decreases by ¥1 |
| IT-002 | PRD AC2 | ... | ... |

### 3.4 Security / Abuse Tests

One negative test per threat in the SPEC's "Security & abuse cases" section (required for auth/money/PII features):

| Case ID | SPEC threat | Attempt | Expected |
|---|---|---|---|
| SEC-001 | S1 cross-user deduction | submit another user's order_id | 403 / rejected |
| SEC-002 | S3 negative/oversized points | points = -100 | 400, balance unchanged |

### 3.5 Playwright E2E

**File**: `tests/e2e/PRD-XXX.spec.ts`

| Case ID | Type | Description | PRD Acceptance Covered |
|---|---|---|---|
| E2E-001 | happy-path | Full user checkout flow including points redemption | AC1, AC2 |
| E2E-002 | edge | Show an error when points exceed the balance | AC3 |
| E2E-003 | edge | Block redemption when points exceed 50% of the order | AC5 |
| E2E-004 | a11y | Accessibility scan of the checkout page | - |

### 3.6 API Boundary-Value Tests

| Endpoint | Test Scenario | Expected |
|---|---|---|
| POST /api/order/calc | points = 0 | Redeem 0, normal response |
| POST /api/order/calc | points = negative | 400 error |
| POST /api/order/calc | points = oversized value | POINTS_INSUFFICIENT |

### 3.7 Performance Budget

Assert/record against the SPEC §9 targets — a target nobody checks is not a target:

| Endpoint | SPEC budget | Measured (round 1) | Pass? |
|---|---|---|---|
| POST /api/order/calc | P95 < 200ms | | |
| POST /api/order/submit | P95 < 500ms | | |

## 4. Round-1 Test Results

**Execution time**: YYYY-MM-DD HH:MM
**Executed by**: qa

### 4.1 Summary

- Total cases: N
- Passed: N
- Failed: N
- Skipped: N

### 4.2 Failure Details

| Case ID | Failure Reason | Severity | Assigned To | Fix Commit |
|---|---|---|---|---|
| E2E-002 | Error message copy is inconsistent | Warning | frontend | (pending fix) |
| IT-003 | Boundary-value calculation error (100 points = ¥1.00, actually computed as ¥0.99) | Critical | backend | (pending fix) |

### 4.3 Coverage Blind Spots

- 

### 4.4 Round-1 Conclusion

- [ ] Pass → stage: awaiting-deploy-approval
- [x] Fail, fixes required → stage: fixing

## 5. Retest Results

**Execution time**: YYYY-MM-DD HH:MM

### 5.1 Summary

- Total cases: N
- Passed: N
- Failed: N

### 5.2 Verification of Round-1 Failed Cases

| Case ID | Round-1 Status | Fix Commit | Retest Status |
|---|---|---|---|
| E2E-002 | Failed | abc1234 | ✅ Passed |
| IT-003 | Failed | def5678 | ✅ Passed |

### 5.3 Regression Test Results

(Which regression suites were run, and what the results were)

### 5.4 Retest Conclusion

- [x] Pass → stage: awaiting-deploy-approval
- [ ] Still failing → stage: fixing (loop again)

## 6. Test Metrics Summary

(Used for automatic aggregation on the STATUS dashboard)

| Metric | Round 1 | Retest |
|---|---|---|
| Unit test pass rate | 100% | 100% |
| E2E pass rate | 75% | 100% |
| a11y violations | 0 | 0 |
| Performance: API P95 | 180ms | 180ms |
