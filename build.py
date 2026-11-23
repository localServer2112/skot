#!/usr/bin/env python3
"""Static site generator for SKOT Communications. Standard library only.

    python3 build.py        # writes the flat .html files to the repo root

Page bodies live in site/pages/*.html and are injected into site/layout.html.
Repeated components (nav, cards, stat cells) are generated here from site/data.py
so the six case studies have exactly one source of truth.
"""
import os, re, struct, sys, html

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "site"))
import data as D
import json as _json
from urllib.parse import quote

_POSTS_PATH = os.path.join(ROOT, "site", "insights.json")
POSTS = _json.load(open(_POSTS_PATH, encoding="utf-8")) if os.path.exists(_POSTS_PATH) else []

ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
CARET = '<svg class="caret" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5"/></svg>'
# Step glyph for "How we work": the SKOT ring with a looping arrow (ri-anticlockwise-2-line).
# Drawn once as Listen; the other two steps are the same shape turned, so the set
# stays one family. Transforms sit on an inner <g> so the hover tilt on the <svg> is free.
# Colour is currentColor (the scarlet token) rather than the file's #D6001C.
_GLYPH = ('<path d="M58.1271 75.6807L66.0527 67.7594L59.9211 61.6277L41.5391 80.0141L59.9211 '
          '98.4004L66.0527 92.2687L58.1271 84.3474H69.3331C75.0794 84.3474 80.5904 82.0647 '
          '84.6537 78.0014C88.717 73.9381 90.9997 68.4271 90.9997 62.6807V45.3474H82.3331V62.6807'
          'C82.3331 66.1285 80.9634 69.4351 78.5255 71.8731C76.0875 74.3111 72.7809 75.6807 '
          '69.3331 75.6807H58.1271Z" fill="currentColor"/>'
          '<path d="M64 33C64 46.8071 52.8071 58 39 58C25.1929 58 14 46.8071 14 33C14 19.1929 '
          '25.1929 8 39 8C52.8071 8 64 19.1929 64 33Z" fill="none" stroke="currentColor" '
          'stroke-width="8"/>')


def _icon(transform=""):
    g = '<g transform="%s">%s</g>' % (transform, _GLYPH) if transform else _GLYPH
    # Padded out from 0 0 104 104 (scale 0.85, centred on the glyph) so Listen and Amplify
    # carry the same visual mass as Speak up, which is wider than it is tall.
    return ('<svg class="mw-icon" viewBox="-9.2 -9.2 122.4 122.4" aria-hidden="true">%s</svg>' % g)


METHOD_ICONS = {
    "listen": _icon(),                                  # ring top-left, arrow bottom-right
    # Speak up is its own drawing (supplied separately), not a mirror of Listen. It is a 24px
    # glyph that fills ~87% of its box where the 104px one fills ~74%, so the viewBox is padded
    # out to give it the same visible footprint as its neighbours.
    "speak-up": ('<svg class="mw-icon" viewBox="-2.2 -2.1 28.2 28.2" aria-hidden="true">'
                 '<path d="M6.53597 13.4139L8.36397 15.2429L9.77897 13.8279L5.53597 9.58594L1.29297 '
                 '13.8279L2.70797 15.2429L4.53597 13.4139L4.53597 15.9999C4.53597 17.326 5.06275 '
                 '18.5978 6.00044 19.5355C6.93812 20.4732 8.20989 20.9999 9.53597 20.9999L13.536 '
                 '20.9999L13.536 18.9999L9.53597 18.9999C8.74032 18.9999 7.97726 18.6839 7.41465 '
                 '18.1213C6.85204 17.5586 6.53597 16.7956 6.53597 15.9999L6.53597 13.4139Z" '
                 'fill="currentColor"/>'
                 '<path d="M16.3839 14.7701C13.1976 14.7701 10.6146 12.1872 10.6146 9.0009C10.6146 '
                 '5.81464 13.1976 3.23167 16.3839 3.23167C19.5701 3.23167 22.1531 5.81464 22.1531 '
                 '9.0009C22.1531 12.1872 19.5701 14.7701 16.3839 14.7701Z" fill="none" '
                 'stroke="currentColor" stroke-width="1.84615"/></svg>'),
    "amplify": _icon("rotate(180 52 52)"),              # turned: ring bottom-right
}

PANELS = ["panel-ink", "panel-scarlet", "panel-putty", "panel-deep", "panel-ink", "panel-putty"]



def case_href(c):   return "case-%s.html" % c["slug"]
def exp_href(e):    return "expertise-%s.html" % e["slug"]
def prog_href(p):   return "programmes-%s.html" % p["slug"]


