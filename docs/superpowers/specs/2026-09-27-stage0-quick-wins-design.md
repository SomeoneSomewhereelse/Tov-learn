# Stage 0 — Quick-Win PR: Design Spec

**Date:** 2026-09-27 · **Status:** approved in brainstorming, pending written-spec review
**Parent:** `docs/prds/project-redesign-2026-09-25.md` (the PRD). References such as "D2 item 5", "§3" and "R14" point there. "Review §2.x" points to `docs/reviews/project-review-2026-09-24.md`.
**Baseline:** `master` at `d04ca2a`. All line numbers below refer to that tree.
**Scope:** Stage 0 only:
- D2's 16 items
- the Stage 0 rows of the D7c lint table
- the three §6 rows assigned to the Stage 0 spec
- §3's Stage 0 "done when"
- three small gaps found while writing this spec (§2)

`courses/_archive/` is out of scope throughout.

---

## 1. Outcome and constraints

**Outcome:** one PR against `master` that:
- fixes what testers hit now: wrong course name, missing lessons, a broken hook, an unsafe lab, deprecated Supabase keys
- adds the first CI lints, each proven by a seeded regression
- moves the repo's CI to `node24` actions

**Constraints:**
- Fresh installs only, and testers only until the first-cohort gate (PRD Assumptions, D10).
- Stdlib-only Python in CI. No `pip`, no `.venv`.
- Edits are minimal and mechanical. Every rewrite stays with its Stage 1 slice.
- The one-unit-per-file rule (D10): Stage 0 touches `learn.md` and all 15 `learn/*.md` sub-modules. Most get frontmatter only, and six get body edits (§4.3). No other unit is open on them, because M depends on Stage 0.
- Workspace:
  - a manual worktree: `git worktree add ../Tov-learn-stage0 -b stage0/quick-wins master`
  - never `EnterWorktree`, because of the redaction wrapper
  - commit or push only when the user asks

---

## 2. Decisions made in this spec

| # | Decision | Reason |
|---|---|---|
| S1 | **Three PRD gaps are absorbed into Stage 0** (user-approved):<br>• **G1:** leaked LLM preambles also at `2.3_exercises.md:1` and `2.6_exercises.md:1`, not only `1.8_exercises.md:1`<br>• **G2:** global install also mentioned at `README.md:202`, `CONTRIBUTING.md:61` and `CLAUDE.md:14,75`<br>• **G4:** `resume.md:23,38,50,74` still offers the final project | Same defect class as the PRD item. The D10 docs rule. Leaving them would ship Stage 0 with the defect it claims to fix |
| S2 | **Hebrew aliases:**<br>• `עצור`/`סיום` = stop<br>• `בוחן`/`בוחן מלא` = quiz me / quiz me full<br>• `המשך` = continue<br>"בחן אותי" **stays diagnostic** | "בחן אותי" already means diagnostic mode (`learn.md:102`, `teaching.md:144`, `setup.md:225`). No word gets two meanings |
| S3 | **The 1.3 hook exercise guards a fake secret against *reading*.**<br>• PreToolUse, `matcher: "Read"`, `if: "Read(secret-demo.txt)"`, exit 2<br>• a live `cat` bypass shows how fragile hooks are | Nothing is written or deleted even if the guard fails. It teaches the corrected exit-code fact. The lesson's focus is hooks in general and their fragility |
| S4 | **Clean-slate moves, never deletes.** | The step contains no delete command, so "backs up before any delete" holds by construction. This reinterprets the PRD's "deletes" as "removes from where it causes harm" (see §8) |
| S5 | **Clean-slate checks three exact paths, with no globs.** | The PRD's `~/.claude/commands/learn*` would also match unrelated personal commands (e.g. `learning.md`) |
| S6 | **Lints are pure functions in `tests/validate_structure.py`, with stdlib `unittest` seeded-regression tests.** | Seeded regressions become permanent tests. It can move to pytest/uv later with no rewrite (§5.4) |
| S7 | **The route/reference lint scans only the tutor files** (`.claude/**/*.md`) | Lesson exercises cite `.claude/…` paths in the *learner's* lab project (e.g. `1.3_exercises.md:63`) |
| S8 | **Manual done-when checks are run by the user interactively and recorded in the PR description** | Headless `claude -p` can't exercise `AskUserQuestion` and doesn't reliably show hook-error notices |
| S9 | **`validate.yml` gets `permissions: contents: read`** | Least privilege, from the secure-use guide. A one-line addition to item 15 |
| S10 | **A new unit N (numbering contract) is proposed between F and 1a.** It's out of scope here (§9) | Renumbering churn (1a, 1b, 1c) comes before any later stage could prevent it |
| S11 | **`changes.md` gets one final `# Changes — stage0/quick-wins branch` section** in the file's current format, written once when the PR is ready (no rolling updates). No branch rename | The D10 docs rule (each unit documents its own change). The two most recent merged PRs (#12, #13) use typed branch names. F converts every section to Keep-a-Changelog (D10) |

