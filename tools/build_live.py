#!/usr/bin/env python3
"""Build the public almaty-travel.kz site from the review snapshot (codex/demo).

Usage: python3 tools/build_live.py <repo_dir> <out_dir>

- strips the /almaty-travel-review prefix (site lives at the domain root)
- removes every demo marker (notice, demo.css/js, AlmatyDemo config, noindex)
- restores the real enquiry form (POST /lead.php + reCAPTCHA v2)
- restores analytics and the WhatsApp widget that the live CMS site used
- writes production robots.txt, sitemap.xml, .htaccess, 404.html
Idempotent: always rebuilds out_dir from scratch.
"""
import html
import os
import re
import shutil
import sys
from datetime import date

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = '/almaty-travel-review'
HOST = 'https://www.almaty-travel.kz'
RECAPTCHA_SITE_KEY = '6LdnN08sAAAAACbRJvizxAs1wwfjlXkNb6WNS0o7'  # public key, same as the old site
SKIP = {'.git', '.github', 'README.md', 'demo.css', 'demo.js', 'tools', 'robots.txt', '.nojekyll'}
TEXT_EXT = ('.html', '.css', '.js', '.xml', '.txt', '.json', '.svg', '.webmanifest')

OWNER_GTM = """<!-- Almaty Travel: owner-managed analytics -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-PM8WSJM8');</script>
<!-- End owner-managed analytics -->"""
OWNER_GTM_NS = """<!-- Almaty Travel: owner-managed analytics (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-PM8WSJM8"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End owner-managed analytics (noscript) -->"""
OLD_GTM = """<!-- Google Tag Manager -->
\t<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-PGX8DN6');</script>
\t<!-- End Google Tag Manager -->"""
OLD_GTM_NS = """<!-- Google Tag Manager (noscript) -->
\t<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-PGX8DN6" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
\t<!-- End Google Tag Manager (noscript) -->"""
METRIKA = """<!-- Yandex.Metrika counter -->
\t<script type="text/javascript">(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym(53138671,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});</script>
\t<noscript><div><img src="https://mc.yandex.ru/watch/53138671" style="position:absolute; left:-9999px;" alt=""></div></noscript>
\t<!-- /Yandex.Metrika counter -->"""
WIDGET = """<!-- WhatsApp button (replaces the dead nashaknopka.ru / whatshelp.io widgets) -->
\t<a class="wa-float" href="https://wa.me/77775259885" target="_blank" rel="noopener" aria-label="WhatsApp +7 777 525 98 85"><svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true" focusable="false"><path fill="currentColor" d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.2.6 4.4 1.7 6.3L3.2 29l7.3-1.9c1.8 1 3.9 1.5 5.9 1.5 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23.4c-1.9 0-3.7-.5-5.3-1.4l-.4-.2-4.3 1.1 1.2-4.2-.3-.4c-1-1.7-1.6-3.6-1.6-5.6C5.3 9.8 10.1 5.1 16 5.1s10.7 4.7 10.7 10.6S21.9 26.4 16 26.4zm5.9-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1c-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2s0-.5.1-.6l.5-.6c.2-.2.2-.4.3-.6s0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.8 1.2 3.2 1.4 3.4c.2.2 2.4 3.6 5.7 5 .8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5s.3-1.3.2-1.5c-.1-.1-.3-.2-.6-.4z"/></svg></a>
\t<!-- /WhatsApp button -->"""


def lang_of(rel):
    return 'en' if re.match(r'(summer/)?en/', rel) else 'ru'


def fix_form(s, lang):
    m = re.search(r'<form id="order_form".*?</form>', s, re.S)
    if not m:
        return s
    f = m.group(0)
    f = re.sub(r'<form id="order_form"[^>]*>', '<form id="order_form" action="/lead.php" method="post">', f)
    f = re.sub(r'<input type="hidden" value="(ru|en)">',
               '<input type="hidden" name="do" value="send"><input type="hidden" name="lang" value="%s">'
               '<input type="text" name="website" value="" tabindex="-1" autocomplete="off" aria-hidden="true" '
               'class="hp-field" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0">' % lang, f)
    for key in ('fio', 'phone', 'email', 'count', 'tourname', 'date'):
        f = f.replace('<input type="text" id="%s"' % key, '<input type="text" name="%s" id="%s"' % (key, key))
    f = f.replace('<textarea id="comments"', '<textarea name="comments" id="comments"')
    f = re.sub(r'<label><input type="checkbox" id="stage-captcha">[^<]*</label>',
               '<div class="g-recaptcha" data-sitekey="%s" data-hl="%s"></div>' % (RECAPTCHA_SITE_KEY, lang), f)
    status = '<p id="order-status" class="order-status" role="status" aria-live="polite" hidden></p>'
    f = f.replace('<form id="order_form" action="/lead.php" method="post">',
                  '<form id="order_form" action="/lead.php" method="post">' + status, 1)
    s = s[:m.start()] + f + s[m.end():]
    if 'recaptcha/api.js' not in s:
        s = s.replace('</body>', '<script src="https://www.google.com/recaptcha/api.js?hl=%s" async defer></script></body>' % lang, 1)
    return s