# ── Components ──────────────────────────────────────────────────────────────
def nav_desktop(active):
    out = []
    for n in D.NAV:
        key = n.get("key")
        cur = ' aria-current="page"' if n["href"] == active else ""
        if key == "expertise":
            sub = "".join(
                '<a href="%s"><span class="t">%s</span></a>' % (exp_href(e), e["short"])
                for e in D.EXPERTISE)
            out.append(
                '<div class="navitem" data-nav="expertise"><button aria-expanded="false" '
                'aria-controls="mega-expertise"%s>Expertise %s</button>'
                '<div class="mega" id="mega-expertise" data-open="false"><div class="mega-list">%s</div></div>'
                '</div>' % (cur, CARET, sub))
        elif key == "programmes":
            sub = "".join(
                '<a href="%s"><span class="t">%s</span></a>' % (prog_href(p), p["name"])
                for p in D.PROGRAMMES)
            elevate = next(p for p in D.PROGRAMMES if p["slug"] == "elevate")
            sub += '<a href="%s#masterclass"><span class="t">Masterclass</span></a>' % prog_href(elevate)
            out.append(
                '<div class="navitem" data-nav="programmes"><button aria-expanded="false" '
                'aria-controls="mega-programmes"%s>Programmes %s</button>'
                '<div class="mega" id="mega-programmes" data-open="false"><div class="mega-list">%s</div></div>'
                '</div>' % (cur, CARET, sub))
        else:
            out.append('<a href="%s"%s>%s</a>' % (n["href"], cur, n["label"]))
    return out


def build_nav(active):
    links = nav_desktop(active)
    # mobile
    mob = []
    for i, n in enumerate(D.NAV):
        mob.append('<a href="%s"><span class="idx">0%d</span>%s</a>' % (n["href"], i + 1, n["label"]))
        if n.get("key") == "expertise":
            mob += ['<a class="sub" href="%s">%s</a>' % (exp_href(e), e["short"]) for e in D.EXPERTISE]
        if n.get("key") == "programmes":
            mob += ['<a class="sub" href="%s">%s</a>' % (prog_href(p), p["name"]) for p in D.PROGRAMMES]
    return "\n".join(links), "\n".join(mob)


def footer_cols():
    exp = "".join('<a href="%s">%s</a>' % (exp_href(e), e["short"]) for e in D.EXPERTISE)
    work = ('<a href="case-studies.html">Our work</a>'
            + "".join('<a href="%s">%s</a>' % (case_href(c), c["client"]) for c in D.CASES[:3]))
    firm = ('<a href="about.html">About us</a><a href="programmes.html">Programmes</a>'
            + "".join('<a href="%s">%s</a>' % (prog_href(p), p["name"]) for p in D.PROGRAMMES)
            + '<a href="contact.html">Get in touch</a>')
    return ('<div class="footer-col"><h4>Expertise</h4>%s</div>'
            '<div class="footer-col"><h4>Work</h4>%s</div>'
            '<div class="footer-col"><h4>Firm</h4>%s</div>') % (exp, work, firm)


def stat_cells(metrics, cols=None):
    n = cols or max(1, min(4, len(metrics)))
    cells = "".join('<div><div class="stat-n">%s</div><div class="stat-l">%s</div></div>' % (_figure(v, "stat-fig"), l)
                    for v, l in metrics)
    return '<div class="stats" style="grid-template-columns:repeat(%d,minmax(0,1fr))">%s</div>' % (n, cells)


def case_card(c, i):
    chip = '<span class="chip chip--onmedia">%s</span>' % html.escape(c["discipline"])
    logo = client_logo(c["slug"])
    if logo:
        panel = ('<div class="card-panel card-panel--logo panel-putty">%s<img class="card-logo" src="%s" alt="%s" '
                 'width="%d" height="%d" loading="lazy" decoding="async"></div>'
                 % (chip, logo[0], html.escape(c["client"]), logo[1], logo[2]))
    else:
        panel = ('<div class="card-panel %s">%s<span class="mark">%s</span></div>'
                 % (PANELS[i % len(PANELS)], chip, html.escape(c.get("panel_name", c["client"]))))
    return ('<article class="card" data-discipline="%s" data-search="%s">%s'
            '<div class="card-body"><h3>%s</h3><p>%s</p>'
            '<a class="alink card-link" href="%s">Read the story %s</a></div></article>'
            % (html.escape(c["discipline"]),
               html.escape((c["client"] + " " + c["title"] + " " + c["sector"]).lower()),
               panel, html.escape(c["title"]), html.escape(c["summary"]), case_href(c), ARROW))


RING_SET = ('<svg class="feat-rings" viewBox="-100 -100 200 200" aria-hidden="true">'
            + "".join('<circle r="%d"/>' % r for r in (22, 40, 58, 76, 94)) + '</svg>')


