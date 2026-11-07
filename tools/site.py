"""
Keeps lavannya.me's SEO and housekeeping correct. Run it after any change:

    python tools/site.py

It does four things, in this order, and is safe to run as often as you like:

  1. Writes the search / link-preview tags into every page's <head>
     (canonical URL, Open Graph, Twitter card, structured data, noindex).
     They live between <!-- seo:start --> and <!-- seo:end --> and are
     rewritten from scratch every run, so never edit them by hand.
  2. Rebuilds sitemap.xml from the PAGES list below.
  3. Makes a small thumbnail for every gallery photo that doesn't have one.
  4. Checks the site and stops with a list of problems if anything is wrong:
     a page missing from PAGES, a page with no title or description, a
     broken link or image, a gallery photo with no full-size file.

Adding a page or blog post means adding one line to PAGES. The page's own
<title> and <meta name="description"> are the single source for its text.
"""

import glob
import html
import io
import json
import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE = "https://lavannya.me"
NAME = "Lavannya Daigavane"
PREVIEW = SITE + "/images/og/lavannya.jpg"     # 1200 x 630, used when a link is shared
PROFILES = [
    "https://instagram.com/laaavannyaa",
    "https://medium.com/@lavannyadaigavane",
    "https://twitter.com/LDaigavane",
]

# ── every page on the site ──────────────────────────────────────────────
#   "home"            the front page
#   "page"            a normal page Google should find
#   ("post", date)    a blog post, with the date it was published
#   "hidden"          kept off Google and out of the sitemap (unlinked or old)
PAGES = {
    "index.html":       "home",
    "about.html":       "page",
    "gallery.html":     "page",
    "blog-topics.html": "page",
    "loveletter.html":  "page",

    "blog8.html":       ("post", "2026-11-04"),
    "blog4.html":       ("post", "2026-09-20"),
    "blog3.html":       ("post", "2026-08-10"),
    "blogsecond.html":  ("post", "2025-07-10"),
    "blog1.html":       ("post", "2025-07-07"),

    "comrade.html":     "page",
    "hiraeth.html":     "page",
    "moonbloom.html":   "page",
    "cosmic.html":      "page",
    "soulthread.html":  "page",
    "vintage.html":     "page",

    # nothing on the site links to these yet. when one gets a link,
    # change "hidden" to "page" and run the script again.
    "games.html":       "hidden",
    "mood.html":        "hidden",
    "heyeheyhey.html":  "hidden",
    "vibes.html":       "hidden",
}

THUMB_SHORT_SIDE = 300

problems = []


def read(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def url_for(page):
    return SITE + "/" if page == "index.html" else SITE + "/" + page


def last_changed(page):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", page],
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or date.today().isoformat()
    except Exception:
        return date.today().isoformat()


def ld(obj):
    # "</" inside a script block would end it early
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")


# ── 1. the tags in each <head> ──────────────────────────────────────────

def seo_block(page, kind, title, desc_raw):
    plain_title = html.unescape(title)
    headline = re.split(r"\s+[·—|-]\s+Lavannya\s*$", plain_title)[0].strip()
    desc = html.unescape(desc_raw)
    url = url_for(page)
    esc = lambda s: html.escape(s, quote=True)

    if kind == "hidden":
        return ['<meta name="robots" content="noindex">']

    is_post = isinstance(kind, tuple)
    lines = [
        '<link rel="canonical" href="%s">' % url,
        '<meta property="og:site_name" content="%s">' % NAME,
        '<meta property="og:type" content="%s">' % ("article" if is_post else "website"),
        '<meta property="og:title" content="%s">' % esc(headline if is_post else plain_title),
        '<meta property="og:description" content="%s">' % esc(desc),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % PREVIEW,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % NAME,
        '<meta name="twitter:card" content="summary_large_image">',
    ]

    me = {"@type": "Person", "name": NAME, "url": SITE + "/"}
    if kind == "home":
        data = dict({"@context": "https://schema.org"}, **me,
                    image=PREVIEW, sameAs=PROFILES)
    elif is_post:
        lines.append('<meta property="article:published_time" content="%s">' % kind[1])
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": headline,
            "description": desc,
            "datePublished": kind[1],
            "dateModified": max(kind[1], last_changed(page)),
            "url": url,
            "mainEntityOfPage": url,
            "image": PREVIEW,
            "author": me,
        }
    else:
        data = None

    if data:
        lines.append('<script type="application/ld+json">\n%s\n</script>' % ld(data))
    return lines


