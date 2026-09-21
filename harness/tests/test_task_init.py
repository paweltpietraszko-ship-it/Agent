"""task_init.py and the pre-commit hook."""
from __future__ import annotations

import shutil

import pytest

from conftest import HARNESS


def install_hooks(repo) -> None:
    shutil.copytree(HARNESS.parent / ".githooks", repo.root / ".githooks", dirs_exist_ok=True)
    repo.git("config", "core.hooksPath", ".githooks")


def test_task_init_creates_folder_and_records_head(repo_and_base):
    repo, base = repo_and_base
    install_hooks(repo)
    code, out = repo.run("task_init.py", "V0A01")
    assert code == 0 and f"HEAD_SHA: {base}" in out
    text = (repo.root / "tasks/V0A01/repo_before.hash").read_text(encoding="utf-8")
    assert text.startswith(f"HEAD_SHA: {base}\n") and "TIMESTAMP:" in text


@pytest.mark.parametrize("task_id", ["bad id", "../x", "CON", "com1", "a/b", ""])
def test_task_init_rejects_bad_ids(repo_and_base, task_id):
    repo, _ = repo_and_base
    install_hooks(repo)
    code, out = repo.run("task_init.py", task_id)
    assert code == 1 and "invalid task_id" in out


def test_task_init_rejects_existing_folder_and_missing_hooks(repo_and_base):
    repo, _ = repo_and_base
    assert "hooks not installed" in repo.run("task_init.py", "T9")[1]
    install_hooks(repo)
    assert repo.run("task_init.py", "T9")[0] == 0
    code, out = repo.run("task_init.py", "T9")
    assert code == 1 and "already exists" in out


def test_hook_blocks_default_branch_commits_except_bookkeeping(repo_and_base):
    repo, _ = repo_and_base
    install_hooks(repo)
    repo.write("app/x.py", "x = 1\n")
    repo.git("add", "app/x.py")
    result = repo.git("commit", "-q", "-m", "x", check=False)
    assert repo.git("log", "--oneline").count("\n") == 0 and "x" not in repo.git("log", "-1", "--format=%s")
    repo.git("reset", "-q")
    repo.write("BOARD.md", "b\n")
    repo.git("add", "BOARD.md")
    repo.git("commit", "-q", "-m", "board")
    assert repo.git("log", "-1", "--format=%s") == "board"
    assert result == ""


def test_hook_allows_task_branches_and_the_first_commit(tmp_path):
    from conftest import Repo
    repo = Repo(tmp_path / "fresh")
    repo.root.mkdir()
    repo.git("init", "-q", "-b", "main")
    repo.git("config", "user.email", "t@example.com")
    repo.git("config", "user.name", "T")
    install_hooks(repo)
    repo.write("a.txt", "a\n")
    repo.git("add", "a.txt")
    repo.git("commit", "-q", "-m", "first")  # first commit on main is allowed
    repo.git("switch", "-q", "-c", "task/x")
    repo.write("b.py", "x = 1\n")
    repo.git("add", "b.py")
    repo.git("commit", "-q", "-m", "on task branch")
    assert repo.git("log", "-1", "--format=%s") == "on task branch"
