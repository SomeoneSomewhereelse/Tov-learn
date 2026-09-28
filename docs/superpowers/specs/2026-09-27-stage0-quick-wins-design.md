# Stage 0 — Quick-Win PR: Design Spec

**Date:** 2026-09-27 · **Revision:** 3 (2026-09-28), after two independent reviews (§10) · **Status:** approved in brainstorming; pending the user's review of revision 3
**Parent:** `docs/prds/project-redesign-2026-09-25.md` (the PRD). References such as "D2 item 5", "§3" and "R14" point there. "Review §2.x" points to `docs/reviews/project-review-2026-09-24.md`. "RV-…" and "RV2-…" point to the spec reviews (§10).
**Baseline:** `master` at `290af75` (= `origin/master`, after #12 and #13 were merged on 2026-09-28). Its tree is identical to the earlier local `d04ca2a` (tree `5bf8edb`), so every line number below refers to that tree.
**Scope:** Stage 0 only:
- D2's 16 items
- the Stage 0 rows of the D7c lint table
- the three §6 rows assigned to the Stage 0 spec, plus the Dependabot row ("any CI-touching spec")
- §3's Stage 0 "done when"
- the gaps and review findings absorbed in §2 and §10

`courses/_archive/` is out of scope throughout.

---

## 1. Outcome and constraints

**Outcome:** one PR against `master` that:
- fixes what testers hit now: wrong course name, missing lessons, a broken hook, an unsafe lab, deprecated Supabase keys, stale lesson cross-references
- adds the first CI lints, each proven by a seeded regression
- moves the repo's CI to `node24` actions, on uv + pytest + ruff

**Constraints:**
- Fresh installs only, and testers only until the first-cohort gate (PRD Assumptions, D10).
- **Contributor tooling:**
  - **uv is a hard requirement for contributors.** The only supported entry point is `uv run pytest -q && uv run ruff check -q`.
  - **This does not apply to learners.**
    - Learner-facing docs (README) never mention uv. CLAUDE.md, which also loads into learner sessions, labels its test section "contributors only".
    - The PRD D8b learner CLI must not inherit uv.
    - The repo root carries **no `.python-version`** file, so nothing pins a learner's `python` (RV2-M5). §9 records this for G, S2a and 1c.
- Edits are minimal and mechanical. Every rewrite stays with its Stage 1 slice.
- **One-unit-per-file rule (D10).** Stage 0 touches `learn.md` and all 15 `learn/*.md` sub-modules. All 15 get frontmatter. Four also get body edits: `setup.md`, `security.md`, `project.md` and `resume.md`. `learn.md` gets body edits too. No other unit is open on these files.
- **Workspace:**
  - Before creating the worktree, confirm `git rev-parse master` equals `git rev-parse origin/master` (RV2-H1).
  - Then create a manual worktree: `git worktree add ../Tov-learn-stage0 -b fix/stage0-quick-wins master`.
  - Never use `EnterWorktree`. uv creates the worktree's own `.venv`.
  - Commit or push only when the user asks.

---

## 2. Decisions made in this spec

| # | Decision | Reason |
|---|---|---|
| S1 | **Three PRD gaps are absorbed** (user-approved):<br>• **G1:** leaked preambles also at `2.3`/`2.6_exercises.md:1`<br>• **G2:** global install also at `README.md:202`, `CONTRIBUTING.md:61` and `CLAUDE.md:14,75`<br>• **G4:** `resume.md:23,38,50,74` still offers the final project | Same defect class; the D10 docs rule |
| S2 | **Hebrew aliases:**<br>• `עצור`/`סיום` = stop<br>• `בוחן`/`בוחן מלא` = quiz me / quiz me full<br>• `המשך` = continue<br>"בחן אותי" **stays diagnostic** | "בחן אותי" already means diagnostic (`learn.md:102`, `teaching.md:144`, `setup.md:225`) |
| S3 | **The 1.3 hook exercise guards a fake secret against *reading*.**<br>• PreToolUse, `matcher: "Read"`, `if: "Read(secret-demo.txt)"`, exit 2<br>• a live `cat` bypass shows how fragile hooks are | Nothing is written or deleted even if the guard fails. The focus is hooks in general and their fragility |
| S4 | **Clean-slate moves, never deletes** | "Backs up before any delete" holds by construction (§8) |
| S5 | **Clean-slate checks three exact paths, with no globs** | `learn*` would match unrelated personal commands |
| S6 | **Lints are `check_*` functions in `tests/validate_structure.py`, tested with pytest; ruff lints the Python; everything runs through uv** | Permanent seeded regressions; a pinned toolchain (user decision) |
| S7 | **The route/reference lint scans only the tutor files** (`.claude/**/*.md`) | Exercises cite `.claude/…` paths in the learner's lab project |
| S8 | **Manual done-when checks are run by the user interactively and recorded in the PR** | Headless `claude -p` can't exercise `AskUserQuestion` or show hook-error notices reliably |
| S9 | **`validate.yml` gets `permissions: contents: read`** | Least privilege |
| S10 | **A new unit N (numbering contract) is proposed between F and 1a** (§9) | Renumbering churn comes before any later stage |
| S11 | **`changes.md` gets one final `# Changes — fix/stage0-quick-wins branch` section**, in the current format, written once. The branch is named `fix/stage0-quick-wins` | The D10 docs rule. It follows the typed names of the most recent merged PRs (#11–#13, all `fix/…`). F converts everything to Keep-a-Changelog |
| S12 | **uv is a hard requirement for contributors only** (§1). The validator is a library module; `test_real_repo_passes` reports the findings | One supported entry point (user decision) |
| S13 | **Python is pinned to 3.14 in `pyproject.toml`** (`requires-python = ">=3.14,<3.15"`), and CI passes `python-version: "3.14"` to setup-uv. **There's no `.python-version` file** | The current release, supported to 2030-10-31 (user decision). A root `.python-version` could pin learners' `python` through pyenv (RV2-M5) |
| S14 | **Claude Code minimum is 2.1.176**, a floor, not an exact pin. It's stated in `1.3_exercises.md:8`, `1.3_script.txt:15` (spoken) and README Prerequisites (`:25`) and Requirements (`:208`). `/learn setup` warns below it, comparing (major, minor, patch) as numbers | 2.1.176 fixed `if` path matching for `Read(...)`, which S3 depends on (user decision) |
| S15 | **Dependabot is adopted now for `github-actions` only**, weekly. The `uv` ecosystem is deferred | Keeps the SHA pins fresh. Dependabot's documented uv version is v0.11 |
| S16 | **The Supabase MCP stays read-only.** `1.6_exercises.md:103` is rewritten, and the documented `/mcp` → Authenticate step is added (RV-H2, RV2-M3) | A read-only boundary for beginners. The exercise must not fail as written |
| S17 | **A new check, `spoken_lesson_refs`:** every spelled "W נקודה W" in course content must name an existing lesson, apart from an explicit phrase allowlist (RV2-M6) | Makes the out-of-window residue pass provably complete, and permanent until N replaces it |
| S18 | **Stage 0's `changes.md` commit also adds the missing sections for #12 and #13** (user decision) | They were merged without `changes.md` entries. Folding them in avoids a direct push to `master` and another conflict-prone edit |

---

## 3. Verified facts (2026-09-27/28)

Checked per D7b. "(reviewer)" marks facts verified by a spec review that are not re-checked here.

| Claim | Result | Source / method |
|---|---|---|
| `master` = `origin/master` = `290af75`; #12 and #13 merged 2026-09-28; tree identical to the earlier local `d04ca2a` | Confirmed | `git fetch`; `gh pr list`; `git diff master origin/master` empty; equal tree hashes |
| `actions/checkout` latest is **v7.0.1** = `3d3c42e5aac5ba805825da76410c181273ba90b1`, `using: node24` | Confirmed | GitHub API; `action.yml` at that SHA |
| `astral-sh/setup-uv` latest is **v10.2.0** = `c18668ad3cf93ea998bef934396af7bb5c839dc7`, `using: "node24"`, with `version`/`python-version`/`version-file` inputs | Confirmed | same method |
| `checkout@v4` / `setup-python@v5` declare `node20`; Node 20 retired on runners 2026-09-23 | Confirmed | `action.yml`; github.blog changelog |
| uv **0.12.19**; pytest **9.1.1** (Python ≥3.10); ruff **0.16.9**; `ruff check -q` prints diagnostics only | Confirmed | GitHub API; PyPI JSON; `ruff check --help` |
| Python 3.14 is current (3.14.7), supported to 2030-10-31 | Confirmed | endoflife.date |
| Dependabot supports `github-actions` and `uv` (the uv row lists v0.11); it updates the version comment beside a SHA pin | Confirmed / (reviewer) | docs.github.com (article-body API) |
| Only exit 2 blocks PreToolUse; exit 1 is non-blocking | Confirmed | hooks.md (raw) |
| Hook `if` added in **2.1.85**; `Read(.env)`-style path patterns match from **2.1.176** | Confirmed | anthropics/claude-code `CHANGELOG.md` (raw) |
| Shell-form hooks run with `sh -c` on macOS/Linux, Git Bash on Windows, PowerShell when Git Bash is missing; no controlling terminal; `permissionDecision: "ask"` exists | Confirmed | hooks.md (raw), "Shell form", `shell` field |
| A bare filename in `Read(…)` matches at any depth; Read deny rules cover `cat`/`head`/`tail` but not `grep -r` or scripts | Confirmed | permissions.md (raw) |
| A "Yes, and don't ask again" approval is saved to `.claude/settings.local.json`, resolved through worktrees to the main checkout | (reviewer) | permissions.md |
| Sandbox is OS-enforced; not native Windows | Confirmed | sandboxing.md (raw) |
| Same-name skills/commands: "personal over project" | Confirmed | skills.md (raw) |
| Routers before `c25e73c` (2026-05-25), e.g. `1bdbd50`, `acbf16c`, contain setup and the global install **inline**. From `c25e73c` on, the router `Read`s `.claude/commands/learn/setup.md` | Confirmed | `git show <sha>:.claude/commands/learn.md` |
| Supabase: anon/service_role keys deprecated by the end of 2026; `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` | Confirmed (rendered) | supabase.com/docs/guides/api/api-keys |
| Supabase hosted MCP: the `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?…"` command; the `read_only=true` / `project_ref=` parameters; then "In a regular terminal (not the IDE extension) run: `claude /mcp`. Select the "supabase" server, then "Authenticate"", a browser login with no PAT | Confirmed (rendered, 2026-09-28) | supabase.com/docs/guides/getting-started/mcp |
| `chattr +i` can be set or cleared only by the superuser | Confirmed | `man chattr` |
| `timingSafeEqual` throws on unequal lengths; command files accept `disable-model-invocation` | PRD §7 | nodejs `crypto.md`; skills.md |

**UNVERIFIED, deliberately not relied on:**
- macOS/Windows equivalents of `chmod 000` + `chattr +i` (→ 1a)
- Dependabot with uv 0.12 lockfiles (→ S15)
- the native-PowerShell hook variant (no Windows machine available)
- the 1.6 MCP flow end to end (needs a Supabase project)

The last two are listed as untested in the PR (§6).

---

## 4. Design

### 4.1 Work groups

| Group | Items | Files |
|---|---|---|
| **P: Platform/CI** | 2, 9, 15, S6/S12/S13/S15/S17 | `.github/workflows/validate.yml`, **new** `.github/dependabot.yml`, **new** `pyproject.toml`, **new** `uv.lock`, `.gitignore`, `tests/validate_structure.py`, **new** `tests/test_validate_structure.py`, `.claude/settings.json` |
| **C: Course content** | 1, 3, 4, 5 (+G1, RV-M1, RV2-M6), 10 (+RV-L2, S14), 16 (+S16, RV-M6) | `COURSE.md`; scripts/exercises in 0.2–0.4, 1.1–1.8, 2.1–2.6 |
| **B: old_B** | 12 (content part) | `projects.md` → **new** `03-final-project/old_B-document-intelligence.md` |
| **T: Tutor** | 6, 7, 11, 12 (+G4), 14, S14 setup check | `learn.md`; all 15 `learn/*.md` (frontmatter); body edits in `setup.md`, `security.md`, `project.md`, `resume.md` |
| **D: Docs** | 8 (+G2), 13, test command, S11, S14, S18, RV-L6 | `setup.md` §F, `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` (lines 57–61 and 65–68 only), `changes.md` |

### 4.2 Course content (groups C and B)

#### Item 1: `COURSE.md`
- Add `| 2.1 | מהו API | מעשי |` and `| 2.2 | עבודה עם API של Claude, OpenAI ו-Gemini | מעשי |` before 2.3.
- Change the module 02 range `2.3–2.6` → `2.1–2.6`.

#### Item 3: VAT 17% → 18% (RV-M2, RV2-M1)
There are seven occurrences:
- `1.3_exercises.md:36`
- `2.2_exercises.md:150` (scenario "כולל מע"מ (17%)")
- `2.2_exercises.md:153` (task "המחיר כולל 17% מע"מ")
- `2.2_exercises.md:175` (docstring)
- `2.2_exercises.md:176` (`vat_rate = 0.17` → `0.18`)
- `2.2_exercises.md:184` (tool description)
- `2.6_script.txt:53` ("שבעה עשר אחוז" → "שמונה עשר אחוז")

**Completion check (for the plan):** `grep -rnE "17%|0\.17|שבעה עשר" courses/ai-dev` returns nothing outside `_archive/`.

#### Item 4: 0.4 markers
All 19 `[SLIDE TRANSITION]` → `[מעבר שקף]`. No other change.

#### Item 5 + G1 + RV-M1 + RV2-M6: archive residue
- **The course name.**
  - Change the course-name uses to "AI Dev":
    - "…קורס AI Engineer" in `0.2_script.txt:3`, `0.3_script.txt:3`, `2.1_script.txt:2`
    - `- **קורס:** AI Engineer` in `0.2/0.3/0.4_exercises.md:7`
  - **Keep** the job-title uses: `0.2_script.txt:9,41,83,123-129,161`, `0.3_script.txt:111`, and the English "AI engineer" in 0.4.
- **Headers:**
  - exercise H1 and `**שיעור:**` lines in 0.2, 0.3, 0.4, 1.7, 1.8 and 2.1–2.6
  - script title lines in 0.2, 0.3 and 0.4, including "Lesson 0.3" in both places in the opening
- **Spoken lesson numbers.** The full inventory from `grep -noE "(אפס|אחת|…|תשע) נקודה [א-ת]+"`, with each rewritten to the real lesson:

  | File:line | Now | Becomes |
  |---|---|---|
  | `1.1:1`, `1.2:1`, `1.3:1`, `1.4:1` (self), `1.5:1`, `1.6:1`, `1.8:2` | "שלוש נקודה X" (self) | "אחת נקודה X" |
  | `1.4:1` (previous-lesson clause) | "שלוש נקודה שלוש" | "אחת נקודה שלוש" |
  | `1.1:167-173` | 3.2/3.3/3.4/3.6/3.8 | 1.2/1.3/1.4/1.6/1.8 |
  | `1.2:245`, `1.3:41`, `1.4:39`, `1.6:77` | 3.3/3.4/3.5/3.7 | 1.3/1.4/1.5/1.7 |
  | `2.1:2`, `2.2:2` (self and previous), `2.4:2`, `2.5:2`, `2.6:1` (self and previous) | "חמש נקודה X" | "שתיים נקודה X" |
  | `2.1:100`, `2.2:57`, `2.4:7`, `2.4:72` | 5.2/5.3/5.3/5.5 | 2.2/2.3/2.3/2.5 |
  | `2.1:5` | "ארבע נקודה שש" (a lesson that never existed) | cut (see the cross-reference list below) |
  | `2.6:77` | "שש נקודה אחת" | cut (see below) |

  **Not lesson numbers, so they stay** (and form the S17 allowlist, §5.1):
  - `0.3:39` "שבע נקודה אחת אחוז"
  - `1.1:83` "ארבע נקודה שש" (Opus 4.6)
  - `1.1:123` "שש נקודה שש מיליארד"
  - `1.3:3,11` "שתיים נקודה אחת נקודה חמישים ותשע" (when auto memory arrived)
  - `2.1:85,90,100` "שתיים נקודה אפס" (OAuth 2.0)
  - `2.5:12` "שלוש נקודה שלוש/ארבע עשרה" (Python 3.13/3.14)
  - `2.5:42` "ארבע נקודה שבע" (Opus 4.7)

  `1.3:15` changes to the S14 floor (item 10).
- **Other ordinal and module forms:**
  - `2.3` "חמישי-שלוש"
  - `1.7` "המודול השלישי"
  - `1.8` "מודול שלוש" (twice)
  - `1.1:165` "בהמשך מודול שלוש"
  - `0.3` "לשיעור השני"
- **Cross-references to lessons or modules that don't exist or have moved:**
  - `1.1_script.txt:5`: Make/n8n/WhatsApp/Telegram → a one-sentence bridge from Module 0.
  - `0.2_script.txt:3` and `:13-15`: the 8-module / 156-hour description → the four modules from `COURSE.md`.
  - `0.2_script.txt:137,165`: "בשיעור 0.3" (prompt engineering) → "בשיעור 0.4".
  - `0.2_exercises.md:146-149`: map to the real modules (01, 02, 03); cut rows with no counterpart.
  - `0.3_script.txt:57`: cut "נלמד את זה לעומק במודול הראשון".
  - `0.3_script.txt:87`: "במודול חמש" → "במודול 02".
  - `0.3_exercises.md:59`: cut "נלמד בדיוק את זה במודולים 1 ו-2".
  - `1.2_script.txt:229-235`: "3.3" → "1.3", "3.7" → "1.7".
  - `1.8_script.txt`, the last slide: → a one-line bridge to Module 02.
  - `2.1_script.txt:5`: → a bridge from Module 01.
  - `2.6_script.txt:77`: cut the "module 6 / lesson 6.1" teaser. The closing summary stays. There's no bridge to the final project, because Stage 0 disables it (RV2-L12).
- **Leaked preambles (G1).** In `1.8`, `2.3` and `2.6_exercises.md`, delete line 1 and the blank/`---` lines that follow it, up to `<div dir="rtl" lang="he">`.
- **Voice:** replacement Hebrew matches the file. It's reviewed by a Hebrew-speaking contributor.
- **Known churn:** 1b renumbers 0.x again.

#### Item 10: the 1.3 hook exercise
**Exercise 5** (`1.3_exercises.md:75-85`) is rewritten:
1. **Setup.** In `claude-advanced-lab`, create `secret-demo.txt` (`FAKE_API_KEY=not-a-real-key`) and `notes.txt`.
2. **The hook,** in project scope, `claude-advanced-lab/.claude/settings.json`:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Read",
           "hooks": [
             {
               "type": "command",
               "if": "Read(secret-demo.txt)",
               "command": "echo 'Blocked by hook: secret-demo.txt is protected' >&2; exit 2"
             }
           ]
         }
       ]
     }
   }
   ```
   The native-Windows (no Git Bash) variant uses `"command": "[Console]::Error.WriteLine('Blocked by hook: secret-demo.txt is protected'); exit 2"`.
3. **Negative test.** Restart Claude Code in the folder and ask it to read `secret-demo.txt`. It is blocked, and Claude repeats the reason. *If Claude immediately tries the terminal on its own, that's step 5 happening early. Note it.*
4. **Positive control.** Reading `notes.txt` works.
5. **The bypass.** Ask explicitly: "run `cat secret-demo.txt` in the terminal" (`Get-Content` without Git Bash). The content appears.
   - *If Claude declines,* the refusal is model behaviour, not enforcement. Record what happened.
6. **Takeaway (text), RV2-L5:**
   - A hook is a deterministic guardrail for the specific tool calls it matches. Other tools (Bash, PowerShell, Grep) still reach the file, so a hook is not a security boundary.
   - Claude Code has stronger layers:
     - permission **deny rules**, which also cover `cat`/`head`/`tail`, though not scripts that open files themselves
     - the **sandbox**, which is OS-enforced (macOS, Linux, WSL2)
   - The strongest enforcement is outside Claude entirely: OS permissions that the agent's user can't undo.
   - Linux illustration, in a box explicitly marked "**להמחשה בלבד — לא להריץ**" (illustration only, don't run): `chmod 000 secret-demo.txt && sudo chattr +i secret-demo.txt`.
   - "Out of reach" means out of reach of every process the agent can start.
7. **Y/N note:** hooks have no terminal. `permissionDecision: "ask"` is the mechanism (optional reading).

**Related edits:**
- `1.3_exercises.md:8`: "v2.1.59+" → "v2.1.176+".
- `1.3_script.txt:15`: the spoken "שתיים נקודה אחת נקודה חמישים ותשע ומעלה" → "…נקודה מאה שבעים ושש ומעלה" (S14).
- `1.3_script.txt:25`: soften "חוסם פעולה באופן מוחלט" to "deterministic for the tool call it matches".
- `1.3_script.txt:27`: the exit-2 vs exit-1 correction.
- `1.3_script.txt:29`: the read-guard demo. No deletion, and no Python-bypass suggestion.
- `1.3_exercises.md:60`: skills trigger through their `description`, not "via Hooks (exercise 5)".
- `1.3_exercises.md:114`: "סקריפט ה-Hook" → "the `.claude/settings.json` with the hook".
- **Rubric "יישום Hooks":** blocks the Read, explains exit 2 vs 1, and explains the `cat` bypass.

Nothing deletes a file or asks the learner to try.

#### Item 16 + S16 + RV-M6: Supabase in 1.6
- `1.6_exercises.md:17,21,30,168`: switch to the publishable key (`NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...`). `:168` adds: "`SUPABASE_SECRET_KEY` is server-only: never `NEXT_PUBLIC_`, never in git".
- `:99`: `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<your-project-ref>&read_only=true"`, followed by a new step (RV2-M3): "in a regular terminal run `claude /mcp`, select **supabase** → **Authenticate**, and log in to Supabase in the browser that opens".
- `:103`: "Using the Supabase MCP, describe the schema of the 'clients' table", then "insert the dummy client row in Supabase's Table Editor". It adds one line explaining that the MCP is read-only on purpose. Questions and rubric are adjusted wherever they assume an MCP insert.
- `1.6_script.txt:33`: "אנון קי" → the publishable key; "מפתח תפקיד השרת" → the secret key.
- The `@supabase/ssr`/auth rewrite and removing Prisma stay in 1d.

