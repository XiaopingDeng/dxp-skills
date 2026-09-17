# Reading the resume document

Detail for Step 1. Read this before your first tool call — the extension trap and the handshake
both produce failures that look like something else entirely.

## 1. Route by file EXTENSION, not by content

The category is decided by extension — not by magic bytes, not by the `file_type` argument
(verified across 7 format variants). Passing `file_type="doc"` to `open_file` does **not** override it.

| Extension | Content | Detected category | Read + export |
|---|---|---|---|
| `.doc` (Word 97 OLE) | `D0CF11E0` | `doc` | ✅ |
| `.docx` (OOXML) | `504B0304` | `doc` | ✅ |
| `.dot` | `D0CF11E0` | **`sheet`** | ❌ |
| `.dotx` | `504B0304` | **`sheet`** | ❌ |
| `.docm` | `504B0304` | **`sheet`** | ❌ |
| `.wps` | `D0CF11E0` | **`sheet`** | ❌ |
| *(no extension)* | `D0CF11E0` | **`sheet`** | ❌ |

Mis-routed files do not "partially work": every doc tool fails with
`Unknown sheet tool: doc_*`, and saving fails with
`SheetEditor::SaveFile: workbook is not open`.

**Fix by renaming a copy, not by converting.** Copy the file to a `.doc` / `.docx` name (the bytes
are never re-read for content, only the extension is consulted) and open that. Verified: `.dot`,
`.wps`, and extensionless files renamed to `.doc` all read and export perfectly — 17 media files and
~18 400 characters of text, identical to the native `.doc`. Keeps the user's original untouched.

## 2. The open → settle → read handshake (mandatory)

`open_file` is **asynchronous despite its name**. It returns `open started (doc)` immediately while
a chunked import runs in the background (`DocEditor::OpenByChunks ... chunk open ok`). Calling
`save_file` or `doc_resolve_document_structure` before the import finishes yields

```
[-1]DocEditor::SaveFile: document is not open
```

— which looks exactly like a format incompatibility but is a **race**, not a format problem.

```python
call("open_file", {"file_path": src})   # 1. starts the import
time.sleep(2)
call("open_file", {"file_path": src})   # 2. same file_id — the completion handshake
time.sleep(3)
for _ in range(10):                       # 3. poll until the model is live
    ok, _ = call("doc_get_outline", {"file_id": src})
    if ok: break
    time.sleep(2)
# 4. only now read / save
```

An extra `open_file` on a file whose import is still running **cancels and restarts** it
(`SyncCancelChunkOpen: chunk open cancelled`), so a tight retry loop starves the import forever.
Pace every call ≥2 s. On a purely background open the returned `file_id` is usually the path string
itself; confirm with `get_pool_status`.

## 3. Reading the structure

- **`doc_resolve_document_structure` alone is not enough.** In `full` mode its `text_preview` for
  table cells is still cut to ~10 characters even with `text_preview_length=200`. Paragraph nodes
  come back complete.
- **`doc_get_table_info` (by `table_id`) returns complete cell text.** Use it per table.
- A resume is nearly always a **stack of one-column tables**; one row is one former paragraph.
- `doc_get_outline` is the cheap readiness probe — small, and the first thing that works once the
  model is live.

Driver script that imports `edsdk` and dumps a readable `.txt`:

```python
import json, importlib.util, os
SKILL = r"<...>\tencent-local-office-edit"
spec = importlib.util.spec_from_file_location("edsdk", os.path.join(SKILL, "edsdk.py"))
edsdk = importlib.util.module_from_spec(spec); spec.loader.exec_module(edsdk)

def call(name, args):
    res = edsdk._rpc("tools/call", {"name": name, "arguments": args})
    return "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")

struct = json.loads(call("doc_resolve_document_structure",
                         {"file_id": FILE_ID, "mode": "compact", "limit": 0}))
for n in struct["nodes"]:
    if n["type"] == "Table":
        info = json.loads(call("doc_get_table_info", {"file_id": FILE_ID, "table_id": n["table_id"]}))
        # walk info["block"]["table"]["cells"] -> (row, col, text)
```

Run it with the managed venv Python, redirect stdout to a file, and Read that file.

## 4. Keep the editor_sdk daemon alive for the whole run

