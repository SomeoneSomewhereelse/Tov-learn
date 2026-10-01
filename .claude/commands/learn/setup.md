---
disable-model-invocation: true
---
# Setup Module

*Loaded by learn.md when settings.json is missing or $ARGUMENTS = "setup".*

Respond in the language the user answers with in section B. Default to Hebrew if unclear.

---

<!-- CLEAN-SLATE:BEGIN — TEMPORARY, remove at first-cohort gate (PRD D10) -->
## 0. Clean slate

*TEMPORARY, for the tester period only. Runs on every `/learn setup`, before section 0.1.*

Leftovers from an earlier install fail quietly: a personal `~/.claude/commands/learn.md` shadows this repo's `/learn` and keeps running old code, and an old `settings.json` is half-read. This step finds them and offers to move them into a backup folder.

**Hard rules for this section:**
- Look at exactly three paths, and nothing else: `~/skill-tutor-tutorials/`, `~/.claude/commands/learn.md` and `~/.claude/commands/learn/`. No globs, no other names.
- Always build them from `$HOME`. Never use a relative path: this repo has its own skill-tutor-tutorials folder, which must never be touched.
- Never touch anything inside this repo. That includes the repo's local settings file (.claude/settings.local.json) and the repo's own skill-tutor-tutorials folder. A path counts as inside this repo when its real location is inside it, after resolving symlinked parent folders, and also when this repo lives inside the path (a clone placed in `~/skill-tutor-tutorials/`, say): a tester may have linked `~/.claude/commands` to this repo's `.claude/commands`. The blocks below check this and print `SKIP` for such a path. Leave a `SKIP` path alone.
- Never touch an earlier backup folder (`~/skill-tutor-tutorials-backup-…`).
- Move, never destroy. This section has no command that destroys files, and you must not run one. If any step fails, stop and report the error. Never retry with force.
- When in doubt, keep.

### Step 1 — Find and show

Run this as **one** Bash tool call (on native Windows without Git Bash, run the PowerShell block instead):

```bash
: "${HOME:?HOME is not set}"
repo=$(cd -P "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && pwd -P)
inside_repo() {
  d=$(cd -P "$(dirname "$1")" 2>/dev/null && pwd -P) || return 1
  r="$d/$(basename "$1")"
  case "$r/" in "$repo"/*) return 0 ;; esac
  case "$repo/" in "$r"/*) return 0 ;; esac
  return 1
}
for p in "$HOME/skill-tutor-tutorials" "$HOME/.claude/commands/learn.md" "$HOME/.claude/commands/learn"; do
  if [ -e "$p" ] || [ -L "$p" ]; then
    if inside_repo "$p"; then echo "SKIP $p (it is inside this repo, or the repo is inside it)"; continue; fi
    echo "FOUND $p"
    echo "  entries: $(find "$p" | wc -l | tr -d ' ')"
    echo "  newest:  $(find "$p" -exec ls -ldt {} + | head -n 1)"
    find "$p" -type l -exec ls -ld {} +
  fi
done
```

