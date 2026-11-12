"""SEO/GEO content patches for the public almaty-travel.kz build (stage 'f', 12.11.2026).

Only facts that are already on the site, on the partner site snow-school.kz, or confirmed by the
owner are used. Anything unconfirmed is phrased as "see the itinerary / confirm with the manager".
"""
import html
import json
import re

HOST = 'https://www.almaty-travel.kz'

# --- meals: the shared "included" block said "3 meals a day" on every tour, incl. day trips
#     where the itinerary says lunch is extra or optional. Same wording style as the
#     accommodation line next to it ("(multi-day tours)").
MEALS = (
    ('Трёхразовое питание в ресторанах и отелях',
     'Трёхразовое питание в ресторанах и отелях (в многодневных турах; в однодневных — см. программу дня)'),
    ('3 meals a day in restaurants and hotels',
     '3 meals a day in restaurants and hotels (multi-day tours; on day trips see the itinerary)'),
)

# --- partner snowboard school (facts from https://snow-school.kz/, checked 12.11.2026)
SCHOOL_BLOCK = {
    'ru': ('<aside class="school-link" aria-label="Школа сноуборда в Алматы"><p class="school-link__title">Хотите попробовать сноуборд?</p>'
           '<p>Наша партнёрская школа <strong>Almaty Snowboard School</strong> проводит индивидуальные уроки, групповые курсы, '
           'детские тренировки и катание вне трасс с гидом в горах Алматы.</p>'
           '<p><a class="school-link__btn" href="https://snow-school.kz/ru/">Перейти на сайт школы</a></p></aside>'),
    'en': ('<aside class="school-link" aria-label="Snowboard school in Almaty"><p class="school-link__title">Want to try snowboarding?</p>'
           '<p>Our partner school <strong>Almaty Snowboard School</strong> offers private lessons, group courses, kids training '
           'and off-piste guiding in the Almaty mountains.</p>'
           '<p><a class="school-link__btn" href="https://snow-school.kz/en/">Visit the school website</a></p></aside>'),
}

SCHOOL_PAGE = {
    'ru': {
        'title': 'Almaty Snowboard School: уроки сноуборда | Kazakhstan Travel',
        'desc': 'Партнёрская школа сноуборда в Алматы: индивидуальные уроки, групповые курсы, детские тренировки от 5 лет '
                'и катание вне трасс с гидом. Запись на snow-school.kz.',
        'intro': ('<p>Almaty Snowboard School — партнёрская школа сноуборда в горах Алматы. Запись, стоимость и даты занятий '
                  'подтверждает сама школа: на сайте <a href="https://snow-school.kz/ru/">snow-school.kz</a> или по телефону '
                  '<a href="tel:+77005259885">+7 700 525 9885</a> (Артур Ковалевский).</p>'
                  '<section class="owner-info" aria-label="Направления школы"><h2>Направления школы</h2><ul>'
                  '<li><strong>Индивидуальные уроки</strong> — один на один с инструктором, 2 часа; для новичков и тех, кто уже катается.</li>'
                  '<li><strong>Групповые курсы</strong> — 5 занятий по 2 часа; для новичков и продолжающих.</li>'
                  '<li><strong>Детские тренировки</strong> — от 5 лет, 1,5 часа, индивидуально или в группе.</li>'
                  '<li><strong>Катание вне трасс с гидом</strong> — полный день, для опытных райдеров.</li>'
                  '</ul><p class="owner-info-note">Нужны трансфер в горы, проживание или экскурсия в свободный от катания день — '
                  'это организует Kazakhstan Travel.</p></section>'),
        'button': '<p><a class="school-link__btn" href="https://snow-school.kz/ru/">Перейти на сайт школы</a></p>',
        'cta': 'Трансфер, проживание или экскурсия в день без катания — напишите нам в WhatsApp.',
    },
    'en': {
        'title': 'Almaty Snowboard School: snowboard lessons | Kazakhstan Travel',
        'desc': 'Our partner snowboard school in Almaty: private lessons, group courses, kids training from age 5 and '
                'off-piste guiding. Book on snow-school.kz.',
        'intro': ('<p>Almaty Snowboard School is our partner snowboard school in the Almaty mountains. The school confirms '
                  'bookings, prices and dates itself: on <a href="https://snow-school.kz/en/">snow-school.kz</a> or by phone '
                  '<a href="tel:+77005259885">+7 700 525 9885</a> (Artur Kovalevskiy).</p>'
                  '<section class="owner-info" aria-label="What the school offers"><h2>What the school offers</h2><ul>'
                  '<li><strong>Private lessons</strong> — one-to-one with an instructor, 2 hours; for beginners and improvers.</li>'
                  '<li><strong>Group courses</strong> — 5 sessions of 2 hours; for beginners and improvers.</li>'
                  '<li><strong>Kids training</strong> — from age 5, 1.5 hours, private or in a group.</li>'
                  '<li><strong>Off-piste with a guide</strong> — a full day, for experienced riders.</li>'
                  '</ul><p class="owner-info-note">Kazakhstan Travel can arrange your transfer to the mountains, accommodation '
                  'or a sightseeing trip on a day off the slopes.</p></section>'),
        'button': '<p><a class="school-link__btn" href="https://snow-school.kz/en/">Visit the school website</a></p>',
        'cta': 'Need a transfer, accommodation or a day trip between ride days? Message us on WhatsApp.',
    },
}

