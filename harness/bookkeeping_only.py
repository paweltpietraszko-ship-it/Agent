#!/usr/bin/env python3
"""
ROLE: decide whether a change is bookkeeping only (needs no brief).
USAGE: bookkeeping_only.py <before_sha> <head_sha>      (run inside the repo)
EXIT 0 = every changed file is BOARD.md or ODLOZONE.md, modified in place as a regular file.
EXIT 1 = anything else (other file, add/delete/rename, symlink or mode change, empty diff, git error).
Fail direction is always "run the full gate": this script can only ever relax the gate for two text files.
"""
from __future__ import annotations

import subprocess
import sys

ALLOWED = {"BOARD.md", "ODLOZONE.md"}
REGULAR = "100644"


def verdict(before: str, head: str) -> tuple[bool, str]:
    result = subprocess.run(["git", "diff", "--raw", "-z", "--no-renames", before, head], capture_output=True)
    if result.returncode != 0:
        return False, "git diff failed"
    fields = result.stdout.split(b"\0")
    entries = [(fields[i].decode("utf-8", "replace"), fields[i + 1].decode("utf-8", "replace")) for i in range(0, len(fields) - 1, 2)]
    if not entries:
        return False, "empty diff"
    for meta, path in entries:
        parts = meta.lstrip(":").split()
        if len(parts) != 5 or parts[4] != "M" or parts[0] != REGULAR or parts[1] != REGULAR:
            return False, f"not an in-place edit of a regular file: {path}"
        if path not in ALLOWED:
            return False, f"file is not bookkeeping: {path}"
    return True, f"{len(entries)} bookkeeping file(s)"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("USAGE: bookkeeping_only.py <before_sha> <head_sha>")
        sys.exit(1)
    ok, reason = verdict(sys.argv[1], sys.argv[2])
    print(f"STATUS: {'BOOKKEEPING_ONLY' if ok else 'NOT_BOOKKEEPING'}\nREASON: {reason}")
    sys.exit(0 if ok else 1)
