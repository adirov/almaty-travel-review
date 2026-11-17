#!/usr/bin/env python3
"""Second SEO/GEO pass on almaty-travel.kz (17.11.2026). Idempotent. Only items that need no owner data.

Source: seo-audit-2026-11-16/almaty-critique.md, section 2 (items 14, 19, 20, 21, 22, 24, 25, 26, 28).

1. hreflang x-default on every en/ru pair -> the EN page (EN is the main version).
2. "Related private tours" block on every tour page (3-4 links by destination, anchors = target H1).
3. EN wording: driver-guide (not guide-driver), Kolsai, Accommodation, local cuisine, 2.5 km, Basshi,
   "arrival at"; no "Central Asia" on tours/23. Never touches href/src values.
4. Junk meta keywords removed; Instagram fallback sentence replaced by a plain link; alt on sidebar thumbs.
5. Photo-gallery pagination (/photo/N/p/M/) noindex,follow (build_live also drops it from the sitemap).

Run on the review repo:  python3 tools/seo_round2.py <repo>
build_live.py calls apply(page_map) after com_seo_port.
"""
import html
import os
import re
import sys

HOST = 'https://www.almaty-travel.kz'
START, END = '<!--related:start-->', '<!--related:end-->'

CHARYN = ['private-tours/1-day-charyn/', 'tours/817/', 'private-tours/1-day-kolsai-kaindy-charyn/',
          'private-tours/3-day-charyn-kolsai-kaindy/', 'private-tours/4-day-golden-ring-almaty/']
LAKES = ['tours/817/', 'private-tours/1-day-kolsai-kaindy-charyn/', 'private-tours/3-day-kolsai-hiking/',
         'private-tours/3-day-kolsai-camping/', 'private-tours/1-day-charyn/']
ALTYN = ['private-tours/2-day-altyn-emel/', 'private-tours/1-day-altyn-emel-singing-dune/',
         'private-tours/1-day-altyn-emel-full-park/', 'private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/']
RING = ['private-tours/4-day-golden-ring-almaty/', 'private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/',
        'private-tours/6-day-golden-ring/', 'private-tours/4-day-kegen-golden-ring/', 'tours/817/']
NEAR = ['tours/51/', 'private-tours/tamgaly-tas/', 'tours/55/', 'tours/50/', 'private-tours/1-day-charyn/']
WINTER = ['private-tours/winter-kolsai-charyn/', 'tours/400/', 'tours/401/', 'private-tours/1-day-charyn/']
AIR = ['private-tours/helicopter-flight/', 'private-tours/airplane-flight/', 'tours/51/', 'private-tours/1-day-charyn/']

GROUPS = [  # (keys in the page path, candidate list)
    (('winter',), WINTER), (('helicopter', 'airplane'), AIR),
    (('golden-ring',), RING), (('altyn-emel', 'tours/379/', 'tours/113/'), ALTYN),
    (('kolsai', 'tours/54/', 'tours/58/'), LAKES), (('charyn', 'tours/57/', 'tours/817/'), CHARYN),
    (('tamgaly', 'tours/51/', 'tours/55/', 'tours/50/', 'tours/23/', 'tours/398/', 'tours/810/'), NEAR),
    (('tours/400/', 'tours/401/'), WINTER),
]
TITLE = {'en': 'Related private tours', 'ru': 'Похожие частные туры'}

EN_TEXT = [
    (re.compile(r'\b[Gg]uide-driver'), lambda m: 'driver-guide' if m.group(0)[0] == 'g' else 'Driver-guide'),
    (re.compile(r'\bKolsay\b'), 'Kolsai'),
    (re.compile(r'\bAccomodation'), 'Accommodation'),
    (re.compile(r'\blocal cousin\b'), 'local cuisine'),
    (re.compile(r'\b2,5 km\b'), '2.5 km'),
    (re.compile(r'\bBashi\b'), 'Basshi'),
    (re.compile(r'\b([Aa])rrival to\b'), r'\1rrival at'),
    (re.compile(r'in Kazakhstan and Central Asia'), 'in the Almaty mountains'),
]
URL_ATTR = re.compile(r'((?:href|src|srcset|content|action|data-[a-z-]+)="(?:https?:)?/[^"]*")')

INSTA = {
    'en': ('<p class="ig-unavailable">The feed is temporarily unavailable. View our latest posts on Instagram.</p>',
           '<p class="ig-unavailable">Photos from our trips: <a href="https://www.instagram.com/kazakhstan_travel/" '
           'target="_blank" rel="noopener">Instagram @kazakhstan_travel</a></p>'),
}
THUMB_ALT = {
    'airplane-03': {'en': 'Airplane flight over the Almaty mountains', 'ru': 'Полёт на самолёте над горами Алматы'},
    'yurt-08': {'en': 'Yurt stay near Kolsai lakes', 'ru': 'Ночь в юрте у Кольсайских озёр'},
}


def _key(rel):
    r = rel[len('summer/'):] if rel.startswith('summer/') else rel
    return r


def _lang(rel):
    return 'en' if _key(rel).startswith('en/') else 'ru'


