# Project Documentation

This directory uses the agent team collaborative documentation system. See the root-level `CLAUDE.md` for the full specification.

## Document Types

| Directory | Type | Numbering |
|---|---|---|
| `prd/` | Product requirements | PRD-XXX (carried through the entire flow) |
| `spec/` | Technical specification | SPEC-XXX (same number as the PRD) |
| `test-plan/` | Test plan | TEST-PLAN-XXX (same number as the PRD) |
| `adr/` | Architecture decision | ADR-XXX (numbered independently) |
| `runbook/` | Incident runbook | RUNBOOK-XXX (numbered independently) |

## Overall Progress

See [STATUS.md](../STATUS.md) or [status.html](../status.html) in the root directory.

## Common Commands

```bash
# Rebuild the index
python scripts/build_index.py

# Rebuild the progress dashboard
python scripts/build_status.py

# Run E2E tests
npx playwright test

# Update metrics after testing
npx playwright test --reporter=json > playwright-report.json
python scripts/parse_playwright_report.py playwright-report.json
python scripts/build_status.py
```
