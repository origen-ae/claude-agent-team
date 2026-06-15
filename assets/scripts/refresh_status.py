#!/usr/bin/env python3
"""PostToolUse hook entry point.

Claude Code runs this after every Edit/Write. It reads the hook payload from
stdin, looks at which file was touched, and rebuilds the document index and the
STATUS board **only** when a tracked document under docs/ changed.

Why a Python entry point instead of a shell one-liner:
- It is cross-platform. The previous hook used POSIX syntax
  (`... 2>/dev/null || true`) that silently does nothing on Windows
  PowerShell / CMD, so the dashboard never refreshed for Windows users.
- It does the path filtering itself. Claude Code hooks only support `matcher`
  (tool name); there is no `pathMatcher`, so filtering must happen here.
- It never fails the originating tool call (always exits 0).
"""
import sys
import json
import importlib
from pathlib import Path


def _edited_path():
    """Pull the edited file path out of the PostToolUse JSON on stdin."""
    try:
        data = json.load(sys.stdin)
    except Exception:
        return None
    tool_input = data.get("tool_input") or {}
    return tool_input.get("file_path") or tool_input.get("path")


def _is_tracked_doc(p):
    """True for docs/**/*.md that the index/board actually care about.

    backlog.md IS tracked here (build_status renders a backlog summary), but
    README.md and the _templates/ files are not.
    """
    if not p:
        return False
    try:
        path = Path(p)
    except Exception:
        return False
    parts_lower = [s.lower() for s in path.parts]
    if "docs" not in parts_lower:
        return False
    if "_templates" in parts_lower:
        return False
    if path.suffix.lower() != ".md":
        return False
    if path.name.lower() == "readme.md":
        return False
    return True


def main():
    edited = _edited_path()
    if not _is_tracked_doc(edited):
        return  # not a tracked document — nothing to rebuild

    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))

    # Index first (keeps the librarian's index.yaml fresh), then the board.
    for mod_name in ("build_index", "build_status"):
        try:
            mod = importlib.import_module(mod_name)
            mod.main()
        except SystemExit:
            # build_index exits non-zero when it finds doc errors; that is a
            # report, not a reason to fail the user's edit.
            pass
        except Exception as e:  # never let a hook break the tool call
            print(f"refresh_status: {mod_name} failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