The daemon is **reaped when the shell that spawned it exits**. The signature of this cause (rather
than a real bug): `WinError 10061` on every call, and nothing listening on 39099–39108.

- `Start-Process -WindowStyle Hidden` does **not** survive; neither does launching it in one tool
  call and using it in the next.
- Detach helpers (`Start-Job`, WMI `Win32_Process Create`, `wscript`/`.vbs`) are **blocked**.
- **Spawn the daemon inside the same Python process as the client**, then `taskkill` it at the end:

```python
DETACHED = 0x00000008 | 0x00000200 | 0x08000000   # no console, own group
proc = subprocess.Popen([SDK_EXE], creationflags=DETACHED,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL, close_fds=True)
for _ in range(80):                    # wait for the port
    time.sleep(0.5)
    if any(port_open(p) for p in range(39099, 39109)):
        break
# ... run the whole job ...
subprocess.run(["taskkill", "/F", "/IM", "editor_sdk.exe"], capture_output=True)
```

At the very end, `save_file` and stop — **do not `close_file`**: the document may be open in the
user's preview panel, and closing it tears down the view they are looking at.

**`save_file` rewrites a legacy `.doc` as OOXML.** Observed: a genuine Word 97 file (`d0cf11e0`) came
back from `save_file` as a ZIP package (`504b0304`, 29 entries, `word/document.xml`) while keeping its
`.doc` name. Nothing breaks — Word/WPS sniff content, and `.doc` still routes to the doc category —
but if you need the file to *stay* a true Word 97 binary, save to a new `.docx` path instead of
saving in place. Also do not trust a naive binary grep for leaked text afterwards: in OOXML the body
text is compressed, so verify by re-reading through the editor, not by scanning bytes.

## 5. When the resume is one big table

Some resumes have no heading styles at all: `doc_get_outline` returns `{"items":[]}` and
`doc_resolve_document_structure` gives only per-table summaries (`table_id`, `row_count`, often
empty `first_row_texts`). The real text lives in the cells.

1. `doc_resolve_document_structure` → list the `table_id`s with their row/col counts.
2. `doc_list_tables` → `first_row_texts` usually carries the section label (`基本情况` /
   `项目经验` / `指导研究生` …), which is how you find the table you need.
3. `doc_get_table_info` → full cells.

**The cell JSON nests as `{"block":{"table":{"cells":[…]}}}`** — `d['block']['table']['cells']`, not
`d['table']['cells']`. Each cell has `row` / `col` / `text`; group by `row`, sort by `col`, join with
` | ` to reconstruct the table. Long multi-line cells use `\n` (map it to ` ~ ` or `<br>` when
printing for review).

## Failure index

| Symptom | Cause | Fix |
|---|---|---|
| `document is not open` on `save_file` or a read, right after `open_file` | `open_file` is async; the chunked import hasn't finished | re-open once as a handshake, then poll `doc_get_outline` (§2) |
| The import never completes at all | reopening in a tight loop repeatedly cancels it | pace calls ≥2 s apart |
| `Unknown sheet tool: doc_*` + `workbook is not open` | the extension isn't mapped to `doc` (`.dot` / `.dotx` / `.docm` / `.wps` / none) — content is fine | rename the copy to `.doc` / `.docx`; `file_type="doc"` does **not** fix it |
| Every call `WinError 10061`, nothing on 39099+ | the daemon was reaped when its spawning shell exited | spawn it inside the same script (§4); don't kill `python.exe` broadly |
| `doc_get_outline` returns `{"items":[]}` | the resume has no heading styles | enumerate tables (§5) |
| Table cell text cut at 10 characters | `doc_resolve_document_structure` preview cap | `doc_get_table_info` |
| `KeyError: 'table'` | cells nest one level deeper | `d['block']['table']['cells']` |
| A carved JPEG decodes to a gray sliver | `.doc` picture records are not raw image files | save as `.docx`, unzip `word/media/` |
| A `.doc` comes back from `save_file` with a different magic number | `save_file` rewrites legacy `.doc` as OOXML under the original name | harmless; save to a new `.docx` path if a true Word 97 binary is required |
| A binary grep for text you just removed finds nothing — even text you *know* is there | OOXML compresses body text inside the ZIP | verify by re-reading through the editor instead of scanning bytes |
