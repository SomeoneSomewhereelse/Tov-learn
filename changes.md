# Changes — yuval_ver branch

## Overview

Three additions to the `/learn` skill system, focused on giving the learner more control over how they experience course content.

---

## 1. Detail Levels (`detail 1 / 2 / 3`)

**What changed:** `teaching.md`, `learn.md`

The learner can now type `detail 1`, `detail 2`, or `detail 3` at any point during a session to change how deeply Claude explains each slide.

| Level | Behavior |
|-------|----------|
| `detail 1` | 1–2 sentences per slide — just the core idea, no follow-up question |
| `detail 2` | Full Journey Format, max 5 sentences — the default |
| `detail 3` | Journey Format + extended insight + bullet points with extra context |

Claude now asks for the preferred detail level at the start of each session so learners don't have to discover this themselves.

**Why:** Some learners are already familiar with parts of the material and want to move faster. Others want a deeper dive. This makes the tutor adapt to the learner rather than forcing everyone through the same pace.

---

## 2. Cover Every Slide Rule

**What changed:** `teaching.md`

Claude is now required to cover every slide in the lesson — no skipping, no merging slides silently. If a slide is short or repetitive, it may summarize briefly (according to the active detail level), but it must represent every slide.

**Why:** Previously Claude could skip slides it deemed redundant. Learners were missing content without knowing it.

---

## 3. Slides Mode (`/learn slides` or `slides` command)

**What changed:** `learn.md` (routing), new file `slides.md`, new scripts `slide-server.ps1` + `generate-slideshow.ps1`

A new mode the learner can switch into at any time. Instead of Claude's teaching format, the learner sees and hears the actual course slides verbatim.

**How it works:**
- Claude opens an interactive browser window showing the real slide images from the course
- The existing הבא / הקודם buttons in the slide images are made clickable via transparent overlays
- Extra controls are added: ⏸ השהה (pause TTS) and ⛶ מסך מלא (fullscreen)
- A local server (`localhost:7823`) keeps the browser viewer and Claude in sync — if Claude advances, the browser follows, and vice versa
- TTS reads the official course script for each slide automatically — no manual trigger needed
- Exercises in this mode are still written fresh by Claude (not pulled verbatim from the exercises file)

**Learner commands in this mode:**

| Command | Action |
|---------|--------|
| `next` | Advance to next slide |
| `stop slides` | Return to teaching mode at the current slide |
| `exercises` | Get fresh exercises based on slides covered so far |

**Supporting scripts** (in `.claude/scripts/`):
- `slide-server.ps1` — preloads all TTS scripts at startup, speaks via Windows TTS on every slide change, handles pause/resume
- `generate-slideshow.ps1` — generates the HTML viewer for any lesson, positions click overlays over the existing nav buttons in the slide images

**Why:** Some learners want to experience the slides the way they were designed — visually, with the recorded voiceover — rather than Claude's reformulation. This mode gives them that while keeping Claude available for exercises and Q&A.

---

## File Map

| File | Status | Purpose |
|------|--------|---------|
| `.claude/commands/learn.md` | Modified | Added slides routing + detail 1/2/3 and slides to learner commands |
| `.claude/commands/learn/teaching.md` | Modified | Cover-every-slide rule, detail levels, ask preference at session start |
| `.claude/commands/learn/slides.md` | New | Slides Mode — verbatim reading, viewer launch, TTS loop |
| `.claude/scripts/generate-slideshow.ps1` | New | Generates interactive HTML slide viewer |
| `.claude/scripts/slide-server.ps1` | New | Local TTS + slide state server on localhost:7823 |
| `CLAUDE.md` | Modified | Added Slides to modules table, noted scripts folder |

---

# Changes — sean_changes branch

Modifications made while testing the `/learn` user flow on the AI Dev course (lesson 1.1) and streamlining the repo.

---

## 1. Quiz flow redesign — [quiz.md](.claude/commands/learn/quiz.md)

**Before:** 4 open-ended questions, asked one at a time (back-and-forth).

**After:**
- **Normal `quiz me`** — 4 multiple-choice questions batched into a single `AskUserQuestion` box, then **1 free-text recall question** at the end.
  - Multiple-choice = token-efficient and fast UX (recognition).
  - The free-text closer preserves the stronger recall test without back-and-forth.
  - Each MC question has 1 correct + 2–3 plausible distractors; the auto-added "Other" option lets the learner free-text any answer.