def home_cases():
    """Home 'Selected work': one featured case on a scarlet block, then a ruled index of the rest.
    Headline figures come from HOME_RESULTS where set, else the case's first metric."""
    figs = {slug: v for slug, v, _ in D.HOME_RESULTS}
    def fig(c):
        return figs.get(c["slug"]) or (c["metrics"][0][0] if c["metrics"] else "")
    lead = next(c for c in D.CASES if c["slug"] == D.HOME_RESULTS[0][0])
    rest = [c for c in D.CASES if c is not lead]
    featured = ('<a class="feat" href="%s"><div class="feat-l">%s<p class="feat-tag">%s &middot; %s</p>%s</div>'
                '<div class="feat-r"><div><p class="label">Featured case study</p>'
                '<h3 class="h3 feat-title">%s</h3><p class="body-copy">%s</p></div>'
                '<span class="alink">Read the story %s</span></div></a>'
                % (case_href(lead), RING_SET, html.escape(lead["discipline"]), html.escape(lead["sector"]),
                   _figure(fig(lead), "feat-fig"), html.escape(lead["title"]), html.escape(lead["summary"]), ARROW))
    rows = "".join('<a class="idx-row" href="%s"><span class="idx-n">%02d</span><h3 class="idx-t">%s</h3>%s</a>'
                   % (case_href(c), i + 2, html.escape(c["title"]), ARROW)
                   for i, c in enumerate(rest))
    return featured + '<div class="idx">%s</div>' % rows


def case_cards(cases=None):
    cases = cases if cases is not None else D.CASES
    return "".join(case_card(c, i) for i, c in enumerate(cases))


def hero_rail():
    """Home hero: our areas of expertise, as a looping marquee.

    The set is emitted twice so the track can translate by exactly -50% and wrap
    seamlessly. The copy is hidden from assistive tech and taken out of the tab
    order so each name is only announced once. Every name links to its expertise page.
    """
    def links(dupe):
        extra = ' tabindex="-1"' if dupe else ""
        return "".join('<a href="%s"%s>%s</a>' % (exp_href(e), extra, html.escape(e["title"]))
                       for e in D.EXPERTISE)
    return ('<div class="vhero-marquee">'
            '<nav class="vhero-set" aria-label="Areas of expertise">%s</nav>'
            '<div class="vhero-set" aria-hidden="true">%s</div>'
            '</div>' % (links(False), links(True)))


def client_logo(slug):
    """(path, width, height) of assets/img/clients/<slug>.png, or None until a logo is dropped in."""
    path = "assets/img/clients/%s.png" % slug
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full, "rb") as f:
        w, h = struct.unpack(">II", f.read(24)[16:24])
    return path, w, h


def case_mark(c):
    """Case study hero panel: the client's logo, else its name set as a wordmark."""
    logo = client_logo(c["slug"])
    if logo:
        return '<img class="case-logo" src="%s" alt="%s" width="%d" height="%d">' % (logo[0], html.escape(c["client"]), logo[1], logo[2])
    return '<span class="mark mark--xl">%s</span>' % html.escape(c["client"])


def client_rail():
    """Home: clients who trust us, as a logo (or wordmark until one exists) linking to the case study."""
    def item(c):
        name = html.escape(c.get("panel_name") or c["client"])
        logo = client_logo(c["slug"])
        if logo:
            return ('<a class="trust-logo" href="%s" aria-label="%s"><img src="%s" alt="%s" width="%d" height="%d" '
                    'loading="lazy" decoding="async"></a>' % ((case_href(c), name) + (logo[0], name, logo[1], logo[2])))
        return '<a href="%s">%s</a>' % (case_href(c), name)
    return "".join(item(c) for c in D.CASES)


def expertise_tabs():
    """Home: the four disciplines as an auto-advancing tablist."""
    tabs, panels = [], []
    for i, e in enumerate(D.EXPERTISE):
        tid, pid = "xp-t-%s" % e["slug"], "xp-p-%s" % e["slug"]
        on = (i == 0)
        tabs.append(
            '<button class="xp-tab" type="button" role="tab" id="%s" aria-controls="%s" '
            'aria-selected="%s" tabindex="%s">'
            '<span class="xp-track" aria-hidden="true"><i class="xp-fill"></i></span>'
            '<span class="xp-name">%s</span></button>'
            % (tid, pid, "true" if on else "false", "0" if on else "-1", html.escape(e["title"])))
        panels.append(
            '<div class="xp-panel" role="tabpanel" id="%s" aria-labelledby="%s" tabindex="0"%s>'
            '<img class="xp-img" src="%s" alt="%s" loading="lazy">'
            '<div class="xp-note"><p>%s %s</p>'
            '<a class="xp-go" href="%s" aria-label="Explore %s">%s</a></div></div>'
            % (pid, tid, "" if on else " hidden", e["image"], html.escape(e["alt"]),
               html.escape(e["lede"]), html.escape(e["body"]), exp_href(e),
               html.escape(e["title"]), ARROW))
    return ('<div class="xp" data-xp>'
            '<div class="xp-tabs" role="tablist" aria-label="Areas of expertise">%s</div>'
            '<div class="xp-stage">%s</div></div>' % ("".join(tabs), "".join(panels)))


