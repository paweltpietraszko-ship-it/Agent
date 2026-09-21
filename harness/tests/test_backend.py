"""backend.py -- every check gets a PASS case and a FAIL/WYMAGA case on a throwaway repo."""
from __future__ import annotations

import pytest

from conftest import DEFAULT_BRIEF, build_repo


def deliver(repo, files: dict[str, str]) -> str:
    for rel, content in files.items():
        repo.write(rel, content)
    return repo.commit()


def verdict(result: tuple[int, str]) -> tuple[int, str]:
    code, out = result
    return code, out.splitlines()[0]


def test_small_in_scope_change_passes(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"app/core.py": "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n"})
    code, out = repo.backend(base, head)
    assert (code, out.splitlines()[0]) == (0, "STATUS: PASS"), out
    assert "AUDIT_TIER: STANDARD" in out
    assert (repo.root / "tasks/T1/backend.txt").read_text(encoding="utf-8").startswith("STATUS: PASS")


def test_file_outside_scope_fails(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"other.py": "x = 1\n"})
    code, out = repo.backend(base, head)
    assert code == 1 and "DIFF_SCOPE: file outside TASK_SCOPE: other.py" in out


def test_deleted_file_outside_scope_fails(repo_and_base):
    repo, base = repo_and_base
    repo.git("rm", "-q", "docs/SPEC.md")
    head = repo.commit()
    code, out = repo.backend(base, head)
    assert code == 1 and "DIFF_SCOPE: file outside TASK_SCOPE: docs/SPEC.md" in out


def test_deleted_and_renamed_in_scope_pass(repo_and_base):
    repo, base = repo_and_base
    repo.git("mv", "app/core.py", "app/core2.py")
    head = repo.commit()
    assert verdict(repo.backend(base, head)) == (0, "STATUS: PASS")


@pytest.mark.parametrize("scope_text", [
    "# T\n",
    "# T\nTASK_SCOPE:\n",
    "# T\nTASK_SCOPE:\n- app/**\nTASK_SCOPE:\n- app/x.py\n",
])
def test_missing_empty_or_duplicate_scope_fails(tmp_path, scope_text):
    repo, base = build_repo(tmp_path / "r", brief=scope_text)
    head = deliver(repo, {"app/x.py": "x = 1\n"})
    code, out = repo.backend(base, head)
    assert code == 1 and "TASK_SCOPE" in out


@pytest.mark.parametrize("entry", [
    "/etc/passwd", "C:/x.py", "app\\x.py", "../x.py", "app/../x.py", "*.py", "**/x.py",
    "harness/backend.py", ".githooks/pre-commit", ".github/workflows/gate.yml", "app/[a].py", "app/{a,b}.py",
])
def test_bad_scope_entries_fail(tmp_path, entry):
    repo, base = build_repo(tmp_path / "r", brief=f"TASK_SCOPE:\n- {entry}\n")
    head = deliver(repo, {"app/x.py": "x = 1\n"})
    code, out = repo.backend(base, head)
    assert code == 1 and "SCOPE_ENTRY" in out, out


def test_directory_glob_matches_nested_but_single_star_does_not_cross_folders(tmp_path):
    repo, base = build_repo(tmp_path / "r", brief="TASK_SCOPE:\n- app/**\n- tests/*.py\n")
    head = deliver(repo, {"app/a/b/c.py": "x = 1\n", "tests/test_x.py": "x = 1\n"})
    assert verdict(repo.backend(base, head)) == (0, "STATUS: PASS")
    head2 = deliver(repo, {"tests/sub/test_y.py": "x = 1\n"})
    code, out = repo.backend(head, head2)
    assert code == 1 and "tests/sub/test_y.py" in out


def test_new_files_limit_and_override(tmp_path):
    files = {f"app/f{i}.py": "x = 1\n" for i in range(3)}
    repo, base = build_repo(tmp_path / "a")
    code, out = repo.backend(base, deliver(repo, files))
    assert code == 1 and "NEW_FILES: 3 new files (max 2)" in out
    repo2, base2 = build_repo(tmp_path / "b", brief=DEFAULT_BRIEF + "MAX_NEW_FILES: 5\n")
    assert verdict(repo2.backend(base2, deliver(repo2, files))) == (0, "STATUS: PASS")


