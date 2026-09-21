"""Shared fixtures: every test builds a throwaway git repo that contains a copy of harness/."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
DEFAULT_BRIEF = "# Task T1\n\nTASK_SCOPE:\n- app/**\n- tests/test_app.py\n"


class Repo:
    def __init__(self, root: Path):
        self.root = root

    def git(self, *args: str, check: bool = True) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        if check and result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
        return result.stdout.strip()

    def write(self, rel: str, content: str) -> None:
        target = self.root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    def commit(self, message: str = "change") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run(self, script: str, *args: str, input_cwd: Path | None = None) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(self.root / "harness" / script), *args],
            cwd=input_cwd or self.root, capture_output=True, text=True,
        )
        return result.returncode, result.stdout + result.stderr

    def backend(self, before: str, head: str, brief: str = "tasks/T1.md") -> tuple[int, str]:
        return self.run("backend.py", brief, before, head, "tasks/T1/backend.txt")


def build_repo(root: Path, brief: str = DEFAULT_BRIEF, extra_harness: dict[str, str] | None = None) -> tuple[Repo, str]:
    """Baseline commit = harness copy + frozen spec + committed brief + one product file."""
    repo = Repo(root)
    root.mkdir(parents=True, exist_ok=True)
    repo.git("init", "-q", "-b", "main")
    repo.git("config", "user.email", "t@example.com")
    repo.git("config", "user.name", "Test")
    repo.git("config", "commit.gpgsign", "false")
    shutil.copytree(HARNESS, root / "harness", ignore=shutil.ignore_patterns("tests", "__pycache__", "FROZEN.lock"))
    for rel, content in (extra_harness or {}).items():
        repo.write(rel, content)
    repo.write("docs/SPEC.md", "frozen spec v1\n")
    repo.write("tasks/T1.md", brief)
    repo.write("app/core.py", "def add(a, b):\n    return a + b\n")
    code, out = repo.run("guard.py", "freeze", "docs/SPEC.md")
    assert code == 0, out
    return repo, repo.commit("baseline")


@pytest.fixture
def repo_and_base(tmp_path):
    return build_repo(tmp_path / "repo")