# --- "Before you go" guide links on tour pages
GUIDES = {
    'ru': {'charyn': ('/ru/guide/charyn-walking-and-day-trip/', 'Чарынский каньон: как выбрать программу и пешую нагрузку'),
           'lakes': ('/ru/guide/kolsai-kaindy-one-or-two-days/', 'Кольсай и Каинды: один день или два?'),
           'yurts': ('/ru/guide/yurt-stay-kolsai/', 'Проживание в юртах на Кольсае: что уточнить до поездки'),
           'booking': ('/ru/guide/booking-private-tour-from-almaty/', 'Как согласовать частный тур из Алматы через WhatsApp'),
           'title': 'Полезно перед поездкой', 'all': ('/ru/guide/', 'Все материалы гида')},
    'en': {'charyn': ('/en/guide/charyn-walking-and-day-trip/', 'Charyn Canyon: choosing an itinerary and walking level'),
           'lakes': ('/en/guide/kolsai-kaindy-one-or-two-days/', 'Kolsai and Kaindy: one day or two?'),
           'yurts': ('/en/guide/yurt-stay-kolsai/', 'Yurt stays near Kolsai: what to confirm before travelling'),
           'booking': ('/en/guide/booking-private-tour-from-almaty/', 'How to arrange a private tour from Almaty on WhatsApp'),
           'title': 'Before you go', 'all': ('/en/guide/', 'All travel guide articles')},
}
CHARYN = ('charyn', 'golden-ring', 'tours/57/', 'tours/817/')
LAKES = ('kolsai', 'kaindy', 'golden-ring', 'tours/54/', 'tours/58/', 'tours/817/')
YURTS = ('kolsai-camping', 'kolsai-hiking', 'pages/47.html')
TOUR_PAGES = re.compile(r'^(ru|en)/(private-tours/[\w-]+/index\.html|tours/(50|51|54|55|57|58|113|379|398|810|817)/index\.html|pages/47\.html)$')

EN_HOME_TEXT = """<h3><strong>Tourism in Almaty</strong></h3>
<p><strong>Almaty</strong> is often called Kazakhstan's southern capital. The city lies in the foothills of the Trans-Ili Alatau, and visitors come for its mountain scenery, mild climate, nature and history.</p>
<p>Orchards, parks and protected natural areas are a big part of <strong>tourism in Almaty</strong>. In the city you can see historical monuments, museums, galleries and cultural centres; beyond it are mountain lakes, canyons and national parks.</p>
<p><strong>Kazakhstan Travel</strong> has organised private tours from Almaty since 2011. We arrange city tours, trips into the mountains, horse riding and quad-bike trips, and multi-day routes to Charyn Canyon, the Kolsai and Kaindy lakes and Altyn-Emel.</p>
<p>In winter the ski resorts near the city are open for skiing and snowboarding among snowy slopes and spruce forests.</p>
<p>Tell us your dates, group size and interests, and we will suggest <strong>tours in Almaty</strong> and <strong>excursions in Almaty</strong> that suit you.</p>"""

DROP = ('ru/stay/yurts/index.html', 'en/stay/yurts/index.html', 'ru/pages/651.html', 'en/pages/651.html')


def _lang(rel):
    r = rel[len('summer/'):] if rel.startswith('summer/') else rel
    return 'en' if r.startswith('en/') else 'ru'


def _guide_box(rel, lang):
    key = rel[len('summer/'):] if rel.startswith('summer/') else rel
    g = GUIDES[lang]
    picks = []
    if any(k in key for k in CHARYN):
        picks.append(g['charyn'])
    if any(k in key for k in LAKES):
        picks.append(g['lakes'])
    if any(k in key for k in YURTS):
        picks.append(g['yurts'])
    picks.append(g['booking'])
    picks.append(g['all'])
    items = ''.join('<li><a href="%s%s">%s</a></li>' % ('/summer' if rel.startswith('summer/') else '', u, t) for u, t in picks)
    return '<nav class="before-you-go" aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>' % (g['title'], g['title'], items)