def test_total_lines_needs_decision_and_threshold_override(tmp_path):
    big = {"app/big.py": "".join(f"v{i} = {i}\n" for i in range(200))}
    repo, base = build_repo(tmp_path / "a")
    code, out = repo.backend(base, deliver(repo, big))
    assert code == 2 and out.splitlines()[0] == "STATUS: WYMAGA_DECYZJI" and "TOTAL_LINES: 200" in out
    repo2, base2 = build_repo(tmp_path / "b", brief=DEFAULT_BRIEF + "TOTAL_LINES_THRESHOLD: 500\n")
    assert verdict(repo2.backend(base2, deliver(repo2, big))) == (0, "STATUS: PASS")


def test_insertion_deletion_ratio_needs_decision(repo_and_base):
    repo, base = repo_and_base
    body = "def add(a, b, c=0):\n" + "    a = a + 1\n" * 12 + "    return a + b + c\n"
    code, out = repo.backend(base, deliver(repo, {"app/core.py": body}))
    assert code == 2 and "RATIO:" in out


def lines(count):
    return "".join(f"v{i} = {i}\n" for i in range(count))


def func(name, body_lines):
    return f"def {name}():\n" + "    print(1)\n" * body_lines + "    return 1\n"


def test_size_soft_limit_needs_decision_hard_limit_fails(repo_and_base):
    repo, base = repo_and_base
    soft = {"app/long.py": lines(601)}
    code, out = repo.backend(base, deliver(repo, soft))
    assert code == 2 and "SIZE_FILE: app/long.py has 601 lines (soft limit 600)" in out
    hard = {"app/huge.py": lines(901)}
    code, out = repo.backend(repo.git("rev-parse", "HEAD"), deliver(repo, hard))
    assert code == 1 and "SIZE_FILE: app/huge.py has 901 lines (hard max 900)" in out


def test_tests_get_higher_file_limit(repo_and_base):
    repo, base = repo_and_base
    code, out = repo.backend(base, deliver(repo, {"tests/test_app.py": lines(1000)}))
    assert "SIZE_FILE:" not in out, out
    assert code == 2 and "TOTAL_LINES" in out


def test_function_size_soft_and_hard(repo_and_base):
    repo, base = repo_and_base
    code, out = repo.backend(base, deliver(repo, {"app/fn.py": func("f", 50)}))
    assert code == 2 and "SIZE_FUNC: app/fn.py:f has 52 lines (soft limit 50)" in out
    code, out = repo.backend(repo.git("rev-parse", "HEAD"), deliver(repo, {"app/fn2.py": func("g", 80)}))
    assert code == 1 and "SIZE_FUNC: app/fn2.py:g has 82 lines (hard max 80)" in out


def test_ruff_and_syntax_errors_fail(repo_and_base):
    repo, base = repo_and_base
    code, out = repo.backend(base, deliver(repo, {"app/unused.py": "import os\n"}))
    assert code == 1 and "RUFF:" in out and "F401" in out
    head = repo.git("rev-parse", "HEAD")
    code, out = repo.backend(head, deliver(repo, {"app/broken.py": "def f(:\n"}))
    assert code == 1 and "SYNTAX: app/broken.py" in out


def test_gate_measures_the_commit_not_the_working_tree(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"app/unused.py": "import os\n"})
    repo.write("app/unused.py", "x = 1\n")  # uncommitted "fix" must not rescue the delivered commit
    code, out = repo.backend(base, head)
    assert code == 1 and "F401" in out


def test_stale_head_and_ancestry_fail_and_short_shas_work(repo_and_base):
    repo, base = repo_and_base
    first = deliver(repo, {"app/a.py": "x = 1\n"})
    deliver(repo, {"app/b.py": "x = 1\n"})
    code, out = repo.backend(base, first)
    assert code == 1 and "STALE_HEAD" in out
    repo.git("switch", "-q", "-c", "side", base)
    side = deliver(repo, {"app/side.py": "x = 1\n"})
    repo.git("switch", "-q", "main")
    head = repo.git("rev-parse", "HEAD")
    code, out = repo.backend(side, head)
    assert code == 1 and "ANCESTRY" in out
    _, short_out = repo.backend(base[:8], head[:8])
    assert "STALE_HEAD:" not in short_out and "ANCESTRY:" not in short_out


