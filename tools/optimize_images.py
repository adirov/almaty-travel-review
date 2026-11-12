"""WebP copies for heavy JPEG/PNG images that pages actually display (img src / CSS url()).

Lab test 12.11.2026 (mobile, 4x CPU, ~1.6 Mbit/s): LCP 5-9 s; the header background
(header_bg2.jpg, 204 KB), the 180x130 side banners served from 960x1280 photos (291 KB on
every page) and 300-500 KB gallery JPEGs were the biggest downloads. Links to full-size photos
(<a href>) keep the original files.
"""
import os
import re
from PIL import Image

MIN_BYTES = 60 * 1024
IMG_TAG = re.compile(r'<img\b[^>]*>')
SRC = re.compile(r'(\ssrc=")(/[^"?]+\.(?:jpe?g|png))(")', re.I)
CSS_URL = re.compile(r'(url\(["\']?)(/[^"\')?]+\.(?:jpe?g|png))', re.I)


def _webp(out, url, width=None):
    src = os.path.join(out, url.lstrip('/'))
    if not os.path.isfile(src) or os.path.getsize(src) < MIN_BYTES:
        return None
    stem = os.path.splitext(url)[0]
    new = '%s-%dw.webp' % (stem, width) if width else stem + '.webp'
    dst = os.path.join(out, new.lstrip('/'))
    if not os.path.exists(dst):
        im = Image.open(src)
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGBA' if 'transparency' in im.info else 'RGB')
        if width and im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=80, method=6)
        if os.path.getsize(dst) >= os.path.getsize(src):
            os.remove(dst)
            return None
    return new if os.path.exists(dst) else None


def run(out):
    saved = [0, 0]
    for root, _, files in os.walk(out):
        for name in files:
            if not name.endswith(('.html', '.css')):
                continue
            path = os.path.join(root, name)
            with open(path, encoding='utf-8', newline='') as fh:
                s = fh.read()
            orig = s

            def tag(m):
                t = m.group(0)
                w = re.search(r'\swidth="(\d+)"', t)
                width = int(w.group(1)) * 2 if w and int(w.group(1)) <= 400 else None

                def rep(sm):
                    new = _webp(out, sm.group(2), width)
                    return sm.group(1) + new + sm.group(3) if new else sm.group(0)
                return SRC.sub(rep, t)
            s = IMG_TAG.sub(tag, s)
            s = CSS_URL.sub(lambda m: m.group(1) + (_webp(out, m.group(2)) or m.group(2)), s)
            if s != orig:
                saved[0] += 1
                with open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(s)
    print('optimize_images: files changed', saved[0])
