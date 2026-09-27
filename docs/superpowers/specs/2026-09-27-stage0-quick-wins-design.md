# Stage 0 — Quick-Win PR: Design Spec

**Date:** 2026-09-27 · **Revision:** 2, after the first independent review (§10) · **Status:** approved in brainstorming; pending the second independent review
**Parent:** `docs/prds/project-redesign-2026-09-25.md` (the PRD). References such as "D2 item 5", "§3" and "R14" point there. "Review §2.x" points to `docs/reviews/project-review-2026-09-24.md`. "RV-H1" etc. point to the first spec review (§10).
**Baseline:** `master` at `d04ca2a`. All line numbers below refer to that tree.
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
  - **uv is a hard requirement for contributors.** The only supported entry point for tests and lint is `uv run pytest -q && uv run ruff check -q`.
  - **This does not apply to learners.** Learner-facing docs never mention uv. The PRD D8b learner CLI (`tovlearn.py`, run via the interpreter that setup resolves) must not inherit this requirement. That's a constraint on G and S2a (§9).
- Edits are minimal and mechanical. Every rewrite stays with its Stage 1 slice.
- **One-unit-per-file rule (D10).** Stage 0 touches `learn.md` and all 15 `learn/*.md` sub-modules. All 15 get frontmatter. Four also get body edits: `setup.md`, `security.md`, `project.md` and `resume.md`. `learn.md` gets body edits too. No other unit is open on these files, because M depends on Stage 0.
- **Workspace:**
  - a manual worktree: `git worktree add ../Tov-learn-stage0 -b fix/stage0-quick-wins master`
  - never `EnterWorktree`, because of the redaction wrapper
  - uv creates the worktree's own `.venv`
  - commit or push only when the user asks

---

## 2. Decisions made in this spec

| # | Decision | Reason |
|---|---|---|
| S1 | **Three PRD gaps are absorbed** (user-approved):<br>• **G1:** leaked preambles also at `2.3_exercises.md:1` and `2.6_exercises.md:1`<br>• **G2:** global install also at `README.md:202`, `CONTRIBUTING.md:61` and `CLAUDE.md:14,75`<br>• **G4:** `resume.md:23,38,50,74` still offers the final project | Same defect class as the PRD item. The D10 docs rule |
| S2 | **Hebrew aliases:**<br>• `עצור`/`סיום` = stop<br>• `בוחן`/`בוחן מלא` = quiz me / quiz me full<br>• `המשך` = continue<br>"בחן אותי" **stays diagnostic** | "בחן אותי" already means diagnostic (`learn.md:102`, `teaching.md:144`, `setup.md:225`) |
| S3 | **The 1.3 hook exercise guards a fake secret against *reading*.**<br>• PreToolUse, `matcher: "Read"`, `if: "Read(secret-demo.txt)"`, exit 2<br>• a live `cat` bypass shows how fragile hooks are | Nothing is written or deleted even if the guard fails. The lesson's focus is hooks in general and their fragility |
| S4 | **Clean-slate moves, never deletes** | "Backs up before any delete" holds by construction. It reinterprets the PRD's "deletes" (§8) |
| S5 | **Clean-slate checks three exact paths, with no globs** | `learn*` would also match unrelated personal commands |
| S6 | **Lints are `check_*` functions in `tests/validate_structure.py`, tested with pytest; ruff lints the Python; everything runs through uv** | Seeded regressions become permanent tests. uv pins the toolchain (user decision) |
| S7 | **The route/reference lint scans only the tutor files** (`.claude/**/*.md`) | Exercises cite `.claude/…` paths in the learner's lab project |
| S8 | **Manual done-when checks are run by the user interactively and recorded in the PR** | Headless `claude -p` can't exercise `AskUserQuestion` or show hook-error notices reliably |
| S9 | **`validate.yml` gets `permissions: contents: read`** | Least privilege, from the secure-use guide |
| S10 | **A new unit N (numbering contract) is proposed between F and 1a** (§9) | Renumbering churn comes before any later stage |
| S11 | **`changes.md` gets one final `# Changes — fix/stage0-quick-wins branch` section**, in the file's current format, written once (no rolling updates). The branch is named `fix/stage0-quick-wins` | The D10 docs rule. Typed branch names follow the most recent merged PRs (#12, #13: `fix/…`). F converts every section to Keep-a-Changelog |
| S12 | **uv is a hard requirement for contributors only** (§1). The validator is a library module with no `main()`. `test_real_repo_passes` reports the findings | One supported entry point (user decision) |
| S13 | **Python is pinned to 3.14:** `requires-python = ">=3.14,<3.15"` and a `.python-version` file containing `3.14` | The current release, supported until 2030-10-31 (user decision) |
| S14 | **Claude Code minimum is 2.1.176**, a floor, not an exact pin. It's stated in `1.3_exercises.md:8` and README "Requirements". `/learn setup` warns below it | 2.1.176 fixed `if` path matching for `Read(...)`, which S3 depends on. It's the lowest version that meets every verified requirement (user decision). An exact pin would block security updates |
| S15 | **Dependabot is adopted now for `github-actions` only**, weekly. The `uv` ecosystem is deferred | Keeps the SHA pins from going stale silently (PRD §6 row). Dependabot's documented uv version is v0.11, and 0.12 lockfile support is unverified |
| S16 | **The Supabase MCP stays read-only. `1.6_exercises.md:103` is rewritten**: describe via MCP, then insert in the Table Editor (RV-H2) | Beginners get a read-only boundary. The exercise must not fail as written |

---

## 3. Verified facts (2026-09-27)

Checked per D7b. "(reviewer)" marks facts the first spec review verified that are not re-checked here.