#### Item 12, content part: old B (RV-L7, RV2-L3)
- Move `projects.md:174-318` (from "## פרויקט ב" up to, but not including, the `---` at `:319`) verbatim to `03-final-project/old_B-document-intelligence.md`.
  - The new file gets its own `<div dir="rtl" lang="he">` … `</div>`, plus a one-line note: unwired, not the new track B (PRD D5).
  - In `projects.md`, delete the now-redundant `---` (formerly `:319`), so one separator remains between A and C.
- `projects.md:7` "מתוך ארבעה" is left stale on purpose until 1e.

### 4.3 Tutor (group T)

#### Item 11: frontmatter
All 15 `learn/*.md` files get a leading `---\ndisable-model-invocation: true\n---` block, with no other keys. `display.md` gets it too, but nothing else (its English-only command list at `:114` is unreferenced; D8a folds it later). `learn.md` is unchanged (S2a decides).

#### Item 7: Hebrew aliases (S2)
- **`learn.md` Learner Commands:**
  - `continue / המשך`
  - `quiz me / בוחן` → `quiz.md` (covered sections)
  - `quiz me full / בוחן מלא` → `quiz.md` in **`quiz me full`** mode
  - `stop / עצור / סיום`
- **`learn.md` Route table (79–80):** the same words, naming the `quiz.md` mode. `quiz.md` is untouched; it's F's.
- `teaching.md:144` and `setup.md:225` are unchanged.

