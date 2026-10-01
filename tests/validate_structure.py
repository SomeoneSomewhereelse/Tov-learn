"""Structural checks for Tov-learn, run through pytest.

Each check is ``check_<name>(root: Path) -> list[str]`` and returns findings
formatted ``path:line: [name] message``. An empty list means the check passes.
``CHECKS`` lists every check. This module does no work at import time.

Contributors run: ``uv run ruff check -q && uv run pytest -q``
"""

import json
import re
import subprocess
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

# --- shared helpers ---------------------------------------------------------

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}


def repo_files(root: Path, pattern: str) -> list[Path]:
    """Repo-relative paths matching ``pattern`` (``PurePath.full_match`` syntax).

    Uses ``git ls-files -z`` when ``root/.git`` exists (a directory in a clone,
    a file in a worktree), so local runs see what CI sees. Tracked entries
    missing on disk are skipped. Otherwise (no .git, no git executable, or a
    .git that git refuses to read) it walks the filesystem.
    """
    tracked = None
    if (root / ".git").exists():
        cmd = ["git", "-C", str(root), "ls-files", "-z"]
        try:
            out = subprocess.run(cmd, capture_output=True, check=True).stdout
            tracked = [PurePosixPath(p) for p in out.decode("utf-8").split("\0") if p]
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass  # git is missing, or refuses this .git: walk instead
    if tracked is not None:
        rels = [r for r in tracked if (root / r).is_file()]
    else:
        rels = []
        for p in root.rglob("*"):
            rel = p.relative_to(root)
            if p.is_file() and not SKIP_DIRS.intersection(rel.parts):
                rels.append(PurePosixPath(rel.as_posix()))
    return sorted(Path(r) for r in rels if r.full_match(pattern))


def finding(check: str, rel: Path, line: int, message: str) -> str:
    return f"{rel.as_posix()}:{line}: [{check}] {message}"


def read(root: Path, rel: Path) -> str:
    """Read UTF-8 text; ``utf-8-sig`` drops a BOM that Windows editors add."""
    return (root / rel).read_text(encoding="utf-8-sig")


def in_course_scope(rel: Path) -> bool:
    """Under ``courses/<course>/``, but not ``courses/_archive/`` or ``old_B*``."""
    parts = rel.parts
    return (
        len(parts) >= 3
        and parts[0] == "courses"
        and parts[1] != "_archive"
        and not rel.name.startswith("old_B")
    )


def course_files(root: Path, suffix: str) -> list[Path]:
    files = repo_files(root, f"courses/**/*{suffix}")
    return [r for r in files if in_course_scope(r)]


def course_dirs(root: Path) -> list[Path]:
    courses = root / "courses"
    if not courses.is_dir():
        return []
    return sorted(d for d in courses.iterdir() if d.is_dir() and d.name != "_archive")


LESSON_DIR = re.compile(r"^(\d+)\.(\d+)-")


def lesson_key(number: str) -> tuple[int, int]:
    major, minor = number.split(".")
    return int(major), int(minor)


def lesson_dirs(course: Path) -> list[Path]:
    """Every folder at ``lessons/<module>/<lesson>/``."""
    lessons = course / "lessons"
    if not lessons.is_dir():
        return []
    modules = sorted(p for p in lessons.iterdir() if p.is_dir())
    return [d for m in modules for d in sorted(m.iterdir()) if d.is_dir()]


def lesson_folders(course: Path) -> dict[str, Path]:
    """Lesson number ("2.1") -> folder, for folders named ``<X.Y>-*``."""
    found = {}
    for d in lesson_dirs(course):
        if m := LESSON_DIR.match(d.name):
            found[f"{m[1]}.{m[2]}"] = d
    return found


def folder_number(rel: Path) -> str | None:
    m = LESSON_DIR.match(rel.parent.name)
    return f"{m[1]}.{m[2]}" if m else None