def test_unresolvable_sha_fails_instead_of_crashing(repo_and_base):
    repo, base = repo_and_base
    code, out = repo.backend(base, "deadbeef")
    assert code == 1 and "STALE_HEAD: cannot resolve" in out


def test_brief_must_be_committed_before_and_unchanged(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"tasks/T1.md": DEFAULT_BRIEF + "TASK_SCOPE:\n- everything\n"})
    code, out = repo.backend(base, head)
    assert code == 1 and "BRIEF_FROZEN: brief tasks/T1.md changed" in out
    repo.write("tasks/T2.md", DEFAULT_BRIEF)
    head2 = repo.commit()
    code, out = repo.backend(head, head2, brief="tasks/T2.md")
    assert code == 1 and "does not exist at before_sha" in out


def test_frozen_file_edit_fails_even_if_lock_is_recomputed(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"docs/SPEC.md": "frozen spec v2\n"})
    code, out = repo.backend(base, head)
    assert code == 1 and "FROZEN_LOCK: docs/SPEC.md modified outside guard" in out
    repo.write("docs/SPEC.md", "frozen spec v3\n")
    assert repo.run("guard.py", "freeze", "--recompute", "docs/SPEC.md")[0] == 0
    head2 = repo.commit()
    code, out = repo.backend(head, head2)
    assert code == 1 and "DIFF_SCOPE: file outside TASK_SCOPE: harness/FROZEN.lock" in out


def test_missing_lock_fails(tmp_path):
    repo, base = build_repo(tmp_path / "r")
    repo.git("rm", "-q", "harness/FROZEN.lock")
    head = repo.commit()
    code, out = repo.backend(base, head)
    assert code == 1 and "FROZEN_LOCK: harness/FROZEN.lock not found" in out


def test_pipeline_artifacts_are_reported_not_scope_checked(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"tasks/T1/notes.md": "n\n", "BOARD.md": "board\n"})
    code, out = repo.backend(base, head)
    assert code == 0 and "tasks/T1/notes.md" in out and "BOARD.md" in out


def test_critical_paths_force_a_tier_decision(tmp_path):
    extra = {"harness/critical_paths.txt": "# c\napp/lifecycle/**\n"}
    repo, base = build_repo(tmp_path / "a", brief="TASK_SCOPE:\n- app/**\n", extra_harness=extra)
    code, out = repo.backend(base, deliver(repo, {"app/lifecycle/x.py": "x = 1\n"}))
    assert code == 2 and "AUDIT_TIER: brief declares STANDARD" in out
    repo2, base2 = build_repo(tmp_path / "b", brief="AUDIT_TIER: CRITICAL\nTASK_SCOPE:\n- app/**\n", extra_harness=extra)
    code, out = repo2.backend(base2, deliver(repo2, {"app/lifecycle/x.py": "x = 1\n"}))
    assert code == 0 and "AUDIT_TIER: CRITICAL" in out


@pytest.mark.parametrize("line", ["AUDIT_TIER: EXTREME", "MAX_NEW_FILES: many", "MAX_NEW_FILES: 0", "TOTAL_LINES_THRESHOLD: 20001", "MAX_NEW_FILES: 201"])
def test_invalid_brief_fields_fail(tmp_path, line):
    repo, base = build_repo(tmp_path / "r", brief=f"{line}\nTASK_SCOPE:\n- app/**\n")
    code, out = repo.backend(base, deliver(repo, {"app/x.py": "x = 1\n"}))
    assert code == 1 and "TASK_SCOPE:" in out


def test_runs_from_a_subdirectory_with_absolute_brief_path(repo_and_base):
    repo, base = repo_and_base
    head = deliver(repo, {"app/z.py": "x = 1\n"})
    code, out = repo.run(
        "backend.py", str(repo.root / "tasks/T1.md"), base, head, str(repo.root / "tasks/T1/out.txt"),
        input_cwd=repo.root / "app",
    )
    assert code == 0 and out.startswith("STATUS: PASS"), out


def test_shipped_brief_template_parses_with_declared_defaults():
    import backend
    from conftest import HARNESS

    brief = backend.read_brief(HARNESS / "templates" / "brief.md")
    assert brief.scope == ["app/**", "tests/test_<x>.py"]
    assert (brief.tier, brief.max_new_files, brief.total_lines) == ("STANDARD", 2, 150)
