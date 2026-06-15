# FAQ

**Q1: How do I open STATUS.html?**
Just double-click the file to open it in a browser locally, or run `open status.html` (Mac) / `start status.html` (Windows) / `xdg-open status.html` (Linux).

**Q2: What if I forget to run build_status.py?**
The PostToolUse hook configured in `.claude/settings.json` runs `scripts/refresh_status.py` automatically after every `docs/*.md` edit (which in turn reruns build_index + build_status). If you notice that STATUS is not updated, the hook may have failed; run `python scripts/build_status.py` manually.

**Q3: How are test results aggregated automatically?**
Run `npx playwright test --reporter=json > playwright-report.json`, then run `python scripts/parse_playwright_report.py playwright-report.json`. This writes the test results into the frontmatter of the corresponding TEST-PLAN. Then build_status reads and displays them.

**Q4: Can status.html refresh automatically?**
In this approach, status.html is a static file. If you need automatic refresh, you can either:
- Add `<meta http-equiv="refresh" content="60">` to the html `<head>` (refresh every minute)
- Use an extension such as VS Code's Live Server

**Q5: Can multiple requirements be in progress at the same time?**
Yes, but we recommend keeping **the number of concurrent requirements ≤ 3** to avoid splitting the agents' attention. Manage priority using the `priority` field in the PRD frontmatter (P0 > P1 > P2).

**Q6: What process do urgent bugs follow?**
Skip PRD/SPEC and let backend/frontend fix it directly, but afterward you must:
- Tag the commit message with [hotfix]
- Run qa to re-test and verify the fix
- If there are important findings, add a RUNBOOK or ADR

Note: even on the hotfix path the team stops at merge-ready code — you run the actual deploy.

**Q7: The project already has code. How do I start?**
On the first run, execute the project-baseline bootstrap step (have the `architect` browse `src/` and generate `docs/spec/SPEC-000-current-state.md`). You are not required to backfill PRDs for existing features; start strictly following the process from new features onward.

**Q8: Can STATUS.md be shown to non-technical people?**
Yes. Markdown renders tables automatically on GitHub/GitLab, so the key information (number of items awaiting approval, number in progress) is clear at a glance. For showing it to the boss, we recommend status.html (it looks nicer).

**Q9: How do I handle a requirement that gets cut?**
The PM changes the corresponding PRD's stage to `cancelled` and adds `cancelled-reason: user decided not to build it` to the frontmatter. Do not delete the document; keep the history.

**Q10: What if an agent doesn't follow the process?**
1. Check whether the agent definition's "position in the process" is clear
2. In the task description, explicitly state "follow the CLAUDE.md process; we are currently at stage X"
3. If problems recur, check whether the agent memory has accumulated faulty patterns

**Q11: The STATUS dashboard isn't auto-updating on Windows.**
This is fixed. The PostToolUse hook is now a cross-platform Python entry point (`scripts/refresh_status.py`) that works in PowerShell/CMD without Git Bash or WSL. If STATUS still doesn't refresh, run `python scripts/build_status.py` manually and confirm Python is on your PATH.

**Q12: Several people work the same project, each with their own agent team — what do we watch out for?**
See CLAUDE.md "Multi-Developer Mode" for the full protocol. Key points:
- Commit `.claude/` as the shared source of truth — don't have each person install the team separately.
- Gitignore `status.html` and `docs/index.yaml`; commit `STATUS.md` only on the integration branch.
- Claim ids with `python scripts/next_id.py prd` on the integration branch before branching (avoids PRD-number collisions).
- Sync from the integration branch before designing so the architect can see others' merged work — in-flight branches are invisible.
- SPEC-000 is reconciled on the integration branch after merge.
- Project memory is local, so shared knowledge goes in committed docs.

**Q13: What if my Claude Code doesn't support agent teams / SendMessage?**
It's experimental. If it's unavailable, the orchestrator (main Claude) acts as router: it invokes each role itself and dispatches the next stage manually. The frontmatter `stage` stays the source of truth, so the document flow is unchanged.

**Q14: How does the team handle security?**
At the layers it controls: for features touching auth, money/balances, PII, file uploads, or untrusted input, the architect's SPEC includes a "Security & abuse cases" section (STRIDE-lite: threat → mitigation → verifying test), and the reviewer runs a security deep-dive on those diffs (authorization/IDOR, injection, secrets & PII, money/state integrity, new dependencies). Dependency/supply-chain scanning and SAST run in **your** CI (consistent with the delivery boundary) — see README → Security for the recommended `npm audit` / `pip-audit` / Dependabot setup. A dedicated security agent isn't bundled (too heavy for a small team).

---

## Version & evolution

- **Guide version**: 1.7.0 — see [CHANGELOG](../CHANGELOG.md) for what changed
- **Target team size**: 5-10 people
- **Estimated rollout time**: 1-2 days (including the first end-to-end run of the process)
- **Scope boundary**: the team stops at approved, tested, merge-ready code — running CI/CD and the actual production deploy stay your responsibility.

Future directions (enable as needed):

- Add a ux-designer agent (once you hire a designer)
- Add a business-analyst agent (when the business gets complex)
- Add external dashboard / notification sync (when non-technical members need visibility)
- Add vector retrieval (when there are more than 100 documents)
- Add Superpowers' systematic-debugging and verification-before-completion skills (after the team has settled in)