def _guide_jsonld(s, rel, org):
    lang = _lang(rel)
    key = rel[len('summer/'):] if rel.startswith('summer/') else rel
    home = HOST + '/' if lang == 'ru' else HOST + '/en/'
    guide = HOST + '/%s/guide/' % lang

    def fix(m):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        for node in data.get('@graph', []):
            if node.get('@type') == 'Organization' and node.get('@id') == HOST + '/#organization':
                node.clear()
                node.update(org)
            if node.get('@type') == 'BreadcrumbList':
                items = node['itemListElement']
                crumbs = [('Главная' if lang == 'ru' else 'Home', home), ('Гид' if lang == 'ru' else 'Guide', guide)]
                if not key.endswith('guide/index.html'):
                    crumbs.append((items[-1]['name'], items[-1]['item']))
                node['itemListElement'] = [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                                           for i, (n, u) in enumerate(crumbs)]
        return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False)
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix, s, flags=re.S)


def trim_desc(d, limit=165):
    if len(d) <= limit:
        return d
    cut = d[:limit - 1].rsplit(' ', 1)[0].rstrip(',.;:—–- ')
    return cut + '…'


def apply(page_map, set_meta):
    # organisation node used on every non-guide page (single entity, same @id)
    org = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', page_map['ru/index.html'], re.S):
        node = json.loads(m.group(1))
        if node.get('@type') == 'TravelAgency' and node.get('@id') == HOST + '/#organization':
            org = {k: v for k, v in node.items() if k != '@context'}
    assert org, 'TravelAgency node not found on the home page'
    yurt_extra = {}
    for lang in ('ru', 'en'):
        src = page_map.get('%s/stay/yurts/index.html' % lang, '')
        x = re.search(r'<section id="owner-yurt-hotel-photos".*?</section>', src, re.S)
        if x:
            yurt_extra[lang] = x.group(0)

    out = {}
    for rel, s in page_map.items():
        base = rel[len('summer/'):] if rel.startswith('summer/') else rel
        if base in DROP:
            continue
        lang = _lang(rel)
        # summer copies are duplicates of the main pages: all absolute URLs point to the main version
        if rel.startswith('summer/'):
            s = s.replace(HOST + '/summer/', HOST + '/')
        # merged yurt page + one URL for yurts
        s = re.sub(r'(/summer)?/(ru|en)/(?:stay/yurts/|pages/651\.html)', lambda m: (m.group(1) or '') + '/%s/pages/47.html' % m.group(2), s)
        if base == '%s/pages/47.html' % lang and lang in yurt_extra and 'owner-yurt-hotel-photos' not in s:
            s = re.sub(r'(<section id="owner-yurt-camp-photos".*?</section>)', lambda m: m.group(1) + yurt_extra[lang], s, count=1, flags=re.S)
        # meals wording
        for a, b in MEALS:
            s = s.replace(a + '<', b + '<')
        # partner school
        s = s.replace('Almaty Snow School', 'Almaty Snowboard School')
        s = re.sub(r'<aside class="school-link".*?</aside>', lambda m: SCHOOL_BLOCK[lang], s, flags=re.S)
        if base == '%s/winter/almaty-snow-school/index.html' % lang:
            p = SCHOOL_PAGE[lang]
            s = re.sub(r'(<h1>Almaty Snowboard School</h1>)<p>.*?</p>', lambda m: m.group(1) + p['intro'] + p['button'], s, count=1, flags=re.S)
            s = re.sub(r'(<p class="owner-contact-cta"><a href="https://wa\.me/77775259885">)[^<]*', lambda m: m.group(1) + p['cta'], s, count=1)
            s = set_meta(s, p['title'], p['desc'])
        # guide entity + breadcrumbs
        if '/guide/' in base and org:
            s = _guide_jsonld(s, rel, org)
        # tour pages: links to the matching practical guides
        if TOUR_PAGES.match(base) and 'before-you-go' not in s:
            box = _guide_box(rel, lang)
            if '<p class="owner-contact-cta">' in s:
                i = s.rfind('<p class="owner-contact-cta">')
                s = s[:i] + box + s[i:]
        # English home: grammar rewrite of the old SEO text (no new claims)
        if base == 'en/index.html':
            s = re.sub(r'<h3>\s*<strong>Tourism in Almaty</strong></h3>.*?(?=</div>)', lambda m: EN_HOME_TEXT, s, count=1, flags=re.S)
        # description length
        d = re.search(r'<meta name="description" content="([^"]*)"', s)
        if d:
            plain = html.unescape(d.group(1))
            t = trim_desc(plain)
            if t != plain:
                s = set_meta(s, desc=t)
        out[rel] = s
    return out
