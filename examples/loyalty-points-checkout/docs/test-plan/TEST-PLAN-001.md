---
id: TEST-PLAN-001
title: Loyalty Points Checkout Discount Test Plan
type: test-plan
stage: deployed
owner: qa
created: 2026-01-15
updated: 2026-02-11
summary: "Verifies the loyalty points checkout discount across integration, E2E, and API boundary layers; target: all acceptance criteria green with zero a11y violations"
priority: P1
related: [PRD-001, SPEC-001]
---

# Loyalty Points Checkout Discount Test Plan

## TL;DR

This plan validates that users can redeem loyalty points for a checkout discount under a strict set of money rules (100 points = $1.00, capped at 50% of subtotal, all amounts in integer cents). Coverage spans integration tests mapped to AC1-AC4, three Playwright E2E flows, and API boundary-value tests. Round 1 surfaced one off-by-one cents rounding defect; Round 2 confirmed the fix with all suites green.

## 1. Links

- **PRD**: PRD-001
- **SPEC**: SPEC-001

## 2. Test Scope

### In Scope

- `POST /api/order/calc` discount calculation, including conversion, cap, and error codes (POINTS_INSUFFICIENT, POINTS_OVER_LIMIT, ORDER_NOT_FOUND).
- `POST /api/order/submit` order completion, points consumption on success, and points refund on payment failure (PAYMENT_FAILED).
- Points lifecycle in `points_transaction`: freeze at calc time, consume on order success, refund on payment failure/refund.
- Integer-cents money handling and correct rounding at the 100-points = $1.00 boundary.
- Checkout UI flow: input points, apply, view discount, submit, and error display.

### Out of Scope

- Points accrual / earning logic (separate requirement, not part of PRD-001).
- Payment gateway internals — the gateway is stubbed; only PAYMENT_FAILED handling is exercised.
- Multi-currency. All amounts are USD cents.
- Concurrent checkout of the same order from two sessions (tracked as a follow-up hardening item).

## 3. Test Cases

### 3.1 Unit Tests (owned by dev)

Written by backend/frontend themselves during implementation; QA reviews the coverage.

Expected coverage:
- backend: core business logic >= 80% (discount calc, cap clamp, cents conversion, transaction state machine)
- frontend: key components 100% (points input, apply button, discount display, error banner)

Reviewed coverage at sign-off:
- backend: 91% line / 88% branch on the discount + transaction modules.
- frontend: 100% on the four checkout components listed above.

### 3.2 Integration Tests

Derived from the PRD acceptance criteria. Each case calls the real API against a seeded test DB.

| Case ID | Source | Description | Expected Result |
|---|---|---|---|
| IT-001 | PRD AC1 | Order subtotal 5000 cents ($50.00), redeem 100 points via `POST /api/order/calc` | `discount` = 100, `points_applied` = 100, `final_amount` = 4900; order total decreases by exactly $1.00 |
| IT-002 | PRD AC2 | User balance is 500 points, request redeems 600 points via `POST /api/order/calc` | HTTP 400, error `POINTS_INSUFFICIENT`; no `freeze` row written to `points_transaction` |
| IT-003 | PRD AC3 | Order subtotal 5000 cents, redeem 3000 points (would discount $30.00 > 50% cap of $25.00) via `POST /api/order/calc` | HTTP 400, error `POINTS_OVER_LIMIT`; `max_deductible_points` = 2500 returned for the caller to clamp |
| IT-004 | PRD AC3 | Boundary: order subtotal 5000 cents, redeem exactly 2500 points (= 50% cap) | HTTP 200, `discount` = 2500, `final_amount` = 2500; accepted at the cap |
| IT-005 | PRD AC4 | Submit order with 100 points frozen, payment gateway returns failure via `POST /api/order/submit` | HTTP 402, error `PAYMENT_FAILED`; a `refund` row of +100 cents is written and the user's balance is restored |
| IT-006 | PRD AC1 + AC4 | Happy submit: redeem 100 points, payment succeeds via `POST /api/order/submit` | HTTP 200, `status` = "paid", `paid_amount` = 4900, `points_consumed` = 100; a `consume` row is written, no `refund` row |
| IT-007 | SPEC | `POST /api/order/calc` for a non-existent order_id | HTTP 404, error `ORDER_NOT_FOUND`; no transaction rows written |

### 3.3 Playwright E2E

**File**: `tests/e2e/PRD-001.spec.ts`

| Case ID | Type | Description | PRD Acceptance Covered |
|---|---|---|---|
| E2E-001 | happy-path | Enter 100 in `checkout-input-points`, click `checkout-btn-apply-points`, assert `checkout-discount` shows "-$1.00", click `checkout-btn-submit`, assert `order-confirmation` is visible | AC1 |
| E2E-002 | edge | Enter more points than the balance, click `checkout-btn-apply-points`, assert `checkout-points-error` shows the POINTS_INSUFFICIENT message and `checkout-btn-submit` stays disabled | AC2 |
| E2E-003 | edge | Enter points whose discount exceeds 50% of subtotal, click `checkout-btn-apply-points`, assert `checkout-points-error` shows the POINTS_OVER_LIMIT message | AC3 |
| E2E-004 | a11y | Axe accessibility scan of the checkout page after points are applied | - |

