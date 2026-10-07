# Building the site

Detail for Step 5: the folder contract, the design system that worked, the photo component, the
content-shaping rules, and the layout traps.

## Folder contract

```
homepage/                  # EXACTLY what gets published
├── index.html
├── en.html                # only when a second language is wanted
├── styles.css             # ONE stylesheet, shared by every page
├── images/profile.jpg
├── files/cv.pdf
└── README.md              # deployment + "which line do I edit to change X" table
```

`homepage/` is the published artifact — no scratch files, probe pages, or helper scripts ever go in
it. Do the work in the parent directory under a `_` prefix and delete it in Step 7.

## Design tokens that worked

```css
:root{
  --ink:#1a1a1a; --body:#333; --muted:#666; --faint:#8a9199;
  --line:#e1e5e9; --line-soft:#eef1f4; --bg-soft:#f8f9fa;
  --accent:#f4a261; --accent-deep:#e76f51; --accent-wash:#fdf3e9;
  --width:900px;
}
```

- `body { max-width:900px; margin:0 auto; padding:0 24px; font-size:15px; line-height:1.75; }`
- Header row: `display:flex; gap:36px` — photo │ name + inline-SVG icons │ right-aligned affiliation
  block (`margin-left:auto; text-align:right; flex:0 1 auto` — see the flex trap below).
- Sticky anchor nav: `position:sticky; top:0; backdrop-filter:saturate(160%) blur(8px)`
  + `html{scroll-behavior:smooth; scroll-padding-top:84px}`.
- Long content → `<details><summary>` panels (the reference aesthetic uses this for "Older News").
  Custom chevron via `summary::before` with a rotated bordered square.
- Long lists become **scannable blocks** rather than one wall of text: `.timeline`
  (education/work), `.pub-list` (numbered papers + `.tag.sci/.tag.ei/.tag.core`), `.card-grid`
  (students), `table.plain` inside `.table-wrap{overflow-x:auto}`.
- Icons: **inline SVG — no Font Awesome, no icon CDN.** Self-contained, fast, and immune to slow or
  blocked foreign CDNs. Same for the favicon: an inline `data:image/svg+xml,...` monogram.
- Fonts: one `<link>` to Google Fonts *plus* a full CJK-aware fallback stack
  (`'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Source Han Sans SC'`) so a failed font
  request degrades gracefully instead of hanging.
- `@media print` (hide nav / back-to-top, flatten `<details>`) and a 760px breakpoint.
- ~25 lines of vanilla JS for scroll-spy nav highlighting + back-to-top. No framework.

## The `figure-grid` photo component

Users want project photos woven into the matching project entries, not dumped in a carousel. One
small reusable grid, repeated:

```css
/* FINAL working version — note height:auto, NOT a fixed height + object-fit:cover */
.figure-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
              gap:12px; margin:10px 0 2px; max-width:720px; align-items:start; }
table.plain td .figure-grid{ margin:10px 0 4px; max-width:100%; }  /* nested in a <td> */
li > .figure-grid{ margin:10px 0 6px; }                            /* nested in a <li> */
.figure-grid .wide{ grid-column:1 / -1; }          /* full-row hero image */
.figure-grid .tall img{ max-height:400px; width:auto; max-width:100%; margin:0 auto; }
.figure-grid figure{ margin:0; border:1px solid var(--line); border-radius:10px;
                     overflow:hidden; background:#fff; display:flex; flex-direction:column;
                     transition:box-shadow .2s ease, transform .2s ease; }
.figure-grid figure:hover{ box-shadow:0 4px 16px rgba(0,0,0,.1); transform:translateY(-2px); }
.figure-grid figure > a{ display:block; line-height:0; background:var(--bg-soft); }
.figure-grid img{ width:100%; height:auto; display:block; cursor:zoom-in; }
.figure-grid figcaption{ font-size:.85rem; color:var(--muted); line-height:1.65;
                         padding:9px 13px 11px 13px; border-top:1px solid var(--line-soft);
                         background:#fff; }
.figure-grid figcaption b{ color:var(--ink); font-weight:600; }
```

