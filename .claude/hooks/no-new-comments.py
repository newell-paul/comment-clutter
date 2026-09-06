"""why: PreToolUse hook that denies Write/Edit calls that add comment lines.

Escape hatch: a comment whose text starts with "why:" is allowed.
Pragmas (noqa, type:, eslint, prettier, ruff, pragma, shebang) are ignored.
"""

import json
import os
import re
import sys

MARKERS = {
    ".py": ("#",),
    ".js": ("//", "/*", "*"),
    ".jsx": ("//", "/*", "*"),
    ".ts": ("//", "/*", "*"),
    ".tsx": ("//", "/*", "*"),
    ".php": ("//", "#", "/*", "*"),
    ".rs": ("//", "/*", "*"),
    ".go": ("//", "/*", "*"),
    ".sh": ("#",),
}
PRAGMA = re.compile(
    r"noqa|type:|eslint|prettier|ruff:|pragma|^#!|@ts-|why:", re.IGNORECASE
)


def comment_lines(text: str, markers: tuple[str, ...]) -> list[str]:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if any(s.startswith(m) for m in markers) and not PRAGMA.search(s):
            out.append(s)
    return out


def main() -> None:
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name")
    inp = payload.get("tool_input", {})
    path = inp.get("file_path", "")
    markers = MARKERS.get(os.path.splitext(path)[1])
    if not markers:
        return

    if tool == "Edit":
        before = comment_lines(inp.get("old_string", ""), markers)
        after = comment_lines(inp.get("new_string", ""), markers)
    elif tool == "Write":
        try:
            with open(path) as fh:
                before = comment_lines(fh.read(), markers)
        except OSError:
            before = []
        after = comment_lines(inp.get("content", ""), markers)
    else:
        return

    added = [c for c in after if c not in before]
    if not added:
        return

    shown = "\n".join(f"  {c}" for c in added[:5])
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Edit adds {len(added)} comment line(s) to {os.path.basename(path)}:\n{shown}\n"
                        "This repo does not allow new comments. Make the code say it instead "
                        "(a named variable, a function name, a test). If the logic is complex and "
                        "the comment explains why, prefix it with 'why:' and retry."
                    ),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
