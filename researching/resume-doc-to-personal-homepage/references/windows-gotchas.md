# Windows / tooling gotchas

Environment traps that cost the most time when discovered late, plus a symptom → cause → fix index
for this pipeline. Domain-specific failures live with their subject: see `reading-the-doc.md`,
`verifying-render.md`, `bilingual.md`, `shipping-pages.md`.

## The environment, in five facts

1. **The Bash tool cannot run ordinary utilities.** `ls`, `mkdir`, `grep`, `tail`, `wc`, `head`,
   `dirname`, `sleep` all return `command not found` — it can only launch **absolute-path
   executables**. So: do every file operation in Python, and call binaries by full path.
   Chain Bash commands with `;`, never `&&` — `mkdir x && chrome …` short-circuits at the missing
   utility and the Chrome step silently never runs (shows up as exit 127 with no output file).
2. **The PowerShell tool does not surface native-process stdout.** A command "succeeds" and prints
   nothing back. Redirect to a file, then Read it:
   ```powershell
   & $exe args *>&1 | Out-String | Set-Content "E:\path\_out.txt" -Encoding UTF8
   ```
3. **Set the encoding before any CLI that prints Chinese**, or you get mojibake (`ä½ å¥½` instead
   of `你好`):
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $env:PYTHONIOENCODING = "utf-8"
   ```
   Python is the safer host for CJK-path work: its source file is read as UTF-8, so paths can
   appear literally and `subprocess.run(..., cwd=<path>)` handles non-ASCII directories.
4. **The security filter rejects `%`.** A percent-encoded `file:///` URL is blocked with
   `cmd.exe %VAR% environment variable syntax is not PowerShell syntax`.
   Serve the site over `http://127.0.0.1:PORT`, or work from an ASCII-only copy of it.
5. **`edsdk.py` lives in the `tencent-local-office-edit` skill directory** and is driven as
   `python edsdk.py call <tool> --json-file <args.json>` — the JSON file avoids shell-quoting pain
   with long paths. Check the schema of the tool you are about to call first:
   `python edsdk.py schema <tool>`.

**Each `open_file` on a file whose import is still running cancels and restarts it.** Pacing calls
≥2 s apart matters; a tight retry loop starves the import forever.

## Key paths

- `editor_sdk.exe`:
  `<app>\resources\app.asar.unpacked\node_modules\@tencent\tencent-docs-ai-engine\bin\win32-x64\editor_sdk.exe`
- The daemon's own log, `<workspace>\editor_sdk.log`, is far more informative than the JSON-RPC
  error strings — it is what revealed the async-`open_file` race.
- **Never kill `python.exe` broadly to tidy up**: the managed venv's `python.exe` may *be* the
  daemon's host. Filter by exact process name (`editor_sdk.exe`) only.

## Symptom → cause → fix

| Symptom | Cause | Fix |
|---|---|---|
| `dirname` / `ls` / `grep` / `tail` / `mkdir` → `command not found` | this box's bash shim only launches absolute-path executables | run Python or the exe by **full path**; use `;`, never `&&` |
| PowerShell command "succeeds" but returns nothing | the tool doesn't surface native stdout | redirect to a file, then Read it |
| `ä½ å¥½` mojibake | console codepage | `[Console]::OutputEncoding=[Text.Encoding]::UTF8` + `PYTHONIOENCODING=utf-8` |
| `cmd.exe %VAR% ... blocked` | `%` in a `file://` URL | local HTTP server, or an ASCII-only path |
| `.ps1` runs but nothing happens (exit 1, not even the first log line) | PowerShell 5.1 decodes a BOM-less `.ps1` as ANSI, so a CJK path inside becomes mojibake | keep `.ps1` files **pure ASCII**; do CJK-path work in Python |
| `& $chrome … --screenshot=$out` produces nothing — no error, empty `$LASTEXITCODE`, no file | the PowerShell tool's sandbox silently blocks spawning Chrome | launch Chrome from the **Bash tool** by full path: `"/c/Program Files/Google/Chrome/Application/chrome.exe" …` |
| `$CH $P ...` → `/c/Program: No such file or directory` | a variable holding a spaced path was expanded unquoted | quote it: `"$CH" $P ...` |
| Chrome exits instantly doing nothing, or every URL dumps byte-identical output | the `--user-data-dir` is locked by another instance | give each run its own `--user-data-dir=<temp dir>` |
| `PermissionError [WinError 5]` from `shutil.rmtree` on the scratch dir | an earlier copy pulled in `.git`, whose object files are read-only | copy only the site's own files, or `rmtree(..., ignore_errors=True)` |
| `git` says `not a git repository`, or `cd` into a CJK path silently fails | the repo root is the *published* directory (e.g. `homepage/`), and this bash shim can't `cd` into non-ASCII paths | use `git -C "<abs path>" …`, or run git from Python with `cwd=<path>` |
| `</ul>` orphaned / a `<li>` vanished after an `Edit` | `old_string` spanned more lines than `new_string` rebuilt | keep `old_string` tight; re-count open/close per tag after any structural edit |
| A tag pair reported as mismatched | the extra tag sits inside an HTML comment (e.g. `<!-- … <a> … -->`) | read the reported line before "fixing" it |
