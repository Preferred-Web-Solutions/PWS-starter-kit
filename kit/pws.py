"""PWS starter kit: the shared plumbing every Preferred Web Solutions site needs.

Only things that are identical on every site live here: page wrapping, the concept
banner, the consent banner hookup, image srcset expansion, the artifact variant and
the legal pages. Everything a visitor sees as "the design" (header, footer, layout,
type, colors, features) is written fresh for each business in that site's own build.

Usage from a site's build.py:

    import sys; sys.path.insert(0, '/path/to/pws-starter-kit/kit')
    import pws
    CFG = pws.Config(name="Wooster Drain Cleaning", ...)
    pages = pws.legal_pages(CFG)          # {'privacy.html': (body, meta), ...}
    html = pws.document(head_html, body_html)
    pws.write_site(pages_rendered, SITE, ART, short_title)
"""
import json, re, shutil, pathlib
from dataclasses import dataclass, field

PWS_EMAIL = 'preferredwebsolutions@gmail.com'
FORMSPREE = 'https://formspree.io/f/xgavryzg'
NT = '<span class="sr-only"> (opens in a new tab)</span>'


@dataclass
class Config:
    name: str                      # full business name, HTML-escaped (use &amp;)
    city: str                      # "Wooster, Ohio"
    phone: str                     # "(330) 262-1543"
    tel: str                       # "tel:+13302621543"
    consent_key: str               # "pws_consent_<slug>"
    updated: str                   # "October 26, 2026"
    version: str = '1.0'
    sms: str = ''                  # "sms:+1..." if the number takes texts
    email: str = ''                # only a PUBLIC business email, never a personal one
    source: str = 'public listings'          # where the preview info came from
    photo_credit: str = ''         # one sentence on where the photos/logo came from
    ratings_note: str = ''         # one sentence on where ratings come from, or ''
    outbound: list = field(default_factory=list)   # names of sites we link to, e.g. ['Google', 'Yelp']
    demo_form: bool = True         # site has a not-connected quote/contact form
    motion: bool = True            # site uses scroll animations (affects accessibility text)
    preview: bool = True           # concept preview (True) or live client site (False)


def call_line(c: Config) -> str:
    verb = 'Call or text' if c.sms else 'Call'
    return f'{verb} <a href="{c.tel}">{c.phone}</a>'


def _template_note(c):
    if not c.preview:
        return '<p><strong>Plain-language template.</strong> These pages describe what this site does. They should be reviewed by a lawyer.</p>'
    return ('<p><strong>Plain-language template.</strong> This is a preview site. These pages describe only what the preview site '
            'actually does today. They are a template and should be reviewed by a lawyer before the site goes live.</p>')


def _links_sentence(c):
    if not c.outbound:
        return ''
    names = c.outbound[0] if len(c.outbound) == 1 else ', '.join(c.outbound[:-1]) + ' and ' + c.outbound[-1]
    return names


