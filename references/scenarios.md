# Worked Scenarios

## Scenario 1: A user submits a new requirement

```
You: New requirement — users can use points to deduct part of the order amount

pm: [starts]
   1. Calls librarian to check whether a related PRD already exists
   2. Asks clarifying questions: points exchange rate, deduction cap, refund rules...
   You: [answer]
   3. Creates docs/prd/PRD-008.md
      stage: pm-designing
   4. Writes the 4 sections: feature, prototype, business flow, data flow
   5. Changes stage to awaiting-prd-approval
   6. Runs build_status.py
   7. Notifies you for approval

You: [open STATUS.html and see PRD-008 awaiting approval]
You: [read docs/prd/PRD-008.md]
You: Approve

pm: Changes stage to architect-designing, notifies architect

architect: [starts]
   ... (architecture design process)
   Changes stage to awaiting-spec-approval

You: [STATUS.html shows PRD-008 awaiting technical-design approval]
You: [read docs/spec/SPEC-008.md]
You: Approve

architect: Changes stage to developing, breaks the work into tasks and assigns them to frontend/backend

frontend + backend: [implement in parallel]
   When done, spawn reviewer
   Once both are finished, SendMessage to notify qa

qa: [starts]
   1. Changes stage to testing-round1
   2. Creates docs/test-plan/TEST-PLAN-008.md
   3. Writes Playwright tests/e2e/PRD-008.spec.ts
   4. Runs the tests
   5. Suppose 2 failures are found -> updates TEST-PLAN with round-1 results
   6. Changes stage to fixing
   7. SendMessage to the corresponding dev

dev: [fixes] -> spawn reviewer -> commit

qa: Changes stage to testing-round2
   Runs the full regression -> all pass
   Updates TEST-PLAN with retest results
   Changes stage to awaiting-deploy-approval
   Notifies pm

pm: Notifies you for deploy approval

You: [STATUS.html shows PRD-008 awaiting deploy approval + all test metrics green]
You: Approve deployment

[after deployment completes]
pm: Changes stage to deployed
Runs build_status

You: [STATUS.html shows PRD-008 done]
```

## Scenario 2: A daily progress check

Your morning routine:

```
1. Open status.html (in a browser)
2. Read the top summary: 8 requirements total | 2 awaiting approval | 4 in progress | 2 done
3. Look at the "Awaiting your approval" section and handle the pending items (click the document links for a quick read)
4. Look at the "In progress" section and spot anomalies (items that have been stalled for too long)
5. Done, close it
```

5-10 minutes a day.

## Scenario 3: An emergency bug

This skips the full process:

```
You: Production bug in PRD-005 points calculation, fix it urgently

backend: [skips PRD/SPEC]
   1. Creates a hotfix branch
   2. Writes a reproduction test
   3. Fixes it
   4. spawn reviewer
   5. commit (with a [hotfix] marker)
   6. SendMessage qa

qa: [quick retest]
   Runs the Playwright tests for that PRD

[after the fix is deployed]
pm: Creates RUNBOOK-002 (documents this incident and its fix)
Updates PRD-005 with the hotfix history
```

---
