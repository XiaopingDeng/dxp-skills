# Adding a second language (the two-file pattern)

A real branch, not a variation: read this in full **before** touching the markup. Skip it entirely
if the user only wants one language.

Academic homepages get asked for this — "add an English mode, with a toggle in the top-right". Use
**two HTML files sharing one stylesheet**, not a runtime `data-i18n` dictionary:

| file | language |
|---|---|
| `index.html` | default / primary language (`<html lang="zh-CN">`) |
| `en.html` | second language (`<html lang="en">`), own translated `<head>` + JSON-LD |

Both approaches cost the same to maintain — either way a content edit means editing two places — but
two files additionally give you: no JS dependency (the second-language page works with scripts off),
a correct `lang` attribute and translated `<meta>` for search engines and screen readers, a printable
second-language version, and a URL you can send to a foreign collaborator on its own.

Do **not** add browser-language auto-redirect: it evicts primary-language visitors from the homepage,
hurts indexing, and misfires into a loop when the rules are wrong. The toggle is enough.

## Hard rules

- **Keep the two files structurally identical, tag for tag.** Same section order, same `<section id>`
  values, same classes, same `<figure>` order, same image filenames, same `<details>` count. Only the
  human-readable text differs. Identical anchor ids are what let the toggle land on the same section
  after switching — drift there breaks the feature.
- **The second-language page is italic-heavy by convention, the primary one is not.** English
  academic style italicises journal and course names; Chinese citations don't. An `<i>` count
  mismatch is therefore expected and correct — don't "fix" it. (`<a>` and `<img>` also throw known
  false positives in a naive tag counter; see below.)
- Copy the resume's Chinese-only journal names to their conventional English titles
  (《自动化学报》 → *Acta Automatica Sinica*, 《仪器仪表学报》 → *Chinese Journal of Scientific
  Instrument*) and romanise Chinese author names (family name in caps, given-name initials). Translate
  patent status words too: 申报中 → application under preparation, 受理 → accepted, 实审 → under
  substantive examination, 初审合格 → passed preliminary examination, 待领证 → certificate pending,
  一通 → first office action, 复审受理 → reexamination accepted.
- Give the second-language page its own `og:locale`, and add reciprocal
  `<link rel="alternate" hreflang="…">` pairs to both `<head>`s.
- Content updates are always "edit the same section twice" — no stylesheet change is involved.

## The toggle

Current language is a non-clickable `<span>`; the other is an `<a>` (swap the two on the second page):

```html
<div class="lang-switch" role="group" aria-label="语言切换 / Language">
  <span class="is-current" lang="zh-CN">中文</span>
  <a href="en.html" id="langLink" data-href="en.html" hreflang="en" lang="en">EN</a>
</div>
```

```css
/* The nav and the toggle share ONE flex row and split the width with flex — so they cannot
   overlap, whatever the label lengths are. */
.banner{ display:flex; align-items:center; justify-content:center; gap:16px; }
                       /* keep the existing sticky / z-index / background / borders */
.navbar{ flex:1 1 auto; }        /* centres inside the space left by the toggle,
                                    instead of centring across the full width */
.lang-switch{ flex:0 0 auto; display:inline-flex; align-items:center; gap:2px;
              padding:2px; border:1px solid var(--line); border-radius:999px;
              background:#fff; font-size:.78rem; line-height:1; }
.lang-switch a,.lang-switch span{ display:inline-block; padding:4px 10px;
              border-radius:999px; font-weight:500; white-space:nowrap; }
.lang-switch .is-current{ color:#fff; background:var(--accent); }
.lang-switch a{ color:var(--muted); }
/* Below N px the nav is about to wrap on its own — drop the toggle to its own centred row
   *before* that happens. N = the measured single-row threshold, not a round number. */
@media (max-width:804px){
  .banner{ flex-wrap:wrap; }
  .navbar{ flex:1 1 100%; }
  .lang-switch{ margin-top:2px; }
}
@media print{ .lang-switch{ display:none; } }
```

**Never `position:absolute` the toggle to the right edge of the banner.** The trap: the nav is centred
across the *full* width, so a longer language (English labels run ~25% wider than the Chinese ones)
pushes the nav's right end past the toggle's left end and they collide. It is invisible in the primary
language and only shows up once the second page exists.

**Measure the wrap threshold; don't guess it.** Probe the second-language page at 5 px steps and find
the viewport width where the nav first renders on a single row (one run: available width 782 px → two
rows, 787 px → one row ⇒ viewport 805 px). Set the media query 1 px *below* that number. Getting it
wrong in the other direction leaves a band where the nav has already wrapped to two rows while the
toggle floats vertically centred in the gap between them — not an overlap, but visibly broken.

```python
# probe: the nav links' tops collapse to one distinct value  ->  nav is on a single row
rows = {round(l.getBoundingClientRect().top) for l in document.querySelectorAll('.nav-link')}
```

Carry the section anchor across the switch — otherwise "click EN while reading Projects" dumps the
reader back at the top. One line in the existing footer script:

```js
var langLink = document.getElementById('langLink');
if (langLink && location.hash) langLink.href = langLink.getAttribute('data-href') + location.hash;
```

## Parity self-check

Run after every content edit to either file:

```python
import re, io
def c(p):
    s = io.open(p, encoding='utf-8').read()
    return {t: (len(re.findall(r'<'+t+r'[\s>/]', s)), len(re.findall(r'</'+t+r'>', s)))
            for t in ['section','div','ul','ol','li','details','summary','table','tr','td',
                      'figure','figcaption','h1','h2','h3','p','span','svg','b']}
a, b = c('index.html'), c('en.html')
for t in a:
    print(t, a[t], b[t], 'OK' if a[t] == b[t] else '<<< MISMATCH')
```

Then add the identity checks — a mismatch in either means the two languages have drifted
structurally, which is the one thing that breaks anchor-carrying language switches:

- the `<section id>` list is equal in both files;
- the `<img src>` list is equal in both files.

Known-benign results: `<a>` reports one more opener than closer in *both* files (the spare tag lives
inside a commented-out contact card), and `<i>` legitimately differs (see the italics rule above).
For structural edits to a single-language site, use the tag-pair check in `verifying-render.md`.

Feeding much longer translated strings into a layout tuned for short ones is where the layout breaks —
see **Layout traps** in `building-the-site.md` before you widen anything.

| Symptom | Cause | Fix |
|---|---|---|
| The nav's last link overlaps the toggle | the toggle was `position:absolute; right:0` while the nav centres across the full width — the wider language pushes over it | put both in one flex row (`.navbar{flex:1 1 auto}`, `.lang-switch{flex:0 0 auto}`) |
| The toggle floats in the gap between two wrapped nav rows | the wrap breakpoint sat *below* the nav's true single-row threshold | measure the threshold, set the media query ~1 px under it |
| A collision probe reports an overlap that isn't there | it compared only `left`/`right`, so the toggle on row 2 "overlapped" the last link on row 1 | include the vertical band: `sr.left<nr.right && sr.top<nav.bottom && sr.bottom>nav.top` |
| The `<i>` count differs between the two files | intentional — English italicises journal and course names, Chinese doesn't | ignore it; don't "fix" it |