```powershell
$ErrorActionPreference = 'Stop'
if (-not $HOME) { throw 'HOME is not set' }
function Get-Entries([string]$Path) {
  $item = Get-Item -LiteralPath $Path -Force
  $item
  if ($item.PSIsContainer -and -not $item.LinkType) {
    Get-ChildItem -LiteralPath $Path -Force | ForEach-Object { Get-Entries $_.FullName }
  }
}
function Test-InRepo([string]$Path) {
  $sep = [System.IO.Path]::DirectorySeparatorChar
  $ic = [System.StringComparison]::OrdinalIgnoreCase
  $repo = $null
  if (Get-Command git -ErrorAction SilentlyContinue) {
    try { $repo = & git rev-parse --show-toplevel 2>$null | Select-Object -First 1 } catch { $repo = $null }
  }
  if (-not $repo) { $repo = (Get-Location).Path }
  $repo = (Resolve-Path -LiteralPath $repo).ProviderPath.TrimEnd('\', '/') + $sep
  $full = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/') + $sep
  if ($full.StartsWith($repo, $ic) -or $repo.StartsWith($full, $ic)) { return $true }
  $d = Split-Path -Parent $Path
  while ($d -and ($d -ne $HOME) -and (Test-Path -LiteralPath $d)) {
    $it = Get-Item -LiteralPath $d -Force
    if ($it.LinkType) {
      $t = @($it.Target)[0]
      if (-not [System.IO.Path]::IsPathRooted($t)) { $t = Join-Path (Split-Path -Parent $d) $t }
      if (([System.IO.Path]::GetFullPath($t).TrimEnd('\', '/') + $sep).StartsWith($repo, $ic)) { return $true }
    }
    $d = Split-Path -Parent $d
  }
  return $false
}
foreach ($p in @((Join-Path $HOME 'skill-tutor-tutorials'), (Join-Path $HOME '.claude\commands\learn.md'), (Join-Path $HOME '.claude\commands\learn'))) {
  if (Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue) {
    if (Test-InRepo $p) { "SKIP $p (it is inside this repo, or the repo is inside it)"; continue }
    $entries = @(Get-Entries $p)
    "FOUND $p"
    "  entries: $($entries.Count)"
    "  newest:  $(($entries | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime)"
    $entries | Where-Object { $_.LinkType } | ForEach-Object { "  link: $($_.FullName) -> $($_.Target)" }
  }
}
```

- `find` without `-L` never follows a symlink: a symlink counts as **one** entry, and its target is printed next to it. The bash block uses only commands that behave the same on GNU (Linux, WSL) and BSD (macOS). The PowerShell block uses `Get-Item -Force`, which also finds a dangling symlink.
- The entry count is always exact. For a very large folder, `find … -exec ls -ldt {} +` can split into batches, so the "newest" line is then only approximate.
- A `SKIP` line is not a leftover: the path is inside this repo, or this repo is inside it, so ignore it everywhere below. Count only the `FOUND` paths.
- **If nothing is found** (no `FOUND` line): say, in Hebrew, "לא נמצאו שאריות מהתקנה קודמת." and continue to section 0.1.
- **Otherwise:** show each path found with its entry count, its newest modification date and any symlink targets, and remember the counts for Step 4.

### Step 2 — Ask

Use `AskUserQuestion`:

```
question: "נמצאו נתוני למידה או התקנה קודמת של /learn (כולל ההתקדמות שלך, אם התחלת ללמוד). מה לעשות איתם?"
header: "ניקוי התקנה"
options:
  - label: "להשאיר הכל"
    description: "שום דבר לא זז. ממשיכים בהגדרה."
  - label: "להעביר לגיבוי ולהתחיל מחדש"
    description: "הכל עובר לתיקייה ~/skill-tutor-tutorials-backup-<תאריך>. שום דבר לא הולך לאיבוד."
```

Only `להעביר לגיבוי ולהתחיל מחדש` is a yes. Any other answer, including free text, means keep: touch nothing and continue to section 0.1.

### Step 3 — Move

Run the whole move as **one single** Bash tool call (or one PowerShell call), never split across calls: shell variables do not survive between tool calls.

