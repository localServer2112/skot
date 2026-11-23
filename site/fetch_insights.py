#!/usr/bin/env python3
"""One-off importer: turns the live WordPress export into site/insights.json
and downloads each post's featured image into assets/img/insights/.

    python3 site/fetch_insights.py        # re-run to refresh from skotcomms.com
"""
import json, os, re, urllib.request, html as H
from html.parser import HTMLParser
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "site", "insights-raw.json")
OUT = os.path.join(ROOT, "site", "insights.json")
IMGDIR = os.path.join(ROOT, "assets", "img", "insights")
UA = {"User-Agent": "Mozilla/5.0"}

KEEP = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "em", "b", "i", "a", "blockquote", "br"}


class Clean(HTMLParser):
    """Keep a small, safe subset of WordPress markup."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in KEEP:
            return
        if tag == "a":
            href = dict(attrs).get("href", "")
            if not href.startswith(("http", "mailto:", "/")):
                return
            self.out.append('<a href="%s" rel="nofollow">' % H.escape(href, quote=True))
            self.stack.append(tag); return
        self.out.append("<%s>" % tag)
        if tag != "br":
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in KEEP and tag != "br" and tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                self.out.append("</%s>" % t)
                if t == tag:
                    break

    def handle_data(self, data):
        self.out.append(H.escape(data).replace("&#x27;", "'"))

    def result(self):
        while self.stack:
            self.out.append("</%s>" % self.stack.pop())
        s = "".join(self.out)
        s = re.sub(r"<p>(\s|&nbsp;)*</p>", "", s)
        s = re.sub(r"\s{2,}", " ", s)
        # WordPress authors subheadings as fully-bold paragraphs; promote the
        # short ones to real headings so the article has a usable outline.
        def promote(m):
            inner = m.group(1).strip()
            if len(re.sub(r"<[^>]*>", "", inner)) <= 80 and not inner.endswith((".", "!", "?", ":")):
                return "<h3>%s</h3>" % re.sub(r"</?(strong|b)>", "", inner)
            return m.group(0)
        s = re.sub(r"<p>\s*<(?:strong|b)>(.*?)</(?:strong|b)>\s*</p>", promote, s)
        return s.strip()


def strip_tags(s):
    s = re.sub(r"<[^>]*>", "", H.unescape(s))
    return re.sub(r"\s+", " ", s).strip()


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main():
    if not os.path.exists(RAW):
        print("fetching posts from skotcomms.com ...")
        url = "https://skotcomms.com/wp-json/wp/v2/posts?per_page=100&_embed=wp:term"
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            open(RAW, "wb").write(r.read())
    posts = json.load(open(RAW, encoding="utf-8"))
    os.makedirs(IMGDIR, exist_ok=True)

    # media lookup
    ids = [str(p["featured_media"]) for p in posts if p.get("featured_media")]
    media = {}
    for i in range(0, len(ids), 50):
        url = ("https://skotcomms.com/wp-json/wp/v2/media?per_page=100&include="
               + ",".join(ids[i:i + 50]))
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
            for m in json.load(r):
                sizes = (m.get("media_details") or {}).get("sizes") or {}
                pick = (sizes.get("medium_large") or sizes.get("large")
                        or sizes.get("full") or {})
                media[m["id"]] = {"url": pick.get("source_url") or m.get("source_url"),
                                  "alt": strip_tags(m.get("alt_text") or "")}

    # slugs are truncated for tidy filenames, so guard against collisions
    seen, slugs = {}, {}
    for p in posts:
        base = p["slug"][:58]
        if base in seen:
            seen[base] += 1
            slugs[p["id"]] = "%s-%d" % (base, seen[base])
        else:
            seen[base] = 1
            slugs[p["id"]] = base

    out = []
    for p in posts:
        title = strip_tags(p["title"]["rendered"])
        slug = slugs[p["id"]]
        cats = [t["name"] for g in (p.get("_embedded", {}).get("wp:term") or []) for t in g]
        cat = "Press" if "Press" in cats else "Insight"
        body = Clean(); body.feed(p["content"]["rendered"])
        content = body.result()
        excerpt = strip_tags(p["excerpt"]["rendered"])
        if len(excerpt) > 190:
            excerpt = excerpt[:190]
            excerpt = excerpt[:excerpt.rfind(" ")].rstrip(" ,;:-") + "…"
        excerpt = re.sub(r"\s*\[?…\]?\s*$", "…", excerpt).strip()

        img = None
        m = media.get(p.get("featured_media"))
        if m and m["url"]:
            ext = os.path.splitext(m["url"].split("?")[0])[1].lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            fname = "%s%s" % (slug, ext)
            dest = os.path.join(IMGDIR, fname)
            if not os.path.exists(dest):
                try:
                    with urllib.request.urlopen(urllib.request.Request(m["url"], headers=UA), timeout=40) as r:
                        data = r.read()
                    open(dest, "wb").write(data)
                except Exception as e:
                    print("  image failed", slug, type(e).__name__); dest = None
            if dest and os.path.exists(dest):
                img = "assets/img/insights/" + fname

        out.append({
            "slug": slug, "title": title, "date": p["date"][:10], "category": cat,
            "excerpt": excerpt, "content": content, "image": img,
            "alt": (m["alt"] if m and m["alt"] else title),
            "words": len(strip_tags(p["content"]["rendered"]).split()),
        })

    # normalise every image to a progressive JPEG no wider than 760px
    try:
        from PIL import Image
        for o in out:
            if not o["image"]:
                continue
            src = os.path.join(ROOT, o["image"])
            im = Image.open(src).convert("RGB")
            if im.width > 760:
                im = im.resize((760, round(im.height * 760 / im.width)), Image.LANCZOS)
            dest = os.path.splitext(src)[0] + ".jpg"
            im.save(dest, quality=78, optimize=True, progressive=True)
            if dest != src:
                os.remove(src)
            o["image"] = os.path.relpath(dest, ROOT).replace("\\", "/")
    except ImportError:
        print("  Pillow not installed - images left at original size")

    out.sort(key=lambda x: x["date"], reverse=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print("wrote %d posts -> %s" % (len(out), OUT))
    print("with images: %d" % sum(1 for o in out if o["image"]))


if __name__ == "__main__":
    main()