- **New `quiz me full` mode** — 8 multiple-choice (two boxes of 4) + 1 free-text synthesis closer, drawn from the **whole** lesson script.
  - No hardcoded section count — scales to whatever sections a lesson has.
  - Reads prior **Quiz History** and **varies the questions** on repeat attempts, keeping them correct and on-topic.
- **Scoring rubric (1–10):**
  - Normal: each MC = 1.5 pts (6 total) + free-text up to 4 pts.
  - Full: each MC = 1 pt (8 total) + free-text up to 2 pts.

## 2. Quiz routing — [learn.md](.claude/commands/learn.md)

- Added `quiz me full` to the Learner Commands table; clarified `quiz me` is scoped to covered sections.

## 3. Global install made opt-in — [setup.md](.claude/commands/learn/setup.md)

**Before:** Section F always copied the skill files to `~/.claude/commands/` (global).

**After:** Global install is **optional, defaulting to off**.
- `/learn` works inside this repo with no install step (the primary goal: learn the material in this repo).
- Setup now asks whether to also install globally (for the future cross-repo use case); most learners say no.
- Avoids a second source of truth / stale copies when repo modules are edited.
- Learner *data* (`~/skill-tutor-tutorials/`) stays per-user and outside the repo — unchanged.

## 4. Docs — [CLAUDE.md](CLAUDE.md)

- "Adding a module" checklist no longer treats global install as required; notes repo-local is the default.

---

## Possible follow-up (not yet implemented)

- A normal `quiz me` can mark a lesson as "Mastered" (score 8+) even if only a few sections were covered. Consider requiring full coverage — or `quiz me full` — before granting mastery in the knowledge map.
- still need to add a FAQ and maybe a walkthrough to help with onboarding.
- also to teach about adding RTL support for claude code https://marketplace.visualstudio.com/items?itemName=yechielby.claude-code-rtl

---

# Changes — fix/lesson-1.8-workers-ai-exercise branch

PR #12, merged 2026-09-28.

## Overview

Repairs the Workers AI exercise in lesson 1.8, which did not compile and used a deprecated model, and moves Cloudflare config references from `wrangler.toml` to `wrangler.jsonc`, the current default.

---

## 1. Lesson 1.8 exercise 7 (AI on the Edge)

**Before:** the `src/index.ts` sample failed TypeScript strict-mode compilation (`request.json()` was untyped), called the deprecated Workers AI model `@cf/meta/llama-2-7b-chat-int8`, and configured the binding in `wrangler.toml`.

**After:**
- `request.json()` is cast to `{ text: string }`, so the sample compiles in strict mode.
- The model is `@cf/meta/llama-3.1-8b-instruct-fp8`, with an inline pointer to Cloudflare's model list.
- An instructor note (an HTML comment, not read to the learner) says to confirm the model ID before teaching and to swap in a current model if it has been deprecated.
- The AI binding is configured in `wrangler.jsonc`.
- The same fix was applied to the archived copy (`courses/_archive/…/3.8_exercises.md`).

## 2. `wrangler.jsonc` references

**Before:** `cli-first.md` and project C in `projects.md` pointed to `wrangler.toml`.

**After:** both use `wrangler.jsonc`, including project C's Cron Trigger config and its checklist line.

---

## File Map

| File | Status | Purpose |
|------|--------|---------|
| `courses/ai-dev/lessons/01-claude-code/1.8-deploy-production/1.8_exercises.md` | Modified | Exercise 7: strict-mode cast, current model, instructor note, `wrangler.jsonc` binding |
| `courses/_archive/ai-engineer/lessons/03-vibe-coding/3.8-deploy-production/3.8_exercises.md` | Modified | The same fix in the archived course |
| `courses/ai-dev/lessons/03-final-project/projects.md` | Modified | Project C: Cron Trigger in `wrangler.jsonc` |
| `.claude/commands/learn/cli-first.md` | Modified | Reproducibility example uses `wrangler.jsonc` |

---

# Changes — fix/lesson-2.5-2.6-content-corrections branch

PR #13, merged 2026-09-28.

## Overview

Corrects outdated API details in lessons 2.5 and 2.6.

---

## 1. Lesson 2.5 exercise 3 (currency converter)

**Before:** the exercise called a defunct Bank of Israel endpoint and read a `rate` field that no longer exists; the instructions didn't say which way to convert (the rate is shekels per dollar).