def legal_pages(c: Config) -> dict:
    """Privacy, Terms, Cookies, Accessibility and Report-an-issue page bodies (each wrapped in <main class="legal">)."""
    meta = lambda t, d: {'title': f'{t} | {c.name}', 'desc': d}
    back = '<p class="legal-back"><a href="index.html">← Back to the home page</a></p>'
    head = lambda t: f'<main id="main" class="legal">\n<h1>{t}</h1>\n<p class="meta">Version {c.version} · Last updated {c.updated}</p>\n'
    links = _links_sentence(c)
    who = f'This site is for {c.name}, {c.city}, phone <a href="{c.tel}">{c.phone}</a>.'
    if c.preview:
        who += f' The preview was built by Preferred Web Solutions (<a href="mailto:{PWS_EMAIL}">{PWS_EMAIL}</a>).'
    out = {}

    collect = ['<li><strong>Browsing this site:</strong> nothing is collected by us. The site has no analytics, advertising pixels, embedded maps, '
               'videos or social widgets. Fonts and photos are hosted on this site, so your browser does not contact Google or other font services. '
               'Like any website, the hosting provider may keep standard server logs (such as IP address and pages requested) for security and operation.</li>',
               '<li><strong>Your cookie choice:</strong> we save your consent choice in your browser’s local storage so we don’t ask on every page '
               '(see the <a href="cookies.html">Cookie Policy</a>).</li>']
    if c.demo_form:
        collect.append('<li><strong>The quote form:</strong> this is a working demo and is not connected. Nothing you type is sent anywhere.</li>')
    collect.append('<li><strong>Report a website issue form:</strong> if you use it, what you type is sent to our form processor, Formspree, so we can read it and reply.</li>')
    if links:
        collect.append(f'<li><strong>Links to {links}:</strong> these links open those companies’ own sites in a new tab. Their privacy policies apply there. '
                       'Nothing from them loads on this site unless you click.</li>')
    out['privacy.html'] = (head('Privacy Policy') + _template_note(c) + f'''
<h2>Who we are</h2>
<p>{who}</p>
<h2>What we collect</h2>
<ul>
{chr(10).join(collect)}
</ul>
<h2>How we use it</h2>
<p>Only to answer your message or fix a site problem you reported. We do not sell personal information.</p>
<h2>Your choices and rights</h2>
<p>Depending on where you live, you may have rights to access, correct or delete personal information. To make a request, email <a href="mailto:{PWS_EMAIL}">{PWS_EMAIL}</a>. You can change or withdraw your cookie choice at any time with the “Cookie settings” button in the footer.</p>
<h2>Children</h2><p>This site is not directed to children under 13.</p>
<h2>Changes</h2><p>If this policy changes, we will update the date and version above.</p>
{back}
</main>''', meta('Privacy Policy', f'How the {c.name} website handles your information.'))

    info = (f'<h2>This is a preview</h2>\n<p>This website is a concept preview made by Preferred Web Solutions for {c.name}. '
            'It is not the official website until the owner approves it and it is made live.</p>\n') if c.preview else ''
    terms = [info,
             f'<h2>Information on this site</h2>\n<p>{"This preview was built from " + c.source + ". " if c.preview else ""}'
             'Details marked “to be confirmed” have not been verified with the owner. Services, hours, availability and prices can change. '
             f'{call_line(c)} to confirm anything before relying on it. Nothing on this site is a quote; prices are given after you talk with us.</p>']
    if c.ratings_note:
        terms.append(f'<h2>Ratings and reviews</h2>\n<p>{c.ratings_note} Reviews belong to the people who wrote them.</p>')
    if c.photo_credit:
        terms.append(f'<h2>Photos</h2>\n<p>{c.photo_credit}</p>')
    terms.append('<h2>Limits</h2>\n<p>The site is provided “as is” for information. To the extent the law allows, the business and Preferred Web Solutions '
                 'are not liable for loss from using it. Nothing here limits rights you have under the law.</p>')
    terms.append(f'<h2>Contact</h2><p><a href="mailto:{PWS_EMAIL}">{PWS_EMAIL}</a></p>')
    out['terms.html'] = (head('Terms &amp; Conditions') + _template_note(c) + '\n' + '\n'.join(t for t in terms if t) + f'\n{back}\n</main>',
                         meta('Terms &amp; Conditions', f'Terms for using the {c.name} website.'))

    third = 'Fonts and images load from this site only. If you send the “Report a website issue” form, your browser sends that form to Formspree, our form processor, only at the moment you submit it.'
    if links:
        third += f' Links to {links} open those sites only when you click them.'
    out['cookies.html'] = (head('Cookie Policy') + _template_note(c) + f'''
<h2>Short version</h2>
<p>This site sets no cookies and loads no analytics, advertising, map, video or social tools. It stores one item in your browser so it remembers your cookie choice.</p>
<h2>What is stored</h2>
<div class="table-wrap"><table><thead><tr><th scope="col">Name</th><th scope="col">Type</th><th scope="col">Purpose</th><th scope="col">Category</th><th scope="col">Duration</th><th scope="col">Set by</th></tr></thead>
<tbody><tr><td><code>{c.consent_key}</code></td><td>Local storage (not a cookie)</td><td>Remembers your cookie choice, the date you made it and the policy version</td><td>Essential</td><td>Until you clear it or the policy version changes</td><td>This site</td></tr></tbody></table></div>
<h2>Third parties</h2>
<p>{third}</p>
<h2>Your choices</h2>
<p>Use the “Cookie settings” button in the footer to reopen the banner at any time. If optional tools are ever added, they will stay off until you opt in, and this page will be updated first.</p>
<h2>Clearing stored data</h2>
<ul><li><strong>Chrome and Edge:</strong> Settings → Privacy → Site data, search for this site and remove it.</li><li><strong>Firefox:</strong> Settings → Privacy &amp; Security → Cookies and Site Data → Manage Data.</li><li><strong>Safari:</strong> Settings → Privacy → Manage Website Data.</li></ul>
{back}
</main>''', meta('Cookie Policy', f'What the {c.name} website stores in your browser.'))

    motion = 'Photos have text descriptions' + (', and animations turn off if your device asks for reduced motion.' if c.motion else '.')
    out['accessibility.html'] = (head('Accessibility') + f'''<p>We want everyone to be able to use this site. It was built with accessibility in mind, aiming for the Web Content Accessibility Guidelines (WCAG) 2.1 level AA.</p>
<h2>What we did</h2>
<ul>
<li>Services, the phone number, hours and the service area are real text on the page, not pictures or PDFs.</li>
<li>Everything works with a keyboard, with a visible focus outline and a “Skip to content” link.</li>
<li>Text and buttons meet color-contrast guidelines, and the page works when zoomed to 200%.</li>
<li>{motion}</li>
<li>Each page was checked with the automated axe accessibility tool and by hand with a keyboard.</li>
</ul>
<h2>Known limits</h2>
<p>Automated tools catch only some problems, and we may have missed something.{(" Links to " + links + " open those sites, which we don’t control.") if links else ""}</p>
<h2>Need help or found a problem?</h2>
<p>{call_line(c)}, or <a href="report.html">report a website issue</a> and we’ll fix it.</p>
{back}
</main>''', meta('Accessibility', f'Accessibility statement for the {c.name} website.'))

    fail = f"Sorry, that did not send. Please email {PWS_EMAIL}."
    script = ("<script>\n(function(){var f=document.getElementById('rf');f.addEventListener('submit',function(e){e.preventDefault();var m=document.getElementById('rmsg');\n"
              "if(!f.checkValidity()){m.textContent='Please add your email and a short description.';var b=f.querySelector(':invalid');if(b)b.focus();return}\n"
              "m.textContent='Sending...';\nfetch(f.action,{method:'POST',body:new FormData(f),headers:{Accept:'application/json'}}).then(function(r){\n"
              " if(r.ok){f.hidden=true;var d=document.getElementById('rdone');d.hidden=false;document.getElementById('rdoneh').focus()}else{m.textContent='" + fail + "'}\n"
              "}).catch(function(){m.textContent='" + fail + "'})})})();\n</script>")
    out['report.html'] = (head('Report a website issue') + f'''<p>Something broken, hard to read or hard to use on this site? Tell us and we’ll look at it. For service, {call_line(c)[0].lower() + call_line(c)[1:]}.</p>
<form id="rf" action="{FORMSPREE}" method="POST" class="legal-form" novalidate>
<input type="hidden" name="business" value="{c.name}{" (preview site)" if c.preview else ""}">
<input type="hidden" name="page" value="report.html">
<label>Your name (optional)<input name="name" autocomplete="name"></label>
<label>Your email (so we can reply)<input name="email" type="email" autocomplete="email" required></label>
<label>What went wrong?<textarea name="message" required placeholder="Which page, what you tried and what happened"></textarea></label>
<button class="btn" type="submit">Send report</button>
<p id="rmsg" class="status" role="status"></p>
</form>
<div id="rdone" hidden><h2 tabindex="-1" id="rdoneh">Thank you</h2><p>Your report was sent. We’ll look at it and reply by email if we need more information.</p></div>
{back}
</main>''', dict(meta('Report a Website Issue', f'Tell us about a problem with the {c.name} website.'), extra_body=script))
    return out