def expertise_cards():
    out = []
    for e in D.EXPERTISE:
        caps = "".join("<li>%s</li>" % n for n, _ in e["capabilities"][:4])
        out.append(
            '<a class="card" href="%s"><div class="card-panel" style="aspect-ratio:16/10">'
            '<img src="%s" alt="%s" loading="lazy"></div>'
            '<div class="card-body"><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p>'
            '<span class="alink">Explore %s</span></div></a>'
            % (exp_href(e), e["image"], html.escape(e["alt"]), e["num"],
               html.escape(e["title"]), html.escape(e["lede"]), ARROW))
    return "".join(out)


def caps_rows(e):
    return "".join('<li><div class="cap-n">%s</div><div class="cap-d">%s</div></li>' % (n, d)
                   for n, d in e["capabilities"])


def _figure(value, cls="res-n"):
    """Markup for a headline figure. The final text is in the HTML, so it reads
    correctly with no JS; data-* lets main.js count up to it. A trailing '+' is
    picked out in scarlet."""
    m = re.match(r"^([\d.,]+)([A-Za-z%]*)(\+?)$", value)
    if not m:
        return '<span class="%s">%s</span>' % (cls, html.escape(value))
    num, unit, plus = m.groups()
    dec = len(num.split(".")[1]) if "." in num else 0
    return ('<span class="%s" data-count="%s" data-dec="%d" data-unit="%s" data-plus="%s">'
            '%s%s%s</span>'
            % (cls, num.replace(",", ""), dec, unit, plus, num, unit, "<i>+</i>" if plus else ""))


def results_board():
    """Home: four headline figures as ruled rows, each linking to its case study."""
    by_slug = {c["slug"]: c for c in D.CASES}
    return '<ul class="res-list">%s</ul>' % "".join(
        '<li><a class="res-row" href="%s">%s<span class="res-l">%s</span></a></li>'
        % (case_href(by_slug[slug]), _figure(value), html.escape(what))
        for slug, value, what in D.HOME_RESULTS)


def who_we_are():
    """Home: lead sentence of the About intro as a statement, the rest as body copy."""
    lead, _, rest = D.ABOUT["intro"][0].partition(". ")
    return html.escape(lead + "."), html.escape(rest)


def method_cards():
    """How we work: three cards, bottom-aligned, each one a step taller."""
    cards = "".join(
        '<article class="mw-card" style="--i:%d">%s<h3 class="h3">%s</h3>'
        '<p class="body-copy">%s</p></article>'
        % (i, METHOD_ICONS[key], html.escape(t), html.escape(b))
        for i, (key, t, b) in enumerate(D.METHOD))
    return '<div class="mw">%s</div>' % cards



MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]


def post_href(p):
    return "insight-%s.html" % p["slug"]


def long_date(iso):
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m) - 1], y)


def read_minutes(p):
    return max(1, round(p.get("words", 400) / 220))


def excerpt(p):
    """insights.json stores excerpts hard-cut at a fixed length, so most of them
    stop mid-word. Trim back to the last whole word and mark the cut."""
    text = p["excerpt"].rstrip()
    if text.endswith((".", "!", "?", "\u2026", '"')):
        return text
    sp = text.rfind(" ")
    return (text[:sp] if sp > 0 else text).rstrip(" ,;:\u2014-") + "\u2026"


def fix_headings(body):
    """Scraped article HTML jumps straight to h3/h4 under the page's h1. Re-level
    the headings actually used so they start at h2 and never skip."""
    used = sorted({int(n) for n in re.findall(r"<h([1-6])\b", body)})
    remap = {n: min(6, i + 2) for i, n in enumerate(used)}
    return re.sub(r"<(/?)h([1-6])\b",
                  lambda m: "<%sh%d" % (m.group(1), remap[int(m.group(2))]), body)


def meta_desc(p, seen):
    """Meta description from the excerpt; if another page already used it, take the
    next paragraph of the article that is still unique."""
    def clip(t):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()
        if len(t) <= 160:
            return t
        cut = t[:157]
        return cut[:cut.rfind(" ")].rstrip(" ,;:") + "\u2026"
    for cand in [p["excerpt"]] + re.findall(r"<p[^>]*>(.*?)</p>", p["content"], re.S):
        d = clip(cand)
        if len(d) >= 60 and d not in seen:
            seen.add(d)
            return d
    return clip(p["excerpt"])


def post_media(p, cls="post-media"):
    if p.get("image"):
        return ('<div class="%s"><img src="%s" alt="%s" loading="lazy"></div>'
                % (cls, p["image"], html.escape(p.get("alt") or p["title"])))
    return '<div class="%s post-media--blank"><span>SKOT</span></div>' % cls


def post_card(p):
    return ('<article class="post" data-category="%s" data-search="%s">'
            '<a class="post-hit" href="%s">%s'
            '<div class="post-body"><span class="chip">%s</span><h3>%s</h3><p>%s</p></div>'
            '<div class="post-foot"><span>%s</span><span>%s min read</span><span class="go">%s</span></div>'
            '</a></article>'
            % (html.escape(p["category"]),
               html.escape((p["title"] + " " + p["excerpt"]).lower()),
               post_href(p), post_media(p), html.escape(p["category"]),
               html.escape(p["title"]), html.escape(excerpt(p)),
               long_date(p["date"]), read_minutes(p), ARROW))