```bash
: "${HOME:?HOME is not set}"
ts=$(date +%Y%m%d-%H%M%S)
dest="$HOME/skill-tutor-tutorials-backup-$ts"
: "${dest:?dest is not set}"
repo=$(cd -P "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && pwd -P)
inside_repo() {
  d=$(cd -P "$(dirname "$1")" 2>/dev/null && pwd -P) || return 1
  r="$d/$(basename "$1")"
  case "$r/" in "$repo"/*) return 0 ;; esac
  case "$repo/" in "$r"/*) return 0 ;; esac
  return 1
}
move_aside() {
  if [ -e "$1" ] || [ -L "$1" ]; then
    if inside_repo "$1"; then echo "SKIP $1 (it is inside this repo, or the repo is inside it)"; return 0; fi
    mv "$1" "$2" || exit 1
  fi
}
mkdir "$dest" && mkdir "$dest/commands" || exit 1
move_aside "$HOME/skill-tutor-tutorials" "$dest/"
move_aside "$HOME/.claude/commands/learn.md" "$dest/commands/"
move_aside "$HOME/.claude/commands/learn" "$dest/commands/"
echo "BACKUP $dest"
for p in "$HOME/skill-tutor-tutorials" "$HOME/.claude/commands/learn.md" "$HOME/.claude/commands/learn"; do
  if { [ -e "$p" ] || [ -L "$p" ]; } && ! inside_repo "$p"; then echo "STILL PRESENT $p"; fi
done
for b in "$dest/skill-tutor-tutorials" "$dest/commands/learn.md" "$dest/commands/learn"; do
  if [ -e "$b" ] || [ -L "$b" ]; then echo "IN BACKUP $b entries: $(find "$b" | wc -l | tr -d ' ')"; fi
done
```

```powershell
$ErrorActionPreference = 'Stop'
if (-not $HOME) { throw 'HOME is not set' }
function Get-Entries([string]$Path) {
  $item = Get-Item -LiteralPath $Path -Force
  $item
  if ($item.PSIsContainer -and -not $item.LinkType) {
    Get-ChildItem -LiteralPath $Path -Force | ForEach-Object { Get-Entries $_.FullName }
  }
}
function Test-InRepo([string]$Path) {
  $sep = [System.IO.Path]::DirectorySeparatorChar
  $ic = [System.StringComparison]::OrdinalIgnoreCase
  $repo = $null
  if (Get-Command git -ErrorAction SilentlyContinue) {
    try { $repo = & git rev-parse --show-toplevel 2>$null | Select-Object -First 1 } catch { $repo = $null }
  }
  if (-not $repo) { $repo = (Get-Location).Path }
  $repo = (Resolve-Path -LiteralPath $repo).ProviderPath.TrimEnd('\', '/') + $sep
  $full = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/') + $sep
  if ($full.StartsWith($repo, $ic) -or $repo.StartsWith($full, $ic)) { return $true }
  $d = Split-Path -Parent $Path
  while ($d -and ($d -ne $HOME) -and (Test-Path -LiteralPath $d)) {
    $it = Get-Item -LiteralPath $d -Force
    if ($it.LinkType) {
      $t = @($it.Target)[0]
      if (-not [System.IO.Path]::IsPathRooted($t)) { $t = Join-Path (Split-Path -Parent $d) $t }
      if (([System.IO.Path]::GetFullPath($t).TrimEnd('\', '/') + $sep).StartsWith($repo, $ic)) { return $true }
    }
    $d = Split-Path -Parent $d
  }
  return $false
}
$dest = Join-Path $HOME ('skill-tutor-tutorials-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (-not $dest) { throw 'dest is not set' }
New-Item -ItemType Directory -Path $dest | Out-Null
New-Item -ItemType Directory -Path (Join-Path $dest 'commands') | Out-Null
$moves = @(
  @((Join-Path $HOME 'skill-tutor-tutorials'), $dest),
  @((Join-Path $HOME '.claude\commands\learn.md'), (Join-Path $dest 'commands')),
  @((Join-Path $HOME '.claude\commands\learn'), (Join-Path $dest 'commands'))
)
foreach ($m in $moves) {
  if (Get-Item -LiteralPath $m[0] -Force -ErrorAction SilentlyContinue) {
    if (Test-InRepo $m[0]) { "SKIP $($m[0]) (it is inside this repo, or the repo is inside it)"; continue }
    Move-Item -LiteralPath $m[0] -Destination $m[1] -ErrorAction Stop
  }
}
"BACKUP $dest"
foreach ($m in $moves) { if ((Get-Item -LiteralPath $m[0] -Force -ErrorAction SilentlyContinue) -and -not (Test-InRepo $m[0])) { "STILL PRESENT $($m[0])" } }
foreach ($b in @((Join-Path $dest 'skill-tutor-tutorials'), (Join-Path $dest 'commands\learn.md'), (Join-Path $dest 'commands\learn'))) {
  if (Get-Item -LiteralPath $b -Force -ErrorAction SilentlyContinue) { "IN BACKUP $b entries: $(@(Get-Entries $b).Count)" }
}
```

