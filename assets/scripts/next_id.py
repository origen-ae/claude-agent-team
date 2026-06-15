#!/usr/bin/env python3
"""Allocate the next document ID of a given type.

"Highest existing ID + 1" is computed locally, so two developers working on
their own branches will both pick the same number and collide at merge time.
This helper centralizes the calculation and — importantly — also scans
`docs/index.yaml` for *reserved* entries, so the multi-developer protocol can
claim a number on the shared branch before anyone starts writing.

Usage:
    python scripts/next_id.py prd          # -> PRD-009
    python scripts/next_id.py spec
    python scripts/next_id.py adr
    python scripts/next_id.py backlog

Multi-developer protocol (see CLAUDE.md "Multi-Developer Mode"):
    1. On the shared/integration branch, run this to get the next free number.
    2. Reserve it by adding a stub entry to docs/index.yaml and pushing.
    3. Branch off and write the real document with that number.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).parent.parent
DOCS_ROOT = ROOT / "docs"

PREFIX = {
    "prd": "PRD",
    "spec": "SPEC",
    "test-plan": "TEST-PLAN",
    "adr": "ADR",
    "runbook": "RUNBOOK",
    "backlog": "BACKLOG",
}


def _max_from_files(prefix):
    """Highest NNN seen across docs/ filenames and frontmatter ids."""
    highest = 0
    pat = re.compile(rf"\b{re.escape(prefix)}-(\d+)\b")
    for md in DOCS_ROOT.rglob("*.md"):
        if "_templates" in md.parts:
            continue
        for m in pat.finditer(md.name):
            highest = max(highest, int(m.group(1)))
        # backlog ids live inside backlog.md, not in filenames
        if prefix == "BACKLOG" and md.name == "backlog.md":
            for m in pat.finditer(md.read_text(encoding="utf-8", errors="ignore")):
                highest = max(highest, int(m.group(1)))
    return highest


def _max_from_index(prefix):
    """Highest NNN reserved in docs/index.yaml (covers not-yet-written docs)."""
    index_path = DOCS_ROOT / "index.yaml"
    if not index_path.exists() or yaml is None:
        return 0
    try:
        data = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return 0
    highest = 0
    pat = re.compile(rf"\b{re.escape(prefix)}-(\d+)\b")
    for doc in data.get("documents", []) or []:
        doc_id = str(doc.get("id", ""))
        for m in pat.finditer(doc_id):
            highest = max(highest, int(m.group(1)))
    return highest


def main():
    if len(sys.argv) != 2 or sys.argv[1].lower() not in PREFIX:
        print(f"usage: python scripts/next_id.py <{'|'.join(PREFIX)}>", file=sys.stderr)
        return 2
    prefix = PREFIX[sys.argv[1].lower()]
    nxt = max(_max_from_files(prefix), _max_from_index(prefix)) + 1
    print(f"{prefix}-{nxt:03d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