def post_cards(posts):
    return "".join(post_card(p) for p in posts)


def post_slide(p):
    """Home: a card for the horizontal insights rail — image, meta, headline."""
    return ('<a class="ins-card" href="%s">%s'
            '<div class="ins-body"><p class="ins-meta">%s <span>&middot;</span> %s</p>'
            '<h3 class="ins-title">%s</h3></div></a>'
            % (post_href(p), post_media(p, "ins-media"),
               html.escape(p["category"]), long_date(p["date"]),
               html.escape(p["title"])))


def post_slides(posts):
    return "".join(post_slide(p) for p in posts)


def featured_post(p):
    """The latest post, as the first card of the insights grid, spanning every column.
    It is a real .post, so search and the type filter treat it like any other card."""
    return ('<article class="post post--featured" data-category="%s" data-search="%s">'
            '<a class="post-hit" href="%s">'
            '<div class="featured-copy"><span class="chip">Latest %s</span>'
            '<h2 class="h2">%s</h2><p class="lede">%s</p>'
            '<span class="alink">Read the article %s</span>'
            '<p class="featured-meta"><span>%s</span><span>%s min read</span></p></div>'
            '%s</a></article>'
            % (html.escape(p["category"]),
               html.escape((p["title"] + " " + p["excerpt"]).lower()),
               post_href(p), html.escape(p["category"].lower()), html.escape(p["title"]),
               html.escape(excerpt(p)), ARROW, long_date(p["date"]), read_minutes(p),
               post_media(p, "featured-media")))


# ── Renderer ────────────────────────────────────────────────────────────────
LAYOUT = open(os.path.join(ROOT, "site", "layout.html")).read()


def _asset_version(rel):
    """Short content hash for a static file. It goes on the <link>/<script> URL so a browser
    that cached an older copy fetches the new one as soon as the file changes."""
    import hashlib
    return hashlib.md5(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]


def render(out_name, title, desc, body, pagekey="", active=""):
    links, mob = build_nav(active or out_name)
    page = LAYOUT
    for token, value in [
        ("{{TITLE}}", title), ("{{DESC}}", desc), ("{{PAGEKEY}}", pagekey),
        ("{{NAV_DESKTOP}}", links), ("{{NAV_MOBILE}}", mob),
        ("{{FOOTER_COLS}}", footer_cols()), ("{{BODY}}", body),
        ("{{CSS_V}}", _asset_version("assets/css/styles.css")),
        ("{{JS_V}}", _asset_version("assets/js/main.js")),
    ]:
        page = page.replace(token, value)
    open(os.path.join(ROOT, out_name), "w").write(page)
    return out_name


def page_body(name, **tokens):
    src = open(os.path.join(ROOT, "site", "pages", name)).read()
    for k, v in tokens.items():
        src = src.replace("{{%s}}" % k, v)
    return src


def programme_duos(limit=None):
    """Programmes index: a summary per programme, each linking through to its own page."""
    out = []
    progs = D.PROGRAMMES if limit is None else D.PROGRAMMES[:limit]
    for i, p in enumerate(progs):
        facts = "".join('<div><div class="stat-n">%s</div>'
                        '<div class="stat-l">%s</div></div>' % (v, l) for v, l in p["facts"])
        flip = " duo--flip" if i % 2 else ""
        out.append(
            '<div class="duo%s" style="border-bottom:1px solid var(--line)">'
            '<div class="duo-copy"><span class="chip">%s</span>'
            '<h2 class="h2" style="margin-top:.25rem">%s</h2>'
            '<p class="lede">%s</p>'
            '<div class="stats" style="grid-template-columns:repeat(3,minmax(0,1fr));margin-top:.75rem;'
            'border-bottom:0">%s</div>'
            '<div style="display:flex;flex-wrap:wrap;gap:.75rem;margin-top:.5rem">'
            '<a class="btn btn-solid" href="%s">Learn more %s</a>'
            '<a class="alink" href="contact.html">%s</a></div>'
            '</div><div class="duo-media"><img src="%s" alt="%s" loading="lazy"></div></div>'
            % (flip, p["badge"], p["name"], p["lede"], facts, prog_href(p), ARROW, p["cta"],
               p["image"], html.escape(p["alt"])))
    return "".join(out)


def programme_strip():
    """Home: the scattered photo band under the programmes panel.

    Purely decorative, so it is hidden from assistive tech. It shows SKOT Impact Academy
    cohort photographs only, one frame each.
    """
    shots = ["full-room", "cohort-closeup", "guest-speaker", "cohort-applause",
             "cohort-attentive", "cohort-kente", "facilitator-presenting"]
    return '<div class="pg-strip" aria-hidden="true">%s</div>' % "".join(
        '<img src="assets/img/academy/%s.jpg" alt="" loading="lazy">' % n for n in shots)