# ---------- images ----------
def img_attrs(IMG: dict, key: str, sizes='100vw', ext='jpg') -> str:
    m = IMG[key]; s = m['sizes']; w0 = s[0]; h0 = round(m['h'] * w0 / m['w'])
    srcset = ', '.join(f'img/{key}-{w}.{ext} {w}w' for w in s)
    return f'src="img/{key}-{w0}.{ext}" srcset="{srcset}" sizes="{sizes}" width="{w0}" height="{h0}"'


def expand_images(html: str, IMG: dict) -> str:
    """<img data-img="key" data-sizes="..."> -> src/srcset/sizes/width/height from img-meta.json."""
    return re.sub(r'data-img="([a-z0-9-]+)"(?: data-sizes="([^"]+)")?',
                  lambda m: img_attrs(IMG, m.group(1), m.group(2) or '100vw'), html)


# ---------- documents ----------
CONCEPT_LONG = 'Concept preview by Preferred Web Solutions, not the official website'
CONCEPT_SHORT = 'Concept preview by Preferred Web Solutions'


def concept_bar(cls='concept') -> str:
    return (f'<aside class="{cls}" aria-label="Preview notice"><span class="long">{CONCEPT_LONG}</span>'
            f'<span class="short">{CONCEPT_SHORT}</span></aside>')