### 3.4 API Boundary-Value Tests

| Endpoint | Test Scenario | Expected |
|---|---|---|
| POST /api/order/calc | `points` = 0 | HTTP 200, `discount` = 0, `final_amount` = `order_amount` (no-op redemption) |
| POST /api/order/calc | `points` = 99 (below the 100-point conversion floor) | HTTP 200, `discount` = 0; 99 points convert to $0.00 by integer-cents flooring (no off-by-one) |
| POST /api/order/calc | `points` = 100 (exact conversion boundary) | HTTP 200, `discount` = 100 cents exactly ($1.00), not 99 |
| POST /api/order/calc | `points` = negative value | HTTP 400, validation error; request rejected before any DB write |
| POST /api/order/calc | `points` exceeding balance | HTTP 400, `POINTS_INSUFFICIENT` |
| POST /api/order/calc | `points` whose discount > 50% subtotal | HTTP 400, `POINTS_OVER_LIMIT`, with `max_deductible_points` in body |
| POST /api/order/submit | valid `order_id` + frozen points, gateway success | HTTP 200, `status` = "paid", `points_consumed` matches frozen amount |
| POST /api/order/submit | valid `order_id`, gateway failure | HTTP 402, `PAYMENT_FAILED`, frozen points refunded |

## 4. Round-1 Test Results

**Execution time**: 2026-02-04 14:20
**Executed by**: qa

### 4.1 Summary

- Total cases: 23 (7 integration + 4 E2E + 8 API boundary + 4 unit-suite gates)
- Passed: 22
- Failed: 1
- Skipped: 0

### 4.2 Failure Details

| Case ID | Failure Reason | Severity | Assigned To | Fix Commit |
|---|---|---|---|---|
| IT-001 | Off-by-one cents rounding: redeeming 100 points produced `discount` = 99 and `final_amount` = 4901 instead of 100 / 4900. Root cause — the conversion used `floor(points / 100 * 100)` in floating point, so `100 / 100 * 100` evaluated to `99.99999...` and floored to 99 cents. The dollar amount was computed as a float before casting to integer cents instead of dividing in integer space. AC1 not met. | Critical | backend | (pending fix) |

The same root cause also threatened the boundary API case `points` = 100 (which asserts exactly 100 cents), confirming this was a calculation defect rather than a test-data issue.

### 4.3 Coverage Blind Spots

- Concurrent submit of the same frozen order from two sessions is not yet covered (deferred to hardening backlog).
- Refund idempotency when a gateway timeout is retried — covered indirectly by IT-005 but not as an explicit duplicate-callback case.

### 4.4 Round-1 Conclusion

- [ ] Pass -> stage: awaiting-deploy-approval
- [x] Fail, fixes required -> stage: fixing

## 5. Retest Results

**Execution time**: 2026-02-09 10:05

### 5.1 Summary

- Total cases: 23
- Passed: 23
- Failed: 0

### 5.2 Verification of Round-1 Failed Cases

| Case ID | Round-1 Status | Fix Commit | Retest Status |
|---|---|---|---|
| IT-001 | Failed | a4f9c21 | Passed — `discount` = 100, `final_amount` = 4900 |

The fix (commit `a4f9c21`) replaced the floating-point conversion with pure integer math: `discount_cents = (points / 100) * 100` is computed entirely in integer cents, so 100 points maps to exactly 100 cents. The 99-point boundary case now correctly floors to 0.

### 5.3 Regression Test Results

- Full integration suite (IT-001 through IT-007): all green.
- Full API boundary suite (8 scenarios): all green, including both `points` = 99 and `points` = 100 cents boundaries.
- Playwright E2E suite (E2E-001 through E2E-004): all green; axe scan reported 0 violations.
- `points_transaction` state-machine assertions (freeze -> consume / freeze -> refund) re-run with no regressions.

### 5.4 Retest Conclusion

- [x] Pass -> stage: awaiting-deploy-approval
- [ ] Still failing -> stage: fixing (loop again)

## 6. Test Metrics Summary

(Used for automatic aggregation on the STATUS dashboard)

| Metric | Round 1 | Retest |
|---|---|---|
| Unit test pass rate | 100% | 100% |
| Integration pass rate | 86% (6/7) | 100% (7/7) |
| E2E pass rate | 100% (4/4) | 100% (4/4) |
| API boundary pass rate | 88% (7/8) | 100% (8/8) |
| a11y violations | 0 | 0 |
| Performance: API P95 | 142ms | 138ms |
