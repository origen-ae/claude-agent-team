#!/usr/bin/env python3
"""Reconcile intended document state against the evidence on disk.

The STATUS board is a faithful renderer: it shows whatever `stage` an agent
wrote, so a skipped step (e.g. jumping straight to awaiting-deploy-approval
without ever writing a TEST-PLAN) is invisible on the board alone. This script
asserts cross-document invariants and exits non-zero when something doesn't add
up, so it can be used as a pre-deploy gate or a CI check.

Usage:
    python scripts/check_state.py          # report; exit 1 if any errors
    python scripts/check_state.py --warn    # also fail on warnings (strict)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_status import load_all_docs, group_by_requirement, compute_state_warnings  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    strict = "--warn" in sys.argv[1:]
    docs = load_all_docs()
    groups = group_by_requirement(docs)
    warnings = compute_state_warnings(groups)

    errors = [m for lvl, m in warnings if lvl == "error"]
    warns = [m for lvl, m in warnings if lvl == "warn"]

    if not warnings:
        print(f"✅ State check passed ({len(groups)} requirements, no inconsistencies)")
        return 0

    for m in errors:
        print(f"🔴 {m}")
    for m in warns:
        print(f"🟡 {m}")

    fail = bool(errors) or (strict and bool(warns))
    print(f"\n{'❌' if fail else '⚠️ '} {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
