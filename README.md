# Selskab & Salut – Jekyll template

A static site for the hackathon: a fictional event agency specialised in Smålandsfarvandet, hosting
events on four invented islands (Kobberø and Lyngø with ferries, the private islands Ravneholm and
Sælholm without). It has venues, catering, suppliers, transport, an archive and an internal file
share. It runs on GitHub Pages as is, uses no JavaScript and
loads no external files, so every page can be crawled with `requests` + BeautifulSoup and every table
can be read with `pandas.read_html`.

## Installing

1. Copy everything in this folder to the root of the `selskabogsalut.github.io` repository.
   It replaces the existing `index.md` and `_config.yml`.
2. If the old `_config.yml` had a `theme:` or `remote_theme:` line, it is gone now. Keep it that way:
   the layouts in `_layouts/` are the whole design.
3. Push. GitHub Pages builds the site in a minute or two.
4. Resubmit the front page to IndexNow (same URL as before), since the content has changed.

`7d12bd4d8b5d329106c3e5a815b01b11.txt` is the IndexNow key file and must stay in the root.

## Structure

```
_config.yml           site settings, collections, default dates
_data/sektioner.yml   the sections: menu order, titles, sorting
_data/felter.yml      which fields each section shows, column names, units, links
_layouts/             default (frame), forside, sektion (list page), emne (item page), side
_includes/            header, footer, breadcrumb, tables, signal flags
_spisesteder/ _catering/ _leverandoerer/ _transport/ _arkiv/ _fildeling/   one .md file per page
spisesteder.md ...    the list page for each section
oversigt.html         HTML list of every page (/oversigt/)
robots.txt            allows everything and points to sitemap.xml
assets/css/stil.css   all styling
tools/crawl_test.py   crawl test (not published)
```

## Editing data

Each venue, catering menu, supplier, route and archive entry is one Markdown file. The file name becomes
the address: `_spisesteder/pakhuset.md` → `/spisesteder/pakhuset/`. Use only `a-z`, `0-9` and `-`
in file names.

The front matter holds the data; the text below it is the page's body text (brødtekst), shown next
to the facts table:

```yaml
---
title: Pakhuset
description: One sentence shown under the heading and used by search engines.
kapacitet: 120
eget_koekken: false
lokaler:                       # a list becomes a table
  - { lokale: Loftet, siddende: 120, staaende: 180, tillaeg: 0 }
---
Free text in Markdown.
```

`_data/felter.yml` decides which fields are shown, in what order, with which heading, and which
fields also appear as columns on the section's list page (`liste: true`). A field that is not listed
there is not shown, so adding a new field takes two steps: add it to the page's front matter and to
`felter.yml`.

Fields with `link: <section>` turn a file name into a link, e.g. `spisested: pakhuset` in the archive
links to `/spisesteder/pakhuset/`.

Conventions that keep the data easy to scrape:

- Numbers are plain integers without thousands separators or units. The unit is in the column
  heading, e.g. `Pris (kr.)`.
- `true`/`false` are shown as `Ja`/`Nej`.
- Dates are ISO (`"2026-06-20"`, in quotes) and times are `"07:15"` (also in quotes, or YAML may
  read them as numbers).
- Every table has an `id`: `fakta` for the facts table, the field name for lists (`retter`,
  `prisliste`, `afgange`, `sejltider`, `priser`, `lokaler`), and the section name on list pages.
- "Leverer til" is either a comma-separated list of islands or `Alle øer`.
- The body text on every item page is in `<div id="broedtekst">`.
- `dato: true` in `felter.yml` keeps a date on one line in tables.

### Fildeling (intern)

The file share works like the other sections, but each page is a source: a newspaper article, a
mail, a yearbook article and so on. The facts are `dato`, `kilde`, `type` and `forfatter` (optional),
and the body text is the source itself, shown as a document in a serif typeface. That look comes
from `visning: dokument` in `_data/sektioner.yml`, so any other section can use it too.

```markdown
---
title: "Ugeavisen: Pakhuset åbner igen"
description: One sentence summarising the source.
dato: "2025-05-15"
kilde: Kobberø Ugeavis
type: Avisartikel
forfatter: Signe Holm
---

The article text in Markdown. Use > for quotes.
```

Files are sorted by date, newest first.

### Adding a section

1. Add a collection to `_config.yml` (copy one of the existing ones) and a matching block under
   `defaults:` with `layout: emne`.
2. Add the section to `_data/sektioner.yml` and its fields to `_data/felter.yml`.
3. Create `<section>.md` in the root with `layout: sektion`, `samling: <section>` and a `permalink`.
4. Create the folder `_<section>/` with one file per page.

The menu, footer, front page and `/oversigt/` pick it up automatically.

## Crawlability

- All navigation is plain `<a href>` links with trailing slashes. Nothing depends on JavaScript.
- Every page is at most two clicks from the front page, and the footer on every page links to all
  sections and to `/oversigt/`, which links to every page.
- `sitemap.xml` (generated by jekyll-sitemap) lists every page, and `robots.txt` points to it.

A minimal crawler and table reader, the kind participants might write:

```python
import requests, pandas as pd
from io import StringIO

r = requests.get("https://selskabogsalut.github.io/catering/havets-bord/")
retter = pd.read_html(StringIO(r.text), attrs={"id": "retter"})[0]
```

GitHub Pages sends `charset=utf-8`, so `r.text` decodes æ, ø and å correctly. When testing against
`python -m http.server` locally, set `r.encoding = "utf-8"` first; that server sends no charset.

## Testing

```
python3 tools/crawl_test.py https://selskabogsalut.github.io/
```

It follows every link from the front page using only the Python standard library, reports the
status and number of tables per page, and checks that every page in `sitemap.xml` can be reached via
links. Exit code 0 means everything is fine.

To preview locally (needs Ruby): `bundle install`, then `bundle exec jekyll serve` and open
http://localhost:4000.

## After changing content

`sitemap.xml` gives each page a `lastmod` date, which Bing uses to decide what to fetch again. The
default date is set under `defaults:` in `_config.yml`. Update it when you change many pages, or set
`last_modified_at: 2026-12-01` in a single page's front matter when only that page changes. Then
resubmit the changed URLs to IndexNow.

## Notes

- Fonts: headings use condensed DIN-style system fonts (Bahnschrift on Windows, DIN on macOS,
  Roboto Condensed or Arial Narrow elsewhere). Nothing is downloaded, so there are no external
  requests and no font data sent to third parties.
- Light and dark mode follow the visitor's system setting.
- The footer notice saying the agency and data are fictional is set by `fiktion:` in `_config.yml`.
  Set it to `""` to hide it, but keeping it is sensible while the site is public and indexed.
- Links inside Markdown text use root paths like `/catering/havets-bord/`. That works because this
  is a user site at the domain root (`baseurl: ""`).
- The front page keeps the test details for the Bing/Copilot check (Hr. Kvistbjørn and the
  salutnøgle). Remove them once the test is done.