#### Item 12 + G4: no capstones until 1e
- **`project.md`:** a new first section, `## Step 0 — TEMPORARY (until unit 1e)`. It shows "the final projects are being rebuilt; meanwhile, continue with the lessons (`/learn`)" in `session.language`, then stops without reading `projects.md`.
- **`resume.md`:** `:23`, `:38` and `:50` → one TEMPORARY rule, "Do not offer the final project until unit 1e". The route row `:74` stays.

#### Item 6: `security.md`
- **Ownership gate.**
  - A new Pre-flight step runs after `target_url` is known and before Phase A, on every entry path (`deploy` handoff, `security http…`).
  - It asks with `AskUserQuestion`: "Is this app yours, or do you have explicit permission to test it?" Only the affirmative option continues.
  - **On any other answer (RV2-L10):**
    - no network request of any kind is made, and no Phase (A–E) runs
    - the module shows a short explanation (testing without permission can cause harm and may be illegal)
    - it suggests rerunning `/learn security` with the URL of an app the learner owns, and then **ends**
- **`timingSafeEqual` (`:128-136`):**
  ```js
  const { createHash, timingSafeEqual } = require('node:crypto')
  const digest = (s) => createHash('sha256').update(String(s)).digest()

  const secret = process.env.SYNC_SECRET
  if (!secret) return res.status(503).json({ error: 'Service unavailable' })

  const provided = req.headers['x-sync-key']
  if (!provided || !timingSafeEqual(digest(provided), digest(secret))) {
    return res.status(401).json({ error: 'Unauthorized' })
  }
  ```
  Plus one sentence on why digests avoid the 500 and hide the key's length.

