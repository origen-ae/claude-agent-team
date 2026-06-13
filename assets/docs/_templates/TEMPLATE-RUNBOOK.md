---
id: RUNBOOK-XXX
title: <Scenario> Incident Runbook
type: runbook
stage: deployed
owner: backend
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: What to do when <abnormal situation> occurs
related: []
---

# <Scenario> Incident Runbook

## TL;DR

<!-- One sentence: under what circumstances do you use this runbook -->

## 1. Applicable Scenarios

<!-- Detailed description: under what symptoms is this used? How do you identify it? -->

## 2. Alert Signals

- **Monitoring metrics**: 
- **Log characteristics**: 
- **User feedback characteristics**: 

## 3. Response Steps

### Step 1: Confirm the Problem

```bash
# Specific command
```

Expected output:

### Step 2: Assess Impact

- Estimated number of affected users:
- Business impact:

### Step 3: Temporary Mitigation

<!-- Restore service first; root cause analysis comes later -->

```bash
# Command
```

### Step 4: Root Cause Investigation

### Step 5: Fix

### Step 6: Verify Recovery

- [ ] Monitoring metrics recovered
- [ ] Sampled user verification

### Step 7: Retrospective

- Create a postmortem
- Update this RUNBOOK

## 4. Escalation Path

| Duration | Escalate to |
|---|---|
| Not recovered after 15 minutes | Notify architect |
| Not recovered after 1 hour | Notify the technical lead |

## 5. Historical Incidents

| Date | Symptom | Resolution | Notes |
|---|---|---|---|