- `mv` and `Move-Item` move a symlink as a link; they never follow it.
- **On any error:** stop and report it. Never retry with force.
- **Across filesystems** (e.g. `~/.claude/commands` is a symlink into `/mnt/c/…`), `mv` copies and then removes the original. An interruption leaves the original intact, or both copies, but never neither. So nothing is lost.

### Step 4 — Verify and report

Check the output: no `STILL PRESENT` line (a `SKIP` path is not one), and each `IN BACKUP` entry count equals the count shown in Step 1. If anything differs, stop and report it. Otherwise tell the learner, in Hebrew, the backup path from the `BACKUP` line.

### Step 5 — Continue or stop

- If `~/.claude/commands/learn.md` or `~/.claude/commands/learn/` was moved: stop setup here. Tell the tester, in Hebrew, to close Claude Code, open it again in this repo and run `/learn setup` again. Do not continue in this session.
- Otherwise continue to section 0.1.
<!-- CLEAN-SLATE:END -->

---

## 0.1 Claude Code version

*Runs on every `/learn setup`, including a first run with no settings file.*

**Floor:** 2.1.176

1. Run `claude --version`. If `claude` is not found (e.g. a Desktop-bundled install with no `claude` on PATH), skip this section silently and continue to section A.
2. Take the first `major.minor.patch` version in the output (e.g. `2.1.284 (Claude Code)` gives `2.1.284`).
3. Compare it with the floor **numerically, one component at a time**: major first, then minor, then patch. Never compare the two strings as text: `2.1.99` is lower than `2.1.100`, although it sorts higher as text.
4. If it is lower than the floor, show this warning in Hebrew, filling in both versions, then continue to section A:
   > "גרסת Claude Code שלך (<installed>) ישנה מהגרסה המינימלית שהקורס צריך (<floor>). כדי לעדכן, הריצו בטרמינל: `claude update`"
5. Otherwise continue to section A without a message.

*Limitation:* `claude --version` reports whichever `claude` comes first on PATH, which may not be the binary running this session.

---

## A. Show Current Settings

If `~/skill-tutor-tutorials/settings.json` exists, display a friendly summary table showing: session language, course path, TTS enabled/disabled, voice name, TTS language, speed, and mode.

If the file does not exist — skip directly to section B.

---

## B. Session Language

Use the `AskUserQuestion` tool:

```
question: "In which language would you like the session to run?"
header: "Session Language"
options:
  - label: "עברית"
    description: "המערכת תתקשר איתך בעברית"
  - label: "English"
    description: "The system will communicate with you in English"
```

Set `session.language` to `"he"` or `"en"`. Use this language for all communication from this point on.

---

## B.1. פנייה אישית (עברית בלבד)

**Run this section only if `session.language == "he"`. Skip entirely if English was selected.**

Use `AskUserQuestion`:

```
question: "איך להתייחס אליך בשיחה?"
header: "פנייה"
options:
  - label: "אתה (יחיד זכר)"
    description: "פנייה בלשון זכר"
  - label: "את (יחיד נקבה)"
    description: "פנייה בלשון נקבה"
  - label: "ניטרלי / מעורב"
    description: "ללא פנייה מגדרית — מתאים לקבוצות מעורבות או העדפה אישית"
  - label: "רבים / רבות"
    description: "פנייה בלשון רבים — ציין אם זכר (אתם) או נקבה (אתן)"
```

