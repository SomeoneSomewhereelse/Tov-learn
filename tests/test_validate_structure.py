"""Seeded regressions and must-pass negatives for validate_structure.

Every fixture test calls the checks through ``fixture_checks()``, which binds
``spoken_lesson_refs`` to the fixture's own allowlist. Only
``test_real_repo_passes`` uses the default ``SPOKEN_ALLOWLIST``.
"""

import shutil
import subprocess
from functools import partial
from pathlib import Path

import pytest
import validate_structure as vs

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ALLOWLIST = (("0.1_script.txt", "גרסה שש נקודה שש"),)
M = "[מעבר שקף]"


def fixture_checks() -> dict:
    """Every check by short name, with spoken_lesson_refs bound to FIXTURE_ALLOWLIST."""
    checks = {}
    for check in vs.CHECKS:
        name = check.__name__.removeprefix("check_")
        if name == "spoken_lesson_refs":
            check = partial(check, allowlist=FIXTURE_ALLOWLIST)
        checks[name] = check
    return checks


def run_all(root: Path) -> dict[str, list[str]]:
    return {name: check(root) for name, check in fixture_checks().items()}


def script(first_line: str, extra: str = "") -> str:
    body = "\n".join(f"{M}\nקטע {n}." for n in range(1, 6))
    return f"{first_line}\nשלום וברוכים הבאים.\n\n{body}\n{extra}"


def exercises(number: str) -> str:
    return (
        '<div dir="rtl" lang="he">\n\n'
        f"# תרגילים - שיעור {number}: נושא\n\n"
        "## פרטי השיעור\n"
        f"- **שיעור:** {number} - נושא\n"
        "- **קורס:** Demo\n\n"
        "</div>\n"
    )


COURSE_MD = """\
# Demo

## מודולים

| מודול | תיקייה | שיעורים |
|-------|--------|---------|
| 00 — Basics | `00-basics/` | 0.1–0.2 |
| 02 — API | `02-api/` | 2.1–2.1 |
| 03 — Final | `03-final/` | — |

## רשימת שיעורים

| מספר | שם | סוג |
|------|----|-----|
| 0.1 | First | תיאורטי |
| 0.2 | Second | תיאורטי |
| 2.1 | API | מעשי |
"""

SETUP_MD = """\
# Setup Module

<!-- CLEAN-SLATE:BEGIN — TEMPORARY, remove at first-cohort gate (PRD D10) -->
## 0. Clean slate

```bash
: "${HOME:?HOME is not set}"
dest="$HOME/skill-tutor-tutorials-backup-$(date +%Y%m%d-%H%M%S)"
mkdir "$dest" || exit 1
mv "$HOME/skill-tutor-tutorials" "$dest/" || exit 1
```

```powershell
$dest = Join-Path $HOME "skill-tutor-tutorials-backup"
New-Item -ItemType Directory -Path $dest -ErrorAction Stop | Out-Null
Move-Item -LiteralPath (Join-Path $HOME "skill-tutor-tutorials") -Destination $dest -ErrorAction Stop
```
<!-- CLEAN-SLATE:END -->

## A. Show Current Settings
"""

LESSONS = "courses/demo/lessons"
S01 = f"{LESSONS}/00-basics/0.1-first/0.1_script.txt"
S02 = f"{LESSONS}/00-basics/0.2-second/0.2_script.txt"
S21 = f"{LESSONS}/02-api/2.1-api/2.1_script.txt"
E01 = f"{LESSONS}/00-basics/0.1-first/0.1_exercises.md"
E02 = f"{LESSONS}/00-basics/0.2-second/0.2_exercises.md"
E21 = f"{LESSONS}/02-api/2.1-api/2.1_exercises.md"
LEARN = ".claude/commands/learn.md"
TEACHING = ".claude/commands/learn/teaching.md"
SETUP = ".claude/commands/learn/setup.md"
SETTINGS = ".claude/settings.json"
COURSE = "courses/demo/COURSE.md"