---

## 3. Verified facts (2026-09-27)

Checked per D7b. Each row gives the source and method.

| Claim | Result | Source / method |
|---|---|---|
| `actions/checkout` latest is **v7.0.1**, commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, `using: node24` | Confirmed | GitHub API `releases`, `git/refs/tags/v7.0.1` (lightweight tag → commit); `action.yml` at that SHA |
| `actions/setup-python` latest is **v7.0.0**, commit `5fda3b95a4ea91299a34e894583c3862153e4b97`, `using: 'node24'` | Confirmed | same method |
| `checkout@v4` (`11d5960…`) and `setup-python@v5` (`a26af69…`) declare `node20` | Confirmed | `action.yml` at the tag's commit |
| The v7 release notes list no breaking change that affects `validate.yml` (checkout v7: blocks fork PR checkout for `pull_request_target`/`workflow_run`, ESM; setup-python v7: removes the `pip-install` input) | Confirmed; neither is used here | GitHub API `releases/tags/…` |
| Node 20 is retired on runners; JS actions run on Node 24 | Confirmed, dated 2026-09-23 | github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions |
| Only exit 2 blocks a PreToolUse call. Exit 1 is non-blocking, and the action goes ahead | Confirmed | code.claude.com/docs/en/hooks.md (raw), "Exit code 2" |
| A handler's `if` field uses permission-rule syntax and runs only on a match | Confirmed | hooks.md (raw), `if` field |
| Hooks run via bash; on Windows via Git Bash, or PowerShell when Git Bash isn't installed; a `shell` field overrides this | Confirmed | hooks.md (raw), `shell` field and "Shell form" |
| Hooks have no controlling terminal (so there's no Y/N prompt); `permissionDecision: "ask"` is the mechanism for confirmation | Confirmed | hooks.md (raw) |
| A bare filename in `Read(…)` follows gitignore rules and matches at any depth under the working directory | Confirmed | code.claude.com/docs/en/permissions.md (raw) |
| Read deny rules also cover `cat`/`head`/`tail`/`sed`/redirections that Claude Code recognizes, but not `grep -r` or scripts that open files themselves | Confirmed (teaching context only) | permissions.md (raw) |
| The sandbox is OS-enforced for Bash/PowerShell/Monitor and their child processes; macOS, Linux and WSL2 only; **not native Windows** | Confirmed (teaching context only) | code.claude.com/docs/en/sandboxing.md (raw) |
| `chattr +i`: "Only the superuser… can set or clear this attribute"; immutable blocks modification, not reads | Confirmed | `man chattr` (e2fsprogs) |
| Supabase is "deprecating the anon and service_role keys by the end of 2026"; env names `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY` | Confirmed (rendered page) | supabase.com/docs/guides/api/api-keys |
| Hosted MCP command `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?…"`; documented query parameters `read_only=true` and `project_ref=<id>` | Confirmed (rendered page) | supabase.com/docs/guides/getting-started/mcp |
| `timingSafeEqual` throws on unequal byte lengths | From the PRD §7; not re-checked (not date-sensitive) | nodejs/node `doc/api/crypto.md` |
| Command files accept `disable-model-invocation` frontmatter | From the PRD §7; not re-checked | code.claude.com/docs/en/skills.md |

**UNVERIFIED, deliberately not relied on:** the macOS and Windows equivalents of `chmod 000` + `chattr +i`. They are mentioned nowhere in Stage 0, and are passed to the 1a spec.

---

## 4. Design

### 4.1 Work groups

| Group | Items | Files |
|---|---|---|
| **P: Platform/CI** | 2, 9, 15 | `.github/workflows/validate.yml`, `tests/validate_structure.py`, **new** `tests/test_validate_structure.py`, `.claude/settings.json` |
| **C: Course content** | 1, 3, 4, 5 (+G1), 10, 16 | `courses/ai-dev/COURSE.md`; scripts and exercises in 0.2–0.4, 1.1–1.3, 1.6–1.8, 2.1–2.6 |
| **B: old_B** | 12 (content part) | `03-final-project/projects.md` → **new** `03-final-project/old_B-document-intelligence.md` |
| **T: Tutor** | 6, 7, 11, 12 (+G4), 14 | `.claude/commands/learn.md`; all 15 `learn/*.md` (frontmatter); body edits in `setup.md`, `security.md`, `project.md`, `resume.md` |
| **D: Docs** | 8 (+G2), 13, the CLAUDE.md test command, the `changes.md` section (S11) | `setup.md` §F, `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` (line 61 only), `changes.md` |

### 4.2 Course content (groups C and B)

#### Item 1: `COURSE.md`
- Add the rows `| 2.1 | מהו API | מעשי |` and `| 2.2 | עבודה עם API של Claude, OpenAI ו-Gemini | מעשי |` before the 2.3 row.
- Change the module 02 range from `2.3–2.6` to `2.1–2.6`.
- The module *name* "Claude API" stays. The rename is 1c's.

#### Item 3: VAT 17% → 18%
The four occurrences are `1.3_exercises.md:36`, `2.2_exercises.md:175`, `2.2_exercises.md:184` and `2.6_script.txt:53`. The implementer greps for any others in these three files and fixes them.

#### Item 4: 0.4 markers
Replace all 19 `[SLIDE TRANSITION]` in `0.4_script.txt` with `[מעבר שקף]`. No other change: the text stays English, and the Hebrew re-authoring is 1b's.

#### Item 5 + G1: archive residue
The spec sets the rules below. The implementation plan inventories every affected line.

- **The course name.**
  - Change the course-name uses to "AI Dev":
    - "…קורס AI Engineer" in `0.2_script.txt:3`, `0.3_script.txt:3` and `2.1_script.txt:2`
    - `- **קורס:** AI Engineer` in `0.2_exercises.md:7`, `0.3_exercises.md:7` and `0.4_exercises.md:7`
  - **Keep** the job-title uses: `0.2_script.txt:41,83,123-129,161`, `0.3_script.txt:111`, and the English "AI engineer" in `0.4_script.txt`.
- **The lesson's own number in headers and openings must match the folder:**
  - exercise H1 (`# תרגילים - שיעור X.Y: …`) and the `- **שיעור:** X.Y` line: 0.2, 0.3, 0.4, 1.7, 1.8 and 2.1–2.6
  - script title lines: `0.2` "שיעור 0.1" → 0.2, `0.3` "0.2" → 0.3, `0.4` "Lesson 0.3" → 0.4 (in both places in the opening)
  - spoken openings and closings: `1.1`–`1.8` "שלוש נקודה X" → "אחת נקודה X"; `2.1`–`2.6` "חמש נקודה X" → "שתיים נקודה X"; also forms the lint can't parse:
    - `2.3` "חמישי-שלוש"
    - `1.7` "בשיעור השביעי של המודול השלישי"
    - `1.8` "מודול שלוש" (twice)
    - `2.6` "בשיעור הקודם, חמש נקודה חמש"
    - `0.3` "לשיעור השני" (it's the third lesson)
- **Claims about lessons that never happened**, replaced with one or two true sentences in the file's own voice:
  - `1.1_script.txt:5`: the Make/n8n/WhatsApp/Telegram "previous lessons" sentence → a one-sentence bridge from Module 0 (AI fundamentals).
  - `0.2_script.txt:3` and `:13-15`: the 8-module / 156-hour / Make/n8n course description → the four modules as listed in `COURSE.md` (00–03). The "hands-on" sentence on line 3 is trimmed to what the course actually covers.
  - `1.2_script.txt:229-235`: "3.3" → "1.3" and "3.7" → "1.7", where those topics are taught today.
  - `1.8_script.txt`, the last slide: the "module 4 images" teaser → a one-line bridge to Module 02 (working with LLM APIs).
- **Leaked preambles (G1).** In `1.8_exercises.md`, `2.3_exercises.md` and `2.6_exercises.md`, delete line 1 ("בטח, …") and any blank or `---` lines that directly follow it, up to the first real content line (`<div dir="rtl" lang="he">`).
- **Voice.** Replacement Hebrew matches the surrounding file, including its transliteration style. The Hebrew style guide is F's (D9b). A Hebrew-speaking contributor reviews it in the PR.
- **Known churn.** 1b reorders Module 0 (D4a), so the 0.2/0.3/0.4 headers fixed here will be renumbered again there.

#### Item 10: the 1.3 hook exercise
**Exercise 5** (`1.3_exercises.md:75-85`) is rewritten:
1. **Setup.** In `claude-advanced-lab`, create:
   - `secret-demo.txt` with obviously fake content, e.g. `FAKE_API_KEY=not-a-real-key`
   - `notes.txt` with any text, as the control file
2. **The hook.** Add it in **project scope**, in `claude-advanced-lab/.claude/settings.json`:
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
   A native-Windows (no Git Bash) variant is shown with the same structure and `"command": "[Console]::Error.WriteLine('Blocked by hook: secret-demo.txt is protected'); exit 2"`.
3. **Negative test.** Restart Claude Code in the folder. Ask it to read `secret-demo.txt`. It is blocked, and Claude repeats the hook's reason.
4. **Positive control.** Ask it to read `notes.txt`. That works.
5. **The bypass, shown live.** Ask Claude to show `secret-demo.txt` "using the terminal". The hook matches only the Read tool, so `cat` or `Get-Content` gets through.
6. **Takeaway (text):**
   - Hooks are a deterministic guardrail for *specific tool calls*, not a security boundary.
   - Real enforcement lives outside Claude's layer. One Linux example is *mentioned* but **not** run: `chmod 000 secret-demo.txt && sudo chattr +i secret-demo.txt`.
   - "Keep secrets out of reach" means out of reach of every process the agent can start, not just "not in this folder".
7. **A note in place of the Y/N requirement:** hooks have no terminal, so they can't ask Y/N. The mechanism for asking is `permissionDecision: "ask"` (optional reading).

**Scripts and rubric:**
- `1.3_script.txt:27`: the exit-code sentence becomes "only exit code 2 blocks the action; exit code 1 is a non-blocking error, and the action goes ahead".
- `1.3_script.txt:29`: the guard demo becomes the read-guard demo above, in spoken form. The "ask Claude to delete a file" demo and the Python-bypass suggestion are removed.
- **Rubric row "יישום Hooks":** "blocks the Read of the protected file, explains exit 2 vs exit 1, and explains why `cat` bypasses the hook".

Nothing in the exercise or script deletes a file or asks the learner to try to.

#### Item 16: Supabase in 1.6
- `1.6_exercises.md:17`: "Anon Key" → "Publishable key" (`sb_publishable_…`).
- `:21`: `NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key` → `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...`
- `:30`: "Anon Key" → "Publishable key". The question stays about RLS.
- `:168`: `anon key` → publishable key, plus: "`SUPABASE_SECRET_KEY` is server-only: never with a `NEXT_PUBLIC_` prefix, never in git".
- `:99`: `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<your-project-ref>&read_only=true"`. It's scoped to one project and read-only, per D4c's "hosted read-only MCP".
- The `@supabase/ssr`/auth rewrite and removing Prisma stay in 1d.

#### Item 12, content part: old B
- Move `projects.md:174-320` ("## פרויקט ב: Document Intelligence Service", up to the line before "## פרויקט ג") verbatim to `courses/ai-dev/lessons/03-final-project/old_B-document-intelligence.md`.
- Add a one-line header note: unwired, not the new track B (PRD D5).
- A, C and D stay in `projects.md` untouched.

### 4.3 Tutor (group T)

#### Item 11: frontmatter
Each of the 15 files in `.claude/commands/learn/` gets a leading block:
```
---
disable-model-invocation: true
---
```
- No other keys.
- `learn.md` itself is unchanged here. Whether it stays model-invocable is S2a's question (§6).

#### Item 7: Hebrew aliases (S2)
- **`learn.md`, Learner Commands table:**
  - `continue / המשך`
  - `quiz me / בוחן`
  - `quiz me full / בוחן מלא`
  - `stop / עצור / סיום`
- **`learn.md`, Route table (lines 79–80):** the "quiz me" and "stop" trigger rows name the same Hebrew words.
- `teaching.md:144` and `setup.md:225` are unchanged.
- The orphan `display.md` is untouched; D8a folds it later.

#### Item 12 + G4: no capstones until 1e
- **`project.md`.** A new first section, `## Step 0 — TEMPORARY (until unit 1e)`:
  - It shows, in `session.language`, "the final projects are being rebuilt; meanwhile, continue with the lessons (`/learn`)".
  - It then **stops the module**, without reading `projects.md`.
  - Steps 1–5 stay as they are, as raw material for 1e.
- **`resume.md`:**
  - The eligibility paragraph (`:23`) and the two `🏗️ Final Project` template lines (`:38`, `:50`) are replaced by one TEMPORARY rule: "Do not offer the final project until unit 1e."
  - The Step 3 route row (`:74`) stays, so a learner who asks gets the message from `project.md`.

#### Item 6: `security.md`
- **Ownership gate.**
  - A new Pre-flight step runs after `target_url` is known and **before Phase A**. Phase A runs silently.
  - It asks with `AskUserQuestion`, in `session.language`: "Is this app yours, or do you have explicit permission to test it?"
  - Only the affirmative option ("yes, it's mine / I have permission") continues.
  - Any other answer, including free text, stops the module with a short explanation: testing a site without permission can harm it and may be illegal. It also offers to review the learner's own code instead (Phase A.2).
  - Every entry point passes through Pre-flight, including the `deploy` handoff and `security http…`.
- **`timingSafeEqual` (`:128-136`).** The snippet becomes:
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
  The explanation gains one sentence: `timingSafeEqual` throws when the lengths differ, so comparing the fixed-length SHA-256 digests avoids a 500 and also hides the key's length.

#### Item 14: the clean-slate step (S4, S5)
- **Placement:** in `setup.md`, a new `## A.0 Clean slate` before "## A. Show Current Settings".
- **Markers:** the section sits between `<!-- CLEAN-SLATE:BEGIN — TEMPORARY, remove at first-cohort gate (PRD D10) -->` and `<!-- CLEAN-SLATE:END -->`.

**Behaviour, in order:**
1. **Find.** Check exactly these paths, anchored on the home directory (`$HOME` in both bash and PowerShell), with no globs:
   - `$HOME/skill-tutor-tutorials/`
   - `$HOME/.claude/commands/learn.md`
   - `$HOME/.claude/commands/learn/`

   The repo itself contains a `skill-tutor-tutorials/` folder (the settings template), so relative paths are forbidden. If none exists, skip silently to A.
2. **Show.** List each path found, with its file count and newest modification date.
3. **Ask.** One `AskUserQuestion`, in Hebrew (the language isn't chosen until B):
   - `להשאיר הכל` (listed first): nothing is touched. For testers mid-test who want to keep their progress.
   - `להעביר לגיבוי ולהתחיל מחדש`: everything moves to `~/skill-tutor-tutorials-backup-<date>`; nothing is deleted.

   Only the second option counts as yes. Free text, "Other" or anything ambiguous counts as keep.
4. **Move.** Give a bash variant (macOS, Linux, WSL, Git Bash) and a PowerShell variant (native Windows without Git Bash). The model uses whichever shell tool it has. Reference shape, bash:
   ```bash
   ts=$(date +%Y%m%d-%H%M%S)
   dest="$HOME/skill-tutor-tutorials-backup-$ts"
   mkdir "$dest" && mkdir "$dest/commands" || exit 1
   if [ -e "$HOME/skill-tutor-tutorials" ]; then mv "$HOME/skill-tutor-tutorials" "$dest/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn.md" ]; then mv "$HOME/.claude/commands/learn.md" "$dest/commands/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn" ]; then mv "$HOME/.claude/commands/learn" "$dest/commands/" || exit 1; fi
   ```
   The PowerShell variant does the same with `New-Item -ItemType Directory -ErrorAction Stop` and `Move-Item -LiteralPath … -ErrorAction Stop`.
   - `mkdir` without `-p` makes the step fail rather than reuse an existing folder.
   - On any error: stop, and report what moved and what didn't. Never retry with force, never fall back to a delete.
5. **Verify and report.** Confirm each original path is gone and present in the backup. Print the backup path. The tester can delete it whenever they like.
6. **Continue or stop.**
   - If a global command was moved: **stop setup**, and tell the tester to close and reopen Claude Code, then run `/learn setup` again. The running session may still be using the old `/learn`.
   - If only data was moved: continue to A. A finds no settings and goes to B.

**Hard rules, stated in the section:**
- only the three paths
- never anything inside the repo, including `.claude/settings.local.json` and the repo's `skill-tutor-tutorials/`
- never an earlier backup folder
- no delete command of any kind
- when in doubt, keep

### 4.4 Docs (group D)

#### Item 8 + G2: remove the global install
- **`setup.md`:** delete "## F. Global Install (optional)" entirely (`:279-309`), and re-letter "## G. Setup Complete — REQUIRED" to **F**.
- **`README.md`:** delete `:46` (the "Optionally install `/learn` globally" bullet) and `:202` (step 4 of "Adding a New Module").
- **`CLAUDE.md`:**
  - The Setup row (`:14`) drops "global install".
  - Step 4 of "הוספת מודול חדש" (`:75`) is deleted.
- **`CONTRIBUTING.md`:** delete `:61` only. Everything else in it is F's.
- The existing `changes.md` sections are history and are left unchanged.

#### Item 13: README tester note
- **Placement:** directly under the README's title/banner, between `<!-- TEMPORARY: remove at first-cohort gate (PRD D10) -->` and `<!-- /TEMPORARY -->`, as a blockquote.
- **Text:** the PRD's wording ("Fresh install only. Before testing, delete `~/skill-tutor-tutorials/` (`%USERPROFILE%\skill-tutor-tutorials` on Windows) and any old global install at `~/.claude/commands/learn.md` and `~/.claude/commands/learn/`."), plus: "…or run `/learn setup`, which offers to move them into a backup for you."

#### `changes.md` section (S11)
- **Where:** appended as a new H1, `# Changes — stage0/quick-wins branch`, after the existing sections. It matches the existing `# Changes — <branch> branch` style: an Overview, numbered `##` entries with Before/After, and a File Map.
- **When:** written **once**, as the last commit of group D, when the PR is otherwise complete. No rolling updates.
- **Content:**
  - one numbered entry per learner- or contributor-visible change (the 16 items and G1/G2/G4), grouped as in §4.1
  - a **Testers** note: "reset your data, or run `/learn setup` and choose the backup option"
- F later converts every section, this one included, to Keep-a-Changelog (D10).

#### Test command in `CLAUDE.md`
A new short section, "## בדיקות":
```
python -m unittest discover -s tests -v && python tests/validate_structure.py
```
It adds a note: use `py -3` instead of `python` on Windows.

---

## 5. Lints, tests and CI (group P)

### 5.1 `tests/validate_structure.py`
- It becomes a set of pure functions, `check_<name>(root: Path) -> list[str]`.
  - Each finding is formatted `path:line: [check] message`, with the path relative to the root.
  - The functions don't print and don't exit.
- `main()` runs every check against the repo root, prints `PASSED — all checks OK` or `FAILED — N error(s)` with the findings, and exits 1 on any finding. It runs under `if __name__ == "__main__":`. Nothing runs at import time.
- **Course scope,** shared by all course checks: `courses/*/` except `courses/_archive/`, skipping any file whose name starts with `old_B`.

| Check | Rule |
|---|---|
| `course_md` | For each course with a `COURSE.md`:<br>(a) the set of lesson numbers in the "רשימת שיעורים" table **equals** the set of lesson folders `lessons/*/<X.Y>-*`, both directions<br>(b) the table order equals the numeric folder order<br>(c) each module-table row's folder exists, and its range cell equals `<min>–<max>` of that folder's lessons, or `—` when it has none. Both `–` and `-` are accepted |
| `slide_markers` | Every `*_script.txt` has **≥ 5** `[מעבר שקף]` (today's minimum is 7) and **zero** `[SLIDE TRANSITION]` |
| `header_numbers` | **Exercises:** the first `# ` heading contains `שיעור X.Y`, and any `**שיעור:**` line contains `X.Y`; both equal the folder number.<br>**Scripts:** within the first 3 non-empty lines, every `(שיעור\|Lesson)\s+X.Y` and every spelled `שיעור\s+W\s+נקודה\s+W` equals the folder number. `W` is mapped by a digit-word table (אפס; אחת/אחד; שתיים/שניים/שתים; שלוש/שלושה; ארבע/ארבעה; חמש/חמישה; שש/שישה; שבע/שבעה; שמונה; תשע/תשעה); an unknown word is a finding. It matches inside prefixed words (לשיעור, בשיעור) |
| `course_name_denylist` | No match for any of these in course scope:<br>• `קורס\s+(ה-)?AI Engineer`<br>• `\*\*קורס:\*\*\s*AI Engineer`<br>• `AI Engineer course` (case-insensitive)<br>The bare job title "AI Engineer" passes. Stage 0 adds only these entries, because it fixes all of them; the rest come in F with the baseline (D7c) |
| `tutor_refs` | In every `.claude/**/*.md`:<br>(a) every backticked path starting with `.claude/` or `courses/` exists relative to the repo root<br>(b) every bare backticked `name.md` (no `/`) on a line containing `Read`/`read`/`Load`/`load` exists in the same folder as the referring file<br>It skips `~/…` paths and placeholders containing `[`, `{`, `*` or `X.Y`. This replaces the hard-coded 6-module list and the `CROSS_REFS` dict |
| `settings_json` | `.claude/settings.json`, if present, parses as JSON, and its text contains no `powershell` (case-insensitive) |
| `relative_links` | In every `*.md` under the root, every `[text](target)` whose target is not `http:`/`https:`/`mailto:`/`#…` resolves relative to the file, after stripping `#fragment`.<br>Skips: fenced code blocks, `.git/`, dot-folders other than `.claude/` and `.github/` (so the local `.review-panel/` is excluded), `_archive/`, `old_B*` files |
| `clean_slate_no_delete` | *Temporary, removed at the gate with the section.* The text between `CLEAN-SLATE:BEGIN` and `CLEAN-SLATE:END` in `.claude/commands/learn/setup.md` contains none of `rm `, `rmdir`, `Remove-Item`, `del `. Missing markers are *not* a finding, so the check survives the gate removal until it's deleted too |
| `lesson_files` *(existing)* | Every lesson folder has a `*_script.txt` and an `*_exercises.md`; now course-scoped (skips `_archive/`) |
| `teaching_step5` *(existing)* | `.claude/commands/learn/teaching.md` contains "Step 5" |

### 5.2 `tests/test_validate_structure.py`
- **Framework:** stdlib `unittest`. It imports `validate_structure` from the same folder, so `discover -s tests` puts it on `sys.path`.
- **`make_good_tree(tmp)`** builds a minimal valid repo:
  - one course with two modules and three lessons
  - valid scripts and exercises
  - `COURSE.md`
  - `.claude/commands/learn.md` with routes, plus two sub-modules
  - `.claude/settings.json`
  - a README with a relative link
  - `setup.md` with CLEAN-SLATE markers
- **`test_good_tree_passes`:** every check returns `[]`.
- **Seeded regressions:** each mutates the good tree once, asserts the named check returns ≥ 1 finding, and asserts every other check still returns `[]`. At minimum:
  - `course_md`: a missing row; an extra row with no folder; two rows swapped; a wrong module range
  - `slide_markers`: 4 markers; one `[SLIDE TRANSITION]`
  - `header_numbers`: exercise H1 `שיעור 5.1` in the 2.1 folder; a mismatched `**שיעור:**`; script `שיעור 0.1` in the 0.2 folder; spelled `חמש נקודה אחת` in the 2.1 folder
  - `course_name_denylist`: `בקורס AI Engineer`; `- **קורס:** AI Engineer`
  - `tutor_refs`: a route to a missing `.claude/commands/learn/missing.md`; a bare `Read \`missing.md\``
  - `settings_json`: `powershell` in the command; invalid JSON
  - `relative_links`: a link to a missing file
  - `clean_slate_no_delete`: `rm -rf` between the markers
  - `lesson_files`: a lesson with no exercises
  - `teaching_step5`: "Step 5" removed
- **Must-pass negative cases:**
  - the job title `AI Engineer הוא…`
  - a denied string inside `_archive/`
  - a denied string inside `old_B-x.md`
  - a `~/…` reference
  - an `http(s)` link, a `#anchor` link, and a broken link inside a code fence
  - `rm` outside the CLEAN-SLATE markers
  - a missing `settings.json`
- **`test_real_repo_passes`:** every check returns `[]` on the real repo. It's red until groups C, T and D land; that red → green is the done-when evidence.

### 5.3 `.github/workflows/validate.yml`
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
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.11"
      - name: Seeded-regression tests
        run: python -m unittest discover -s tests -v
      - name: Structural validation
        run: python tests/validate_structure.py
```

### 5.4 Item 2 and forward compatibility
- **Item 2:** `.claude/settings.json` becomes `{}`. The file stays for the settings check and for later units. `auto-save-progress.ps1` stays for M to drop (D8a).
- **pytest/uv later.** pytest collects `unittest.TestCase` tests as they are. Adopting it takes three changes:
  1. `pyproject.toml` with a dev group (`uv add --dev pytest`)
  2. `astral-sh/setup-uv` in CI, SHA-pinned and checked for `node24` at the time, then `uv run pytest`
  3. the CLAUDE.md test command

  Two design rules keep this true: no import-time work, and root-parameterized checks.

---

## 6. Verification and the PR

### 6.1 Commit order
In `../Tov-learn-stage0`, on branch `stage0/quick-wins`, and only when the user asks:
1. **P1:** `validate.yml`
2. **P2:** the validator rewrite and the tests. The commit message lists the findings on the current tree (the red state).
3. **P3:** `settings.json` → `{}`
4. **C:** COURSE.md → VAT → 0.4 markers → residue → 1.3 hook → 1.6 Supabase → old_B, one commit each
5. **T:** frontmatter → aliases → project/resume → security → clean-slate
6. **D:** global-install removal → tester note → test command → `changes.md` section (last)

Each commit is followed by a local run of the test command. The last commit must be fully green.

### 6.2 The PR description (required sections)
- **Summary:** a table of the 16 items and G1/G2/G4, each mapped to its commit, plus a link to the new `changes.md` section.
- **Automated verification:**
  - the unittest output, including the seeded-regression list
  - the validator's `PASSED`
  - the Actions run link
  - the pasted command and output showing no Node 20 / deprecation annotation (`gh run view <id>` plus the check-runs annotations API)
- **Manual verification.** The user runs these interactively in the worktree. Each records its steps, date, OS/shell, who ran it, the result and fixture cleanup. This machine has no `~/skill-tutor-tutorials/` and no `~/.claude/commands/`, so the fixtures can't overwrite real data.
  1. **Resume:** create fake `~/skill-tutor-tutorials/progress/lesson-0.1.md` … `lesson-1.8.md`, plus a minimal `settings.json` and `learner_profile.md`, so neither setup nor the profile questions run. Run `/learn`. It must offer lesson 2.1 as the next new lesson. Remove the fixtures afterwards.
  2. **Hook error:** in a Claude Code session in the worktree, get two replies. No "hook error" notice may appear.
  3. **Clean-slate:** create fake leftovers at the three paths. Run `/learn setup`:
     - Choose `להשאיר הכל`: nothing moved.
     - Run it again and choose `להעביר לגיבוי ולהתחיל מחדש`: all three paths are in the timestamped backup, the originals are gone, `git status` in the worktree is clean, and `.claude/settings.local.json` is untouched.
     - Remove the backup afterwards.
- **Future concerns:** the §9 list.
- **Reviewer note:** Hebrew text changes need a Hebrew-speaking contributor's approval (D9b's intent; branch protection itself lands in G).

### 6.3 Done-when (§3) → proof

| Done when | Proof |
|---|---|
| Each new lint fails on a seeded regression and passes on the fixed tree | §5.2 seeded regressions, `test_real_repo_passes`, and the P2 commit message |
| `resume` offers 2.1 after 1.8 | `course_md` (b) plus manual check 1 |
| 0.4 splits into slides | `slide_markers` |
| No hook error after replies | `settings_json` plus manual check 2 |
| `validate.yml` runs with no Node deprecation warning | the annotations evidence in the PR |
| The clean-slate step backs up before any delete | by construction (S4), `clean_slate_no_delete`, and manual check 3 |

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| The heuristic `header_numbers` misses a spoken number form | The residue rules (§4.2) list the unparseable forms for hand-fixing. Unit N replaces the heuristic (§9) |
| The replacement Hebrew reads badly | Minimal edits in the file's own voice; a Hebrew-speaking reviewer in the PR |
| A clean-slate move fails part-way | It stops at the first error and reports; nothing is deleted, so nothing is lost |
| An action tag is re-pointed upstream | SHA pins (D7d) |
| A tester keeps a stale global `/learn` running after the move | Setup stops and tells them to restart Claude Code |

---

## 8. Proposed PRD amendments

Recorded here and to be applied to the PRD in a separate, approved edit:
1. **D2 item 5:** add the preambles at `2.3_exercises.md:1` and `2.6_exercises.md:1` (G1).
2. **D2 item 8:** add `README.md:202`, `CONTRIBUTING.md:61` and `CLAUDE.md:14,75` (G2).
3. **D2 item 12:** `resume.md` also stops offering the final project until 1e (G4).
4. **D2 item 7:** the alias set is as in S2. "בחן אותי" stays diagnostic.
5. **D2 item 14:** "backs up and deletes" is implemented as a **move** into a timestamped backup, with exact paths (not `learn*`).
6. **New unit N (numbering contract)** between F and 1a, in §3 and D1's order: 0 → M → F → **N** → G → 1a → … (§9).

---

## 9. Out of scope: future concerns

| Unit | Concern carried forward from this spec |
|---|---|
| M | Drop `auto-save-progress.ps1` and the slide viewer; the CLAUDE.md module table and its lint; the `tutor_refs` check must pass on `.claude/skills/learn/` |
| F | `landscape.md`; the baseline, model-string and full denylist lints; the rest of CONTRIBUTING; the Hebrew style guide; `changes.md` format |
| **N (proposed)** | **Numbering contract:**<br>• stable lesson ids (the folder slug) as the contract; numbers derived<br>• one manifest (id → number, title, module, order)<br>• a deterministic generator for COURSE.md tables, exercise H1/`**שיעור:**` lines and script title lines (inside `<!-- generated -->` markers)<br>• CI `--check` (regenerate and diff)<br>• prose cross-references as id references rendered by the tutor<br>• a lint against literal lesson numbers in prose<br>• a thin skill (`renumber`/`add-lesson`) that calls the generator and lists what's left for human review<br>• a new CLAUDE.md rule: run the generator before any push (a convenience; CI `--check` stays the enforcement)<br>Replaces Stage 0's heuristic `header_numbers`. Needs its own spec and the PRD amendment (§8) |
| G | Interpreter resolution; owned `settings.local.json` entries; the no-`python3` lint; branch protection |
| 1a | The full 1.3 hook lab and its non-destructive target; macOS/Windows equivalents of `chmod 000` + `chattr +i` (UNVERIFIED); 1.2 fixes; 1.1 homework |
| 1b | Module 0 reorder; the 0.x headers fixed here get renumbered again |
| 1c | Module 02 rename, including the folder |
| 1d | `@supabase/ssr`/auth rewrite; removing Prisma |
| 1e | Restore `/learn project` and the `resume.md` offer; delete the TEMPORARY blocks added in §4.3 |
| Gate | Remove the README tester note, the CLEAN-SLATE section and the `clean_slate_no_delete` check |
| S2a | Whether `learn.md` stays model-invocable; pytest 3-OS CI |
