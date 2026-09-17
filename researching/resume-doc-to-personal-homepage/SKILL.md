---
name: resume-doc-to-personal-homepage
description: "Turn a resume/CV document (.doc / .docx / .wps) into a deployable GitHub Pages personal homepage — a self-contained static site (index.html + styles.css + images/ + files/cv.pdf). Triggers: 个人主页 / 个人网站 / 学术主页 / GitHub Pages 主页 built from a resume; restyling an existing resume as a web page; matching the layout of a reference academic homepage URL; adding a second language with a 中英文切换 toggle to an existing homepage. Not for editing the resume document itself, and not for a multi-page site with a backend."
agent_created: true
---

# Resume document → GitHub Pages personal homepage

A static single-page site built from a resume: `index.html` (+ optional `en.html`), one shared
`styles.css`, `images/`, `files/cv.pdf`. Validated end-to-end on a Chinese academic CV — legacy
Word 97 `.doc`, 997 KB, 8 tables, ~19 000 UTF-16 units — including a bilingual second pass.

**No resume at hand?** Hand the user `assets/resume-template.docx` to fill in — it is the expected
shape (stacked one-column tables, one section per table, `XXXX` marks a placeholder) — then read
it back in Step 1 like any other resume.

## The pipeline

| # | Step | Done when |
|---|---|---|
| 1 | Read the resume | every table's cell text is dumped to a `.txt` you have actually read |
| 2 | Extract the portrait photo | a photo file exists **and you have looked at it** and confirmed no third-party faces |
| 3 | *(optional)* export `files/cv.pdf` via Word COM | the PDF opens |
| 4 | *(only if a reference URL was given)* study the reference page | you hold its raw HTML **and** CSS, not rendered prose |
| 5 | Build the site | `homepage/` renders with zero horizontal overflow at every tested width |
| 6 | Verify rendering | the numeric probe reports `overflow=0` and `bad=[]` at every width, with every breakpoint sampled on both sides |
| 7 | Clean up and hand off | scratch files gone, user's source doc untouched (`is_dirty: false`), README + live preview delivered |

Read this file end to end first — it is the map. Each step below carries only its own hard rules
and points at the reference that holds the detail.

## Hard rules (invariant across every run)

1. **Extension picks the code path, not content.** `.doc` and `.docx` read fine; `.wps` / `.dot` /
   `.docm` / extensionless are silently mis-routed to the *sheet* category and every doc call then
   fails with `Unknown sheet tool: doc_*`. Fix by renaming a **copy** — byte-identical, the extension
   is all that is read. Never rename or rewrite the user's original.
2. **`open_file` is asynchronous.** Open → sleep 2 s → open again → poll `doc_get_outline` until it
   answers. Calling `save_file` too early reports `document is not open`, which looks like a broken
   file but is a race. Never reopen in a tight loop — each reopen cancels the import in flight.
3. **`doc_resolve_document_structure` truncates table cells to ~10 characters.** Real cell text comes
   from `doc_get_table_info`, whose cells nest as `d['block']['table']['cells']`.
4. **Never carve JPEGs out of the `.doc` binary.** Save it as `.docx` and unzip `word/media/`.
5. **Nest each project's photos inside that project's own container** (`<td>` or `<li>`) — a gallery
   batched below the table is the single most-corrected mistake.
6. **Project photos: `height:auto`, never a fixed height with `object-fit:cover`.** Aspect ratios in
   one resume folder ranged 0.75 → 2.27.
7. **A flex block holding free text gets `flex:0 1 auto` + `max-width`.** `flex-shrink:0` on a long
   translated unit name pushes the whole row off the page.
8. **Screenshot from an ASCII-only copy of the site, and launch Chrome from the Bash tool.** The
   PowerShell tool's sandbox cannot spawn Chrome at all — it fails silently.
9. **This box's Bash has no `ls` / `grep` / `mkdir` / `dirname`.** Do file work in Python; separate
   Bash commands with `;`, never `&&` (a missing utility short-circuits everything after it).
10. **The repo name is exactly `<GitHub-username>.github.io`, case included** — read the username off
    a link the user already gave you, never guess it from the pinyin of their name.
11. **Privacy, by default, without being asked:** omit the mobile number (leave it in an HTML comment
    with a one-line "uncomment to publish" note and say so in the final reply), never publish group
    photos containing students, home address, or ID numbers.

Hit an error mid-run? `references/windows-gotchas.md` is a symptom → cause → fix table covering the
environment traps above plus every failure this pipeline has actually produced. Check it before
debugging from first principles.