GOOD_TREE = {
    COURSE: COURSE_MD,
    S01: script("שיעור 0.1 - הראשון", "גרסה שש נקודה שש יצאה השנה.\n"),
    E01: exercises("0.1"),
    S02: script("שיעור 0.2 - השני"),
    E02: exercises("0.2"),
    S21: script(
        "שיעור שתיים נקודה אחת - API", "בשיעור הקודם, אפס נקודה שתיים, ראינו.\n"
    ),
    E21: exercises("2.1"),
    f"{LESSONS}/03-final/projects.md": "# Projects\n",
    LEARN: (
        "# /learn\n\n"
        "| lesson | Read `.claude/commands/learn/teaching.md` |\n"
        "| quiz me | Read `.claude/commands/learn/quiz.md` |\n"
        "| setup | Read `.claude/commands/learn/setup.md` |\n"
    ),
    TEACHING: "# Teaching\n\n## Step 5 — End of Lesson\n\nRead `quiz.md` when asked.\n",
    ".claude/commands/learn/quiz.md": "# Quiz\n",
    SETUP: SETUP_MD,
    SETTINGS: "{}\n",
    "README.md": "# Demo\n\nSee the [course](courses/demo/COURSE.md).\n",
}


def write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


@pytest.fixture
def good_tree(tmp_path: Path) -> Path:
    """A small valid repo on disk. Deliberately not a git repo."""
    write_tree(tmp_path, GOOD_TREE)
    return tmp_path


def replace(rel: str, old: str, new: str):
    def mutate(root: Path) -> None:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"seed anchor {old!r} not in {rel}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    return mutate


def append(rel: str, text: str):
    def mutate(root: Path) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(text)

    return mutate


def overwrite(rel: str, text: str):
    def mutate(root: Path) -> None:
        (root / rel).write_text(text, encoding="utf-8")

    return mutate


def chain(*mutations):
    def mutate(root: Path) -> None:
        for m in mutations:
            m(root)

    return mutate


def delete(rel: str):
    def mutate(root: Path) -> None:
        (root / rel).unlink()

    return mutate


def test_good_tree_passes(good_tree: Path) -> None:
    assert run_all(good_tree) == {name: [] for name in fixture_checks()}


SEEDS = [
    # course_md
    ("course_md", "missing-row", replace(COURSE, "| 0.2 | Second | תיאורטי |\n", "")),
    (
        "course_md",
        "extra-row",
        replace(
            COURSE,
            "| 2.1 | API | מעשי |\n",
            "| 2.1 | API | מעשי |\n| 2.2 | Ghost | מעשי |\n",
        ),
    ),
    (
        "course_md",
        "swap",
        replace(
            COURSE,
            "| 0.1 | First | תיאורטי |\n| 0.2 | Second | תיאורטי |",
            "| 0.2 | Second | תיאורטי |\n| 0.1 | First | תיאורטי |",
        ),
    ),
    ("course_md", "wrong-range", replace(COURSE, "| 0.1–0.2 |", "| 0.1–0.3 |")),
    # slide_markers
    ("slide_markers", "four-markers", replace(S02, M, "")),
    ("slide_markers", "english-marker", append(S02, "[SLIDE TRANSITION]\n")),
    # header_numbers
    ("header_numbers", "numeric-5.1-in-2.1", replace(E21, "שיעור 2.1:", "שיעור 5.1:")),
    (
        "header_numbers",
        "bold-line-mismatch",
        replace(E21, "**שיעור:** 2.1", "**שיעור:** 2.2"),
    ),
    ("header_numbers", "script-0.1-in-0.2", replace(S02, "שיעור 0.2 -", "שיעור 0.1 -")),
    (
        "header_numbers",
        "spelled-existing-wrong-lesson",
        replace(S21, "שיעור שתיים נקודה אחת", "שיעור אפס נקודה אחת"),
    ),
    (
        "header_numbers",
        "unmapped-word",
        replace(S21, "שיעור שתיים נקודה אחת", "שיעור שתיים נקודה מאה"),
    ),
    # spoken_lesson_refs (seeds sit after line 3, so header_numbers never sees them)
    (
        "spoken_lesson_refs",
        "no-lesson-3.2",
        append(S01, "בשיעור שלוש נקודה שתיים נמשיך.\n"),
    ),
    ("spoken_lesson_refs", "prefixed", append(S01, "ראינו בשיעור ושלוש נקודה חמש.\n")),
    ("spoken_lesson_refs", "gendered", append(S01, "ראו שישה נקודה שבעה.\n")),
    ("spoken_lesson_refs", "hyphen-ordinal", append(S01, "בשיעור הבא, חמישי-ארבע.\n")),
    (
        "spoken_lesson_refs",
        "punctuation-does-not-hide",
        append(S01, "ראו שלוש נקודה שתיים, ואז נמשיך.\n"),
    ),
    (
        "spoken_lesson_refs",
        "stale-allowlist",
        replace(S01, "גרסה שש נקודה שש יצאה השנה.\n", ""),
    ),
    # course_name_denylist
    (
        "course_name_denylist",
        "course-name",
        append(S01, "ברוכים הבאים בקורס AI Engineer.\n"),
    ),
    (
        "course_name_denylist",
        "bold-course-line",
        replace(E01, "**קורס:** Demo", "**קורס:** AI Engineer"),
    ),
    (
        "course_name_denylist",
        "anon-key",
        append(E01, "NEXT_PUBLIC_SUPABASE_ANON_KEY=xyz\n"),
    ),
    # tutor_refs
    (
        "tutor_refs",
        "missing-route",
        append(LEARN, "| gone | Read `.claude/commands/learn/missing.md` |\n"),
    ),
    ("tutor_refs", "missing-bare-read", append(TEACHING, "Then Read `missing.md`.\n")),
    # settings_json
    (
        "settings_json",
        "powershell",
        overwrite(
            SETTINGS, '{"hooks": {"Stop": [{"command": "PowerShell -File x.ps1"}]}}\n'
        ),
    ),
    ("settings_json", "invalid-json", overwrite(SETTINGS, "{\n")),
    # relative_links
    (
        "relative_links",
        "missing-target",
        append("README.md", "\nSee [missing](docs/missing.md).\n"),
    ),
    (
        "relative_links",
        "root-absolute-missing",
        append("docs/guide.md", "[gone](/docs/gone.md)\n"),
    ),
    # clean_slate_no_delete
    (
        "clean_slate_no_delete",
        "rm-rf",
        replace(
            SETUP, 'mkdir "$dest" || exit 1', 'rm -rf "$dest"; mkdir "$dest" || exit 1'
        ),
    ),
    (
        "clean_slate_no_delete",
        "remove-item",
        replace(SETUP, "Move-Item -LiteralPath", "Remove-Item -LiteralPath"),
    ),
    (
        "clean_slate_no_delete",
        "remove-item-lower",
        replace(SETUP, "Move-Item -LiteralPath", "remove-item -LiteralPath"),
    ),
    (
        "clean_slate_no_delete",
        "dotnet-delete",
        replace(
            SETUP,
            "New-Item -ItemType",
            "[IO.Directory]::Delete($dest); New-Item -ItemType",
        ),
    ),
    (
        "clean_slate_no_delete",
        "end-marker-missing",
        replace(SETUP, "<!-- CLEAN-SLATE:END -->\n", ""),
    ),
    # lesson_files
    ("lesson_files", "missing-exercises", delete(E02)),
    # teaching_step5
    ("teaching_step5", "step5-removed", replace(TEACHING, "Step 5", "Step 4")),
]