def transform_html(s, rel):
    lang = lang_of(rel)
    s = s.replace(BASE + '/', '/').replace('"' + BASE + '"', '"/"')
    s = re.sub(r'<meta name="robots" content="noindex[^"]*">', '', s)
    s = re.sub(r'<link rel="stylesheet" href="/demo\.css">', '', s)
    s = re.sub(r'<aside class="demo-notice"[^>]*>.*?</aside>', '', s, flags=re.S)
    s = re.sub(r'<script>window\.AlmatyDemo=[^<]*</script>', '', s)
    s = re.sub(r'<script src="/demo\.js"></script>', '', s)
    s = s.replace('data-geo-demo=', 'data-geo=')
    s = re.sub(r'<!-- Almaty Travel: owner-managed analytics -->.*?<!-- End owner-managed analytics -->', lambda m: OWNER_GTM, s, flags=re.S)
    s = re.sub(r'<!-- Almaty Travel: owner-managed analytics \(noscript\) -->.*?<!-- End owner-managed analytics \(noscript\) -->', lambda m: OWNER_GTM_NS, s, flags=re.S)
    s = re.sub(r'<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->', lambda m: OLD_GTM, s, count=1, flags=re.S)
    s = re.sub(r'<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->', lambda m: OLD_GTM_NS, s, count=1, flags=re.S)
    s = re.sub(r'<!-- Yandex\.Metrika counter -->.*?<!-- /Yandex\.Metrika counter -->', lambda m: METRIKA, s, count=1, flags=re.S)
    s = re.sub(r'<!-- Наша кнопка -->.*?<!-- /WhatsHelp\.io widget -->', lambda m: WIDGET, s, count=1, flags=re.S)
    # empty Elfsight block (its script was dropped; reviews live in the home "Google reviews" section)
    s = re.sub(r'\s*<section id="reviews" class="reviews-section">\s*<div class="reviews-wrapper">\s*<div class="elfsight-app-[^"]*"></div>\s*</div>\s*</section>', '', s)
    # footer copyright
    s = re.sub(r'(\d{4}) © KAZTOUR\.com', '2011–2026 © Kazakhstan Travel', s)
    s = fix_form(s, lang)
    return s


REMOVED = ('ru/photo/432/', 'ru/photo/463/', 'summer/ru/photo/432/', 'summer/ru/photo/463/')  # empty albums
TITLE_FIX = {
    'ru/tours/400/index.html': ('Хели-ски в горах Алматы | Kazakhstan Travel',
        'Хели-ски из Алматы: вертолёт доставляет к внетрассовым спускам для лыжников и сноубордистов. Обсудите даты и программу с Kazakhstan Travel в WhatsApp.'),
    'en/tours/400/index.html': ('Heli-skiing in the Almaty mountains | Kazakhstan Travel',
        'Heli-skiing from Almaty: a helicopter drop to off-piste runs for skiers and snowboarders. Contact Kazakhstan Travel on WhatsApp to discuss dates and the route.'),
    'ru/winter/almaty-snow-school/index.html': ('Almaty Snow School — уроки лыж и сноуборда | Kazakhstan Travel',
        'Almaty Snow School: занятия на лыжах и сноуборде в горах Алматы для начинающих и опытных. Напишите даты и уровень катания в WhatsApp.'),
    'en/winter/almaty-snow-school/index.html': ('Almaty Snow School — ski and snowboard lessons | Kazakhstan Travel',
        'Almaty Snow School: ski and snowboard lessons in the Almaty mountains for beginners and confident riders. Send your dates and level on WhatsApp.'),
}


def set_meta(s, title=None, desc=None):
    if title:
        s = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % html.escape(title, quote=False), s, count=1)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), s)
        s = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), s)
    if desc:
        for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            s = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + html.escape(desc), s)
    return s


