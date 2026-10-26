# PWS starter kit

The shared plumbing for every Preferred Web Solutions site, so each build spends its time on design.

**Only things that are the same on every site belong here.** The look of a site (layout, type, colors,
header, footer, copy) and its features (before/after slider, service-area map, menu layout, gallery
filters, and so on) are designed fresh for each business. A feature is used only when it fits that
business, never because an earlier site had it.

## What's inside

| Path | What it is |
|---|---|
| `kit/pws.py` | Page wrapping, concept banner, skip link, consent script tag, image srcset expansion, the artifact variant of each page, and the five legal pages (Privacy, Terms, Cookies, Accessibility, Report an issue) generated from a small `Config`. |
| `kit/assets/consent.js` | The consent banner. `<script src="assets/consent.js" data-key="pws_consent_<slug>">`. Stores only the choice. |
| `kit/assets/kit.css` | Base styles for the skip link, consent banner, concept bar and legal pages. Theme with `--kit-*` variables. |
| `kit/prep_photos.py` | Exports photos at two widths with light correction and fractional crops; writes `img-meta.json`. |
| `kit/tests/` | `test.js` (axe, storage, requests, SEO, links, padding, phone overflow, tap targets, 200% zoom), `kb.js` (keyboard, consent, report form, reduced motion), `weight.js`, `shots.js`. Run `npm i` in `kit/tests` once. |
| `kit/tools/map/` | Census TIGER map tool (`fetch_tiger.js` + `render_map.py`). A tool, not a default feature. |
| `kit/tools/photos.md` | How to collect a business's public photos through the browser, with permission. |

## Using it in a build

```python
import sys; sys.path.insert(0, '/home/claude/pws-starter-kit/kit')
import pws
CFG = pws.Config(name='Business Name', city='Town, Ohio', phone='(555) 555-5555', tel='tel:+15555555555',
                 sms='sms:+15555555555', consent_key='pws_consent_slug', updated='October 26, 2026',
                 source='its Google listing, BBB profile and Yelp page',
                 photo_credit='Photos and logo are the business’s own, from its Google and Yelp listings, used for this preview.',
                 ratings_note='The Google rating is shown as listed in October 2026.', outbound=['Google', 'Yelp'])
legal = pws.legal_pages(CFG)   # {'privacy.html': (main_html, meta), ...}
```

Each site still writes its own `build.py` (header, footer, pages) and `style.css`, and copies
`kit/assets/consent.js` and `kit/assets/kit.css` into its `assets/` folder.

Legal pages are plain-language templates. A lawyer should review them before a site goes live.