| Claim | Result | Source / method |
|---|---|---|
| `actions/checkout` latest is **v7.0.1**, commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, `using: node24` | Confirmed | GitHub API `releases`, `git/refs/tags` (lightweight tag); `action.yml` at that SHA |
| `astral-sh/setup-uv` latest is **v10.2.0** (2026-09-21), commit `c18668ad3cf93ea998bef934396af7bb5c839dc7`, `using: "node24"`, with `version`/`python-version`/`version-file` inputs | Confirmed | same method |
| `checkout@v4` / `setup-python@v5` declare `node20` | Confirmed | `action.yml` at the tag's commit |
| Node 20 is retired on runners; JS actions run on Node 24 | Confirmed, dated 2026-09-23 | github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions |
| uv latest is **0.12.19** (2026-09-25); pytest **9.1.1** (requires Python ≥3.10); ruff **0.16.9** | Confirmed | GitHub API `astral-sh/uv` releases; PyPI JSON |
| `ruff check -q` means "Print diagnostics, but nothing else" | Confirmed | `ruff check --help`, ruff 0.16.9 |
| Python 3.14 is current (3.14.7), supported until 2030-10-31 | Confirmed | endoflife.date/api/python.json |
| Dependabot supports the `github-actions` and `uv` ecosystems; the uv row lists **v0.11** | Confirmed | docs.github.com (article-body API), "Supported ecosystems and repositories" |
| Only exit 2 blocks a PreToolUse call; exit 1 is non-blocking | Confirmed | code.claude.com/docs/en/hooks.md (raw) |
| The hook `if` field was added in **2.1.85**; `if` path patterns for Read/Edit/Write (e.g. `Read(.env)`) match correctly from **2.1.176** | Confirmed | anthropics/claude-code `CHANGELOG.md` (raw), under the `## 2.1.85` and `## 2.1.176` headings |
| Hooks run via bash; on Windows via Git Bash, or PowerShell without it; there's no controlling terminal; `permissionDecision: "ask"` exists | Confirmed | hooks.md (raw) |
| A bare filename in `Read(…)` matches at any depth under the working directory | Confirmed | permissions.md (raw) |
| Read deny rules cover `cat`/`head`/`tail`/`sed`/redirections, not `grep -r` or scripts | Confirmed (teaching context) | permissions.md (raw) |
| Sandbox is OS-enforced; not native Windows | Confirmed (teaching context) | sandboxing.md (raw) |
| Same-name skills and commands: "Enterprise over personal, and personal over project" | Confirmed | skills.md (raw), "Resolve skills that share a name" |
| In a worktree, Claude Code uses the main checkout's `.claude/settings.local.json` | (reviewer) | code.claude.com/docs/en/settings.md |
| `chattr +i` can be set or cleared only by the superuser | Confirmed | `man chattr` |
| Supabase deprecates anon/service_role keys by the end of 2026; env names `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` | Confirmed (rendered) | supabase.com/docs/guides/api/api-keys |
| Hosted MCP command, plus the `read_only=true` / `project_ref=` parameters | Confirmed (rendered) | supabase.com/docs/guides/getting-started/mcp |
| `timingSafeEqual` throws on unequal lengths; command files accept `disable-model-invocation` | PRD §7 (not date-sensitive) | nodejs `crypto.md`; skills.md |

**UNVERIFIED, deliberately not relied on:**
- macOS/Windows equivalents of `chmod 000` + `chattr +i` (→ 1a)
- whether Dependabot handles uv 0.12 lockfiles (→ S15)
- the native-PowerShell variant of the 1.3 hook. It follows hooks.md, but no Windows machine is available to test it. The PR says so (§6)

---

## 4. Design

### 4.1 Work groups

| Group | Items | Files |
|---|---|---|
| **P: Platform/CI** | 2, 9, 15, S6/S12/S13/S15 | `.github/workflows/validate.yml`, **new** `.github/dependabot.yml`, **new** `pyproject.toml`, **new** `uv.lock`, **new** `.python-version`, `.gitignore`, `tests/validate_structure.py`, **new** `tests/test_validate_structure.py`, `.claude/settings.json` |
| **C: Course content** | 1, 3, 4, 5 (+G1, RV-M1), 10 (+RV-L2, S14), 16 (+RV-H2, RV-M6) | `COURSE.md`; scripts/exercises in 0.2–0.4, 1.1–1.3, 1.6–1.8, 2.1–2.6 |
| **B: old_B** | 12 (content part) | `projects.md` → **new** `03-final-project/old_B-document-intelligence.md` |
| **T: Tutor** | 6, 7, 11, 12 (+G4), 14, S14 setup check | `learn.md`; all 15 `learn/*.md` (frontmatter); body edits in `setup.md`, `security.md`, `project.md`, `resume.md` |
| **D: Docs** | 8 (+G2), 13, test command, S11, RV-L6 | `setup.md` §F, `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` (lines 57–61 and 65–68 only), `changes.md` |

### 4.2 Course content (groups C and B)

#### Item 1: `COURSE.md`
- Add `| 2.1 | מהו API | מעשי |` and `| 2.2 | עבודה עם API של Claude, OpenAI ו-Gemini | מעשי |` before the 2.3 row.
- Change the module 02 range `2.3–2.6` → `2.1–2.6`.
- The module name stays; the rename is 1c's.

#### Item 3: VAT 17% → 18% (RV-M2)
There are five occurrences, and every one is fixed:
- `1.3_exercises.md:36` ("17%")
- `2.2_exercises.md:175` (docstring "17% VAT")
- `2.2_exercises.md:176` (`vat_rate = 0.17` → `0.18`)
- `2.2_exercises.md:184` (tool description "17%")
- `2.6_script.txt:53` (spelled "שבעה עשר אחוז" → "שמונה עשר אחוז")

The implementer also greps these files for `17%`, `0.17` and `שבעה עשר`, so none are missed.