def _path(rel):
    """en/tours/57/index.html -> tours/57/"""
    k = _key(rel)[3:]
    return k[:-len('index.html')] if k.endswith('index.html') else k


def _prefix(rel, s):
    return ('/almaty-travel-review' if '/almaty-travel-review/' in s else '') + ('/summer' if rel.startswith('summer/') else '')


def is_tour(rel):
    p = _path(rel)
    return bool(re.fullmatch(r'(private-tours/[a-z0-9-]+/|tours/\d+/)', p))


def x_default(s):
    if 'hreflang="x-default"' in s:
        return s
    m = re.search(r'<link rel="alternate" hreflang="en" href="([^"]+)">', s)
    if not m or 'hreflang="ru"' not in s:
        return s
    tag = '<link rel="alternate" hreflang="x-default" href="%s">' % m.group(1)
    last = list(re.finditer(r'<link rel="alternate" hreflang="(?:en|ru)" href="[^"]+">', s))[-1]
    return s[:last.end()] + tag + s[last.end():]


def related(rel, s, h1s):
    s = re.sub(re.escape(START) + '.*?' + re.escape(END), '', s, flags=re.S)
    if not is_tour(rel):
        return s
    lang, path = _lang(rel), _path(rel)
    cands = []
    for keys, lst in GROUPS:
        if any(k in path for k in keys):
            cands += lst
    if not cands:
        cands = CHARYN
    picks = []
    for c in cands + RING:
        if c != path and c not in picks and (lang + '/' + c) in h1s:
            picks.append(c)
        if len(picks) == 4:
            break
    pre = _prefix(rel, s)
    items = ''.join('<li><a href="%s/%s/%s">%s</a></li>' % (pre, lang, c, html.escape(h1s[lang + '/' + c], quote=False)) for c in picks)
    block = '%s<nav class="before-you-go related-tours" aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>%s' % (
        START, TITLE[lang], TITLE[lang], items, END)
    # inside the content card: after the WhatsApp call-to-action, else before the guide box / footer
    m = re.search(r'<p class="owner-contact-cta">.*?</p>', s, re.S)
    if m:
        i = m.end()
    else:
        i = s.find('<nav class="before-you-go"')
        if i < 0:
            i = s.find('<div id="center_footer"')
    if i < 0:
        return s
    return s[:i] + block + s[i:]


def en_text(s):
    parts = URL_ATTR.split(s)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            for rx, rep in EN_TEXT:
                p = rx.sub(rep, p)
        out.append(p)
    return ''.join(out)


def patch(rel, s, h1s):
    lang = _lang(rel)
    s = x_default(s)
    s = related(rel, s, h1s)
    if lang == 'en':
        s = en_text(s)
        a, b = INSTA['en']
        s = s.replace(a, b)
    else:
        s = s.replace('<p class="ig-unavailable">Лента временно недоступна. Последние публикации можно посмотреть в Instagram.</p>',
                      '<p class="ig-unavailable">Фото из наших поездок: <a href="https://www.instagram.com/kazakhstan_travel/" '
                      'target="_blank" rel="noopener">Instagram @kazakhstan_travel</a></p>')
    s = re.sub(r'<meta name="keywords" content="[^"]*Message Kazakhstan Travel on WhatsApp\.">\s*', '', s)
    s = re.sub(r'<meta name="keywords" content="[^"]*Kazakhstan Travel в WhatsApp\.">\s*', '', s)
    s = re.sub(r'<meta name="keywords" content="(?:KAZTOUR|[^"]{300,})">\s*', '', s)
    for f, alts in THUMB_ALT.items():
        s = re.sub(r'(<img src="[^"]*/%s(?:-\d+w)?\.(?:jpe?g|png|webp)" )alt=""' % re.escape(f), lambda m: m.group(1) + 'alt="%s"' % alts[lang], s)
    if re.search(r'/photo/(?:\d+/)?p/\d+/', _key(rel)) and 'name="robots"' not in s:
        s = s.replace('</head>', '<meta name="robots" content="noindex, follow"></head>', 1)
    return s


def collect_h1(page_map):
    h1s = {}
    for rel, s in page_map.items():
        if rel.startswith('summer/') or not rel.endswith('.html') or not is_tour(rel):
            continue
        m = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        if m:
            h1s[_lang(rel) + '/' + _path(rel)] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
    return h1s


def apply(page_map):
    h1s = collect_h1(page_map)
    return {rel: (patch(rel, s, h1s) if rel.endswith('.html') else s) for rel, s in page_map.items()}


if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    pm = {}
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools', 'articles')]
        for name in files:
            if name.endswith('.html'):
                path = os.path.join(root, name)
                with open(path, encoding='utf-8', newline='') as fh:
                    pm[os.path.relpath(path, repo)] = fh.read()
    out = apply(pm)
    n = 0
    for rel, s in out.items():
        if s != pm[rel]:
            with open(os.path.join(repo, rel), 'w', encoding='utf-8', newline='') as fh:
                fh.write(s)
            n += 1
    print('changed files:', n)