@pytest.mark.parametrize(
    ("check", "mutate"),
    [(c, m) for c, _, m in SEEDS],
    ids=[f"{c}-{i}" for c, i, _ in SEEDS],
)
def test_seeded_regression_fails_only_its_check(
    good_tree: Path, check: str, mutate
) -> None:
    mutate(good_tree)
    results = run_all(good_tree)
    assert results[check], f"{check} did not catch the seed"
    others = {name: found for name, found in results.items() if name != check and found}
    assert not others, f"other checks fired: {others}"


NEGATIVES = [
    (
        "root-absolute-link",
        append("docs/guide.md", "[home](/README.md)\n"),
    ),
    ("job-title", append(S01, "תפקיד ה-AI Engineer מבוקש. AI Engineer הוא תפקיד.\n")),
    (
        "archive-denied",
        append(
            "courses/_archive/old/lessons/00-x/0.1-x/0.1_script.txt",
            "בקורס AI Engineer\n[x](missing.md)\n",
        ),
    ),
    (
        "old-b-denied",
        append(
            f"{LESSONS}/03-final/old_B-x.md",
            "בקורס AI Engineer\nNEXT_PUBLIC_SUPABASE_ANON_KEY\n[x](missing.md)\n",
        ),
    ),
    ("home-path", append(TEACHING, "Save to `~/skill-tutor-tutorials/progress/`.\n")),
    ("local-only", append(TEACHING, "Never touch `.claude/settings.local.json`.\n")),
    ("skill-dir", append(TEACHING, "Read `${CLAUDE_SKILL_DIR}/x.md` later.\n")),
    ("already", append(TEACHING, "If it was already `x.md`, skip it.\n")),
    ("load-from", append(TEACHING, "Load the list from `projects.md`.\n")),
    (
        "http-and-anchor",
        append(
            "README.md",
            "[a](https://example.com) [b](http://example.com) [c](#usage) [d](mailto:a@b.c)\n",
        ),
    ),
    (
        "fenced-link",
        append(
            "README.md",
            "\n```\n[x](missing.md)\n```\n\n````md\n```\n[y](missing.md)\n```\n````\n",
        ),
    ),
    ("inline-code-link", append("README.md", "Write `[x](missing.md)` to link.\n")),
    (
        "punctuation",
        append(S02, "ראינו אפס נקודה אחת, אפס נקודה אחת: ואפס נקודה אחת.\n"),
    ),
    (
        "allowlisted-and-existing",
        append(S01, "שוב גרסה שש נקודה שש, ובשיעור אפס נקודה שתיים.\n"),
    ),
    (
        "verbs-inside-words",
        replace(
            SETUP,
            "## 0. Clean slate\n",
            "## 0. Clean slate\n\nConfirm the model, then perform the move.\n",
        ),
    ),
    ("rm-outside-markers", append(SETUP, "\nThe old flow ran `rm -rf` here.\n")),
    ("missing-settings", delete(SETTINGS)),
]