## Step 1 — Read the resume

Read `references/reading-the-doc.md` before your first tool call: it carries the extension routing
matrix, the handshake, daemon lifecycle, and the read pattern for a resume that is one big table.

```python
call("open_file", {"file_path": src})    # starts the chunked import
time.sleep(2)
call("open_file", {"file_path": src})    # same file_id — the completion handshake
time.sleep(3)
for _ in range(10):                      # poll until the model is live
    ok, _ = call("doc_get_outline", {"file_id": src})
    if ok: break
    time.sleep(2)
# only now read / save
```

Then dump the whole document to a readable `.txt` — outline, then per-table cell text via
`doc_get_table_info` — and read that file. Work from the dump, not from memory.

## Step 2 — Extract the portrait

Save the open `.doc` **as `.docx`**, unzip, and take `word/media/*` (clean, complete images; the
carving approach yields a ~20-row sliver). Expect one portrait, N identical 12×12 section-header
PNGs, and possibly a group photo.

**Read every candidate image before using it.** A CV often ends with a group/graduation photo full of
identifiable third parties — never publish that. Ship the portrait only.

Resize to the full frame and let CSS crop it to a circle; `object-position: center 20%` keeps the
head in frame where the default `center` clips the skull:

```python
im.resize((520, 756), Image.LANCZOS).save(site/"images/profile.jpg", "JPEG", quality=92)
```

## Step 3 — *(optional)* CV PDF

Word COM works here and leaves the source unmodified when opened read-only:

```powershell
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
$doc = $w.Documents.Open($src, $false, $true)   # ReadOnly
$doc.ExportAsFixedFormat($outPdf, 17)           # 17 = wdExportFormatPDF
$doc.Close(0); $w.Quit()
```

Put it at `files/cv.pdf` and link it from the header icon row and the contact section.

## Step 4 — *(only with a reference URL)* study the reference page

Download the raw HTML **and** CSS — the visual identity lives in the CSS, and fetching rendered text
loses it. Extract content width, section order, accent colours, font stack, and how collapsibles /
nav / publication lists are built. Reproduce the *layout system*, never the other person's content.

## Step 5 — Build the site

Read `references/building-the-site.md` before writing any CSS: design tokens, the `figure-grid`
photo component, the content-shaping rules, and the long-text layout trap all live there.

The shape of the deliverable:

```
homepage/                  # exactly what gets published — no scratch files, ever
├── index.html
├── en.html                # only when a second language is wanted
├── styles.css             # ONE stylesheet, shared by every page
├── images/profile.jpg
├── files/cv.pdf
└── README.md              # deployment + "which line do I edit to change X"
```

Do the work in the parent directory under a `_` prefix, then delete it in Step 7.

**Wanted a second language?** That is a real branch — read
`references/bilingual.md` in full before touching the markup. Two HTML files sharing one stylesheet
(the toggle is a top-right flex sibling of the nav, never absolutely positioned).

## Step 6 — Verify rendering

Read `references/verifying-render.md` for the ASCII-copy recipe, the Chrome invocation, the numeric
overflow probe, and the tall-screenshot techniques.

The two rules that matter even if you skip the file: copy the site to an ASCII-only path first
(`file:///` URLs under a CJK path render blank, and percent-encoding does not help), and verify
overflow with **numbers, not eyes** — inject a probe that writes `scrollWidth` / `clientWidth` /
overflow / out-of-bounds elements into `document.title` and read it back via `chrome --dump-dom`.

`--window-size` has a Windows **minimum width around 491 px**: asking for 430 silently yields a
491 px layout, which looks exactly like an overflow bug and is not one. For true phone widths, wrap
the page in an `<iframe width="390">` instead.

## Step 7 — Clean up and hand off

- Delete every `_*` scratch file. Confirm the user's source document is untouched (`get_pool_status`
  → `is_dirty: false`).
- Write the workspace memory note.
- `present_files` the `index.html` (the host opens a live preview) plus the README.
- The README must document deployment. Read `references/shipping-pages.md` and use its
  HTTPS + Personal-Access-Token recipe — SSH is the flow that most often dead-ends on a fresh
  Windows box, because the `id_rsa` there was never registered with GitHub. That file also carries
  the symptom → cause → fix table for the five deployment failures that actually happen.
- In the final reply state: where the folder is, how to push it (`<username>.github.io` for a root
  site, or a project repo + Settings → Pages), that all paths are relative so both work, and what
  you deliberately left out (phone number, group photo).
