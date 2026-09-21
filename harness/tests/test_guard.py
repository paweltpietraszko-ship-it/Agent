"""guard.py -- multi-file FROZEN.lock behaviour."""
from __future__ import annotations

import pytest

import guard


def lock_text(repo) -> str:
    return (repo.root / "harness/FROZEN.lock").read_text(encoding="utf-8")


def test_freeze_writes_sorted_records_and_check_passes(repo_and_base):
    repo, _ = repo_and_base
    repo.write("docs/A.md", "a\n")
    assert repo.run("guard.py", "freeze", "docs/A.md")[0] == 0
    lines = [ln for ln in lock_text(repo).splitlines() if not ln.startswith("#")]
    assert [ln.split("  ")[1] for ln in lines] == ["docs/A.md", "docs/SPEC.md"]
    code, out = repo.run("guard.py", "check")
    assert code == 0 and "CHECKED: 2" in out


def test_check_detects_modification_missing_and_unfrozen(repo_and_base):
    repo, _ = repo_and_base
    repo.write("docs/SPEC.md", "changed\n")
    code, out = repo.run("guard.py", "check")
    assert code == 1 and "docs/SPEC.md: hash mismatch" in out
    (repo.root / "docs/SPEC.md").unlink()
    assert "file missing" in repo.run("guard.py", "check")[1]
    assert "not frozen" in repo.run("guard.py", "check", "docs/other.md")[1]


def test_refreeze_requires_recompute_and_recompute_requires_existing(repo_and_base):
    repo, _ = repo_and_base
    assert "already frozen" in repo.run("guard.py", "freeze", "docs/SPEC.md")[1]
    repo.write("docs/New.md", "n\n")
    assert "not frozen yet" in repo.run("guard.py", "freeze", "--recompute", "docs/New.md")[1]
    repo.write("docs/SPEC.md", "v2\n")
    assert repo.run("guard.py", "freeze", "--recompute", "docs/SPEC.md")[0] == 0
    assert repo.run("guard.py", "check")[0] == 0


@pytest.mark.parametrize("arg", ["../outside.md", "harness/backend.py", ".githooks/pre-commit", "nope.md"])
def test_freeze_rejects_outside_protected_or_missing(repo_and_base, arg):
    repo, _ = repo_and_base
    code, out = repo.run("guard.py", "freeze", arg)
    assert code == 1 and out.startswith("STATUS: FAIL")


def test_malformed_and_duplicate_locks_fail_closed(repo_and_base):
    repo, _ = repo_and_base
    good = lock_text(repo)
    for bad in ("nonsense\n", good + good.splitlines()[-1] + "\n", "# only a comment\n"):
        repo.write("harness/FROZEN.lock", bad)
        code, out = repo.run("guard.py", "check")
        assert code == 1 and "REASON" in out, bad


def test_parse_lock_text_unit():
    sha = "a" * 64
    assert guard.parse_lock_text(f"{sha}  x y.md\n") == ({"x y.md": sha}, None)
    assert guard.parse_lock_text(f"{sha} x\n")[1] is not None


def test_usage_errors_exit_nonzero(repo_and_base):
    repo, _ = repo_and_base
    assert repo.run("guard.py")[0] == 1
    assert repo.run("guard.py", "freeze")[0] == 1
    assert repo.run("guard.py", "check", "--all")[0] == 1