@pytest.mark.parametrize(
    "mutate", [m for _, m in NEGATIVES], ids=[i for i, _ in NEGATIVES]
)
def test_must_pass_negative(good_tree: Path, mutate) -> None:
    mutate(good_tree)
    assert run_all(good_tree) == {name: [] for name in fixture_checks()}


def git_repo(path: Path):
    return partial(subprocess.run, cwd=path, check=True, capture_output=True)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_git_tree_ignores_untracked_files(good_tree: Path, tmp_path_factory) -> None:
    root = tmp_path_factory.mktemp("git") / "repo"
    shutil.copytree(good_tree, root)
    git = git_repo(root)
    git(["git", "init", "-q"])
    git(["git", "add", "-A"])
    (root / "broken.md").write_text("[x](missing.md)\n", encoding="utf-8")
    assert vs.check_relative_links(root) == []
    git(["git", "add", "broken.md"])
    assert vs.check_relative_links(root) == [
        "broken.md:1: [relative_links] link target 'missing.md' does not exist"
    ]


def windows_saved(rel: str):
    """Rewrite ``rel`` the way a Windows editor may save it: BOM + CRLF."""

    def mutate(root: Path) -> None:
        path = root / rel
        text = path.read_text(encoding="utf-8").replace("\n", "\r\n")
        path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))

    return mutate


# Review Focus: inputs the spec implies but its seeds never exercise.
H1_FIRST = "# תרגילים - שיעור 2.1: נושא\n\n- **שיעור:** 2.1 - נושא\n"
REVIEW_FOCUS = [
    ("bom-crlf-h1-on-line-1", chain(overwrite(E21, H1_FIRST), windows_saved(E21))),
    ("bom-crlf-script", windows_saved(S21)),
    ("bom-crlf-course-md", windows_saved(COURSE)),
    ("ascii-hyphen-range", replace(COURSE, "| 0.1–0.2 |", "| 0.1-0.2 |")),
    (
        "percent-encoded-link",
        chain(
            append("docs/my notes.md", "# Notes\n"),
            append("README.md", "[notes](docs/my%20notes.md)\n"),
        ),
    ),
]


@pytest.mark.parametrize(
    "mutate", [m for _, m in REVIEW_FOCUS], ids=[i for i, _ in REVIEW_FOCUS]
)
def test_review_focus_passes(good_tree: Path, mutate) -> None:
    mutate(good_tree)
    assert run_all(good_tree) == {name: [] for name in fixture_checks()}


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_git_tree_hebrew_file_name(good_tree: Path, tmp_path_factory) -> None:
    root = tmp_path_factory.mktemp("heb") / "repo"
    shutil.copytree(good_tree, root)
    append("docs/מדריך.md", "[back](../README.md)\n")(root)
    append("README.md", "[guide](docs/מדריך.md)\n")(root)
    git = git_repo(root)
    git(["git", "init", "-q"])
    git(["git", "add", "-A"])
    assert Path("docs/מדריך.md") in vs.repo_files(root, "**/*.md")
    assert run_all(root) == {name: [] for name in fixture_checks()}


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_worktree_git_file(good_tree: Path, tmp_path_factory) -> None:
    base = tmp_path_factory.mktemp("wt")
    main = base / "main"
    shutil.copytree(good_tree, main)
    git = git_repo(main)
    git(["git", "init", "-q"])
    git(["git", "add", "-A"])
    ident = [
        "-c", "user.name=t",
        "-c", "user.email=t@example.com",
        "-c", "commit.gpgsign=false",
        "-c", "core.hooksPath=/dev/null",
    ]
    git(["git", *ident, "commit", "-q", "-m", "init"])
    git(["git", "worktree", "add", "-q", str(base / "wt")])
    wt = base / "wt"
    assert (wt / ".git").is_file()
    (wt / "untracked.md").write_text("[x](missing.md)\n", encoding="utf-8")
    assert run_all(wt) == {name: [] for name in fixture_checks()}