def skip_link(target='#main') -> str:
    return f'<a class="skip" href="{target}">Skip to content</a>'


def scripts(consent_key: str, extra=('assets/app.js',)) -> str:
    s = f'<script src="assets/consent.js" data-key="{consent_key}"></script>'
    return s + ''.join(f'\n<script src="{x}"></script>' for x in extra)


def head(meta: dict, css='assets/style.css', preload=(), theme='#ffffff', favicon='img/favicon.png', noindex=True) -> str:
    pre = ''.join(f'\n<link rel="preload" href="{p}" as="font" type="font/woff2" crossorigin>' for p in preload)
    robots = '\n<meta name="robots" content="noindex,nofollow">' if noindex else ''
    return (f'<title>{meta["title"]}</title>\n<meta name="description" content="{meta["desc"]}">{robots}\n'
            f'<meta name="theme-color" content="{theme}">\n<link rel="icon" href="{favicon}" type="image/png">{pre}\n'
            f'<link rel="stylesheet" href="{css}">\n<script>document.documentElement.className+=\' js\'</script>\n{meta.get("extra_head", "")}')


def document(head_html: str, body_html: str) -> str:
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'{head_html}\n</head>\n<body>\n{body_html}\n</body>\n</html>\n')


def artifact_index(head_html: str, body_html: str, short_title: str) -> str:
    """Artifact pages are wrapped by the host, so index has no html/head/body tags."""
    h = re.sub(r'<title>.*?</title>', f'<title>{short_title}</title>', head_html, count=1)
    return h + '\n' + body_html


def write_site(pages, SITE: pathlib.Path, ART: pathlib.Path, short_title: str):
    """pages: list of (filename, head_html, body_html). Writes GitHub build and artifact build."""
    ART.mkdir(parents=True, exist_ok=True)
    for name, h, b in pages:
        (SITE / name).write_text(document(h, b))
        out = artifact_index(h, b, short_title) if name == 'index.html' else document(h, b)
        (ART / name).write_text(out.replace('href="index.html"', 'href="./"'))
    for d in ('assets', 'img'):
        if (SITE / d).exists():
            shutil.rmtree(ART / d, ignore_errors=True); shutil.copytree(SITE / d, ART / d)
    return len(pages)


def read_page_sources(folder: pathlib.Path):
    """build/pages/*.html files start with <!--META{json}--> and hold the <main> body."""
    out = []
    for p in sorted(folder.glob('*.html')):
        raw = p.read_text()
        m = re.match(r'<!--META(.*?)-->\s*', raw, re.S)
        out.append((p.name, raw[m.end():], json.loads(m.group(1))))
    return out