```html
<div class="figure-grid">
  <figure>
    <a href="images/xxx.png" target="_blank" rel="noopener">
      <img src="images/xxx.png" alt="accessible description" loading="lazy">
    </a>
    <figcaption><b>Project short name</b><br>What the photo actually shows</figcaption>
  </figure>
</div>
```

Rules that make it work:

- **Nest, don't batch.** A gallery collected below a whole table ("here are all the project photos")
  looks wrong — the reader can't tell which photo belongs to which project. Put each `figure-grid`
  **inside the description container of its own project** — inside the `<tr>`'s description `<td>`
  for a table, inside the matching `<li>` for a list. Match photo → project by filename first, then
  by looking at the image. Only fall back to a shared gallery if a photo belongs to no single entry.
- **Never fix the image height with `object-fit:cover` on project photos.** Resume photo sets have
  wildly mixed aspect ratios (0.75 → 2.27 in one folder); a fixed `height` crops screenshots and
  slices wide hardware shots. `height: auto` shows every image in full; `align-items: start` stops
  unequal heights from stretching.
- **Portrait images get a `.tall` variant — but it must not take a whole row.** Limit its height;
  do **not** give it `grid-column: 1 / -1`, which strands the other images in a lopsided
  one-column-plus-row layout (observed and reverted). `minmax(180px,1fr)` plus `.tall` in the flow
  keeps three mixed-ratio photos side by side.
- Wrap each `<img>` in `<a target="_blank">` — a free lightbox, no JS.
- Always write `alt` and `loading="lazy"`.
- Add `.wide` to one hero shot per gallery; leave the rest as equal tiles.
- At the 760px breakpoint: `grid-template-columns: 1fr` **only**. Do not reintroduce a fixed `img`
  height there — that re-crops on mobile.
- In `@media print`: `figure{break-inside:avoid}`, `img{height:auto; cursor:default}` (no
  `max-height` — it distorts tall images), `figure:hover{box-shadow:none;transform:none}`.

## Content rules

- Faithfully transcribe the resume — **never invent** affiliations, links, or metrics. Don't guess a
  department URL; link the university root you can verify.
- Condense: raw resume tables run 25–78 rows. Put the **top ~10–15** items in the open list and move
  the rest into a `<details>` panel. Keep every award and publication reachable, just not all at once.
- Translate the flat structure into **sections with a narrative order**:
  About → Research → News → Projects → Publications & IP → Teaching & Awards → Contact.

## Privacy checklist (do this by default, tell the user)

- **Mobile phone number: omit it.** A resume is sent to specific people; a `github.io` page is
  crawled by bots. Leave it inside an HTML comment with a one-line "uncomment to publish" note, and
  say so in the final reply.
- Group photos containing students → never publish.
- Home address / ID numbers → never publish.

## Layout traps

**Free text in a flex row.** A right-aligned affiliation block holding a long unit name will push the
whole row off the page if it can't shrink — and then squeeze its sibling column until the icon row
wraps. Use `flex: 0 1 auto` plus a `max-width` and let it wrap; **never `flex-shrink: 0`** on a block
that holds free text. Adding a second language is really an exercise in feeding much longer strings
into a layout tuned for short ones.

| Symptom | Cause | Fix |
|---|---|---|
| Photos cropped / sliced | fixed `img{height:NNNpx; object-fit:cover}` on wildly mixed aspect ratios | `height:auto`; a `.tall` variant that limits height only, never a full row |
| The user says photos don't match the projects | galleries batched below the whole table instead of nested per entry | nest each `figure-grid` in its project's own `<td>` / `<li>` |
| A photo's head is cropped in the circle | `object-fit:cover` centres vertically | `object-position: center 20%` |
| The header row slides off the page and the icons wrap to two rows | one long string in a `flex-shrink:0` block made the row wider than the page | `flex: 0 1 auto` + `max-width` on the free-text block |