#### Item 4: 0.4 markers
Replace all 19 `[SLIDE TRANSITION]` in `0.4_script.txt` with `[מעבר שקף]`. No other change.

#### Item 5 + G1 + RV-M1: archive residue
The plan inventories every line. The rules are:

- **The course name.**
  - Change the course-name uses to "AI Dev":
    - "…קורס AI Engineer" in `0.2_script.txt:3`, `0.3_script.txt:3` and `2.1_script.txt:2`
    - `- **קורס:** AI Engineer` in `0.2/0.3/0.4_exercises.md:7`
  - **Keep** the job-title uses: `0.2_script.txt:9,41,83,123-129,161`, `0.3_script.txt:111`, and the English "AI engineer" in `0.4_script.txt`.
- **The lesson's own number must match the folder:**
  - exercise H1 and `- **שיעור:**` lines in 0.2, 0.3, 0.4, 1.7, 1.8 and 2.1–2.6
  - script title lines: `0.2` → 0.2, `0.3` → 0.3, `0.4` "Lesson 0.3" → 0.4, in both places in the opening
  - spoken openings and closings: `1.1`–`1.8` "שלוש נקודה X" → "אחת נקודה X"; `2.1`–`2.6` "חמש נקודה X" → "שתיים נקודה X"
  - forms the lint can't parse:
    - `2.3` "חמישי-שלוש"
    - `1.7` "המודול השלישי"
    - `1.8` "מודול שלוש" (twice)
    - `1.1_script.txt:165` "בהמשך מודול שלוש"
    - `2.6` "בשיעור הקודם, חמש נקודה חמש"
    - `0.3` "לשיעור השני" (it's the third lesson)
- **Cross-references to lessons and modules that don't exist or have moved.** Each is replaced with the real lesson or module, or cut:
  - `1.1_script.txt:5`: the Make/n8n/WhatsApp/Telegram "previous lessons" sentence → a one-sentence bridge from Module 0.
  - `0.2_script.txt:3` and `:13-15`: the 8-module / 156-hour / Make/n8n description → the four modules from `COURSE.md`. The line-3 "hands-on" sentence is trimmed to what the course covers.
  - `0.2_script.txt:137` and `:165`: "בשיעור 0.3" for prompt engineering → "בשיעור 0.4".
  - `0.2_exercises.md:146-149`: the module mapping ("מודולים 1+2", "מודול 3", "1+6", "2+5") → the real AI Dev modules (01 Claude Code, 02 APIs, 03 final project). A row with no real counterpart is cut.
  - `0.3_script.txt:57`: "Make ו-n8n… נלמד את זה לעומק במודול הראשון" → cut the promise. The factual clause about Make/n8n working through an API stays.
  - `0.3_script.txt:87`: "במודול חמש" → "במודול 02".
  - `0.3_exercises.md:59`: "n8n / Make… במודולים 1 ו-2" → cut the promise.
  - `1.2_script.txt:229-235`: "3.3" → "1.3", "3.7" → "1.7".
  - `1.8_script.txt`, the last slide: the "module 4 images" teaser → a one-line bridge to Module 02.
  - `2.1_script.txt:5`: "במודול הקודם, ובמיוחד בשיעור ארבע נקודה שש… נכסים שיווקיים… סרטונים" → a bridge from Module 01 (building apps with Claude Code).
  - `2.6_script.txt:77`: "במודול שש… בשיעור הבא, שש נקודה אחת" → a bridge to the final project (module 03).
- **Leaked preambles (G1).** In `1.8`, `2.3` and `2.6_exercises.md`, delete line 1 ("בטח, …") and any blank or `---` lines that directly follow it, up to `<div dir="rtl" lang="he">`.
- **Voice.** Replacement Hebrew matches the surrounding file. A Hebrew-speaking contributor reviews it in the PR.
- **Known churn.** 1b reorders Module 0 (D4a), so these 0.x numbers change again there.

#### Item 10: the 1.3 hook exercise
**Exercise 5** (`1.3_exercises.md:75-85`) is rewritten:
1. **Setup.** In `claude-advanced-lab`, create `secret-demo.txt` with obviously fake content (`FAKE_API_KEY=not-a-real-key`) and `notes.txt` with any text.
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
   A native-Windows (no Git Bash) variant uses `"command": "[Console]::Error.WriteLine('Blocked by hook: secret-demo.txt is protected'); exit 2"`.
3. **Negative test.** Restart Claude Code in the folder and ask it to read `secret-demo.txt`. It is blocked, and Claude repeats the reason. *If Claude immediately tries the terminal on its own, that's step 5 happening early. Note it and carry on.*
4. **Positive control.** Ask it to read `notes.txt`. That works.
5. **The bypass.** Ask explicitly: "run `cat secret-demo.txt` in the terminal" (Windows without Git Bash: `Get-Content secret-demo.txt`). The hook matches only the Read tool, so the content appears.
   - *Fallback if Claude declines:* the refusal is model behaviour, not enforcement, and the next session may decide differently. That's the point of the lesson. The learner records what happened.
6. **Takeaway (text):**
   - Hooks are a deterministic guardrail for specific tool calls, not a security boundary. Other tools, such as Bash, PowerShell and Grep, can still reach the content.
   - Real enforcement lives outside Claude's layer. One Linux example is *mentioned*, not run: `chmod 000 secret-demo.txt && sudo chattr +i secret-demo.txt`.
   - "Out of reach" means out of reach of every process the agent can start.
7. **A note in place of the Y/N requirement:** hooks have no terminal, so they can't ask Y/N. The mechanism for asking is `permissionDecision: "ask"` (optional reading).

**Related edits (RV-L2, S14):**
- `1.3_exercises.md:8`: "v2.1.59+" → "v2.1.176+" (S14).
- `1.3_script.txt:25`: "הוק הוא קוד קשיח שחוסם פעולה באופן מוחלט" is softened to match the takeaway: deterministic for the tool call it matches, not an absolute block.
- `1.3_script.txt:27`: "only exit code 2 blocks the action; exit code 1 is a non-blocking error, and the action goes ahead".
- `1.3_script.txt:29`: becomes the read-guard demo in spoken form. The file-deletion demo and the Python-bypass suggestion are gone.
- `1.3_exercises.md:60`: the "automatic via Hooks (exercise 5)" claim → skills are triggered by their `description`; exercise 5 no longer runs a skill.
- `1.3_exercises.md:114`: "סקריפט ה-Hook" → "the `.claude/settings.json` with the hook".
- **Rubric "יישום Hooks":** "blocks the Read of the protected file, explains exit 2 vs exit 1, and explains why `cat` bypasses the hook".

Nothing deletes a file or asks the learner to try to.

#### Item 16 + RV-H2 + RV-M6: Supabase in 1.6
- `1.6_exercises.md:17`: "Anon Key" → "Publishable key" (`sb_publishable_…`).
- `:21`: `NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key` → `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...`
- `:30`: "Anon Key" → "Publishable key". The question stays about RLS.
- `:168`: → publishable key, plus: "`SUPABASE_SECRET_KEY` is server-only: never `NEXT_PUBLIC_`, never in git".
- `:99`: `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<your-project-ref>&read_only=true"`.
- `:103` (S16): the prompt becomes "Using the Supabase MCP, describe the schema of the 'clients' table", followed by an instruction to insert the dummy client row in Supabase's Table Editor. It adds a line explaining that the MCP is read-only on purpose. The exercise's questions and rubric are adjusted wherever they assume an MCP insert.
- `1.6_script.txt:33` (RV-M6): "אנון קי" → the publishable key; "מפתח תפקיד השרת" → the secret key. Same meaning otherwise.
- The `@supabase/ssr`/auth rewrite and removing Prisma stay in 1d.

#### Item 12, content part: old B (RV-L7)
- Move `projects.md:174-320` ("## פרויקט ב: …", up to the line before "## פרויקט ג") verbatim to `courses/ai-dev/lessons/03-final-project/old_B-document-intelligence.md`.
- The new file gets its own `<div dir="rtl" lang="he">` … `</div>` wrapper and a one-line note: unwired, not the new track B (PRD D5).
- In `projects.md`, collapse the now-adjacent `---` separators into one.
- `projects.md:7` "מתוך ארבעה" is left stale on purpose: `/learn project` doesn't offer the projects until 1e rewrites the file.

### 4.3 Tutor (group T)

#### Item 11: frontmatter
Each of the 15 `learn/*.md` files gets a leading `---\ndisable-model-invocation: true\n---` block, with no other keys. `display.md` gets it too; it gets no other change. `learn.md` stays as it is (S2a decides, §9).

#### Item 7: Hebrew aliases (S2)
- **`learn.md`, Learner Commands table:**
  - `continue / המשך`
  - `quiz me / בוחן` → `quiz.md` (covered sections)
  - `quiz me full / בוחן מלא` → `quiz.md` in **`quiz me full`** mode
  - `stop / עצור / סיום`
- **`learn.md`, Route table (79–80):** the same Hebrew words. The rows say which `quiz.md` mode to use, so `quiz.md:14`, which knows only the English triggers and belongs to F, isn't touched (RV-L8).
- `teaching.md:144` and `setup.md:225` are unchanged.

#### Item 12 + G4: no capstones until 1e
- **`project.md`:** a new first section, `## Step 0 — TEMPORARY (until unit 1e)`. It shows, in `session.language`, "the final projects are being rebuilt; meanwhile, continue with the lessons (`/learn`)", then stops the module without reading `projects.md`. Steps 1–5 stay.
- **`resume.md`:** the eligibility paragraph (`:23`) and the `🏗️ Final Project` lines (`:38`, `:50`) → one TEMPORARY rule, "Do not offer the final project until unit 1e". The route row (`:74`) stays.

#### Item 6: `security.md`
- **Ownership gate.**
  - A new Pre-flight step runs after `target_url` is known and before Phase A. It asks with `AskUserQuestion`: "Is this app yours, or do you have explicit permission to test it?"
  - Only the affirmative option continues.
  - Anything else, including free text, stops with a short explanation (testing without permission can cause harm and may be illegal) and offers the learner's own code review (Phase A.2) instead.
  - Every entry point passes through Pre-flight, including the `deploy` handoff and `security http…`.
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
  Plus one sentence: `timingSafeEqual` throws when the lengths differ; fixed-length digests avoid a 500 and hide the key's length.

#### Item 14: the clean-slate step (S4, S5)
- **Placement:** `setup.md` gets a new `## A.0 Clean slate` before "## A. Show Current Settings".
- **Markers:** it sits between `<!-- CLEAN-SLATE:BEGIN — TEMPORARY, remove at first-cohort gate (PRD D10) -->` and `<!-- CLEAN-SLATE:END -->`.

**Behaviour:**
1. **Find.** Check exactly these paths, with no globs:
   - `$HOME/skill-tutor-tutorials/`
   - `$HOME/.claude/commands/learn.md`
   - `$HOME/.claude/commands/learn/`

   The repo contains its own `skill-tutor-tutorials/` folder, so relative paths are forbidden. If none exists, skip silently to A.1.
2. **Show.** Each path found, with its file count and newest modification date.
3. **Ask.** One `AskUserQuestion`, in Hebrew:
   - `להשאיר הכל` (listed first): nothing is touched.
   - `להעביר לגיבוי ולהתחיל מחדש`: everything moves to `~/skill-tutor-tutorials-backup-<date>`; nothing is deleted.

   Only the second option is a yes. Anything else counts as keep.
4. **Move.** A bash variant and a PowerShell variant. Reference shape (bash):
   ```bash
   ts=$(date +%Y%m%d-%H%M%S)
   dest="$HOME/skill-tutor-tutorials-backup-$ts"
   mkdir "$dest" && mkdir "$dest/commands" || exit 1
   if [ -e "$HOME/skill-tutor-tutorials" ]; then mv "$HOME/skill-tutor-tutorials" "$dest/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn.md" ]; then mv "$HOME/.claude/commands/learn.md" "$dest/commands/" || exit 1; fi
   if [ -e "$HOME/.claude/commands/learn" ]; then mv "$HOME/.claude/commands/learn" "$dest/commands/" || exit 1; fi
   ```
   PowerShell uses `New-Item -ItemType Directory -ErrorAction Stop` and `Move-Item -LiteralPath … -ErrorAction Stop`. On any error: stop and report. Never retry with force, and never fall back to a delete.
5. **Verify and report.** Each original path is gone and present in the backup. Print the backup path.
6. **Continue or stop.** If a global command was moved, **stop** and tell the tester to reopen Claude Code and run `/learn setup` again. Otherwise continue.

**Hard rules, stated in the section:** only the three paths; never anything inside the repo (including `.claude/settings.local.json` and the repo's `skill-tutor-tutorials/`); never an earlier backup; no delete command; when in doubt, keep. When the section names `.claude/settings.local.json`, it writes it **without** backticks, because the file is gitignored and absent in CI (RV-H4). §5.1 handles this anyway.

**Shadowing note (RV-H5).** Per skills.md, a personal `~/.claude/commands/learn.md` shadows the repo's `/learn`. The step still runs for such a tester, because every old router `Read`s `.claude/commands/learn/setup.md` by relative path. The manual check proves this with a fixture that is a **copy of the worktree's `learn.md`** (§6.2).

#### S14: Claude Code version check in setup (permanent)
- **Placement:** `setup.md` gets a new `## A.1 Claude Code version`, after A.0 and outside the CLEAN-SLATE markers.
- **Behaviour:**
  - Run `claude --version` and parse the first `X.Y.Z`.
  - If it's below 2.1.176, show a short Hebrew warning that some lessons need 2.1.176+ and how to update (`claude update`), then continue.
  - If `claude` isn't on PATH (e.g. Desktop-only installs), skip silently.
- F moves the number into `landscape.md`.

### 4.4 Docs (group D)

#### Item 8 + G2: remove the global install
- **`setup.md`:** delete "## F. Global Install (optional)" (`:279-309`), and re-letter "## G. Setup Complete" → **F**.
- **`README.md`:** delete `:46` and `:202`.
- **`CLAUDE.md`:** drop "global install" from the Setup row (`:14`), and delete step 4 of "הוספת מודול חדש" (`:75`).
- **`CONTRIBUTING.md`:** delete `:61`.
- The existing `changes.md` sections are history and are left unchanged.

#### RV-L6: document the new frontmatter
The "add a module" steps in `README.md:196-202`, `CONTRIBUTING.md:57-61` and `CLAUDE.md` "הוספת מודול חדש" each gain one step: "start the file with the `disable-model-invocation: true` frontmatter block".

#### Item 13: README tester note
- **Placement:** under the title/banner, between `<!-- TEMPORARY: remove at first-cohort gate (PRD D10) -->` and `<!-- /TEMPORARY -->`, as a blockquote.
- **Text:** the PRD's wording, plus "…or run `/learn setup`, which offers to move them into a backup for you."

#### README "Requirements" (S14)
"Claude Code (Pro plan or higher)" → "Claude Code 2.1.176 or later (Pro plan or higher)". uv is **not** mentioned there (learner-facing).

#### Contributor test command (S12)
- **`CLAUDE.md`:** a new "## בדיקות" section. It says uv is required (install: https://docs.astral.sh/uv/getting-started/installation/) and gives:
  ```
  uv run pytest -q && uv run ruff check -q
  ```
- **`CONTRIBUTING.md` "Pull Requests" (`:65-68`):** one line, "run `uv run pytest -q && uv run ruff check -q` before opening a PR".

#### `changes.md` section (S11)
- **Where:** a new H1, `# Changes — fix/stage0-quick-wins branch`, after the existing sections, in the same style: an Overview, numbered `##` entries with Before/After, and a File Map.
- **When:** written once, as the last commit of group D.
- **Content:** one entry per learner- or contributor-visible change, plus a **Testers** note ("reset your data, or run `/learn setup` and choose the backup option").

---

## 5. Toolchain, lints, tests and CI (group P)

### 5.1 `tests/validate_structure.py` (library module)
- It contains only pure functions, `check_<name>(root: Path) -> list[str]`. Each finding is formatted `path:line: [check] message`, with the path relative to the root.
- A module-level `CHECKS` tuple lists them all.
- No `main()`, no printing, no import-time work.
- **Course scope:** `courses/*/` except `courses/_archive/`, skipping files named `old_B*`.

| Check | Rule |
|---|---|
| `course_md` | For each course with a `COURSE.md`:<br>(a) the set of lesson numbers in "רשימת שיעורים" **equals** the set of lesson folders `lessons/*/<X.Y>-*`<br>(b) the table order equals numeric folder order<br>(c) each module row's folder exists, and its range cell equals `<min>–<max>` of that folder's lessons, or `—` if it has none (`–` or `-` accepted) |
| `slide_markers` | Every `*_script.txt` has ≥ 5 `[מעבר שקף]` and zero `[SLIDE TRANSITION]` |
| `header_numbers` | **Exercises:** the first `# ` heading contains `שיעור X.Y`, and any `**שיעור:**` line contains `X.Y`, both equal to the folder number.<br>**Scripts:** in the first 3 non-empty lines, every `(שיעור\|Lesson)\s+(\d+\.\d+)` and every `שיעור\s+([א-ת]+)\s+נקודה\s+([א-ת]+)` equals the folder number. Words are `[א-ת]+` only, so trailing punctuation never joins a word (RV-M7). They're mapped by a digit-word table (אפס; אחת/אחד; שתיים/שניים/שתים; שלוש/שלושה; ארבע/ארבעה; חמש/חמישה; שש/שישה; שבע/שבעה; שמונה; תשע/תשעה). An unmapped word is a finding |
| `course_name_denylist` | No match in course scope for `קורס\s+(ה-)?AI Engineer`, `\*\*קורס:\*\*\s*AI Engineer` or `AI Engineer course` (case-insensitive). The bare job title passes |
| `tutor_refs` | In every `.claude/**/*.md`:<br>(a) every backticked path starting with `.claude/` or `courses/` exists from the repo root, except the explicit `LOCAL_ONLY = {".claude/settings.local.json"}` (gitignored, absent in CI; RV-H4)<br>(b) every backticked bare `name.md` (no `/`) **directly after** a word-bounded `Read`/`Load` (any case), i.e. `\b(?i:read\|load)\s+`name.md``, exists in the referring file's folder (RV-H1)<br>Skips `~/…` and placeholders containing `[`, `{`, `*` or `X.Y`. On today's tree, (b) matches only `teaching.md:66,80` → `quiz.md` |
| `settings_json` | `.claude/settings.json`, if present, parses as JSON and contains no `powershell` (case-insensitive) |
| `relative_links` | In every `*.md`, after removing fenced code blocks **and inline code spans** (RV-M4), every `[text](target)` whose target isn't `http:`, `https:`, `mailto:` or `#…` resolves relative to the file (with `#fragment` stripped).<br>Skips `.git/`, dot-folders other than `.claude/` and `.github/`, `.venv/`, `_archive/` and `old_B*` |
| `clean_slate_no_delete` | *Temporary.* Between the CLEAN-SLATE markers in `setup.md`, no match for word-bounded delete commands (RV-H3): `\brm\b`, `\brmdir\b`, `\bdel\b`, `\berase\b`, `\brd\b`, `\bri\b`, `Remove-Item`, `\bunlink\b`, `-delete\b`, `rmtree`, `shutil\.rmtree`. Missing markers are not a finding |
| `lesson_files` *(existing)* | Every lesson folder has `*_script.txt` and `*_exercises.md`; course-scoped |
| `teaching_step5` *(existing)* | `teaching.md` contains "Step 5" |

### 5.2 `tests/test_validate_structure.py` (pytest)
- **Fixture:** a `good_tree` fixture (built in `tmp_path`) creates a minimal valid repo:
  - one course, two modules, three lessons, with valid scripts and exercises
  - `COURSE.md`
  - `.claude/commands/learn.md` with routes to three sub-modules:
    - `teaching.md` containing "Step 5" and a `Read \`quiz.md\`` reference
    - `quiz.md`
    - `setup.md` with CLEAN-SLATE markers
  - `.claude/settings.json`
  - a README with a relative link
- **`test_good_tree_passes`:** every check in `CHECKS` returns `[]`.
- **Seeded regressions.** A parametrized test, one case per mutation. Each asserts the named check returns ≥ 1 finding and every other check returns `[]`. At minimum:
  - `course_md`: a missing row; an extra row; two rows swapped; a wrong range
  - `slide_markers`: 4 markers; a `[SLIDE TRANSITION]`
  - `header_numbers`: H1 `שיעור 5.1` in 2.1; a mismatched `**שיעור:**`; script `שיעור 0.1` in 0.2; spelled `חמש נקודה אחת` in 2.1; an unmapped spelled word
  - `course_name_denylist`: `בקורס AI Engineer`; `- **קורס:** AI Engineer`
  - `tutor_refs`: a route to a missing `.claude/commands/learn/missing.md`; `Read \`missing.md\``
  - `settings_json`: `powershell`; invalid JSON
  - `relative_links`: a link to a missing file
  - `clean_slate_no_delete`: `rm -rf` between the markers; `Remove-Item` between them
  - `lesson_files`: a lesson without exercises
  - `teaching_step5`: "Step 5" removed
- **Must-pass negative cases,** parametrized. Each asserts every check returns `[]`:
  - the job title `AI Engineer הוא…`
  - a denied string in `_archive/`, and in `old_B-x.md`
  - a `~/…` reference
  - `.claude/settings.local.json` in backticks (LOCAL_ONLY)
  - "already … `other-dir-file.md`" and "load … from `projects.md`" (not directly after Read/Load)
  - an `http(s)` link, a `#anchor` link, a broken link inside a code fence, and a broken `[text](target)` inside inline code
  - spelled numbers followed by `,`, `:` or `.`
  - "Confirm", "model" and "perform" between the CLEAN-SLATE markers
  - `rm` outside the markers
  - a missing `settings.json`
- **`test_real_repo_passes`:** runs every check on the real repo, and its assertion message is the joined findings list. It's red until groups C, T and D land.

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
- **`.python-version`:** `3.14`.
- **`uv.lock`:** generated with `uv lock` and committed.
- **`.gitignore`:** add `.venv/`, `__pycache__/`, `.pytest_cache/` and `.ruff_cache/`.

### 5.4 `.github/workflows/validate.yml`
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
      - name: Sync (locked)
        run: uv sync --locked
      - name: Tests (seeded regressions + real repo)
        run: uv run pytest -q
      - name: Ruff
        run: uv run ruff check -q
```
- `setup-python` is dropped. uv installs Python 3.14 from `.python-version`. This needs an item-15 wording amendment (§8).
- **`.github/dependabot.yml` (S15):**
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
F and G add checks as new `check_*` functions plus test cases. If F needs `jsonschema` (D8c), it goes in the dev group and is used from the test side.

---

## 6. Verification and the PR

### 6.1 Commit order
On `fix/stage0-quick-wins`, only when the user asks:
1. **P1:** toolchain and CI together: `pyproject.toml`, `.python-version`, `uv.lock`, `.gitignore`, the validator, the tests, `validate.yml` and `dependabot.yml`. They land together because CI needs the tests to exist; pytest exits 5 when it collects nothing. The commit message lists `test_real_repo_passes`'s findings on the current tree (the red state).
2. **P2:** `settings.json` → `{}`.
3. **C:** COURSE.md → VAT → 0.4 markers → residue → 1.3 hook → 1.6 Supabase → old_B, one commit each.
4. **T:** frontmatter → aliases → project/resume → security → clean-slate → version check.
5. **D:** global-install removal → frontmatter docs → tester note → Requirements → test command → `changes.md` (last).

Each commit is followed by `uv run pytest -q && uv run ruff check -q`. Only `test_real_repo_passes` may be red before the end, and the last commit must be fully green.

### 6.2 The PR description (required sections)
- **Summary:** the 16 items, G1/G2/G4 and the RV-* fixes, each mapped to a commit, plus a link to the new `changes.md` section.
- **Automated verification:**
  - the pytest output, including the parametrized seeded-regression IDs
  - ruff's clean result
  - the Actions run link, and the pasted `gh run view <id>` / check-runs annotations output showing no Node 20 / deprecation annotation
- **Manual verification.** The user runs these interactively in the worktree. Each records its steps, date, OS/shell, Claude Code version, who ran it, the result and fixture cleanup. This machine has no `~/skill-tutor-tutorials/` or `~/.claude/commands/`.
  1. **Resume:**
     - Setup: fake `progress/lesson-0.1…1.8.md`, plus a minimal `settings.json` and `learner_profile.md`, under `~/skill-tutor-tutorials/`.
     - Run `/learn`. It offers lesson 2.1 as the next new lesson, and **no** "🏗️ Final Project" line appears.
  2. **Hook error:** two replies in a session in the worktree. No "hook error" notice appears.
  3. **Clean-slate:**
     - Before: hash `/home/emanresu/Tov-learn/.claude/settings.local.json`, the main checkout's file (RV-L1).
     - Create fixtures: `~/skill-tutor-tutorials/` with one file, `~/.claude/commands/learn/` with one file, and `~/.claude/commands/learn.md` **as a copy of the worktree's `learn.md`** (RV-H5).
     - Run `/learn setup` and confirm the A.0 prompt appears. That shows the copied router reached the worktree's `setup.md`.
     - Choose keep: nothing moved.
     - Rerun and choose move: all three are in the timestamped backup, the originals are gone, `git status` is clean, the hash is unchanged, no `settings.local.json` was created in the worktree, and setup stopped with the restart message.
     - Record any permission prompts.
     - Remove the backup afterwards.
  4. **1.3 exercise 5** (Linux/bash variant): steps 1–5 as written, in a throwaway `claude-advanced-lab`. Record the step-5 outcome. The native-PowerShell variant is listed as **untested** (§3).
  5. **Security gate:** run `/learn security https://example.com` and answer "no". It stops before any `curl` runs.
  6. **Aliases and project:** in a lesson, type `בוחן` (a quiz starts), then `עצור` (progress is saved). `/learn project` shows the rebuilt message.
- **Future concerns:** the §9 list.
- **Reviewer note:** Hebrew changes need a Hebrew-speaking contributor's approval.

### 6.3 Done-when (§3) → proof

| Done when | Proof |
|---|---|
| Each new lint fails on a seeded regression and passes on the fixed tree | §5.2 seeded regressions, `test_real_repo_passes`, and the P1 commit message |
| `resume` offers 2.1 after 1.8 | `course_md` (b) plus manual check 1 |
| 0.4 splits into slides | `slide_markers` |
| No hook error after replies | `settings_json` plus manual check 2 |
| `validate.yml` runs with no Node deprecation warning | the annotations evidence |
| The clean-slate step backs up before any delete | S4 by construction, `clean_slate_no_delete`, and manual check 3 |

Manual checks 4–6 cover behaviour that §3 doesn't name but Stage 0 changes (RV-M8).

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| The heuristic `header_numbers` misses a spoken form | §4.2 lists the unparseable forms for hand-fixing; unit N replaces the heuristic |
| The replacement Hebrew reads badly | Minimal edits in the file's own voice; a Hebrew-speaking reviewer |
| A clean-slate move fails part-way | It stops at the first error and reports; nothing is deleted |
| Upstream action tags are re-pointed, or pins go stale | SHA pins plus weekly Dependabot (S15) |
| A stale global `/learn` stays loaded after the move | Setup stops and asks for a restart |
| Contributors without uv | CLAUDE.md and CONTRIBUTING state the requirement and install link. Learners are unaffected (§1) |
| The Windows hook variant is wrong | It follows hooks.md; flagged as untested in the PR; 1a replaces the lab |

---

## 8. Proposed PRD amendments

To be applied to the PRD in a separate, approved edit:
1. **D2 item 5:**
   - add the preambles at `2.3`/`2.6_exercises.md:1` (G1)
   - add the stale cross-references in RV-M1 (`2.1:5`, `2.6:77`, `0.2:137,165`, `0.2_exercises:146-149`, `0.3:57,87`, `0.3_exercises:59`, `1.1:165`)
2. **D2 item 8:** add `README.md:202`, `CONTRIBUTING.md:61` and `CLAUDE.md:14,75` (G2), and the frontmatter step in the add-a-module docs (RV-L6).
3. **D2 item 12:** `resume.md` also stops offering the final project (G4).
4. **D2 item 7:** the alias set per S2.
5. **D2 item 14:** a move into a timestamped backup, with exact paths (S4, S5).
6. **D2 item 15:** `setup-python` is replaced by `astral-sh/setup-uv` (SHA-pinned, `node24`). The contributor toolchain is uv + pytest + ruff, with Python pinned to 3.14 (S6, S12, S13).
7. **D2 item 16:** also `1.6_script.txt:33` (RV-M6), and the read-only MCP rewrite of `1.6_exercises.md:103` (S16).
8. **D2 item 10:** the Claude Code floor of 2.1.176 (S14). §7 gains the CHANGELOG facts.
9. **§6 Dependabot row:** decided in Stage 0: `github-actions` weekly, `uv` deferred (S15).
10. **New unit N** between F and 1a (S10).

---

## 9. Out of scope: future concerns

| Unit | Concern carried forward |
|---|---|
| M | Drop `auto-save-progress.ps1` and the slide viewer; the CLAUDE.md module table and its lint; `tutor_refs` must pass on `.claude/skills/learn/` |
| F | `landscape.md`, including the Claude Code floor (S14) and the Node row; the baseline/model-string/full denylist; the rest of CONTRIBUTING; the style guide; `changes.md` → Keep-a-Changelog; `quiz.md:14` Hebrew triggers; `jsonschema` in the dev group if needed |
| **N (proposed)** | Numbering contract:<br>• stable lesson ids (the folder slug) as the contract; numbers derived<br>• a manifest<br>• a deterministic generator for COURSE.md tables, exercise H1/`**שיעור:**` lines and script title lines (inside `<!-- generated -->` markers)<br>• CI `--check`<br>• id references in prose, rendered by the tutor<br>• a lint against literal lesson numbers in prose<br>• a thin `renumber`/`add-lesson` skill<br>• a CLAUDE.md rule to run the generator before any push (convenience; CI enforces)<br>Replaces `header_numbers` |
| G | Interpreter resolution; owned `settings.local.json` entries; the no-`python3` lint; branch protection. **Constraint: learner tooling must not require uv** |
| 1a | The full 1.3 lab; macOS/Windows equivalents of `chmod 000` + `chattr +i` (UNVERIFIED); 1.2 fixes; 1.1 homework |
| 1b | Module 0 reorder, renumbering 0.x again |
| 1c | Module 02 rename, including the folder |
| 1d | `@supabase/ssr`/auth rewrite; removing Prisma |
| 1e | Restore `/learn project` and the resume offer; delete the TEMPORARY blocks; update `projects.md:7` |
| Gate | Remove the README tester note, the CLEAN-SLATE section and `clean_slate_no_delete` |
| S2a | Whether `learn.md` stays model-invocable; 3-OS pytest CI (already on uv); **learner CLI must not require uv**; Dependabot `uv` ecosystem once support for 0.12 is confirmed |

---

## 10. Change log: first independent review (2026-09-27)

A fresh Opus 5.5 Plan agent (single agent, read-only, no conversation context) raised 22 findings: 5 High, 8 Medium, 9 Low. All were accepted.

| # | Finding | Resolution |
|---|---|---|
| RV-H1 | The `tutor_refs` (b) "line contains read" rule flagged 5 real lines | Directly-after-Read/Load regex; negative tests (§5.1, §5.2) |
| RV-H2 | The read-only MCP broke `1.6_exercises.md:103` | S16 |
| RV-H3 | `clean_slate_no_delete` substrings hit "Confirm"/"model" | Word-bounded command regexes; negative tests |
| RV-H4 | `.claude/settings.local.json` is gitignored, so `tutor_refs` would fail in CI | `LOCAL_ONLY`; written without backticks |
| RV-H5 | A personal `learn.md` fixture shadows the project command | Fixture = copy of the worktree's `learn.md`; A.0 prompt as proof |
| RV-M1 | Missed stale cross-references | Added to §4.2 and §8 |
| RV-M2 | VAT had five occurrences, including `vat_rate = 0.17` | All five listed |
| RV-M3 | `python` missing locally; the unittest exit-5 trap | uv + pytest + ruff, Python 3.14 pin (S6, S12, S13); P1 lands tests and CI together |
| RV-M4 | `relative_links` flagged inline code | Strip inline code spans |
| RV-M5 | `if` needs a newer Claude Code than v2.1.59 | Floor 2.1.176 plus a setup check (S14) |
| RV-M6 | `1.6_script.txt:33` still taught anon/service_role | Fixed in item 16 |
| RV-M7 | Spelled-number tokenizing was unspecified | `[א-ת]+`; punctuation tests |
| RV-M8 | Changed behaviours had no evidence | Manual checks 4–6; the resume check asserts no 🏗️; step-3/5 fallbacks |
| RV-L1 | The worktree `settings.local.json` assertion was vacuous | Hash the main checkout's file; confirm none was created |
| RV-L2 | 1.3 leftovers (`:25`, `ex:60`, `ex:114`) | Fixed in item 10 |
| RV-L3 | The body-edit count was wrong; `display.md` wording | §1 and §4.3 corrected |
| RV-L4 | S11's reason didn't match the branch name | Branch `fix/stage0-quick-wins` |
| RV-L5 | Dependabot was undecided | S15 |
| RV-L6 | The add-a-module docs lacked the frontmatter step | §4.4 |
| RV-L7 | old_B move details | §4.2 |
| RV-L8 | `quiz.md:14` knows only English triggers | Route rows name the mode; F owns `quiz.md` |
| RV-L9 | `0.2_script.txt:9` job title missing from the keep list | Added |