**After:** it calls `https://boi.org.il/PublicApi/GetExchangeRate?key=USD`, reads `currentExchangeRate` divided by `unit`, and states that the rate is shekels per one dollar, so shekels ÷ rate = dollars.

## 2. Lesson 2.6 script (filesystem MCP server)

**Before:** the script narrated installing the filesystem MCP server with `pip`, contradicting the exercises.

**After:** the script connects the server through Claude Code (`claude mcp add`), matching the exercises, which run the official Node.js package with `npx`.

---

## File Map

| File | Status | Purpose |
|------|--------|---------|
| `courses/ai-dev/lessons/02-claude-api/2.5-python-patterns/2.5_exercises.md` | Modified | Current Bank of Israel endpoint and fields; conversion direction |
| `courses/ai-dev/lessons/02-claude-api/2.6-mcp/2.6_script.txt` | Modified | MCP server added through Claude Code, not `pip` |

---

# Changes — fix/stage0-quick-wins branch

Stage 0 of the project redesign (the "quick-win PR"). Spec: `docs/superpowers/specs/2026-09-27-stage0-quick-wins-design.md`.

## Overview

Fixes what testers hit now (wrong course name, missing lessons, a broken hook, an unsafe lab, deprecated Supabase keys, stale lesson cross-references), adds the first CI lints, and moves CI to `node24` actions on uv + pytest + ruff.

**Testers:** reset your data before testing this branch: delete `~/skill-tutor-tutorials/`, or run `/learn setup` and choose the backup option.

---

## 1. `COURSE.md` lists lessons 2.1 and 2.2

**Before:** module 02 listed only 2.3–2.6, so `/learn` resume skipped from 1.8 to 2.3.

**After:** rows for 2.1 and 2.2, and the module range is 2.1–2.6.

## 2. PowerShell Stop hook removed

**Before:** `.claude/settings.json` ran a PowerShell Stop hook, which showed a "hook error" after every reply on macOS and Linux.

**After:** `.claude/settings.json` is `{}`. (`auto-save-progress.ps1` stays until unit M.)

## 3. Israeli VAT is 18%

**Before:** seven places in lessons 1.3, 2.2 and 2.6 used 17% (including `vat_rate = 0.17`).

**After:** all seven use 18%.

## 4. Lesson 0.4 splits into slides

**Before:** 0.4 used `[SLIDE TRANSITION]`, which the tutor does not recognise, so the lesson was one slide.

**After:** all 19 markers are `[מעבר שקף]`.

## 5. Archive residue removed from course content

**Before:** the course called itself "AI Engineer"; lesson headers and spoken lesson numbers used the archived course's numbering (e.g. "שלוש נקודה ארבע" for 1.4, "חמש נקודה שתיים" for 2.2); scripts pointed to lessons and modules that don't exist; three exercise files began with a leaked AI preamble.

**After:** "AI Dev" throughout (the job title "AI Engineer" stays); every header and spoken lesson number names the real lesson; the dead cross-references are replaced with bridges between the real modules; the preambles are gone.

## 6. Lesson 1.3 hook exercise is safe

**Before:** exercise 5 asked for a Bash hook that prompts for Y/N (hooks have no terminal), with no exit code, in global or project settings; the script claimed exit code 1 blocks.

**After:** a project-scoped PreToolUse hook blocks *reading* a fake secret (`if: "Read(secret-demo.txt)"`, exit 2), then a `cat` in the terminal shows the bypass. Nothing is written or deleted. The script explains that only exit 2 blocks. The lesson needs Claude Code 2.1.176 or later.

## 7. Supabase keys and MCP in lesson 1.6

**Before:** the deprecated anon/service_role keys, and an invalid `claude mcp add` command.

**After:** `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`; the hosted MCP server added read-only at project scope, then authenticated through `claude /mcp` (Claude Code also asks once to approve a project-scoped server). The exercise inserts its sample row in the Table Editor, not through MCP.

## 8. Old project B moved out

**Before:** `projects.md` offered project B (Document Intelligence Service).

**After:** it lives, unwired, in `03-final-project/old_B-document-intelligence.md`. It is not the new track B.

## 9. Tutor: sub-modules can't be auto-invoked

**Before:** Claude could invoke any `learn/*.md` sub-module as a command on its own.

**After:** all 15 start with `disable-model-invocation: true`. The router still `Read`s them; only the model's own command invocation is blocked.

