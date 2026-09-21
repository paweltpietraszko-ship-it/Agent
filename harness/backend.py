#!/usr/bin/env python3
"""
ROLE: mechanical gate for a delivered Task -- no interpretation, no negotiation.
RUNS: after the implementer's commit, BEFORE ARCHITECT_REVIEW / Codex.
USAGE: backend.py <brief.md> <before_sha> <head_sha> <output.txt>   (run inside the repo)
OUTPUT: STATUS PASS (exit 0) | WYMAGA_DECYZJI (exit 2) | FAIL (exit 1), plus reasons.
The verdict is quoted verbatim in the delivery, never paraphrased.

Everything is measured on the delivered COMMIT (git show head:path), never on the
working tree, so an uncommitted fix cannot make a bad commit pass.

BRIEF FIELDS (declared by the architect in the frozen brief, never by the implementer):
  TASK_SCOPE:                 "- path" lines. Exact repo-relative files or directory
                              globs ("app/**", "tests/*.py"). First path segment must be literal.
  MAX_NEW_FILES: <n>          optional, 1-200, default 2
  TOTAL_LINES_THRESHOLD: <n>  optional, 1-20000, default 150
  AUDIT_TIER: LIGHT|STANDARD|CRITICAL   optional, default STANDARD

CHECKS:
  TASK_SCOPE / SCOPE_ENTRY  brief has a valid, non-empty scope (no absolute, "..", protected paths)
  STALE_HEAD / ANCESTRY     head_sha is the repository HEAD; before_sha is its ancestor
  GIT_DIFF                  git must succeed, never silently ignored
  BRIEF_FROZEN              the brief is unchanged between before_sha and head_sha
  FROZEN_LOCK               every file in harness/FROZEN.lock matches its hash at head_sha
  DIFF_SCOPE / NEW_FILES    every changed file is in scope; at most MAX_NEW_FILES new files
  SYNTAX / RUFF             changed .py files parse and pass harness/ruff.toml
  SIZE_FILE / SIZE_FUNC     max 600 lines per file, 50 lines per function
  RATIO / TOTAL_LINES       insertions:deletions > 5:1, or > threshold lines => WYMAGA_DECYZJI
  AUDIT_TIER                changed files matching harness/critical_paths.txt but brief tier
                            below CRITICAL => WYMAGA_DECYZJI

KNOWN_LIMITATION: RATIO does not fire when deletions == 0 (a brand-new file); NEW_FILES and
TOTAL_LINES guard that case. tasks/, log/, BOARD.md, ODLOZONE.md are pipeline artifacts:
reported, not scope-checked.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard  # noqa: E402

MAX_FILE_LINES = 600
MAX_FUNC_LINES = 50
DEFAULT_MAX_NEW_FILES = 2
DEFAULT_TOTAL_LINES = 150
RATIO_THRESHOLD = 5
TIERS = ("LIGHT", "STANDARD", "CRITICAL")
PROTECTED_PREFIXES = guard.PROTECTED_PREFIXES
ARTIFACT_PREFIXES = ("tasks/", "log/")
ARTIFACT_FILES = ("BOARD.md", "ODLOZONE.md")
CRITICAL_PATHS_FILE = "harness/critical_paths.txt"
RUFF_CONFIG = "harness/ruff.toml"
CHECKS = (
    "TASK_SCOPE / STALE_HEAD / ANCESTRY / GIT_DIFF / BRIEF_FROZEN / FROZEN_LOCK / DIFF_SCOPE / "
    "NEW_FILES / SYNTAX / RUFF / SIZE_FILE / SIZE_FUNC / RATIO / TOTAL_LINES / AUDIT_TIER"
)


@dataclass
class Brief:
    scope: list[str]
    max_new_files: int
    total_lines: int
    tier: str


def git(args: list[str], text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=text)


def git_show(sha: str, path: str) -> bytes | None:
    result = git(["show", f"{sha}:{path}"], text=False)
    return result.stdout if result.returncode == 0 else None


def is_artifact(path: str) -> bool:
    return path.startswith(ARTIFACT_PREFIXES) or path in ARTIFACT_FILES


def parse_int_field(text: str, name: str, upper: int) -> tuple[int | None, str | None]:
    found = re.findall(rf"^{name}:[ \t]*(\S*)[ \t]*$", text, re.MULTILINE)
    if not found:
        return None, None
    if len(found) > 1:
        return None, f"{name} declared more than once"
    if not found[0].isdigit() or not 1 <= int(found[0]) <= upper:
        return None, f"{name} must be an integer 1-{upper}, got {found[0]!r}"
    return int(found[0]), None


def parse_scope(text: str) -> list[str]:
    scope, in_scope, found = [], False, False
    for line in text.splitlines():
        if line.startswith("TASK_SCOPE:"):
            if found:
                raise ValueError("TASK_SCOPE declared more than once")
            in_scope, found = True, True
            continue
        if in_scope:
            stripped = line.strip()
            if stripped.startswith("-"):
                scope.append(stripped[1:].strip().strip("`").strip())
            elif stripped and not stripped.startswith("#"):
                in_scope = False
    if not found:
        raise ValueError("TASK_SCOPE missing in brief")
    return scope


def read_brief(brief_path: Path) -> Brief:
    try:
        text = brief_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"unable to read brief: {exc}") from exc
    scope = parse_scope(text)
    new_files, err1 = parse_int_field(text, "MAX_NEW_FILES", 200)
    total, err2 = parse_int_field(text, "TOTAL_LINES_THRESHOLD", 20000)
    tiers = re.findall(r"^AUDIT_TIER:[ \t]*(\S*)[ \t]*$", text, re.MULTILINE)
    errors = [e for e in (err1, err2) if e]
    if len(tiers) > 1 or (tiers and tiers[0] not in TIERS):
        errors.append(f"AUDIT_TIER must be one of {'/'.join(TIERS)} (declared once)")
    if errors:
        raise ValueError("; ".join(errors))
    return Brief(scope, new_files or DEFAULT_MAX_NEW_FILES, total or DEFAULT_TOTAL_LINES, tiers[0] if tiers else "STANDARD")


def check_scope_entries(scope: list[str]) -> list[str]:
    if not scope:
        return ["TASK_SCOPE: scope is empty"]
    errors = []
    for entry in scope:
        posix = PurePosixPath(entry)
        first = posix.parts[0] if posix.parts else ""
        if not entry:
            errors.append("SCOPE_ENTRY: empty entry")
        elif "\\" in entry or entry.startswith("/") or re.match(r"^[A-Za-z]:", entry):
            errors.append(f"SCOPE_ENTRY: not a repo-relative posix path: {entry}")
        elif ".." in posix.parts:
            errors.append(f"SCOPE_ENTRY: escapes repository (parent traversal): {entry}")
        elif re.search(r"[?\[\]{}]", entry):
            errors.append(f"SCOPE_ENTRY: only * and ** wildcards are supported: {entry}")
        elif "*" in first:
            errors.append(f"SCOPE_ENTRY: first path segment must be literal (no repo-wide wildcard): {entry}")
        elif entry.startswith(PROTECTED_PREFIXES) or first in (".git", "harness", ".githooks"):
            errors.append(f"SCOPE_ENTRY: protected path cannot be in a Task scope: {entry}")
    return errors


def glob_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r"\Z")


def in_scope(path: str, scope: list[str]) -> bool:
    return any(entry == path or glob_regex(entry).match(path) for entry in scope)


def resolve_commit(ref: str) -> tuple[str | None, str | None]:
    result = git(["rev-parse", "--verify", f"{ref}^{{commit}}"])
    if result.returncode != 0:
        return None, f"cannot resolve {ref!r}: {result.stderr.strip()}"
    return result.stdout.strip(), None


def check_commits(before_arg: str, head_arg: str) -> tuple[str, str, list[str]]:
    blockers = []
    head, err = resolve_commit(head_arg)
    if err:
        blockers.append(f"STALE_HEAD: {err}")
    before, err = resolve_commit(before_arg)
    if err:
        blockers.append(f"GIT_DIFF: {err}")
    if head and before:
        actual = git(["rev-parse", "HEAD"]).stdout.strip()
        if head != actual:
            blockers.append(f"STALE_HEAD: head_sha {head} does not match repository HEAD {actual}")
        if git(["merge-base", "--is-ancestor", before, head]).returncode != 0:
            blockers.append(f"ANCESTRY: before_sha {before} is not an ancestor of head_sha {head}")
    return before or before_arg, head or head_arg, blockers


def changed_files(before: str, head: str) -> tuple[dict[str, list[str]], str | None]:
    result = git(["diff", "--name-status", "--no-renames", "-z", before, head])
    empty: dict[str, list[str]] = {"added": [], "modified": [], "deleted": []}
    if result.returncode != 0:
        return empty, f"git diff failed for {before}..{head}: {result.stderr.strip() or 'unknown error'}"
    fields = result.stdout.split("\0")
    buckets: dict[str, list[str]] = {"added": [], "modified": [], "deleted": []}
    for i in range(0, len(fields) - 1, 2):
        status, path = fields[i], fields[i + 1]
        if status == "A":
            buckets["added"].append(path)
        elif status in ("M", "T"):
            buckets["modified"].append(path)
        elif status == "D":
            buckets["deleted"].append(path)
        else:
            return empty, f"unrecognized git status {status!r} for {path}"
    return buckets, None


def check_brief_frozen(brief_rel: str | None, before: str, head: str) -> list[str]:
    if brief_rel is None:
        return ["BRIEF_FROZEN: brief must live inside the repository"]
    if git_show(before, brief_rel) is None:
        return [f"BRIEF_FROZEN: brief {brief_rel} does not exist at before_sha (commit the brief before implementing)"]
    diff = git(["diff", "--name-only", before, head, "--", brief_rel])
    if diff.returncode != 0 or diff.stdout.strip():
        return [f"BRIEF_FROZEN: brief {brief_rel} changed between before_sha and head_sha"]
    return []


def check_frozen_lock(head: str) -> list[str]:
    raw = git_show(head, guard.LOCK_PATH)
    if raw is None:
        return [f"FROZEN_LOCK: {guard.LOCK_PATH} not found at head_sha"]
    try:
        records, error = guard.parse_lock_text(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        return [f"FROZEN_LOCK: lock is not valid text: {exc}"]
    if error:
        return [f"FROZEN_LOCK: {error}"]
    problems = []
    for path, expected in sorted(records.items()):
        content = git_show(head, path)
        if content is None:
            problems.append(f"FROZEN_LOCK: frozen file missing at head_sha: {path}")
        elif guard.sha256_bytes(content) != expected:
            problems.append(f"FROZEN_LOCK: {path} modified outside guard")
    return problems


def check_scope_and_files(changed: dict[str, list[str]], brief: Brief) -> list[str]:
    errors = []
    added, modified, deleted = ([f for f in changed[k] if not is_artifact(f)] for k in ("added", "modified", "deleted"))
    for path in added + modified + deleted:
        if not in_scope(path, brief.scope):
            errors.append(f"DIFF_SCOPE: file outside TASK_SCOPE: {path}")
    if len(added) > brief.max_new_files:
        errors.append(f"NEW_FILES: {len(added)} new files (max {brief.max_new_files})")
    return errors


def max_func_lines(tree: ast.AST) -> tuple[int, str]:
    best, name = 0, ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.end_lineno:
            length = node.end_lineno - node.lineno + 1
            if length > best:
                best, name = length, node.name
    return best, name


def ruff_command() -> list[str]:
    return ["ruff"] if shutil.which("ruff") else [sys.executable, "-m", "ruff"]


def check_python_file(path: str, content: bytes, ruff: list[str]) -> list[str]:
    errors = []
    text = content.decode("utf-8", errors="replace")
    lines = len(text.splitlines())
    if lines > MAX_FILE_LINES:
        errors.append(f"SIZE_FILE: {path} has {lines} lines (max {MAX_FILE_LINES})")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return errors + [f"SYNTAX: {path}: {exc.msg} (line {exc.lineno})"]
    length, name = max_func_lines(tree)
    if length > MAX_FUNC_LINES:
        errors.append(f"SIZE_FUNC: {path}:{name} has {length} lines (max {MAX_FUNC_LINES})")
    try:
        result = subprocess.run(
            [*ruff, "check", "--config", RUFF_CONFIG, "--stdin-filename", path, "-"],
            input=content, capture_output=True,
        )
    except OSError as exc:
        return errors + [f"RUFF: unable to launch ruff: {exc}"]
    if result.returncode != 0:
        output = (result.stdout + result.stderr).decode("utf-8", errors="replace").splitlines()
        errors += [f"RUFF: {line}" for line in output if line.strip()]
    return errors


def check_python(changed: dict[str, list[str]], brief: Brief, head: str) -> list[str]:
    ruff = ruff_command()
    errors = []
    for path in changed["added"] + changed["modified"]:
        if is_artifact(path) or not path.endswith(".py") or not in_scope(path, brief.scope):
            continue
        content = git_show(head, path)
        if content is not None:
            errors += check_python_file(path, content, ruff)
    return errors


def diff_stats(before: str, head: str, paths: list[str]) -> tuple[dict[str, int], str | None]:
    if not paths:
        return {"insertions": 0, "deletions": 0}, None
    result = git(["diff", "--numstat", "--no-renames", before, head, "--", *paths])
    if result.returncode != 0:
        return {"insertions": 0, "deletions": 0}, f"git diff --numstat failed: {result.stderr.strip()}"
    ins = dels = 0
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            ins, dels = ins + int(parts[0]), dels + int(parts[1])
    return {"insertions": ins, "deletions": dels}, None


def check_ratio(stats: dict[str, int], threshold: int) -> list[str]:
    ins, dels, wymaga = stats["insertions"], stats["deletions"], []
    if dels > 0 and ins / dels > RATIO_THRESHOLD:
        wymaga.append(f"RATIO: {ins}/{dels} = {ins / dels:.1f}:1 (threshold {RATIO_THRESHOLD}:1)")
    if ins + dels > threshold:
        wymaga.append(f"TOTAL_LINES: {ins + dels} lines changed (threshold {threshold})")
    return wymaga


def check_tier(changed: dict[str, list[str]], brief: Brief, head: str) -> list[str]:
    raw = git_show(head, CRITICAL_PATHS_FILE)
    if raw is None or brief.tier == "CRITICAL":
        return []
    patterns = [ln.strip() for ln in raw.decode("utf-8", errors="replace").splitlines() if ln.strip() and not ln.startswith("#")]
    touched = sorted({p for k in ("added", "modified", "deleted") for p in changed[k]
                      if not is_artifact(p) and any(glob_regex(g).match(p) for g in patterns)})
    if not touched:
        return []
    return [f"AUDIT_TIER: brief declares {brief.tier} but changed files match {CRITICAL_PATHS_FILE}: {', '.join(touched)}"]


def import_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.ImportFrom):
        return [(node.module or "").split(".")[-1]]
    if isinstance(node, ast.Import):
        return [a.name.split(".")[-1] for a in node.names]
    return []


def find_importers(changed_py: list[str]) -> list[str]:
    stems = {Path(f).stem for f in changed_py}
    if not stems:
        return []
    importers = []
    for py in git(["ls-files", "*.py"]).stdout.splitlines():
        if py in changed_py or not Path(py).is_file():
            continue
        try:
            tree = ast.parse(Path(py).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        if any(name in stems for node in ast.walk(tree) for name in import_names(node)):
            importers.append(py)
    return importers


def build_output(status: str, head: str, tier: str, blockers: list[str], wymaga: list[str],
                 importers: list[str], excluded: list[str]) -> str:
    lines = [f"STATUS: {status}", f"HEAD_SHA: {head}", f"AUDIT_TIER: {tier}", f"CHECKS: {CHECKS}"]
    for title, items in (("REASON:", blockers), ("WYMAGA_DECYZJI:", wymaga), ("IMPORTERS_FOR_REVIEW:", importers)):
        if items:
            lines += [title] + [f"  - {i}" for i in items]
    lines += (["EXCLUDED_ARTIFACTS:"] + [f"  - {e}" for e in excluded]) if excluded else ["EXCLUDED_ARTIFACTS: NONE"]
    return "\n".join(lines)


def run_backend(brief_arg: Path, before_arg: str, head_arg: str, output_path: Path) -> int:
    top = git(["rev-parse", "--show-toplevel"])
    if top.returncode != 0:
        print("STATUS: FAIL\nREASON: not inside a git repository")
        return 1
    brief_abs, output_abs = brief_arg.resolve(), output_path.resolve()
    os.chdir(top.stdout.strip())
    try:
        brief_rel = brief_abs.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        brief_rel = None

    blockers: list[str] = []
    brief = Brief([], DEFAULT_MAX_NEW_FILES, DEFAULT_TOTAL_LINES, "STANDARD")
    try:
        brief = read_brief(brief_abs)
        blockers += check_scope_entries(brief.scope)
    except ValueError as exc:
        blockers.append(f"TASK_SCOPE: {exc}")

    before, head, commit_errors = check_commits(before_arg, head_arg)
    blockers += commit_errors
    changed: dict[str, list[str]] = {"added": [], "modified": [], "deleted": []}
    wymaga: list[str] = []
    if not commit_errors:
        changed, diff_err = changed_files(before, head)
        blockers += [f"GIT_DIFF: {diff_err}"] if diff_err else []
        blockers += check_brief_frozen(brief_rel, before, head)
        blockers += check_frozen_lock(head)
        if not any(b.startswith(("TASK_SCOPE", "SCOPE_ENTRY")) for b in blockers):
            blockers += check_scope_and_files(changed, brief)
            blockers += check_python(changed, brief, head)
            paths = [p for k in ("added", "modified", "deleted") for p in changed[k] if not is_artifact(p)]
            stats, stats_err = diff_stats(before, head, paths)
            blockers += [f"GIT_DIFF: {stats_err}"] if stats_err else []
            wymaga = check_ratio(stats, brief.total_lines) + check_tier(changed, brief, head)

    changed_py = [p for k in ("added", "modified") for p in changed[k] if p.endswith(".py") and not is_artifact(p)]
    excluded = [p for k in ("added", "modified", "deleted") for p in changed[k] if is_artifact(p)]
    status = "FAIL" if blockers else "WYMAGA_DECYZJI" if wymaga else "PASS"
    output = build_output(status, head, brief.tier, blockers, wymaga, find_importers(changed_py), excluded)
    output_abs.parent.mkdir(parents=True, exist_ok=True)
    output_abs.write_text(output, encoding="utf-8", newline="\n")
    print(output)
    return {"PASS": 0, "WYMAGA_DECYZJI": 2, "FAIL": 1}[status]


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("USAGE: backend.py <brief.md> <before_sha> <head_sha> <output_backend.txt>")
        sys.exit(1)
    sys.exit(run_backend(Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])))