def clean_slate_block(heading: str) -> str:
    """The first bash block under ``heading`` in the real setup.md."""
    text = (REPO_ROOT / SETUP).read_text(encoding="utf-8")
    section = text.split(heading, 1)[1]
    return section.split("```bash\n", 1)[1].split("```", 1)[0]


def clean_slate_home(tmp_path: Path, *, link_commands: bool):
    """A fake HOME with learner data, and a fake repo holding tutor files.

    With ``link_commands``, ``~/.claude/commands`` is a symlink into the repo
    (a tester who made the repo's commands global that way). Otherwise it is a
    real folder with a real old global install.
    """
    home, repo = tmp_path / "home", tmp_path / "repo"
    (home / "skill-tutor-tutorials").mkdir(parents=True)
    (home / "skill-tutor-tutorials" / "settings.json").write_text("{}", encoding="utf-8")
    (repo / ".claude" / "commands" / "learn").mkdir(parents=True)
    (repo / ".claude" / "commands" / "learn.md").write_text("# router\n", encoding="utf-8")
    (repo / ".claude" / "commands" / "learn" / "x.md").write_text("# x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    (home / ".claude").mkdir()
    if link_commands:
        (home / ".claude" / "commands").symlink_to(repo / ".claude" / "commands")
    else:
        shutil.copytree(repo / ".claude" / "commands", home / ".claude" / "commands")
    return home, repo


def run_clean_slate(block: str, home: Path, repo: Path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(home)}
    return subprocess.run(
        ["bash", "-c", block],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


needs_bash_git = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("git") is None,
    reason="bash and git are required",
)


@needs_bash_git
def test_clean_slate_move_leaves_the_repo_alone(tmp_path: Path) -> None:
    """RV-final M2: a symlinked ~/.claude/commands must not drag the repo's files away."""
    home, repo = clean_slate_home(tmp_path, link_commands=True)
    result = run_clean_slate(clean_slate_block("### Step 3"), home, repo)
    assert result.returncode == 0, result.stderr
    assert (repo / ".claude" / "commands" / "learn.md").is_file()
    assert (repo / ".claude" / "commands" / "learn" / "x.md").is_file()
    assert not (home / "skill-tutor-tutorials").exists()
    (backup,) = home.glob("skill-tutor-tutorials-backup-*")
    assert (backup / "skill-tutor-tutorials" / "settings.json").is_file()
    assert not (backup / "commands" / "learn.md").exists()
    assert "STILL PRESENT" not in result.stdout


@needs_bash_git
def test_clean_slate_move_takes_a_real_global_install(tmp_path: Path) -> None:
    home, repo = clean_slate_home(tmp_path, link_commands=False)
    result = run_clean_slate(clean_slate_block("### Step 3"), home, repo)
    assert result.returncode == 0, result.stderr
    (backup,) = home.glob("skill-tutor-tutorials-backup-*")
    assert (backup / "commands" / "learn.md").is_file()
    assert (backup / "commands" / "learn" / "x.md").is_file()
    assert not (home / ".claude" / "commands" / "learn.md").exists()
    assert (repo / ".claude" / "commands" / "learn.md").is_file()


@needs_bash_git
def test_clean_slate_find_skips_paths_inside_the_repo(tmp_path: Path) -> None:
    home, repo = clean_slate_home(tmp_path, link_commands=True)
    result = run_clean_slate(clean_slate_block("### Step 1"), home, repo)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert f"FOUND {home}/skill-tutor-tutorials" in lines
    assert sum(line.startswith("SKIP ") for line in lines) == 2
    assert not [line for line in lines if line.startswith("FOUND ") and "commands" in line]


def test_repo_files_without_git_falls_back_to_walking(
    good_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RV-final L4: a .git folder but no git executable must not crash the lints."""
    (good_tree / ".git").mkdir()

    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(vs.subprocess, "run", no_git)
    assert Path("README.md") in vs.repo_files(good_tree, "**/*.md")


def test_real_repo_passes() -> None:
    findings = [f for check in vs.CHECKS for f in check(REPO_ROOT)]
    assert not findings, f"{len(findings)} finding(s):\n" + "\n".join(findings)