*(The tool auto-adds an "Other" option for free text — use that value as-is.)*

Save the result as `session.address`. Examples:
- "אתה (יחיד זכר)" → `"masculine"`
- "את (יחיד נקבה)" → `"feminine"`
- "ניטרלי / מעורב" → `"neutral"`
- "רבים / רבות" → `"plural-m"` or `"plural-f"` (ask follow-up if needed)
- free text → save verbatim as `"other:<text>"`

**Use `session.address` for all Hebrew communication from this point on.**

---

## B.2. RTL Extension for Hebrew Users

**Run this section only if `session.language == "he"`. Skip entirely if English was selected.**

First, check if the extension is already installed:

```powershell
code --list-extensions | Select-String "yechielby.claude-code-rtl"
```

**If already installed:** skip this section entirely — no message needed.

**If not installed:** use `AskUserQuestion`:

```
question: "האם להתקין את תוסף ה-RTL?"
header: "תוסף RTL"
options:
  - label: "כן, התקן"
    description: "yechielby.claude-code-rtl — משפר תצוגת עברית ב-Claude Code"
  - label: "לא תודה"
    description: "דלג על שלב זה"
```

**If yes:** first tell the user:

> "מתקין את התוסף. שים לב שהתקנה עלולה לקטוע את השיחה — אם זה יקרה: אם השיחה עדיין פתוחה, כתוב **המשך**; אם נסגרה, פתח שיחה חדשה וכתוב **`/learn setup`**."

Then run:

```powershell
code --install-extension yechielby.claude-code-rtl
```

After the command completes, add:

> "לאחר שה-extension ייטען, הפעל מצב אוטומטי פעם אחת:
> `Ctrl+Shift+P` ← **Activate RTL (Auto)**
>
> **למה זה חשוב?** בלי מצב זה, כל הטקסט מוצג משמאל לימין — עברית מופיעה הפוכה, פסקאות מתחילות בצד הלא נכון, והקריאה מסורבלת. מצב Auto מזהה לבד איזה בועת שיחה היא עברית ואיזו אנגלית, ומסדר כל אחת בכיוון הנכון — בלי שתצטרך לעשות כלום.
>
> התוסף מוסיף כפתור קטן בשורת הסטטוס בתחתית המסך — משם ניתן בכל עת לשנות מצב או לבטל לחלוטין."

**If no:** skip silently and continue to section C.

---

## C. Course Selection

Use the `AskUserQuestion` tool to display a course picker:

```
question: "באיזה מסלול תרצה ללמוד?"
header: "בחירת מסלול"
options:
  - label: "AI Dev"
    description: "פיתוח מוצרי AI עם Claude Code ו-API (המסלול הפעיל היחיד)"
  - label: "נתיב מותאם אישית"
    description: "הגדרת נתיב מסלול ידנית"
```

Map the selection to settings:

| בחירה | course.name | course.path |
|-------|-------------|-------------|
| AI Dev | `ai-dev` | `courses/ai-dev/lessons` |
| נתיב מותאם אישית | (שאל שם) | (שאל נתיב) |

> מסלול ה-AI Engineer הועבר לארכיון תחת `courses/_archive/ai-engineer/`. אם לומד צריך אותו — אפשר להזין נתיב מותאם אישית: `courses/_archive/ai-engineer/lessons`.

If the learner types "Other" with free text — treat as custom path.

---

## D. TTS Setup

Use the `AskUserQuestion` tool:

```
question: "האם תרצה שהמורה ידבר בקול?"
header: "קול מורה"
options:
  - label: "כן"
    description: "המערכת תקרא את התשובות בקול"
  - label: "לא"
    description: "טקסט בלבד"
```

**If yes:**

1. Run PowerShell to list available voices:
```powershell
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer,Windows.Media.Speech,ContentType=WindowsRuntime]
[Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | ForEach-Object { "$($_.DisplayName) — $($_.Language)" }
```