def main():
    built = []
    T = {"ARROW": ARROW}

    # ── Home ────────────────────────────────────────────────────────────────
    built.append(render(
        "index.html",
        "SKOT Communications — Find your voice. Speak to your people.",
        "Strategic communications and reputation management consultancy with a Sub-Saharan Africa focus.",
        page_body("index.html", WHO_LEAD=who_we_are()[0], WHO_REST=who_we_are()[1],
                  HERO_RAIL=hero_rail(), CLIENT_RAIL=client_rail(), RESULTS_BOARD=results_board(), EXPERTISE_TABS=expertise_tabs(), METHOD_CARDS=method_cards(),
                  FEATURED_CASES=home_cases(), PROGRAMME_STRIP=programme_strip(),
                  RECENT_POSTS=post_slides(POSTS[:8]), **T)))

    # ── About ───────────────────────────────────────────────────────────────
    intro = "".join('<p class="body-copy t-lead">%s</p>' % p for p in D.ABOUT["intro"])
    clients = '<div class="cells cells-3" style="border-bottom:1px solid var(--line)">' + "".join(
        '<div><p class="eyebrow">%s</p><p class="h4" style="margin-top:.9rem">%s</p>'
        '<a class="alink alink--sm" style="margin-top:1rem" href="%s">Read the story %s</a></div>'
        % (c["sector"], c["client"], case_href(c), ARROW) for c in D.CASES) + "</div>"
    built.append(render(
        "about.html", "About — SKOT Communications",
        "SKOT Communications is a strategic communications and reputation management consultancy with a Sub-Saharan Africa focus.",
        page_body("about.html", ABOUT_INTRO=intro, VISION=D.ABOUT["vision"], MISSION=D.ABOUT["mission"],
                  CLIENT_CELLS=clients, METHOD_CARDS=method_cards(), **T)))

    # ── Expertise index + four sub-pages ────────────────────────────────────
    built.append(render(
        "expertise.html", "Expertise — SKOT Communications",
        "Corporate and brand communications, public affairs, digital and creative strategy, crisis and reputation management.",
        page_body("expertise.html", EXPERTISE_CARDS=expertise_cards(), METHOD_CARDS=method_cards(), **T),
        pagekey="expertise", active="expertise.html"))

    for e in D.EXPERTISE:
        rel = [c for c in D.CASES if c["discipline"].split()[0].lower() in e["title"].lower()][:2]
        if len(rel) < 2:
            rel = (rel + [c for c in D.CASES if c not in rel])[:2]
        sibs = "".join('<a class="btn btn-ghost btn-sm" href="%s">%s</a>' % (exp_href(o), o["short"])
                       for o in D.EXPERTISE if o["slug"] != e["slug"])
        built.append(render(
            exp_href(e), "%s — SKOT Communications" % e["title"], e["lede"],
            page_body("_expertise.html", NUM=e["num"], TITLE=html.escape(e["title"]),
                      LEDE=html.escape(e["lede"]), BODY=html.escape(e["body"]), IMAGE=e["image"],
                      ALT=html.escape(e["alt"]), CAPS=caps_rows(e), RELATED=case_cards(rel),
                      **T),
            pagekey="expertise", active="expertise.html"))

    # ── Work ────────────────────────────────────────────────────────────────
    # ── Case studies index ──────────────────────────────────────────────────
    filters = "".join('<button type="button" data-filter="%s" aria-pressed="%s">%s</button>'
                      % (html.escape(d), "true" if d == "All" else "false", html.escape(d))
                      for d in D.DISCIPLINES)
    built.append(render(
        "case-studies.html", "Our work and case studies — SKOT Communications",
        "Strategic discipline applied to corporate milestones, public affairs mandates and reputation-critical moments: selected mandates across technology, energy, leadership, agriculture, financial services and live experience.",
        page_body("case-studies.html", FILTERS=filters, ALL_CASES=case_cards(),
                  RESULT_STATS=stat_cells(
                      [("526M+", "Estimated reach"), ("105", "Media mentions"),
                       ("21.87M", "Impressions"), ("100%", "Positive sentiment")]),
                  **T)))

    # ── Case study detail pages ─────────────────────────────────────────────
    for i, c in enumerate(D.CASES):
        if c["metrics"]:
            metrics = ('<section class="sec sec--flush" style="border-bottom:0;padding-block:0">'
                       '<div class="shell" style="padding-inline:0">%s</div></section>'
                       % stat_cells(c["metrics"]))
        else:
            metrics = ('<section class="sec sec--flush" style="border-bottom:0;padding-block:0">'
                       '<div class="shell" style="padding-inline:0"><div class="stats"><div '
                       'class="cell-accent"><p class="label">Impact</p><p class="body-copy" '
                       'style="margin-top:.75rem">%s</p></div></div></div></section>' % c["qualitative"])
        approach = "".join('<p class="body-copy">%s</p>' % p for p in c["approach"])
        nxt = [o for o in D.CASES if o["slug"] != c["slug"]][:2]
        built.append(render(
            case_href(c), "%s — Case study — SKOT Communications" % c["client"], c["summary"],
            page_body("_case.html", DISCIPLINE=html.escape(c["discipline"]), TITLE=html.escape(c["title"]),
                      SUMMARY=html.escape(c["summary"]), CLIENT=html.escape(c["client"]),
                      PANEL="panel-putty" if client_logo(c["slug"]) else PANELS[i % len(PANELS)],
                      CASE_MARK=case_mark(c), METRICS=metrics, PANEL_NAME=html.escape(c.get("panel_name", c["client"])),
                      CHALLENGE='<p class="body-copy">%s</p>' % c["challenge"], APPROACH=approach,
                      IMPACT='<p class="body-copy">%s</p>' % c["impact"],
                      CONTRIBUTION=c["contribution"], NEXT_CASES=case_cards(nxt), **T),
            active="case-studies.html"))

    # ── Programmes index + two dedicated pages ──────────────────────────────
    built.append(render(
        "programmes.html", "Programmes — SKOT Communications",
        "SKOT Impact Academy, SKOT Elevate and the quarterly Masterclass.",
        page_body("programmes.html", PROGRAMME_DUOS=programme_duos(), **T),
        pagekey="programmes", active="programmes.html"))

    masterclass_topics = '<div class="cells cells-3" style="border-bottom:1px solid var(--line)">' + "".join(
        '<div><p class="h4">%s</p></div>' % t for t in D.MASTERCLASS["topics"]) + "</div>"
    masterclass_section = (
        '<section class="sec" id="masterclass">'
        '<div class="shell"><div class="sec-split">'
        '<div><p class="label">Under SKOT Elevate</p><h2 class="h2" style="margin-top:1rem">Masterclass.</h2></div>'
        '<div><p class="body-copy t-lead">%s</p>'
        '<a class="alink" href="contact.html" style="margin-top:1.75rem">Register interest %s</a></div>'
        '</div></div>'
        '<div class="shell" style="padding-inline:0;margin-top:clamp(2rem,4vw,3rem)">%s</div>'
        '</section>' % (D.MASTERCLASS["body"], ARROW, masterclass_topics))

    def _ph(name, alt, cls="", pos="50% 50%"):
        return ('<img class="%s" src="assets/img/academy/%s.jpg" alt="%s" loading="lazy" decoding="async" '
                'style="object-position:%s">' % (cls, name, html.escape(alt), pos))

    _how = [
        ("Practical exercises", "Build strategies and analyse real campaigns.", "cohort-attentive",
         "Cohort members listening closely during a session", "50% 40%"),
        ("Peer learning", "Guided group discussions with fellow early-career professionals.", "cohort-closeup",
         "Smiling cohort members in the front rows", "50% 35%"),
        ("Interactive workshops", "Led by industry practitioners, with role-play, scenario planning and live feedback.",
         "facilitator-presenting", "A facilitator presenting to a classroom of participants", "50% 40%"),
    ]
    _pillar_html = "".join(
        '<li class="acad-pillar"><div class="acad-ph">%s</div>'
        '<p class="acad-n">%02d</p><p class="h4">%s</p><p class="acad-d">%s</p></li>'
        % (_ph(n, a, pos=pos), i + 1, t, d)
        for i, (t, d, n, a, pos) in enumerate(_how))

    _mosaic = [
        ("full-room", "The full cohort seated in the Academy classroom", "a1", "In session", "50% 50%"),
        ("cohort-applause", "Cohort members applauding and smiling during a session", "a2", "Peer learning", "40% 40%"),
        ("cohort-kente", "A facilitator and cohort members during a session", "a3", "Facilitator-led", "50% 50%"),
    ]
    _mosaic_html = "".join(
        '<figure class="acad-tile %s">%s<figcaption>%s</figcaption></figure>' % (c, _ph(n, a, pos=pos), cap)
        for n, a, c, cap, pos in _mosaic)

    _mod_html = "".join(
        '<li class="acad-mod"><span class="acad-mod-n">%02d</span><h3 class="h4">%s</h3></li>' % (i + 1, html.escape(t))
        for i, t in enumerate(D.ACADEMY_LEARN))

    academy_section = (
        '<section class="sec acad-who"><div class="shell">'
        '<div class="sec-split"><div><p class="label">Who it&rsquo;s for</p></div>'
        '<div><p class="h4">%s</p></div></div>'
        '</div></section>'
        '<section class="sec acad-modules"><div class="shell">'
        '<div class="sec-split"><div><p class="label">What you&rsquo;ll learn</p></div>'
        '<div><h2 class="h2">The PR Foundation Course.</h2>'
        '<p class="body-copy" style="margin-top:1.25rem;max-width:62ch">%s</p><ol class="acad-mods">%s</ol></div></div>'
        '</div></section>'
        '<section class="sec acad-how"><div class="shell">'
        '<div class="sec-split"><div><p class="label">How you&rsquo;ll learn</p></div>'
        '<div><h2 class="h2">Practical, shared and led by practitioners.</h2></div></div>'
        '<ol class="acad-pillars">%s</ol></div></section>'
        '<section class="acad-band"><div class="shell">'
        '<div class="acad-head"><p class="label label--light">Inside the Academy</p>'
        '<h2 class="h2">The cohorts, in the room.</h2></div>'
        '<div class="acad-mosaic">%s</div></div></section>'
        '<section class="acad-cta"><div class="acad-cta-ph">%s</div>'
        '<div class="acad-cta-body"><p class="label label--light">Next cohort</p>'
        '<h2 class="h2">Start your PR journey with SKOT Impact Academy.</h2>'
        '<a class="btn btn-light" href="contact.html">Apply for the next cohort %s</a></div></section>'
        % (html.escape(D.ACADEMY_WHO), html.escape(D.ACADEMY_COURSE), _mod_html, _pillar_html, _mosaic_html,
           _ph("embrace", "Two members of the Academy community sharing an embrace", pos="50% 30%"), ARROW))

    for p in D.PROGRAMMES:
        facts = stat_cells(p["facts"], cols=2 if p["slug"] == "impact-academy" else None)
        built.append(render(
            prog_href(p), "%s — SKOT Communications" % p["name"], p["lede"],
            page_body("_programme.html", SLUG=p["slug"], BADGE=html.escape(p["badge"]), NAME=html.escape(p["name"]),
                      LEDE=html.escape(p["lede"]), CTA=html.escape(p["cta"]), BODY=html.escape(p["body"]),
                      IMAGE=p["image"], ALT=html.escape(p["alt"]), FACTS=facts,
                      MASTERCLASS_SECTION=masterclass_section if p["slug"] == "elevate" else "",
                      ACADEMY_SECTION=academy_section if p["slug"] == "impact-academy" else "",
                      SIBLINGS=sibs, **T),
            pagekey="programmes", active="programmes.html"))

    # ── Contact ─────────────────────────────────────────────────────────────
    built.append(render(
        "contact.html", "Get in touch — SKOT Communications",
        "Speak with the SKOT Communications advisory team in Victoria Island, Lagos.",
        page_body("contact.html", **T), pagekey="contact"))

    # ── Insights index + article pages ──────────────────────────────────────
    if POSTS:
        cats = ["All"] + sorted({p["category"] for p in POSTS})
        pfilters = "".join('<button type="button" data-filter="%s" aria-pressed="%s">%s</button>'
                           % (html.escape(c), "true" if c == "All" else "false", html.escape(c))
                           for c in cats)
        feat, rest = POSTS[0], POSTS[1:]
        built.append(render(
            "insights.html", "Insights — SKOT Communications",
            "Perspectives on reputation, influence and communications across Sub-Saharan Africa and beyond.",
            page_body("insights.html", FILTERS=pfilters,
                      POSTS=featured_post(feat) + post_cards(rest), **T),
            active="insights.html"))

        seen_desc = set()
        for i, p in enumerate(POSTS):
            if p.get("image"):
                hero = ('<div class="bleed"><img src="%s" alt="%s"><div class="spectrum" '
                        'aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div></div>'
                        % (p["image"], html.escape(p.get("alt") or p["title"])))
            else:
                hero = ('<div class="bleed"><div class="post-media--blank" style="height:clamp(10rem,20vw,15rem)">'
                        '<span>SKOT</span></div><div class="spectrum" aria-hidden="true">'
                        '<i></i><i></i><i></i><i></i><i></i></div></div>')
            rel = [o for o in POSTS if o["slug"] != p["slug"]][:3]
            share = "https://www.linkedin.com/sharing/share-offsite/?url=" + quote(
                "https://skotcomms.com/" + post_href(p))
            built.append(render(
                post_href(p), "%s — SKOT Communications" % p["title"], meta_desc(p, seen_desc),
                page_body("_article.html", TITLE=html.escape(p["title"]),
                          TITLE_ENC=quote(p["title"]), CATEGORY=html.escape(p["category"]),
                          DATE_LONG=long_date(p["date"]), EXCERPT=html.escape(p["excerpt"]),
                          MINUTES=str(read_minutes(p)), HERO_MEDIA=hero,
                          CONTENT=fix_headings(p["content"]), RELATED=post_cards(rel),
                          LINKEDIN_SHARE=html.escape(share, quote=True), **T),
                active="insights.html"))

    # drop pages from a previous build that this run no longer generates
    man = os.path.join(ROOT, "site", ".manifest.json")
    previous = _json.load(open(man)) if os.path.exists(man) else []
    for old in previous:
        if old not in built and os.path.isfile(os.path.join(ROOT, old)):
            os.remove(os.path.join(ROOT, old))
            print("   removed stale", old)
    _json.dump(sorted(built), open(man, "w"), indent=0)

    print("built %d pages:" % len(built))
    for b in built:
        print("  ", b)


if __name__ == "__main__":
    main()
