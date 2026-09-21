#!/usr/bin/env python3
"""
ROLE: FROZEN.lock management -- structural tripwire for frozen contracts.
COMMANDS:
  guard freeze [--recompute] <file>...   add (or, with --recompute, update) records
  guard check [<file>...]                verify given files; no args = every record
  guard list                             print every record
LOCK: harness/FROZEN.lock, one line per file: "<sha256>  <repo-relative posix path>".
Only the owner/architect freezes or recomputes; the change is a visible diff.
The gate (backend.py) treats any edit to harness/ as out of scope for a Task.
OUTPUT: structured key:value, no prose. Exit 0 = ok, 1 = failure.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

LOCK_PATH = "harness/FROZEN.lock"
PROTECTED_PREFIXES = ("harness/", ".githooks/", ".github/", ".git/")
LOCK_HEADER = "# FROZEN.lock -- managed by harness/guard.py; change only via `guard freeze --recompute`\n"
LINE = re.compile(r"^([0-9a-f]{64})  (\S.*)$")


def sha256_bytes(data: bytes) -> str:
    """Hash with CRLF folded to LF: on Windows (core.autocrlf) the working-tree copy is CRLF while
    the committed blob is LF; both must give the same hash or every check gives a false alarm."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def parse_lock_text(text: str) -> tuple[dict[str, str], str | None]:
    """Returns ({path: sha256}, error). Any malformed or duplicate line is an error."""
    records: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.startswith("#"):
            continue
        match = LINE.match(raw)
        if not match:
            return {}, f"FROZEN.lock line {number} malformed"
        sha, path = match.groups()
        if path in records:
            return {}, f"FROZEN.lock has conflicting records for {path}"
        records[path] = sha
    if not records:
        return {}, "FROZEN.lock has no records"
    return records, None


def repo_root() -> Path:
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if result.returncode != 0:
        fail("not inside a git repository")
    return Path(result.stdout.strip())


def fail(reason: str) -> None:
    print(f"STATUS: FAIL\nREASON: {reason}")
    sys.exit(1)


def normalize(root: Path, arg: str, must_exist: bool = True) -> str:
    path = Path(arg)
    absolute = path if path.is_absolute() else (Path.cwd() / path)
    try:
        rel = absolute.resolve().relative_to(root.resolve())
    except ValueError:
        fail(f"path is outside the repository: {arg}")
    posix = PurePosixPath(rel.as_posix()).as_posix()
    if ".." in PurePosixPath(posix).parts:
        fail(f"path escapes the repository: {arg}")
    if posix.startswith(PROTECTED_PREFIXES) or posix == ".git":
        fail(f"protected path cannot be frozen: {posix}")
    if must_exist and not (root / posix).is_file():
        fail(f"file not found: {posix}")
    return posix


def load_lock(root: Path, required: bool = True) -> dict[str, str]:
    lock = root / LOCK_PATH
    if not lock.exists():
        if required:
            fail(f"{LOCK_PATH} not found -- run guard freeze first")
        return {}
    try:
        text = lock.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{LOCK_PATH} is not valid text: {exc}")
    records, error = parse_lock_text(text)
    if error:
        fail(error)
    return records


def write_lock(root: Path, records: dict[str, str]) -> None:
    body = LOCK_HEADER + "".join(f"{sha}  {path}\n" for path, sha in sorted(records.items()))
    target = root / LOCK_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    written = tmp.write_text(body, encoding="utf-8", newline="\n")
    if written != len(body):
        tmp.unlink(missing_ok=True)
        raise OSError(f"partial write: wrote {written} of {len(body)} characters")
    tmp.replace(target)


def cmd_freeze(root: Path, args: list[str]) -> None:
    recompute = "--recompute" in args
    files = [a for a in args if a != "--recompute"]
    if not files or any(a.startswith("--") for a in files):
        fail("usage: guard freeze [--recompute] <file>...")
    records = load_lock(root, required=False)
    for arg in files:
        posix = normalize(root, arg)
        if posix in records and not recompute:
            fail(f"{posix} is already frozen -- use --recompute to update")
        if posix not in records and recompute:
            fail(f"{posix} is not frozen yet -- use freeze without --recompute")
        records[posix] = sha256_bytes((root / posix).read_bytes())
    write_lock(root, records)
    for arg in files:
        posix = normalize(root, arg)
        print(f"STATUS: FROZEN\nFILE: {posix}\nSHA256: {records[posix]}")


def cmd_check(root: Path, args: list[str]) -> None:
    if any(a.startswith("--") for a in args):
        fail("usage: guard check [<file>...]")
    records = load_lock(root)
    targets = [normalize(root, a, must_exist=False) for a in args] if args else sorted(records)
    problems = []
    for posix in targets:
        if posix not in records:
            problems.append(f"{posix}: not frozen")
        elif not (root / posix).is_file():
            problems.append(f"{posix}: file missing")
        elif sha256_bytes((root / posix).read_bytes()) != records[posix]:
            problems.append(f"{posix}: hash mismatch")
    if problems:
        print("STATUS: FAIL\nREASON:")
        print("\n".join(f"  - {p}" for p in problems))
        sys.exit(1)
    print(f"STATUS: PASS\nCHECKED: {len(targets)}")


def cmd_list(root: Path) -> None:
    for path, sha in sorted(load_lock(root).items()):
        print(f"{sha}  {path}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in ("freeze", "check", "list"):
        print("USAGE: guard freeze [--recompute] <file>...\n       guard check [<file>...]\n       guard list")
        sys.exit(1)
    root = repo_root()
    {"freeze": cmd_freeze, "check": cmd_check, "list": lambda r, _a: cmd_list(r)}[args[0]](root, args[1:])


if __name__ == "__main__":
    main()
