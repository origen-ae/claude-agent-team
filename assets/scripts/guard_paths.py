#!/usr/bin/env python3
"""PreToolUse guard: enforce the frontend/backend write boundary mechanically.

The role split ("frontend doesn't touch backend code, and vice-versa") used to
be prose-only — it silently evaporated if SPEC-000 was wrong/missing. This hook
turns it into a real guardrail: on an Edit/Write it reads which agent is making
the call (`agent_type` in the PreToolUse payload) and blocks writes that cross
the boundary defined in `.claude/agent-team-boundaries.json`.

Design principle — **fail open**. This is defense-in-depth on top of the prose
rules, NOT the sole protection. If anything is uncertain (no agent identity, no
boundaries file, a parse error, an unknown agent), the call is ALLOWED. A guard
that fails closed would block the orchestrator and every other agent and break
the whole system — far worse than the prose it backs up.

It only ever blocks when ALL of these hold:
  - the caller's `agent_type` is exactly `frontend` or `backend`, and
  - the target path matches a `deny_write` glob for that agent in the config.

Caveat: this relies on Claude Code populating `agent_type` for subagent tool
calls (experimental agent-teams behaviour). If that field is absent, the guard
is inert (everything is allowed) and the prose rules remain the backstop.

Block mechanism: exit code 2 with a reason on stderr (the most reliably
honored "deny" signal across versions).
"""
import sys
import json
import re
from pathlib import Path

ENFORCED_AGENTS = ("frontend", "backend")


def _glob_to_regex(glob):
    """Translate a path glob (supporting ** and *) to a regex.

    ** matches across directory separators; * matches within one segment.
    """
    i, n, out = 0, len(glob), []
    while i < n:
        c = glob[i]
        if c == "*":
            if i + 1 < n and glob[i + 1] == "*":
                i += 2
                if i < n and glob[i] == "/":
                    i += 1
                    out.append("(?:.*/)?")  # zero or more directories
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
            i += 1
            continue
        if c == "?":
            out.append("[^/]")
        elif c in ".+()[]{}^$|\\":
            out.append("\\" + c)
        else:
            out.append(c)
        i += 1
    return "^" + "".join(out) + "$"


def _normalize(file_path, cwd):
    """Return the target path relative to the project root, slash-separated."""
    p = Path(file_path)
    if cwd:
        try:
            if p.is_absolute():
                p = p.relative_to(Path(cwd))
        except Exception:
            pass  # not under cwd — fall back to the raw path
    rel = str(p).replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    return rel


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # can't parse — allow

    agent = (data.get("agent_type") or "").strip().lower()
    if agent not in ENFORCED_AGENTS:
        return 0  # main agent / pm / architect / qa / unknown — allow

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0

    cwd = data.get("cwd") or ""
    config_path = Path(cwd) / ".claude" / "agent-team-boundaries.json" if cwd else Path(".claude/agent-team-boundaries.json")
    if not config_path.exists():
        return 0  # not configured (e.g. monorepo with no clean split) — allow
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    deny_globs = ((config.get(agent) or {}).get("deny_write")) or []
    if not deny_globs:
        return 0  # boundary disabled for this agent — allow

    rel = _normalize(file_path, cwd)
    for glob in deny_globs:
        try:
            if re.match(_glob_to_regex(glob), rel, re.IGNORECASE):
                print(
                    f"Blocked: the '{agent}' agent may not write '{rel}' "
                    f"(matches boundary '{glob}' in .claude/agent-team-boundaries.json). "
                    f"If the API/contract must change, have the architect update the SPEC first, "
                    f"or re-classify the tier.",
                    file=sys.stderr,
                )
                return 2  # block the tool call
        except Exception:
            continue  # bad glob — skip, never crash

    return 0


if __name__ == "__main__":
    sys.exit(main())