#### Item 14: the clean-slate step (S4, S5)
- **Placement:** `setup.md` gets a new **`## 0. Clean slate`**, before "## A. Show Current Settings" (RV2-L12).
- **Markers:** it sits between `<!-- CLEAN-SLATE:BEGIN — TEMPORARY, remove at first-cohort gate (PRD D10) -->` and `<!-- CLEAN-SLATE:END -->`.

**Behaviour:**
1. **Find.** Check exactly these paths, with no globs:
   - `$HOME/skill-tutor-tutorials/`
   - `$HOME/.claude/commands/learn.md`
   - `$HOME/.claude/commands/learn/`

   Relative paths are forbidden, because the repo has its own `skill-tutor-tutorials/`. If none exists, skip silently to A.
2. **Show.** Each path found, with its file count and newest modification date. If a path is a **symlink**, show that and its target (RV2-L11).
3. **Ask.** One `AskUserQuestion`, in Hebrew:
   - `להשאיר הכל` (listed first): nothing is touched.
   - `להעביר לגיבוי ולהתחיל מחדש`: everything moves to `~/skill-tutor-tutorials-backup-<date>`; nothing is deleted.

   Only the second option is a yes.
4. **Move.** A bash variant and a PowerShell variant. Reference shape (bash):
   ```bash
   : "${HOME:?HOME is not set}"
   ts=$(date +%Y%m%d-%H%M%S)
   dest="$HOME/skill-tutor-tutorials-backup-$ts"
   mkdir "$dest" && mkdir "$dest/commands" || exit 1
   if [ -e "$HOME/skill-tutor-tutorials" ] || [ -L "$HOME/skill-tutor-tutorials" ]; then mv "$HOME/skill-tutor-tutorials" "$dest/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn.md" ] || [ -L "$HOME/.claude/commands/learn.md" ]; then mv "$HOME/.claude/commands/learn.md" "$dest/commands/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn" ] || [ -L "$HOME/.claude/commands/learn" ]; then mv "$HOME/.claude/commands/learn" "$dest/commands/" || exit 1; fi
   ```
   - `mv` moves a symlink as a link and never follows it. PowerShell uses `Move-Item -LiteralPath … -ErrorAction Stop`, after checking `$HOME` is non-empty.
   - On any error: stop and report. Never retry with force, and never delete.
