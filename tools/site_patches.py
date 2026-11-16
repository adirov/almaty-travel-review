#!/usr/bin/env python3
"""Owner corrections of 16.11.2026 (Artur, Emil). Idempotent.

1. "Included" block on tour pages: tour price = private SUV + transport, English-speaking driver-guide,
   hotel pickup, park tickets and eco fees, water. Meals and accommodation are separate or the
   All inclusive package (Emil, 15.11.2026). No more "3 meals a day".
2. Kyrgyzstan removed everywhere (not offered now).
3. pages/26 "Transfers and transport" -> "Private driver-guide and our fleet" (Artur, voice note 15.11):
   English is the main version (private driver-guide / private tours), Russian is a copy.

Run on the review repo:  python3 tools/site_patches.py <repo>   (so the review site shows the same text)
build_live.py also calls apply() on the public build.
"""
import os
import re
import sys

HOST = 'https://www.almaty-travel.kz'

INCLUDED = {
    'en': ('<h2>The final price includes</h2>',
           '<ul class="tour-included"><li>Private 4x4 SUV and all transport costs</li><li>English-speaking driver-guide</li>'
           '<li>Pickup and drop-off at your hotel in Almaty</li><li>National park entrance tickets and eco fees</li>'
           '<li>Drinking water</li></ul><p class="owner-info-note tour-excluded">Meals and accommodation are paid separately, '
           'or choose the <strong>All inclusive</strong> package with hotels in the national parks and meals.</p>'),
    'ru': ('<h2>Что входит в стоимость</h2>',
           '<ul class="tour-included"><li>Частный внедорожник 4x4 и все расходы на дорогу</li><li>Англоговорящий гид-водитель</li>'
           '<li>Встреча и доставка до вашего отеля в Алматы</li><li>Входные билеты в национальные парки и экосборы</li>'
           '<li>Питьевая вода</li></ul><p class="owner-info-note tour-excluded">Питание и проживание оплачиваются отдельно '
           'или по пакету <strong>All inclusive</strong> — с отелями в национальных парках и питанием.</p>'),
}

TEXT = [
    ('<li>Kyrgyzstan can be added to any tour</li>', ''),
    ('<li>Кыргызстан можно добавить к туру отдельно</li>', ''),
    (' custom jeep tours across Kazakhstan, with Kyrgyzstan available on request.', ' custom jeep tours across Kazakhstan.'),
    (' индивидуальные джип-туры по Казахстану, а по запросу — и в Кыргызстан.', ' индивидуальные джип-туры по Казахстану.'),
    # menu label of pages/26 on every page
    ('>TRANSFERS AND MEETINGS<', '>PRIVATE DRIVER-GUIDE<'),
    ('>Трансферы и встречи<', '>Частный водитель-гид<'),
    ('content="TRANSFERS AND MEETINGS"', 'content="private driver-guide Almaty, private tours Almaty, 4x4 SUV"'),
    ('content="Трансферы и встречи"', 'content="частный водитель-гид Алматы, частные туры Алматы, внедорожник 4x4"'),
    ('>Transfers and transport<', '>Private driver-guide and our fleet<'),
    ('>Трансферы и транспорт<', '>Частный водитель-гид и наш автопарк<'),
]

