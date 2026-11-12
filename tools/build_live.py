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
WIDGET = """<!-- Наша кнопка -->
\t<div id="whatsApp_widget"></div>
\t<script src="https://api.nashaknopka.ru/widget.js"></script>
\t<script>if(window.whatsApp_widget)whatsApp_widget.init('2d37b622400659924f4a1bf388491c15');</script>
\t<!-- /Наша кнопка -->"""


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
                 'Disallow: /summer/\nDisallow: /lead.php\nDisallow: /ajax.php\n\n'
                 'Sitemap: %s/sitemap.xml\n' % HOST)
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htaccess.txt'), os.path.join(OUT, '.htaccess'))
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lead.php'), os.path.join(OUT, 'lead.php'))
    here = os.path.dirname(os.path.abspath(__file__))
    for src, dst in (('enquiry-status.js', 'assets/almaty-enquiry.js'), ('enquiry-status.css', 'assets/almaty-responsive.css')):
        with open(os.path.join(here, src), encoding='utf-8') as a, open(os.path.join(OUT, dst), 'a', encoding='utf-8') as b:
            b.write('\n' + a.read())
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