# Spoken Hebrew digits, as the scripts use them ("שתיים נקודה אחת" = 2.1).
DIGIT_WORDS = {
    "אפס": 0,
    "אחת": 1, "אחד": 1,
    "שתיים": 2, "שניים": 2, "שתים": 2,
    "שלוש": 3, "שלושה": 3,
    "ארבע": 4, "ארבעה": 4,
    "חמש": 5, "חמישה": 5,
    "שש": 6, "שישה": 6,
    "שבע": 7, "שבעה": 7,
    "שמונה": 8,
    "תשע": 9, "תשעה": 9,
}  # fmt: skip
ORDINALS = {
    "ראשון": 1, "שני": 2, "שלישי": 3, "רביעי": 4,
    "חמישי": 5, "שישי": 6, "שביעי": 7, "שמיני": 8,
}  # fmt: skip
PREFIXES = "ובלשהמכ"


def digit_value(word: str) -> int | None:
    """Map a spoken digit, stripping at most one leading prefix letter."""
    if word in DIGIT_WORDS:
        return DIGIT_WORDS[word]
    if len(word) > 1 and word[0] in PREFIXES:
        return DIGIT_WORDS.get(word[1:])
    return None


# --- checks -----------------------------------------------------------------

ROW = re.compile(r"^\|(.+)\|$")


