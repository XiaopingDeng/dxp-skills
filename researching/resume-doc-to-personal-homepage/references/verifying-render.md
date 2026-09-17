# Verifying the render

Detail for Step 6. Rendering is verified with **numbers first, screenshots second** — a screenshot
only ever confirms what the numbers already told you.

## Copy the site to an ASCII-only path

`file:///` URLs pointing at a path containing CJK characters reliably produce a blank render
("无法访问您的文件" / `ERR_FILE_NOT_FOUND`), and percent-encoding does not help. Copy the site first.

Do the copy **in Python**, not in a shell: the workspace path itself may contain CJK, and PowerShell
can't reliably hold a CJK path literal. Copy only the files the site needs — pulling in `.git` drags
along read-only objects that break the next cleanup:

```python
import os, shutil
SRC = r"<workspace>\homepage"
DST = os.path.join(os.environ['TEMP'], 'hp_test')
if os.path.isdir(DST):
    shutil.rmtree(DST, ignore_errors=True)
os.makedirs(DST, exist_ok=True)
for item in ['index.html', 'styles.css', 'images', 'files']:      # add en.html if bilingual
    s, d = os.path.join(SRC, item), os.path.join(DST, item)
    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)
```

## Screenshot from the Bash tool, Chrome by full path

The PowerShell tool's sandbox cannot spawn Chrome at all — it fails silently, with no error and no
output file:

```bash
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
T="${TEMP//\\//}"                       # must be a forward-slash path
P="--headless=new --disable-gpu --hide-scrollbars --no-first-run --force-device-scale-factor=1"
"$CH" $P --user-data-dir="$T/hp_prof" --window-size=1180,5200 \
       --virtual-time-budget=8000 --screenshot="$T/hp_shot.png" \
       "file:///$T/hp_test/index.html"
```

Chrome prints `N bytes written to file …`; `--screenshot` messages go to stderr and the exit code is
not authoritative — **check that the file exists.**

**Locating content in a tall screenshot.** If Pillow is available, scan for photo bands instead of
guessing crop offsets: step a coarse grid down the image, count rows whose dark-pixel density exceeds
a threshold, and group contiguous rows. Photo regions jump out (density 4000+ vs ~2100 for text).

## Probe overflow numerically

**`--window-size` has a Windows minimum width around 491 px.** Asking for `430` silently yields a
491 px layout viewport while the PNG is still 430 px wide. The result looks exactly like a horizontal
overflow bug — text sliced at the right edge, nav cut mid-item — but it is purely a screenshot
artifact. Do **not** "fix" CSS because of it.

Inject a probe into a throwaway copy of the page that writes the measurements into `document.title`,
then read the title back from `chrome --dump-dom`. Driving Chrome from Python
(`subprocess.run(capture_output=True)`) *does* return its stdout — only the PowerShell tool swallows
it — and this beats an on-screen overlay, which covers the very content you are inspecting:

```python
PROBE = u"""<script>
window.addEventListener('load', function(){ setTimeout(function(){
  var de=document.documentElement, cw=de.clientWidth, bad=[];
  Array.prototype.forEach.call(document.querySelectorAll('body *'), function(el){
    var r=el.getBoundingClientRect();
    if(r.width===0&&r.height===0) return;
    if(r.right>cw+1) bad.push(el.tagName.toLowerCase()+'.'+el.className+'='+Math.round(r.right));
  });
  document.title='METRICS|scrollW='+de.scrollWidth+'|clientW='+cw+'|overflow='+(de.scrollWidth-cw)
    +'|bad=['+bad.slice(0,6).join(' ; ')+']';
}, 400); });
</script>
</body>"""
s = io.open(page, encoding='utf-8').read().replace('</body>', PROBE, 1)
io.open(probe_page, 'w', encoding='utf-8').write(s)
```

Then `chrome --headless=new --user-data-dir=<temp> --window-size=W,900 --dump-dom <url>` and regex out
`METRICS\|[^<]*`. Require `overflow=0` and `bad=[]` at every width worth checking, and **sample both
sides of every breakpoint you wrote** (e.g. 1120 / 960 / 940 / 810 / 800 / 790 / 760 / 720 / 600 /
420) — a rule correct at 900 px can still be wrong at 806 px.

## True narrow viewports

Wrap the page in an iframe: it gets the width you give it regardless of the window minimum.

```html
<iframe src="index.html" width="390" height="1500"></iframe>
```

Screenshot that wrapper — this is the reliable way to eyeball 360 / 390 px phones. For mid-page detail,
reuse the trick with a clipping window:

```html
<div style="width:1000px;height:1150px;overflow:hidden">
  <iframe src="index.html" style="width:1000px;height:10000px;margin-top:-2950px"></iframe>
</div>
```

An anchor such as `#projects` does **not** scroll a headless screenshot — `html{scroll-behavior:smooth}`
hasn't finished when the shot is taken. Clip a fixed-height box around an iframe offset by a negative
`top`, using that section's measured `offsetTop`.

## Structural self-check

After any edit that touches list or table structure, count tag pairs before rendering:

```python
import re, io
s = io.open(path, encoding='utf-8').read()
for t in ['ul','ol','li','div','figure','figcaption','details','section','a']:
    o = len(re.findall(r'<'+t+r'[ >]', s)); c = len(re.findall(r'</'+t+r'>', s))
    print(t, o, c, 'OK' if o == c else '<<< MISMATCH')
```

One known false positive: a tag inside an HTML comment (e.g. `<!-- … <a> … -->`) counts as an opener —
read the reported line before "fixing" it. For a **bilingual** site use the parity variant in
`bilingual.md` instead (counts compared *between* the two files).

| Symptom | Cause | Fix |
|---|---|---|
| Blank render / `ERR_FILE_NOT_FOUND` from `file:///` | the path contains CJK characters — percent-encoding doesn't help | copy the site to an ASCII-only dir and screenshot that |
| "Horizontal overflow" at 430 px | Chrome clamps the window width to ~491 px | trust `scrollWidth`, or use an iframe |
| An anchor like `#projects` doesn't scroll the screenshot | smooth scrolling hasn't finished when the shot is taken | clip a fixed-height box around an iframe offset by a negative `top` |
| Eyeballing screenshots misses overflow | the offending element may be below the fold | probe `scrollWidth` / `clientWidth` / overflow **and** the out-of-bounds element list into `document.title`, then read it back with `--dump-dom` |