5. **Verify and report.** Each original path is gone and present in the backup. Print the backup path.
6. **Continue or stop.** If a global command was moved, stop and ask the tester to reopen Claude Code and run `/learn setup` again. Otherwise continue.

**Hard rules, stated in the section:**
- only the three paths
- never anything inside the repo (the local settings file and the repo's `skill-tutor-tutorials/` are named explicitly; the settings file is written **without** backticks, RV-H4)
- never an earlier backup
- no delete command
- when in doubt, keep

**Reach (RV-H5, RV2-M2).** A personal `~/.claude/commands/learn.md` shadows the repo's `/learn` (skills.md). If it's a router from `c25e73c` or later, `/learn setup` still reaches this step, because such a router `Read`s the repo's `setup.md`. **Older global installs (before 2026-05-25) run their own inline setup, and this step never appears.** The README tester note therefore gives the manual fallback (§4.4).

#### S14: Claude Code version check (permanent)
- **Placement:** `setup.md` gets a new **`## A.1 Claude Code version`**, directly after "## A. Show Current Settings" (RV2-L12), outside the CLEAN-SLATE markers.
- **Behaviour:**
  - Run `claude --version` and take the first `X.Y.Z`.
  - Compare it with 2.1.176 **numerically, component by component (major, then minor, then patch), never as text** (RV2-L2).
  - If it's lower, show a short Hebrew warning and the update command (`claude update`), then continue.
  - If `claude` isn't on PATH (e.g. Desktop-bundled installs, the PRD D9a route), skip silently. The PR notes this limitation.

### 4.4 Docs (group D)

#### Item 8 + G2: remove the global install
- **`setup.md`:** delete §F (`:279-309`), and re-letter "G. Setup Complete" → **F**.
- **`README.md`:** delete `:46` and `:202`.
- **`CLAUDE.md`:** drop "global install" from `:14`, and delete step 4 at `:75`.
- **`CONTRIBUTING.md`:** delete `:61`.
- The existing `changes.md` sections are unchanged.

#### RV-L6: document the new frontmatter
The "add a module" steps in `README.md:196-202`, `CONTRIBUTING.md:57-61` and CLAUDE.md "הוספת מודול חדש" each gain one step: "start the file with the `disable-model-invocation: true` frontmatter block".

#### Item 13: README tester note
- **Placement:** under the title/banner, between `<!-- TEMPORARY: remove at first-cohort gate (PRD D10) -->` and `<!-- /TEMPORARY -->`.
- **Text:** the PRD's wording, then: "…or run `/learn setup`, which offers to move them into a backup for you. **If `/learn setup` doesn't show that offer, you have an older global install: move or delete `~/.claude/commands/learn.md` and `~/.claude/commands/learn/` by hand, then restart Claude Code**" (RV2-M2).

#### README version floor (S14, RV2-L6)
- "Step 1 — Prerequisites" (`:25`): "Claude Code 2.1.176 or later installed (Pro plan or higher)".
- "Requirements" (`:208`): the same.
- uv is not mentioned (learner-facing).

#### Contributor test command (S12, RV2-L7)
- **`CLAUDE.md`:** a new "## בדיקות (למפתחי הקורס בלבד — contributors only)" section. It says uv is required for contributors (install: https://docs.astral.sh/uv/getting-started/installation/), that learners don't need it, and gives:
  ```
  uv run pytest -q && uv run ruff check -q
  ```
- **`CONTRIBUTING.md` "Pull Requests" (`:65-68`):** add one line, "run `uv run pytest -q && uv run ruff check -q` before opening a PR".

#### `changes.md` (S11, S18)
Written once, as the last commit of group D, appended after the existing sections in the same style (an Overview, numbered `##` entries with Before/After, and a File Map):
1. `# Changes — fix/lesson-1.8-workers-ai-exercise branch` (#12, merged 2026-09-28), summarised from its merged diff
2. `# Changes — fix/lesson-2.5-2.6-content-corrections branch` (#13, merged 2026-09-28), likewise
3. `# Changes — fix/stage0-quick-wins branch`, with one entry per learner- or contributor-visible change, and a **Testers** note ("reset your data, or run `/learn setup` and choose the backup option")

---

## 5. Toolchain, lints, tests and CI (group P)

### 5.1 `tests/validate_structure.py` (library module)
- Pure functions, `check_<name>(root: Path) -> list[str]`, with findings formatted `path:line: [check] message`.
- A `CHECKS` tuple lists them all. No `main()`, no printing, no import-time work.
- **Course scope:** `courses/*/` except `courses/_archive/`, skipping `old_B*` files.
- **File discovery (RV2-L8):** a helper `repo_files(root, pattern)`:
  - uses `git ls-files` when `root/.git` exists, so local results match CI
  - otherwise walks the filesystem (the pytest fixture trees)

| Check | Rule |
|---|---|
| `course_md` | For each course with a `COURSE.md`:<br>(a) the lesson numbers in "רשימת שיעורים" **equal** the lesson folders `lessons/*/<X.Y>-*`<br>(b) the table order equals numeric folder order<br>(c) each module row's folder exists, and its range equals `<min>–<max>` (or `—`; `–`/`-` both accepted) |
| `slide_markers` | Every `*_script.txt` has ≥ 5 `[מעבר שקף]` and zero `[SLIDE TRANSITION]` |
| `header_numbers` | **Exercises:** the first `# ` heading contains `שיעור X.Y`, and any `**שיעור:**` line contains `X.Y`, both equal to the folder.<br>**Scripts:** in the first 3 non-empty lines, every `(שיעור\|Lesson)\s+(\d+\.\d+)` and every `שיעור\s+([א-ת]+)\s+נקודה\s+([א-ת]+)` equals the folder. `W` is `[א-ת]+`, mapped by the digit-word table (אפס; אחת/אחד; שתיים/שניים/שתים; שלוש/שלושה; ארבע/ארבעה; חמש/חמישה; שש/שישה; שבע/שבעה; שמונה; תשע/תשעה); an unmapped word is a finding |
| `spoken_lesson_refs` (S17) | In every course-scope `*_script.txt` and `*_exercises.md`, every match of `\b([א-ת]+)\s+נקודה\s+([א-ת]+)`, where both words are in the digit-word table, must form an `X.Y` that is an **existing lesson folder number** in that course, unless the match sits inside an allowlisted phrase. `SPOKEN_ALLOWLIST` is a tuple of (file-name glob, exact phrase), seeded from §4.2's "stay" list:<br>• `0.3_script.txt`, "שבע נקודה אחת אחוז"<br>• `1.1_script.txt`, "ארבע נקודה שש" and "שש נקודה שש מיליארד"<br>• `1.3_script.txt`, "שתיים נקודה אחת נקודה חמישים ותשע"<br>• `2.1_script.txt`, "שתיים נקודה אפס"<br>• `2.5_script.txt`, "שלוש נקודה שלוש עשרה", "שלוש נקודה ארבע עשרה" and "ארבע נקודה שבע"<br>An allowlist entry that no longer matches anything is **also a finding**, so the list can't go stale (the same rule as D7c's baseline). N replaces this check |
| `course_name_denylist` | No `קורס\s+(ה-)?AI Engineer`, `\*\*קורס:\*\*\s*AI Engineer` or `AI Engineer course` (case-insensitive) in course scope. The job title passes |
| `tutor_refs` | In `.claude/**/*.md`:<br>(a) backticked paths starting with `.claude/` or `courses/` exist, except `LOCAL_ONLY = {".claude/settings.local.json"}`<br>(b) a backticked bare `name.md` directly after a word-bounded `Read`/`Load` (any case) exists in the referring file's folder<br>Skips `~/…` and placeholders (`[`, `{`, `*`, `X.Y`). **`${CLAUDE_SKILL_DIR}` resolution is M's extension (§9; RV2-M4)** |
| `settings_json` | `.claude/settings.json`, if present, parses, and contains no `powershell` (case-insensitive) |
| `relative_links` | In every tracked `*.md`, after removing fenced blocks and inline code spans, every `[text](target)` that isn't `http:`/`https:`/`mailto:`/`#…` resolves (after stripping `#fragment`). Skips `_archive/` and `old_B*` |
| `clean_slate_no_delete` | *Temporary.* Between the CLEAN-SLATE markers in `setup.md`: no `\brm\b`, `\brmdir\b`, `\bdel\b`, `\berase\b`, `\brd\b`, `\bri\b`, `Remove-Item`, `\bunlink\b`, `-delete\b`, `rmtree`. Missing markers are not a finding |
| `lesson_files` *(existing)* | Every lesson folder has `*_script.txt` and `*_exercises.md`; course-scoped |
| `teaching_step5` *(existing)* | `teaching.md` contains "Step 5" |

### 5.2 `tests/test_validate_structure.py` (pytest)
- **Fixture:** a `good_tree` fixture in `tmp_path`, deliberately **not** a git repo, so it exercises the filesystem path of `repo_files`. It contains:
  - one course (two modules, three lessons, valid scripts/exercises), and `COURSE.md`
  - `.claude/commands/learn.md` routing to `teaching.md` ("Step 5" plus `Read \`quiz.md\``), `quiz.md`, and `setup.md` (with CLEAN-SLATE markers)
  - `.claude/settings.json`
  - a README with a relative link
  - a script with a spoken reference to an existing lesson and one allowlisted phrase
- **`test_good_tree_passes`:** every check returns `[]`.
- **A separate `git_tree` test:** `git init` + `git add` on a copy of the good tree, plus one **untracked** broken-link file. `relative_links` ignores the untracked file.
- **Seeded regressions,** parametrized. Each asserts the named check fails and all others pass. At minimum:
  - `course_md`: a missing row; an extra row; a swap; a wrong range
  - `slide_markers`: 4 markers; `[SLIDE TRANSITION]`
  - `header_numbers`: `שיעור 5.1` in 2.1; a mismatched `**שיעור:**`; `שיעור 0.1` in 0.2; spelled `חמש נקודה אחת`; an unmapped word
  - `spoken_lesson_refs`: "שלוש נקודה שתיים" (no lesson 3.2); a stale allowlist entry
  - `course_name_denylist`: `בקורס AI Engineer`; `- **קורס:** AI Engineer`
  - `tutor_refs`: a missing `.claude/…` route; `Read \`missing.md\``
  - `settings_json`: `powershell`; invalid JSON
  - `relative_links`: a missing target
  - `clean_slate_no_delete`: `rm -rf`; `Remove-Item`
  - `lesson_files`: missing exercises
  - `teaching_step5`: "Step 5" removed
- **Must-pass negatives,** parametrized:
  - the job title
  - denied strings in `_archive/` and `old_B-x.md`
  - `~/…`; `.claude/settings.local.json`; `${CLAUDE_SKILL_DIR}/x.md`
  - "already … `x.md`"; "load … from `projects.md`"
  - `http(s)` and `#anchor` links; a broken link in a code fence and in inline code
  - spelled numbers followed by `,` `:` `.`
  - an allowlisted phrase; a spoken reference to an existing lesson
  - "Confirm", "model" and "perform" between the markers; `rm` outside them
  - a missing `settings.json`
- **`test_real_repo_passes`:** every check on the real repo, with the findings in the assertion message. Red until groups C, T and D land.

### 5.3 Toolchain files
- **`pyproject.toml`:**
  ```toml
  [project]
  name = "tov-learn"
  version = "0.0.0"
  requires-python = ">=3.14,<3.15"

  [dependency-groups]
  dev = ["pytest>=9.1.1", "ruff>=0.16.9"]

  [tool.uv]
  package = false
  required-version = ">=0.12"

  [tool.pytest.ini_options]
  testpaths = ["tests"]

  [tool.ruff]
  target-version = "py314"
  ```
- **No `.python-version`** (S13).
- **`uv.lock`:** generated **with the CI-pinned uv 0.12.19** (e.g. `uvx --from uv==0.12.19 uv lock`), so `uv sync --locked` can't drift between the local 0.12.1 and CI (RV2-L9). Committed.
- **`.gitignore`:** add `.venv/`, `__pycache__/`, `.pytest_cache/` and `.ruff_cache/`.

### 5.4 CI
**`.github/workflows/validate.yml`:**
```yaml
name: Validate Skill Structure

on:
  pull_request:
    branches: [master]
  push:
    branches: [master]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0
        with:
          version: "0.12.19"
          python-version: "3.14"
      - name: Sync (locked)
        run: uv sync --locked
      - name: Tests (seeded regressions + real repo)
        run: uv run pytest -q
      - name: Ruff
        run: uv run ruff check -q
```

**`.github/dependabot.yml`:**
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 5.5 Item 2
`.claude/settings.json` becomes `{}`. `auto-save-progress.ps1` stays for M.

### 5.6 Forward compatibility
F and G add checks as `check_*` functions plus test cases. `jsonschema`, if needed (D8c), goes in the dev group.

---

## 6. Verification and the PR

### 6.1 Commit order
On `fix/stage0-quick-wins`, only when the user asks:
1. **P1:** `pyproject.toml`, `uv.lock`, `.gitignore`, the validator, the tests, `validate.yml` and `dependabot.yml`. They land together because CI needs the tests. The message lists the red findings.
2. **P2:** `settings.json` → `{}`.
3. **C:** COURSE.md → VAT → 0.4 markers → residue → 1.3 → 1.6 → old_B, one commit each.
4. **T:** frontmatter → aliases → project/resume → security → clean-slate → version check.
5. **D:** global install → frontmatter docs → tester note → version floor → test command → `changes.md` (last).

Each commit runs `uv run pytest -q && uv run ruff check -q`. Only `test_real_repo_passes` may be red before the end, and the last commit is fully green.

### 6.2 PR description (required sections)
- **Summary:** every item, G*, RV-* and RV2-* fix, each mapped to a commit; links to the three new `changes.md` sections.
- **Automated verification:**
  - the pytest output (the parametrized IDs)
  - ruff clean
  - the Actions run, plus the pasted `gh run view` / annotations output showing no Node 20 / deprecation annotation
  - the item-3 VAT grep returning nothing
- **Manual verification.** The user runs these interactively in the worktree. Each records steps, date, OS/shell, Claude Code version, who ran it, result and cleanup.
  1. **Resume:** fake `progress/lesson-0.1…1.8.md`, `settings.json` and `learner_profile.md` under `~/skill-tutor-tutorials/`. `/learn` offers 2.1, with **no** 🏗️ line.
  2. **Hook error:** two replies in a worktree session. No "hook error" notice.
  3. **Clean-slate:**
     - Hash the main checkout's local settings file first.
     - Fixtures: `~/skill-tutor-tutorials/` (one file), `~/.claude/commands/learn/` (one file), and `~/.claude/commands/learn.md` as a **copy of the worktree's `learn.md`**.
     - Run `/learn setup`. The step-0 prompt appears.
     - Keep → nothing moved.
     - Rerun, move → all three are in the backup, originals gone, `git status` clean, restart message shown, no local settings file created in the worktree.
     - **At every permission prompt, answer "Yes" (once), never "Yes, and don't ask again"**, which would write an approval into the hashed file (RV2-L1). The hash must then be unchanged. Record the prompts.
     - Remove the backup.
  4. **1.3 exercise 5** (Linux/bash): steps 1–5 in a throwaway lab. Record the step-5 outcome.
  5. **Security gate:** `/learn security https://example.com` → "no". No `curl` runs, and the module ends.
  6. **Aliases and project:**
     - `בוחן` starts a quiz.
     - `עצור` saves progress.
     - `בחן אותי` still switches to **diagnostic** mode (RV2-L12).
     - `/learn project` shows the rebuilt message.
- **Untested (stated explicitly):**
  - the native-PowerShell hook variant
  - the 1.6 MCP add + Authenticate flow, unless a contributor with a Supabase project runs it
  - the version check on Desktop-bundled installs (it skips)
- **Future concerns:** §9.
- **Reviewer note:** Hebrew changes need a Hebrew-speaking contributor's approval.

### 6.3 Done-when (§3) → proof

| Done when | Proof |
|---|---|
| Each new lint fails on a seeded regression and passes on the fixed tree | §5.2, `test_real_repo_passes`, and the P1 message |
| `resume` offers 2.1 after 1.8 | `course_md` (b) plus manual check 1 |
| 0.4 splits into slides | `slide_markers` |
| No hook error after replies | `settings_json` plus manual check 2 |
| `validate.yml` has no Node deprecation warning | the annotations evidence |
| The clean-slate step backs up before any delete | S4, `clean_slate_no_delete`, and manual check 3 |

Manual checks 4–6, the VAT grep and `spoken_lesson_refs` cover changes that §3 doesn't name.

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| The heuristics miss a spoken form | §4.2 inventory; `spoken_lesson_refs`; N replaces both |
| The replacement Hebrew reads badly | Minimal edits; a Hebrew reviewer |
| A clean-slate move fails part-way | It stops at the first error; nothing is deleted |
| A tester with a pre-2026-05-25 global install never sees the step | The README fallback instructions (§4.4) |
| Pins go stale | SHA pins plus Dependabot (S15) |
| Contributors without uv | Install link in CLAUDE.md and CONTRIBUTING; learners unaffected |
| The Windows hook variant or the MCP flow is wrong | Flagged untested; 1a and 1d rewrite them |

---

## 8. Proposed PRD amendments

To be applied in a separate, approved edit:
1. **D2 item 5:** G1 preambles; the RV-M1 cross-references; the full spoken-number inventory (RV2-M6).
2. **D2 item 8:** G2 locations; the frontmatter step in the add-a-module docs.
3. **D2 item 12:** `resume.md` too (G4).
4. **D2 item 7:** aliases per S2.
5. **D2 item 14:** a move, exact paths, and the README fallback for pre-`c25e73c` installs.
6. **D2 item 15:** `setup-python` → `setup-uv`; the contributor toolchain uv + pytest + ruff; Python 3.14 in `pyproject.toml` only.
7. **D2 item 16:** `1.6_script.txt:33`; the read-only MCP with the `/mcp` Authenticate step; the `:103` rewrite.
8. **D2 item 10:** the Claude Code floor 2.1.176 (S14), in `1.3_exercises.md:8`, `1.3_script.txt:15` and README; the CHANGELOG facts go into §7.
9. **D2 item 3:** seven VAT occurrences.
10. **D7c:** Stage 0 also adds `spoken_lesson_refs` (S17), with the stale-allowlist rule.
11. **§6 Dependabot row:** decided (S15).
12. **New unit N** between F and 1a (S10).

---

## 9. Out of scope: future concerns

| Unit | Concern carried forward |
|---|---|
| M | Drop `auto-save-progress.ps1` and the slide viewer; the CLAUDE.md module table and its lint. **Before `tutor_refs` can serve as M's done-when (PRD D8d), M must extend it to resolve `${CLAUDE_SKILL_DIR}/…` against the folder of the nearest `SKILL.md`, with seeded tests (RV2-M4).** Otherwise the lint passes vacuously |
| F | `landscape.md` (including the Claude Code floor and the Node row); baseline/model-string/full denylist; the rest of CONTRIBUTING; the style guide; `changes.md` → Keep-a-Changelog; `quiz.md:14` Hebrew triggers; `jsonschema` in the dev group if needed |
| **N (proposed)** | Numbering contract:<br>• stable lesson ids as the contract; numbers derived<br>• a manifest<br>• a deterministic generator (COURSE.md tables, exercise and script headers, inside `<!-- generated -->` markers)<br>• CI `--check`<br>• id references in prose<br>• a thin `renumber`/`add-lesson` skill<br>• a CLAUDE.md rule to run the generator before any push (convenience; CI enforces)<br>Replaces `header_numbers` and `spoken_lesson_refs` |
| G | Interpreter resolution; owned `settings.local.json` entries; the no-`python3` lint; branch protection. **Constraints: learner tooling must not require uv; no `.python-version` at the repo root** |
| 1a | The full 1.3 lab; macOS/Windows OS-lock equivalents (UNVERIFIED); 1.2 fixes; 1.1 homework |
| 1b | Module 0 reorder, renumbering 0.x again (update `SPOKEN_ALLOWLIST` accordingly) |
| 1c | Module 02 rename. **If 2.0 teaches uv, learner projects live outside the repo folder** (uv project discovery would otherwise attach to `tov-learn`) |
| 1d | `@supabase/ssr`/auth rewrite; Prisma removal; an end-to-end check of the MCP flow |
| 1e | Restore `/learn project` and the resume offer; delete the TEMPORARY blocks; `projects.md:7` |
| Gate | Remove the README tester note, the CLEAN-SLATE section and `clean_slate_no_delete` |
| S2a | Whether `learn.md` stays model-invocable; 3-OS pytest CI (already on uv); learner CLI without uv; Dependabot `uv` once 0.12 support is confirmed |

---

## 10. Change log

### First independent review (2026-09-27)
A fresh Opus 5.5 Plan agent (single, read-only, no context) raised 22 findings: 5 High, 8 Medium, 9 Low. All were accepted.

| # | Finding | Resolution |
|---|---|---|
| RV-H1 | `tutor_refs` (b) flagged 5 real lines | Directly-after-Read/Load regex |
| RV-H2 | The read-only MCP broke `:103` | S16 |
| RV-H3 | Delete-command substrings hit "Confirm"/"model" | Word-bounded regexes |
| RV-H4 | `settings.local.json` is absent in CI | `LOCAL_ONLY`; no backticks |
| RV-H5 | A personal `learn.md` fixture shadows the project command | Fixture = copy of the worktree router |
| RV-M1 | Missed cross-references | §4.2 |
| RV-M2 | VAT `0.17` missed | §4.2 (now seven, RV2-M1) |
| RV-M3 | `python` missing; the unittest exit-5 trap | uv + pytest + ruff (S6, S12, S13) |
| RV-M4 | `relative_links` flagged inline code | Strip inline code |
| RV-M5 | `if` needs a newer Claude Code | S14 |
| RV-M6 | `1.6_script.txt:33` | Item 16 |
| RV-M7 | Tokenizing unspecified | `[א-ת]+` |
| RV-M8 | Behaviours without evidence | Manual checks 4–6 |
| RV-L1…L9 | Worktree settings assertion; 1.3 leftovers; counts; S11 reason; Dependabot; frontmatter docs; old_B tidy; `quiz.md:14`; `0.2:9` | §6.2, §4.2, §1, S11, S15, §4.4, §4.2, §4.3, §4.2 |

### Second independent review (2026-09-28)
A fresh Opus 5.5 Plan agent (single, read-only, no context) raised 19 findings: 1 High, 6 Medium, 12 Low. All were accepted.

| # | Finding | Resolution |
|---|---|---|
| RV2-H1 | Local `master` was 4 commits ahead of `origin/master` (#12/#13 open), and S11 said they were merged | The user merged #12 and #13 on 2026-09-28. Local `master` was moved to `origin/master` after proving identical trees, and the docs branch was rebased. Baseline and S11 corrected; §1 adds a pre-worktree check |
| RV2-M1 | VAT had seven occurrences | §4.2, plus a completion grep in the PR |
| RV2-M2 | Pre-`c25e73c` routers set up inline, so the step never runs | The reach note is corrected; the README fallback |
| RV2-M3 | The MCP authentication step was missing | The `/mcp` → Authenticate step (S16) |
| RV2-M4 | `tutor_refs` can't prove M | Recorded as M's extension (§9) |
| RV2-M5 | A root `.python-version` could pin learners' Python | Dropped; `requires-python` plus setup-uv's `python-version` (S13) |
| RV2-M6 | Out-of-window spoken numbers had no completion check | Full inventory (§4.2) plus `spoken_lesson_refs` (S17) |
| RV2-L1 | "Don't ask again" writes to the hashed file | Answer "Yes" once only |
| RV2-L2 | Version compare unspecified | Numeric by component; the Desktop skip is noted |
| RV2-L3 | The old_B range carried a `---` | Move 174–318 |
| RV2-L4 | "Hooks run via bash" | §3 wording |
| RV2-L5 | Takeaway imprecise; `sudo` line risky | Deny rules and sandbox named; "illustration only, don't run" box |
| RV2-L6 | README Prerequisites missed the floor | `:25` added |
| RV2-L7 | CLAUDE.md loads for learners | "contributors only" heading |
| RV2-L8 | Filesystem walk ≠ CI | `git ls-files` via `repo_files` |
| RV2-L9 | Lock generated with a different uv | Lock with 0.12.19 |
| RV2-L10 | Refusal path unclear | No network, no phases; the module ends |
| RV2-L11 | `HOME` and symlink guards | `: "${HOME:?}"`; links moved, not followed |
| RV2-L12 | A.1 ordering; `2.6:77` bridge; alias mix-up; `display.md` | `0.` / `A.1` placement; teaser cut; manual check for `בחן אותי`; noted |