## 10. Tutor: Hebrew aliases

**After:** `המשך` = continue, `בוחן` / `בוחן מלא` = quiz me / quiz me full, `עצור` / `סיום` = stop. "בחן אותי" still switches to diagnostic mode.

## 11. Tutor: no final project until unit 1e

**Before:** `/learn project` and resume offered the final projects, which are being rebuilt.

**After:** `/learn project` says they are being rebuilt and points back to the lessons; resume no longer offers them.

## 12. Tutor: `/learn security` asks first

**Before:** it scanned any URL; its `timingSafeEqual` sample returned a 500 on keys of a different length.

**After:** it asks whether the app is the learner's (or they have permission) and makes no request unless they say yes; the sample compares SHA-256 digests.

## 13. Setup: temporary clean-slate step

**After:** `/learn setup` looks for leftovers at exactly `~/skill-tutor-tutorials/`, `~/.claude/commands/learn.md` and `~/.claude/commands/learn/`, shows them, and on an explicit yes moves them into `~/skill-tutor-tutorials-backup-<date>`. Nothing is deleted. A path that lives inside this repo, or that contains it (a `~/.claude/commands` symlinked to the repo, or a clone placed inside `~/skill-tutor-tutorials/`), is shown as `SKIP` and never moved. Removed at the first-cohort gate.

## 14. Setup: Claude Code version check

**After:** `/learn setup` warns when `claude --version` is below 2.1.176 (compared numerically).

## 15. Global install removed

**Before:** setup offered to copy `/learn` into `~/.claude/commands`, creating a stale second copy.

**After:** the option is gone from `setup.md`, README, CONTRIBUTING and CLAUDE.md.

## 16. Docs

- README: a temporary tester note; Claude Code 2.1.176 or later; the Hebrew aliases.
- The "add a module" steps (README, CONTRIBUTING, CLAUDE.md) include the frontmatter block.
- CLAUDE.md (contributors only) and CONTRIBUTING: the test command `uv run ruff check -q && uv run pytest -q`.
- CONTRIBUTING: what CI now checks for every lesson.

## 17. CI and contributor toolchain

**Before:** `validate.yml` used `checkout@v4` and `setup-python@v5` (both `node20`, retired on runners) and ran a script with 4 checks.

**After:** SHA-pinned `actions/checkout` v7.0.1 and `astral-sh/setup-uv` v10.2.0 (`node24`), `permissions: contents: read`, and `uv sync --locked` → `ruff check` → `pytest`. The lints are `check_*` functions in `tests/validate_structure.py`, each proven by a seeded regression in `tests/test_validate_structure.py`. Dependabot keeps the action pins fresh. uv is required for contributors only; learners never need it.

---

## File Map

| File | Status | Purpose |
|------|--------|---------|
| `pyproject.toml`, `uv.lock` | New | Contributor toolchain: Python 3.14, pytest, ruff |
| `tests/validate_structure.py` | Rewritten | The lints, as a library of `check_*` functions |
| `tests/test_validate_structure.py` | New | Seeded regressions, must-pass negatives, real-repo check |
| `.github/workflows/validate.yml` | Modified | node24 actions, uv, least privilege |
| `.github/dependabot.yml` | New | Weekly `github-actions` updates |
| `.gitignore` | Modified | Python caches and `.venv/` |
| `.claude/settings.json` | Modified | `{}` |
| `.claude/commands/learn.md` | Modified | Aliases; project route wording |
| `.claude/commands/learn/*.md` (15 files) | Modified | `disable-model-invocation: true` frontmatter |
| `.claude/commands/learn/setup.md` | Modified | Clean-slate step, version check, global install removed |
| `.claude/commands/learn/security.md` | Modified | Ownership gate, digest comparison |
| `.claude/commands/learn/project.md`, `resume.md` | Modified | No final project until unit 1e |
| `.claude/commands/learn/progress.md` | Modified | Hebrew stop triggers |
| `courses/ai-dev/COURSE.md` | Modified | Lessons 2.1 and 2.2 |
| `courses/ai-dev/lessons/**` | Modified | VAT, 0.4 markers, residue, 1.3 hook exercise, 1.6 Supabase |
| `courses/ai-dev/lessons/03-final-project/old_B-document-intelligence.md` | New | Old project B, unwired |
| `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` | Modified | Docs above |