def dedupe_descriptions(pages):
    groups = {}
    for i, (rel, s) in enumerate(pages):
        if rel.startswith('summer/'):
            continue
        m = re.search(r'<meta name="description" content="([^"]*)"', s)
        if m:
            groups.setdefault(m.group(1), []).append(i)
    fixed = {}
    for desc, idx in groups.items():
        if len(idx) < 2:
            continue
        for i in idx:
            rel, s = pages[i]
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
            head = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', h1.group(1)).strip()) if h1 else ''
            plain = html.unescape(desc)
            rest = plain.split('. ', 1)[1] if '. ' in plain else plain
            new = (head.rstrip('.') + '. ' + rest).strip()
            if len(new) > 165:
                new = new[:162].rsplit(' ', 1)[0].rstrip(',.;:') + '…'
            fixed[rel] = new
    for i, (rel, s) in enumerate(pages):
        key = rel[len('summer/'):] if rel.startswith('summer/') else rel
        if key in fixed:
            pages[i] = (rel, set_meta(s, desc=fixed[key]))
    return pages


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    pages = []
    for root, dirs, files in os.walk(SRC):
        rel_root = os.path.relpath(root, SRC)
        dirs[:] = [d for d in dirs if not (rel_root == '.' and d in SKIP)]
        for name in files:
            rel = os.path.normpath(os.path.join(rel_root, name))
            if rel_root == '.' and name in SKIP:
                continue
            src, dst = os.path.join(root, name), os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if name.endswith(TEXT_EXT):
                with open(src, encoding='utf-8', newline='') as fh:
                    s = fh.read()
                if name.endswith('.html'):
                    s = transform_html(s, rel)
                    pages.append((rel, s))
                else:
                    s = s.replace(BASE + '/', '/')
                with open(dst, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(s)
            else:
                shutil.copy2(src, dst)
    # production home = the updated RU home (root copy in the snapshot is stale)
    page_map = dict(pages)
    for root_rel, src_rel in (('index.html', 'ru/index.html'), ('summer/index.html', 'summer/ru/index.html')):
        page_map[root_rel] = page_map[src_rel]
    for rel in REMOVED:
        shutil.rmtree(os.path.join(OUT, rel), ignore_errors=True)
        page_map.pop(rel + 'index.html', None)
    for rel, (title, desc) in TITLE_FIX.items():
        for r in (rel, 'summer/' + rel):
            if r in page_map:
                page_map[r] = set_meta(page_map[r], title, desc)
    pages = dedupe_descriptions(sorted(page_map.items()))
    for rel, s in pages:
        with open(os.path.join(OUT, rel), 'w', encoding='utf-8', newline='') as fh:
            fh.write(s)
    write_extras(pages)


def write_extras(pages):
    today = date.today().isoformat()
    urls = []
    for rel, s in pages:
        if rel.startswith('summer/'):
            continue
        url = '/' + rel[:-len('index.html')] if rel.endswith('index.html') else '/' + rel
        m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
        canon = m.group(1) if m else HOST + url
        if canon == HOST + url:
            urls.append(canon)
    urls = sorted(set(urls), key=lambda u: (u.count('/'), u))
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            fh.write('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (html.escape(u), today))
        fh.write('</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write('User-agent: *\n'
                 'Disallow: /cms/\nDisallow: /admin/\nDisallow: /base/\nDisallow: /block/\nDisallow: /cache/\n'
                 'Disallow: /mod/\nDisallow: /temp/\nDisallow: /sql/\nDisallow: /ext/\nDisallow: /kaztour.com.kz/\n'
                 'Disallow: /lead.php\nDisallow: /ajax.php\n\n'
                 'Sitemap: %s/sitemap.xml\n' % HOST)
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htaccess.txt'), os.path.join(OUT, '.htaccess'))
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lead.php'), os.path.join(OUT, 'lead.php'))
    here = os.path.dirname(os.path.abspath(__file__))
    for src, dst in (('enquiry-status.js', 'assets/almaty-enquiry.js'), ('enquiry-status.css', 'assets/almaty-responsive.css')):
        with open(os.path.join(here, src), encoding='utf-8') as a, open(os.path.join(OUT, dst), 'a', encoding='utf-8') as b:
            b.write('\n' + a.read())
    shutil.copy(os.path.join(here, 'llms.txt'), os.path.join(OUT, 'llms.txt'))
    make_404(pages)
    print('pages', len(pages), 'sitemap urls', len(urls))


def make_404(pages):
    s = dict(pages)['ru/map/index.html']
    s = re.sub(r'<title>[^<]*</title>', '<title>Страница не найдена | Kazakhstan Travel</title>', s)
    s = re.sub(r'<link rel="(canonical|alternate)"[^>]*>', '', s)
    s = s.replace('</head>', '<meta name="robots" content="noindex"></head>', 1)
    body = ('<div class="main_container"><h1>Страница не найдена / Page not found</h1>'
            '<p>Такой страницы нет или она переехала. Начните с <a href="/">главной страницы</a>, '
            'посмотрите <a href="/ru/tours/">экскурсии</a> или напишите нам в '
            '<a href="https://wa.me/77775259885">WhatsApp</a>.</p>'
            '<p>This page does not exist or has moved. Go to the <a href="/en/">home page</a> or '
            '<a href="/en/tours/">tours</a>, or message us on <a href="https://wa.me/77775259885">WhatsApp</a>.</p></div>')
    s = re.sub(r'<div class="main_container">.*?(?=\s*<div id="center_footer")', body, s, count=1, flags=re.S)
    with open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8') as fh:
        fh.write(s)


if __name__ == '__main__':
    main()
