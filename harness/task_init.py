#!/usr/bin/env python3
"""
ROLE: start a Task -- create tasks/<task_id>/ and snapshot the base commit.
USAGE: task_init.py <task_id>          (run inside the repo, on the Task branch)
CREATES: tasks/<task_id>/repo_before.hash   (HEAD_SHA + TIMESTAMP)
REFUSES (FAIL): invalid/reserved id, existing folder, git hooks not installed.
The hooks check is the mechanical reminder that `git config core.hooksPath .githooks`
was run in this clone -- without it nothing stops a commit to the default branch.
OUTPUT: structured key:value, no prose.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = re.compile(r"^[A-Za-z0-9_-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def fail(reason: str) -> None:
    print(f"STATUS: FAIL\nREASON: {reason}")
    sys.exit(1)


def git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")


def head_sha() -> str:
    result = git(["rev-parse", "HEAD"])
    sha = result.stdout.strip()
    if result.returncode != 0 or not SHA.fullmatch(sha):
        fail(f"git did not return a valid HEAD sha: {sha!r}")
    return sha


def require_hooks() -> None:
    configured = git(["config", "--get", "core.hooksPath"]).stdout.strip()
    if configured != ".githooks":
        fail("git hooks not installed in this clone -- run: git config core.hooksPath .githooks")


def run_task_init(task_id: str) -> None:
    if not TASK_ID.fullmatch(task_id) or task_id.upper() in RESERVED:
        fail(f"invalid task_id: {task_id!r}")
    top = git(["rev-parse", "--show-toplevel"])
    if top.returncode != 0:
        fail("not inside a git repository")
    os.chdir(top.stdout.strip())
    require_hooks()
    sha = head_sha()
    task_path = Path("tasks") / task_id
    if task_path.exists():
        fail(f"tasks/{task_id}/ already exists")
    task_path.mkdir(parents=True)
    try:
        stamp = datetime.now(timezone.utc).isoformat()
        (task_path / "repo_before.hash").write_text(f"HEAD_SHA: {sha}\nTIMESTAMP: {stamp}\n", encoding="utf-8", newline="\n")
    except OSError:
        shutil.rmtree(task_path, ignore_errors=True)
        raise
    print(f"STATUS: CREATED\nTASK: {task_id}\nHEAD_SHA: {sha}\nPATH: {task_path.as_posix()}/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USAGE: task_init.py <task_id>")
        sys.exit(1)
    run_task_init(sys.argv[1])