2. Show the list and ask which voice they want (free text — list is dynamic).

3. Use the `AskUserQuestion` tool for speaking rate:

```
question: "באיזה קצב תרצה שהמורה ידבר?"
header: "קצב דיבור"
options:
  - label: "רגיל"
    description: "קצב ברירת מחדל (0)"
  - label: "איטי"
    description: "מומלץ למתחילים (-2)"
  - label: "מהיר"
    description: "למי שרוצה להאיץ (+2)"
```

Map: רגיל → 0, איטי → -2, מהיר → 2.

4. Use the `AskUserQuestion` tool for TTS mode:

```
question: "מתי תרצה שהמורה ידבר?"
header: "מצב קול"
options:
  - label: "אוטומטי"
    description: "מדבר אחרי כל תשובה"
  - label: "לפי דרישה"
    description: "רק כשתבקש"
```

Map: אוטומטי → `"auto"`, לפי דרישה → `"on-demand"`.

5. Test the voice by speaking a greeting in the configured session language.

6. Use the `AskUserQuestion` tool:

```
question: "הקול נשמע טוב?"
header: "בדיקת קול"
options:
  - label: "כן, מעולה"
    description: "שמור את ההגדרות"
  - label: "לא, שנה קול"
    description: "חזור לבחירת קול (שלב 2)"
```

**If no:** set `tts.enabled = false`.

---

## D.5. Learning Style

Use `AskUserQuestion` (two questions, can be shown together):

```
question: "איך תעדיף ללמוד בדרך כלל?"
header: "סגנון למידה"
options:
  - label: "standard — הסבר ואז שאלה (ברירת מחדל)"
    description: "אסביר כל נושא ואז אשאל שאלה לבדיקת הבנה"
  - label: "diagnostic — בחן אותי קודם"
    description: "תבחן אותי על כל השיעור קודם, ותלמד אותי רק את מה שטעיתי"
  - label: "socratic — הדרך אותי בשאלות"
    description: "תשאל שאלות שיובילו אותי לגלות את התשובות בעצמי"
```

```
question: "איזו רמת פירוט מתאימה לך?"
header: "רמת פירוט"
options:
  - label: "detail 1 — קצר מאוד"
    description: "רק הרעיון המרכזי, 1–2 משפטים לשקף"
  - label: "detail 2 — ברירת מחדל"
    description: "מאוזן — הסבר + דוגמה + שאלה"
  - label: "detail 3 — עומק מלא"
    description: "כל הפרטים, תוספות, השוואות"
```

Map to values:
- mode: `"standard"` / `"diagnostic"` / `"socratic"`
- detail_level: `1` / `2` / `3`

---

## E. Save Settings

Save `~/skill-tutor-tutorials/settings.json`:

```json
{
  "session": {
    "language": "he",
    "address": "masculine"
  },
  "course": {
    "name": "ai-dev",
    "path": "courses/ai-dev/lessons"
  },
  "tts": {
    "enabled": true,
    "voice_name": "[selected voice name]",
    "voice_lang": "[voice language code]",
    "rate": 0,
    "mode": "auto"
  },
  "learning_style": {
    "mode": "standard",
    "detail_level": 2
  }
}
```

---

## F. Setup Complete — REQUIRED

**You MUST always send this message after completing all steps above, regardless of which options the learner chose.**

Send a summary message in `session.language` that includes:
1. A confirmation that setup is complete and settings are saved.
2. A one-line recap of the chosen settings (language, course, TTS on/off).
3. A prompt asking what they'd like to do next — offer to start the first lesson or jump to a specific one.

Example (English):
```
Setup complete! Here's your configuration:
- Language: English
- Course: AI Dev
- Voice: Off

Ready to start learning. Would you like to begin with Lesson 0.1, or jump somewhere specific?
```

Do not skip this step even if any previous section was skipped or the learner said "no" to optional features.