DRIVER = {
    'en': {
        'old': 'Transfers and transport',
        'name': 'Private driver-guide and our fleet',
        'title': 'Private driver-guide in Almaty and our 4x4 fleet | Kazakhstan Travel',
        'desc': 'Hire a private English-speaking driver-guide in Almaty with our own 4x4 SUVs: hotel pickup, '
                'private tours to Charyn, Kolsay, Kaindy and Altyn-Emel, or transport only.',
        'intro': '<div class="driver-guide-intro"><p>Book a <strong>private driver-guide in Almaty</strong>: you travel only with '
                 'your own group in our 4x4 SUV, with an English-speaking driver-guide who meets you at your hotel, drives the route '
                 'at your pace and tells you about the places on the way.</p>'
                 '<p>Use it for a <a href="{b}/en/private-tours/1-day-charyn/">private tour to Charyn Canyon</a>, the '
                 '<a href="{b}/en/private-tours/1-day-kolsai-kaindy-charyn/">Kolsay and Kaindy lakes</a> or '
                 '<a href="{b}/en/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">Altyn-Emel</a>, for a day in the mountains '
                 'around Almaty, or simply as transport with a driver-guide. The tour price includes the car and fuel, the driver-guide, '
                 'park tickets and eco fees, water and hotel pickup; meals and accommodation are separate or come as an All inclusive package.</p>'
                 '<p>Send your dates, the number of travellers and the route on WhatsApp, and we will reply with a price.</p></div>',
    },
    'ru': {
        'old': 'Трансферы и транспорт',
        'name': 'Частный водитель-гид и наш автопарк',
        'title': 'Частный водитель-гид в Алматы и наш автопарк | Kazakhstan Travel',
        'desc': 'Частный водитель-гид в Алматы на наших внедорожниках 4x4: встреча в отеле, частные туры на Чарын, '
                'Кольсай, Каинды и Алтын-Эмель или только транспорт.',
        'intro': '<div class="driver-guide-intro"><p>Закажите <strong>частного водителя-гида в Алматы</strong>: вы едете только своей '
                 'группой на нашем внедорожнике 4x4, гид-водитель встречает вас в отеле, ведёт маршрут в вашем темпе и рассказывает '
                 'о местах по дороге.</p>'
                 '<p>Это подходит для <a href="{b}/ru/private-tours/1-day-charyn/">частного тура на Чарынский каньон</a>, '
                 '<a href="{b}/ru/private-tours/1-day-kolsai-kaindy-charyn/">озёра Кольсай и Каинды</a> или '
                 '<a href="{b}/ru/private-tours/3-day-altyn-emel-charyn-kolsai-kaindy/">Алтын-Эмель</a>, для дня в горах '
                 'вокруг Алматы или просто как транспорт с водителем-гидом. В стоимость тура входят машина и топливо, гид-водитель, '
                 'билеты в парки и экосборы, вода и встреча в отеле; питание и проживание — отдельно или пакетом All inclusive.</p>'
                 '<p>Напишите в WhatsApp даты, сколько вас и маршрут — пришлём стоимость.</p></div>',
    },
}


def _lang(rel):
    r = rel[len('summer/'):] if rel.startswith('summer/') else rel
    return 'en' if r.startswith('en/') else 'ru'


def _base(s):
    return '/almaty-travel-review' if '/almaty-travel-review/' in s else ''


def patch(rel, s, set_meta):
    lang = _lang(rel)
    key = rel[len('summer/'):] if rel.startswith('summer/') else rel
    h2, block = INCLUDED[lang]
    s = re.sub(re.escape(h2) + r'<ul[^>]*>.*?</ul>(?:<p class="owner-info-note tour-excluded">.*?</p>)?',
               lambda m: h2 + block, s, flags=re.S)
    for a, b in TEXT:
        s = s.replace(a, b)
    if key == '%s/pages/26.html' % lang:
        d = DRIVER[lang]
        s = s.replace('"name":"%s' % d['old'], '"name":"%s' % d['name']).replace('"name": "%s' % d['old'], '"name": "%s' % d['name'])
        s = s.replace('<span>%s</span>' % d['old'], '<span>%s</span>' % d['name'])
        s = s.replace('<h1>%s</h1>' % d['old'], '<h1>%s</h1>' % d['name'])
        s = re.sub(r'("description":\s*")[^"]*', lambda m: m.group(1) + d['desc'], s, count=1)
        s = set_meta(s, d['title'], d['desc'])
        s = re.sub(r'("@type":\s*"WebPage".*?"name":\s*")[^"]*', lambda m: m.group(1) + d['title'], s, count=1, flags=re.S)
        if 'driver-guide-intro' not in s:
            s = s.replace('<h1>%s</h1>' % d['name'], '<h1>%s</h1>' % d['name'] + d['intro'].replace('{b}', _base(s)), 1)
    return s


def apply(page_map, set_meta):
    return {rel: patch(rel, s, set_meta) for rel, s in page_map.items()}


def _set_meta(s, title=None, desc=None):
    import html
    if title:
        s = re.sub(r'<title>[^<]*</title>', lambda m: '<title>%s</title>' % html.escape(title, quote=False), s, count=1)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), s)
        s = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), s)
    if desc:
        for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            s = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + html.escape(desc), s)
    return s


if __name__ == '__main__':
    repo = sys.argv[1]
    n = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools', 'articles')]
        for name in files:
            if not name.endswith('.html'):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, repo)
            with open(p, encoding='utf-8', newline='') as fh:
                s = fh.read()
            t = patch(rel, s, _set_meta)
            if t != s:
                with open(p, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(t)
                n += 1
    print('changed files:', n)