def tag_pages():
    on_disk = sorted(os.path.basename(p) for p in glob.glob("*.html"))
    for page in on_disk:
        if page not in PAGES:
            problems.append("%s is not in the PAGES list in tools/site.py — add it" % page)
    for page in PAGES:
        if page not in on_disk:
            problems.append("PAGES lists %s but the file doesn't exist" % page)

    for page in on_disk:
        if page not in PAGES:
            continue
        s = read(page)
        nl = "\r\n" if "\r\n" in s else "\n"

        t = re.search(r"<title>(.*?)</title>", s, re.S)
        d = re.search(r'<meta name="description" content="([^"]*)"\s*/?>', s)
        if not t or not t.group(1).strip():
            problems.append("%s has no <title>" % page)
            continue
        if not d and PAGES[page] != "hidden":
            problems.append("%s has no <meta name=\"description\">" % page)
            continue

        # out with the old block, and any stray copies of tags it now owns
        s = re.sub(r"[ \t]*<!-- seo:start -->.*?<!-- seo:end -->[ \t]*\r?\n?", "", s, flags=re.S)
        s = re.sub(r'[ \t]*<link rel="canonical"[^>]*>[ \t]*\r?\n?', "", s)

        block = seo_block(page, PAGES[page], re.sub(r"\s+", " ", t.group(1)).strip(),
                          d.group(1) if d else "")
        text = nl.join(["<!-- seo:start -->"] + block + ["<!-- seo:end -->"])
        text = text.replace("\n", nl) if nl == "\r\n" else text

        anchor = d.end() if d else t.end()
        s = s[:anchor] + nl + text + s[anchor:]
        write(page, s)


# ── 2. the sitemap ──────────────────────────────────────────────────────

def sitemap():
    def order(item):
        page, kind = item
        if kind == "home": return (0, "")
        if page == "blog-topics.html": return (1, "")
        if isinstance(kind, tuple): return (2, "~" + str(10**9 - int(kind[1].replace("-", ""))))
        return (3, page)

    rows = []
    for page, kind in sorted(PAGES.items(), key=order):
        if kind == "hidden" or not os.path.exists(page):
            continue
        rows.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>"
                    % (url_for(page), last_changed(page)))
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(rows) + "\n</urlset>\n")
    return len(rows)


# ── 3. gallery thumbnails ───────────────────────────────────────────────

def thumbnails():
    made = 0
    try:
        from PIL import Image, ImageOps
    except ImportError:
        Image = None
    os.makedirs("images/thumbs", exist_ok=True)
    for full in sorted(glob.glob("images/gallery-*.jpeg")):
        thumb = "images/thumbs/" + os.path.basename(full)
        if os.path.exists(thumb) and os.path.getmtime(thumb) >= os.path.getmtime(full):
            continue
        if Image is None:
            problems.append("%s needs a thumbnail but Pillow isn't installed (pip install pillow)" % full)
            continue
        im = ImageOps.exif_transpose(Image.open(full)).convert("RGB")
        scale = THUMB_SHORT_SIDE / min(im.size)
        if scale < 1:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        im.save(thumb, quality=78, optimize=True, progressive=True)
        made += 1
    return made


# ── 4. checks ───────────────────────────────────────────────────────────

def check():
    for page in sorted(glob.glob("*.html")):
        s = read(page)
        refs = set(re.findall(r'(?:src|href|data-full)="((?:images/)?[^"/:#?]+(?:/[^"/:#?]+)*'
                              r'\.(?:html|jpe?g|png|css|js))"', s))
        for r in sorted(refs):
            if not os.path.exists(r):
                problems.append("%s points at %s, which doesn't exist" % (page, r))

    # a new page is usually started by copying an old one, and the old
    # description is the thing most often forgotten
    seen = {}
    for page in sorted(glob.glob("*.html")):
        if PAGES.get(page) == "hidden":
            continue
        d = re.search(r'<meta name="description" content="([^"]*)"', read(page))
        if d:
            key = html.unescape(d.group(1)).strip().lower()
            if key in seen:
                problems.append("%s has the same description as %s — give it its own" % (page, seen[key]))
            seen.setdefault(key, page)

    g = read("gallery.html")
    for full in re.findall(r'data-full="([^"]+)"', g):
        thumb = "images/thumbs/" + os.path.basename(full)
        if not os.path.exists(thumb):
            problems.append("gallery photo %s has no thumbnail" % full)
    plain = re.findall(r'<div class="slot"><img src="(images/gallery-[^"]+)"', g)
    for p in plain:
        problems.append("gallery slot %s should use images/thumbs/… with data-full=\"%s\"" % (p, p))


if __name__ == "__main__":
    made = thumbnails()
    tag_pages()
    n = sitemap()
    check()

    print("thumbnails made: %d" % made)
    print("pages tagged:    %d" % len(PAGES))
    print("sitemap entries: %d" % n)
    if problems:
        print("\nPROBLEMS — fix these before publishing:")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("\nall good.")