def table_rows(lines: list[str], heading: str) -> list[tuple[int, list[str]]]:
    """Data rows (1-based line, cells) of the table under the ``heading`` title."""
    rows, inside = [], False
    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            if inside:
                break
            inside = line.lstrip("#").strip() == heading
        elif inside and (m := ROW.match(line.strip())):
            cells = [c.strip() for c in m[1].split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                rows.append((i, cells))
    return rows


def module_range(folders: dict[str, Path], module: Path) -> str:
    nums = sorted((n for n, d in folders.items() if d.parent == module), key=lesson_key)
    return f"{nums[0]}–{nums[-1]}" if nums else "—"


def check_course_md(root: Path) -> list[str]:
    out = []
    for course in course_dirs(root):
        rel = (course / "COURSE.md").relative_to(root)
        if not (root / rel).is_file():
            continue
        lines = read(root, rel).splitlines()
        folders = lesson_folders(course)
        rows = [
            (i, cells[0])
            for i, cells in table_rows(lines, "רשימת שיעורים")
            if re.fullmatch(r"\d+\.\d+", cells[0])
        ]
        listed = [n for _, n in rows]
        head = next((i for i, ln in enumerate(lines, 1) if "רשימת שיעורים" in ln), 1)
        for n in sorted(set(folders) - set(listed), key=lesson_key):
            out.append(finding("course_md", rel, head, f"lesson {n} has no row"))
        for i, n in rows:
            if n not in folders:
                out.append(finding("course_md", rel, i, f"row {n} has no folder"))
        if listed != sorted(listed, key=lesson_key):
            msg = f"rows out of numeric order: {', '.join(listed)}"
            out.append(finding("course_md", rel, head, msg))
        for i, cells in table_rows(lines, "מודולים"):
            m = re.search(r"`([^`]+)`", cells[1]) if len(cells) >= 3 else None
            if not m:
                continue
            module = course / "lessons" / m[1].rstrip("/")
            if not module.is_dir():
                out.append(finding("course_md", rel, i, f"no folder {m[1]}"))
            elif cells[2].replace("-", "–") != (want := module_range(folders, module)):
                msg = f"range {cells[2]!r} for {m[1]}, expected {want!r}"
                out.append(finding("course_md", rel, i, msg))
    return out


def check_slide_markers(root: Path) -> list[str]:
    out = []
    for rel in course_files(root, "_script.txt"):
        lines = read(root, rel).splitlines()
        count = sum(ln.count("[מעבר שקף]") for ln in lines)
        if count < 5:
            msg = f"{count} [מעבר שקף] markers, need at least 5"
            out.append(finding("slide_markers", rel, 1, msg))
        english = [i for i, ln in enumerate(lines, 1) if "[SLIDE TRANSITION]" in ln]
        if english:
            msg = f"{len(english)} [SLIDE TRANSITION] line(s); use [מעבר שקף]"
            out.append(finding("slide_markers", rel, english[0], msg))
    return out


NUMERIC_LESSON = re.compile(r"(?:שיעור|Lesson)\s+(\d+\.\d+)")
SPELLED_LESSON = re.compile(r"שיעור\s+([א-ת]+)\s+נקודה\s+([א-ת]+)")
BOLD_LESSON = re.compile(r"\*\*שיעור:\*\*\s*(\d+\.\d+)?")


def exercise_headers(rel: Path, lines: list[str], want: str) -> list[str]:
    out = []
    h1 = next(((i, ln) for i, ln in enumerate(lines, 1) if ln.startswith("# ")), None)
    m = re.search(r"שיעור\s+(\d+\.\d+)", h1[1]) if h1 else None
    if not m or m[1] != want:
        msg = f"first heading names {m[1] if m else 'no lesson'}, folder is {want}"
        out.append(finding("header_numbers", rel, h1[0] if h1 else 1, msg))
    for i, ln in enumerate(lines, 1):
        if (b := BOLD_LESSON.search(ln)) and b[1] != want:
            msg = f"**שיעור:** names {b[1] or 'no lesson'}, folder is {want}"
            out.append(finding("header_numbers", rel, i, msg))
    return out


def script_opening(rel: Path, lines: list[str], want: str) -> list[str]:
    out = []
    opening = [(i, ln) for i, ln in enumerate(lines, 1) if ln.strip()][:3]
    for i, ln in opening:
        for m in NUMERIC_LESSON.finditer(ln):
            if m[1] != want:
                msg = f"opening names {m[1]}, folder is {want}"
                out.append(finding("header_numbers", rel, i, msg))
        for m in SPELLED_LESSON.finditer(ln):
            x, y = DIGIT_WORDS.get(m[1]), DIGIT_WORDS.get(m[2])
            if x is None or y is None:
                msg = f"unmapped spoken number {m[0]!r}"
                out.append(finding("header_numbers", rel, i, msg))
            elif f"{x}.{y}" != want:
                msg = f"opening names {x}.{y}, folder is {want}"
                out.append(finding("header_numbers", rel, i, msg))
    return out


def check_header_numbers(root: Path) -> list[str]:
    out = []
    for rel in course_files(root, "_exercises.md"):
        if want := folder_number(rel):
            out += exercise_headers(rel, read(root, rel).splitlines(), want)
    for rel in course_files(root, "_script.txt"):
        if want := folder_number(rel):
            out += script_opening(rel, read(root, rel).splitlines(), want)
    return out


# (file-name glob, exact phrase): spelled numbers that are not lesson numbers.
SPOKEN_ALLOWLIST = (
    ("0.3_script.txt", "ושבע נקודה אחת אחוז"),
    ("1.1_script.txt", "ארבע נקודה שש"),
    ("1.1_script.txt", "שש נקודה שש מיליארד"),
    ("1.5_script.txt", "שישה נקודה שישה מיליארד"),
    ("2.1_script.txt", "שתיים נקודה אפס"),
    ("2.5_script.txt", "שלוש נקודה שלוש עשרה"),
    ("2.5_script.txt", "שלוש נקודה ארבע עשרה"),
    ("2.5_script.txt", "ארבע נקודה שבע"),
)
SPOKEN_DOT = re.compile(r"(?<![א-ת])([א-ת]+)\s+נקודה\s+([א-ת]+)")
HYPHEN_ORDINAL = re.compile(r"(" + "|".join(ORDINALS) + r")-([א-ת]+)")


def spoken_refs(line: str) -> list[tuple[re.Match, str]]:
    """Every spelled lesson-number form in ``line``, with its ``X.Y``."""
    refs = []
    for m in SPOKEN_DOT.finditer(line):
        x, y = digit_value(m[1]), digit_value(m[2])
        if x is not None and y is not None:
            refs.append((m, f"{x}.{y}"))
    for m in HYPHEN_ORDINAL.finditer(line):
        if (y := digit_value(m[2])) is not None:
            refs.append((m, f"{ORDINALS[m[1]]}.{y}"))
    return refs


def check_spoken_lesson_refs(root: Path, allowlist=SPOKEN_ALLOWLIST) -> list[str]:
    out = []
    files = course_files(root, "_script.txt") + course_files(root, "_exercises.md")
    texts = {rel: read(root, rel) for rel in files}
    for glob, phrase in allowlist:
        matching = [rel for rel in files if fnmatch(rel.name, glob)]
        if matching and not any(phrase in texts[rel] for rel in matching):
            msg = f"stale allowlist entry ({glob!r}, {phrase!r})"
            out.append(finding("spoken_lesson_refs", matching[0], 1, msg))
    lessons = {c.name: set(lesson_folders(c)) for c in course_dirs(root)}
    for rel in files:
        existing = lessons.get(rel.parts[1], set())
        phrases = [p for g, p in allowlist if fnmatch(rel.name, g)]
        for i, ln in enumerate(texts[rel].splitlines(), 1):
            spans = [
                (a.start(), a.end())
                for p in phrases
                for a in re.finditer(re.escape(p), ln)
            ]
            for m, number in spoken_refs(ln):
                allowed = any(s <= m.start() and m.end() <= e for s, e in spans)
                if number not in existing and not allowed:
                    msg = f"{m[0]!r} names lesson {number}, which does not exist"
                    out.append(finding("spoken_lesson_refs", rel, i, msg))
    return out


DENYLIST = (
    re.compile(r"קורס\s+(ה-)?AI Engineer", re.IGNORECASE),
    re.compile(r"\*\*קורס:\*\*\s*AI Engineer", re.IGNORECASE),
    re.compile(r"AI Engineer course", re.IGNORECASE),
    re.compile(r"NEXT_PUBLIC_SUPABASE_ANON_KEY"),
)


def check_course_name_denylist(root: Path) -> list[str]:
    out = []
    for rel in course_files(root, ".md") + course_files(root, ".txt"):
        for i, ln in enumerate(read(root, rel).splitlines(), 1):
            for pattern in DENYLIST:
                if m := pattern.search(ln):
                    msg = f"denied string {m[0]!r}"
                    out.append(finding("course_name_denylist", rel, i, msg))
    return out


LOCAL_ONLY = {".claude/settings.local.json"}
BACKTICKED = re.compile(r"`([^`\n]+)`")
READ_BARE = re.compile(r"\b(?:read|load)\b\s+`([^`/\s]+\.md)`", re.IGNORECASE)
PLACEHOLDER = re.compile(r"[\[{*]|X\.Y")


def check_tutor_refs(root: Path) -> list[str]:
    out = []
    for rel in repo_files(root, ".claude/**/*.md"):
        for i, ln in enumerate(read(root, rel).splitlines(), 1):
            for m in BACKTICKED.finditer(ln):
                path = m[1].strip()
                if not path.startswith((".claude/", "courses/")):
                    continue
                if PLACEHOLDER.search(path) or path in LOCAL_ONLY:
                    continue
                if not (root / path).exists():
                    out.append(
                        finding("tutor_refs", rel, i, f"`{path}` does not exist")
                    )
            for m in READ_BARE.finditer(ln):
                if PLACEHOLDER.search(m[1]) or (root / rel.parent / m[1]).exists():
                    continue
                msg = f"`{m[1]}` not found next to {rel.name}"
                out.append(finding("tutor_refs", rel, i, msg))
    return out


def check_settings_json(root: Path) -> list[str]:
    rel = Path(".claude/settings.json")
    if not (root / rel).is_file():
        return []
    text = read(root, rel)
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        return [finding("settings_json", rel, e.lineno, f"invalid JSON: {e.msg}")]
    msg = "mentions powershell; hooks must run on every OS"
    lines = enumerate(text.splitlines(), 1)
    return [
        finding("settings_json", rel, i, msg)
        for i, ln in lines
        if "powershell" in ln.lower()
    ]


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
MD_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")


def prose_lines(text: str) -> list[str]:
    """Lines with fenced blocks blanked and inline code spans removed.

    A fence closes only on a line of the same character, at least as long as
    the opener, with nothing after it (CommonMark), so ```` blocks can hold ```.
    """
    out, fence = [], None
    for ln in text.splitlines():
        m = FENCE.match(ln)
        if fence is None and not m:
            out.append(INLINE_CODE.sub("", ln))
            continue
        if fence is None:
            fence = m[1]
        elif m and m[1][0] == fence[0] and len(m[1]) >= len(fence) and not m[2].strip():
            fence = None
        out.append("")
    return out


def check_relative_links(root: Path) -> list[str]:
    out = []
    for rel in repo_files(root, "**/*.md"):
        if "_archive" in rel.parts or rel.name.startswith("old_B"):
            continue
        for i, ln in enumerate(prose_lines(read(root, rel)), 1):
            for m in MD_LINK.finditer(ln):
                target = m[1]
                if target.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                path = unquote(target.split("#", 1)[0])
                # "/x.md" is relative to the repo root, as on GitHub
                base = root if path.startswith("/") else root / rel.parent
                if path and not (base / path.lstrip("/")).exists():
                    msg = f"link target {target!r} does not exist"
                    out.append(finding("relative_links", rel, i, msg))
    return out


CLEAN_BEGIN = "<!-- CLEAN-SLATE:BEGIN"
CLEAN_END = "<!-- CLEAN-SLATE:END -->"
DELETE_VERBS = re.compile(
    r"\brm\b|\brmdir\b|\bdel\b|\berase\b|\brd\b|\bri\b|Remove-Item|\bunlink\b"
    r"|-delete\b|rmtree|::Delete\(",
    re.IGNORECASE,
)


def check_clean_slate_no_delete(root: Path) -> list[str]:
    """TEMPORARY: removed with the CLEAN-SLATE section at the gate (PRD D10)."""
    rel = Path(".claude/commands/learn/setup.md")
    lines = read(root, rel).splitlines() if (root / rel).is_file() else []
    begin = next((i for i, ln in enumerate(lines) if CLEAN_BEGIN in ln), None)
    end = next((i for i, ln in enumerate(lines) if CLEAN_END in ln), None)
    if begin is None or end is None or end < begin:
        msg = "CLEAN-SLATE:BEGIN/END markers missing or out of order"
        return [finding("clean_slate_no_delete", rel, 1, msg)]
    return [
        finding("clean_slate_no_delete", rel, i + 1, f"delete command {m[0]!r}")
        for i in range(begin + 1, end)
        for m in DELETE_VERBS.finditer(lines[i])
    ]


def check_lesson_files(root: Path) -> list[str]:
    out = []
    for course in course_dirs(root):
        for d in lesson_dirs(course):
            for pattern in ("*_script.txt", "*_exercises.md"):
                if not list(d.glob(pattern)):
                    rel = d.relative_to(root)
                    out.append(finding("lesson_files", rel, 1, f"missing {pattern}"))
    return out


def check_teaching_step5(root: Path) -> list[str]:
    rel = Path(".claude/commands/learn/teaching.md")
    if (root / rel).is_file() and "Step 5" in read(root, rel):
        return []
    return [finding("teaching_step5", rel, 1, "missing 'Step 5 — End of Lesson'")]


CHECKS = (
    check_course_md,
    check_slide_markers,
    check_header_numbers,
    check_spoken_lesson_refs,
    check_course_name_denylist,
    check_tutor_refs,
    check_settings_json,
    check_relative_links,
    check_clean_slate_no_delete,
    check_lesson_files,
    check_teaching_step5,
)
