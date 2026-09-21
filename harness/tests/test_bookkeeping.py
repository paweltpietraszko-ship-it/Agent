"""bookkeeping_only.py -- may relax the gate only for in-place edits of BOARD.md / ODLOZONE.md."""
from __future__ import annotations

import subprocess

from conftest import build_repo

NL = chr(10)


def with_files(repo, files):
    for rel, content in files.items():
        repo.write(rel, content)
    return repo.commit()


def verdict(repo, before, head):
    return repo.run("bookkeeping_only.py", before, head)[0]


def test_bookkeeping_files_edited_in_place_pass(tmp_path):
    repo, base = build_repo(tmp_path / "r")
    base = with_files(repo, {"BOARD.md": "a" + NL, "ODLOZONE.md": "a" + NL})
    head = with_files(repo, {"BOARD.md": "b" + NL, "ODLOZONE.md": "b" + NL})
    assert verdict(repo, base, head) == 0


def test_other_file_empty_diff_add_delete_are_not_bookkeeping(tmp_path):
    repo, base = build_repo(tmp_path / "r")
    base = with_files(repo, {"BOARD.md": "a" + NL})
    assert verdict(repo, base, with_files(repo, {"BOARD.md": "b" + NL, "app/core.py": "x = 1" + NL})) == 1
    assert verdict(repo, base, base) == 1
    added = with_files(repo, {"ODLOZONE.md": "new" + NL})
    assert verdict(repo, base, added) == 1
    repo.git("rm", "-q", "BOARD.md")
    assert verdict(repo, base, repo.commit("delete")) == 1


def test_symlink_and_lookalike_names_are_not_bookkeeping(tmp_path):
    repo, base = build_repo(tmp_path / "r")
    base = with_files(repo, {"BOARD.md": "a" + NL})
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo.root, input="BOARD.md", capture_output=True, text=True).stdout.strip()
    repo.git("update-index", "--cacheinfo", f"120000,{blob},BOARD.md")
    assert verdict(repo, base, repo.commit("symlink")) == 1
    repo.git("config", "core.protectNTFS", "false")
    repo.git("update-index", "--force-remove", "BOARD.md")
    repo.git("update-index", "--add", "--cacheinfo", f"100644,{blob},BOARD.md ")
    assert verdict(repo, base, repo.commit("lookalike")) == 1
