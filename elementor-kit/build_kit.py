#!/usr/bin/env python3
"""Builds the SKOT Communications Elementor Pro Template Kit (.zip).

    python3 elementor-kit/build_kit.py [--asset-base URL]

Reads the same content model the static site uses (site/data.py, site/insights.json via
build.py) and writes native Elementor documents: Flexbox Containers plus core / Pro widgets
(Heading, Text Editor, Button, Image, Image Box, Icon Box, Counter, Form, Nav Menu, Posts ...).
Nothing is emitted as raw HTML except the rich text inside Text Editor widgets.

Output: elementor-kit/dist/skot-template-kit.zip
    manifest.json, site-settings.json, readme.txt, templates/*.json, images/*
Standard library only.
"""
import datetime, hashlib, json, os, re, sys, zipfile
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import build as B          # noqa: E402  (client_logo, excerpt, read_minutes ... one source of truth)
D = B.D

ASSET_BASE = os.environ.get("ASSET_BASE", "https://raw.githubusercontent.com/localServer2112/skot/main")
if "--asset-base" in sys.argv:
    ASSET_BASE = sys.argv[sys.argv.index("--asset-base") + 1]
ASSET_BASE = ASSET_BASE.rstrip("/")

KIT_VERSION = "1.0.0"
ELEMENTOR_VERSION = "3.18.0"          # minimum: Flexbox Containers are stable from here
USED_IMAGES = set()                   # repo-relative paths, bundled into images/

# ── Design tokens → Global Colors / Global Fonts ───────────────────────────────────────────
# key: (kit id, title, value).  Elementor reserves primary/secondary/text/accent as system ids.
COLOR = {
    "scarlet": ("primary", "Scarlet (primary)", "#D6001C"),
    "ink": ("secondary", "Ink (secondary)", "#111315"),
    "text": ("text", "Text", "#111315"),
    "teal": ("accent", "Teal (accent)", "#013D47"),
    "canvas": ("canvas", "Canvas", "#FBFBF9"),
    "panel": ("panel", "Panel", "#F4F2ED"),
    "panel2": ("panel_2", "Panel 2", "#EFEDE7"),
    "card": ("card", "Card", "#F7F7F7"),
    "white": ("white", "White", "#FFFFFF"),
    "ink72": ("ink_72", "Ink 72%", "#111315B8"),
    "ink56": ("ink_56", "Ink 56%", "#1113158F"),
    "ink38": ("ink_38", "Ink 38%", "#11131561"),
    "line": ("line", "Line", "#E3E0DA"),
    "linesoft": ("line_soft", "Line soft", "#EDEBE6"),
    "scarlet_hover": ("scarlet_hover", "Scarlet hover", "#B30018"),
    "teal_light": ("teal_light", "Teal light", "#0A7C8F"),
    "teal_deep": ("teal_deep", "Teal deep", "#012A31"),
    "on_dark": ("on_dark", "On dark", "#FBFBF9"),
    "on_dark64": ("on_dark_64", "On dark 64%", "#FBFBF9A3"),
    "on_dark38": ("on_dark_38", "On dark 38%", "#FBFBF961"),
    "line_dark": ("line_dark", "Line on dark", "#FBFBF929"),
    "amber": ("amber", "Spectrum amber", "#EE9B3A"),
    "orange": ("orange", "Spectrum orange", "#E8662B"),
    "crimson": ("crimson", "Spectrum crimson", "#A8121C"),
}
SYSTEM_COLOR_IDS = ("primary", "secondary", "text", "accent")

SANS, MONO = "Instrument Sans", "IBM Plex Mono"
# role: (kit id, title, family, weight, size px d/t/m, line-height d/t/m, letter-spacing em, transform)
# Sizes and leading come from the --fs-* / --lh-* tokens in assets/css/styles.css; tablet is the
# <1024 step, mobile the <768 step. Elementor weights are whole hundreds, so 510/590/680 -> 500/600/700.
TYPE = {
    "title":   ("title", "Title", SANS, "500", (72, 56, 38), (1, 1.1, 1.1), -.022, ""),
    "display": ("display", "Display", SANS, "500", (64, 56, 38), (1, 1.1, 1.1), -.022, ""),
    "h2":      ("primary", "Heading 2 (primary)", SANS, "500", (48, 32, 24), (1, 1.12, 1.33), -.022, ""),
    "h3":      ("h3", "Heading 3", SANS, "600", (32, 24, 24), (1.125, 1.33, 1.33), -.022, ""),
    "h4":      ("h4", "Heading 4", SANS, "600", (24, 24, 20), (1.33, 1.33, 1.35), -.012, ""),
    "h5":      ("h5", "Heading 5", SANS, "600", (20, 20, 20), (1.33, 1.33, 1.33), -.012, ""),
    "lead":    ("lead", "Lead", SANS, "400", (20, 20, 18), (1.6, 1.6, 1.6), -.01, ""),
    "read":    ("read", "Article text", SANS, "400", (18, 18, 17), (1.6, 1.6, 1.6), 0, ""),
    "body":    ("text", "Body (text)", SANS, "400", (17, 17, 16), (1.6, 1.6, 1.6), -.011, ""),
    "ui":      ("secondary", "UI (secondary)", SANS, "500", (16, 16, 16), (1.6, 1.6, 1.6), -.011, ""),
    "button":  ("accent", "Button (accent)", SANS, "500", (16, 16, 16), (1.33, 1.33, 1.33), 0, ""),
    "small":   ("small", "Small", SANS, "400", (15, 15, 15), (1.5, 1.5, 1.5), -.013, ""),
    "xs":      ("xs", "Extra small", SANS, "400", (14, 14, 14), (1.5, 1.5, 1.5), -.01, ""),
    "tag":     ("tag", "Tag (mono)", MONO, "400", (13, 13, 13), (1.4, 1.4, 1.4), 0, "uppercase"),
}

# ── Element ids / settings plumbing ─────────────────────────────────────────────────────────
_n = [0]


def eid():
    _n[0] += 1
    return hashlib.md5(b"skot-kit-%d" % _n[0]).hexdigest()[:7]


def px(v, unit="px"):
    return {"unit": unit, "size": v, "sizes": []}


def dim(t, r=None, b=None, l=None, unit="px"):
    r, b, l = (t if r is None else r), (t if b is None else b), (r if l is None and r is not None else (t if l is None else l))
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b), "left": str(l),
            "isLinked": t == r == b == l}


def gap(v):
    return {"column": str(v), "row": str(v), "isLinked": True, "unit": "px", "size": v}


class S(dict):
    """Widget / container settings with helpers for global colours and typography.
    Every global is written twice: the literal value (so a widget still renders if the kit's
    site settings are not imported) and the __globals__ reference (so it follows the kit)."""

    def col(self, ctrl, key):
        gid, _, val = COLOR[key]
        self[ctrl] = val
        self.setdefault("__globals__", {})[ctrl] = "globals/colors?id=%s" % gid
        return self

    def ty(self, prefix, role):
        gid, _, fam, wt, sz, lh, ls, tt = TYPE[role]
        self["%s_typography" % prefix] = "custom"
        self["%s_font_family" % prefix] = fam
        self["%s_font_weight" % prefix] = wt
        for suffix, i in (("", 0), ("_tablet", 1), ("_mobile", 2)):
            self["%s_font_size%s" % (prefix, suffix)] = px(sz[i])
            self["%s_line_height%s" % (prefix, suffix)] = px(lh[i], "em")
        self["%s_letter_spacing" % prefix] = px(ls, "em")
        if tt:
            self["%s_text_transform" % prefix] = tt
        self.setdefault("__globals__", {})["%s_typography" % prefix] = "globals/typography?id=%s" % gid
        return self


def W(widget, settings):
    return {"id": eid(), "elType": "widget", "widgetType": widget, "settings": dict(settings), "elements": []}


def url(href):
    """Site hrefs -> WordPress paths: about.html -> /about/ (name the WP pages after the templates)."""
    if href.startswith(("http", "mailto:", "tel:", "#")):
        return href
    base, _, frag = href.partition("#")
    path = "/" if base in ("", "index.html") else "/" + base[:-5] + "/"
    return path + ("#" + frag if frag else "")


def link(href, external=False):
    return {"url": url(href), "is_external": "on" if external else "", "nofollow": "", "custom_attributes": ""}


def img_url(path):
    USED_IMAGES.add(path)
    return "%s/%s" % (ASSET_BASE, path)


# ── Containers ────────────────────────────────────────────────────────────────────────────────
def con(kids=(), *, row=False, stack=True, w=None, gap_=None, jc=None, ai=None, wrap=False, bg=None,
        pad=None, border=None, css="", tag=None, min_h=None, boxed=False, full=False, **extra):
    """Flexbox Container. `w` is a desktop width in %; tablet/mobile go full width when `stack`.
    `pad` is (top, right, bottom, left) or {'d':..,'t':..,'m':..}; `border` e.g. dict(b=1, color='line')."""
    s = S(content_width="boxed" if boxed else "full", flex_direction="row" if row else "column")
    if boxed:
        s["boxed_width"] = px(1400)
    if row and stack:
        s["flex_direction_tablet"] = "column"
        s["flex_direction_mobile"] = "column"
    if row and wrap:
        s["flex_wrap"] = "wrap"
    s["flex_gap"] = gap(gap_ if gap_ is not None else 0)
    if jc:
        s["flex_justify_content"] = jc
    if ai:
        s["flex_align_items"] = ai
    if w is not None:
        s["width"] = px(w, "%")
        if stack:
            s["width_tablet"] = px(100 if w < 100 else w, "%")
            s["width_mobile"] = px(100, "%")
    if bg:
        s["background_background"] = "classic"
        s.col("background_color", bg)
    if pad:
        d = pad if isinstance(pad, dict) else {"d": pad}
        s["padding"] = dim(*d["d"])
        if "t" in d:
            s["padding_tablet"] = dim(*d["t"])
        if "m" in d:
            s["padding_mobile"] = dim(*d["m"])
    if border:
        sides = [border.get(k, 0) for k in "trbl"]
        s["border_border"] = "solid"
        s["border_width"] = dim(*sides)
        s.col("border_color", border.get("color", "line"))
    if min_h:
        s["min_height"] = px(min_h)
    if css:
        s["css_classes"] = css
    if tag:
        s["html_tag"] = tag
    s.update(extra)
    kids = list(kids)
    for k in kids:
        if k["elType"] == "container":
            k["isInner"] = True
    return {"id": eid(), "elType": "container", "settings": dict(s), "isInner": False, "elements": kids}


def pads(y=(112, 80, 60), x=(48, 32, 18), top=None, bottom=None):
    """Section padding for desktop / tablet / mobile. top/bottom override the vertical value."""
    out = {}
    for i, k in enumerate("dtm"):
        t = y[i] if top is None else top[i]
        b = y[i] if bottom is None else bottom[i]
        out[k] = (t, x[i], b, x[i])
    return out


def section(kids, *, bg="canvas", border=True, gap_=48, css="", y=(112, 80, 60), **kw):
    return con(kids, boxed=True, bg=bg, pad=pads(y), gap_=gap_, css=css,
               border=dict(b=1) if border else None, **kw)


# ── Widgets ───────────────────────────────────────────────────────────────────────────────────
def heading(text, role="h2", color="ink", tag="h2", align=None, css="", href=None):
    s = S(title=text, header_size=tag).col("title_color", color).ty("typography", role)
    if align:
        s["align"] = align
    if css:
        s["_css_classes"] = css
    if href:
        s["link"] = link(href)
    return W("heading", s)


def label(text, *, light=False, teal=False):
    css = "skot-label" + (" skot-label--light" if light else "") + (" skot-label--teal" if teal else "")
    return heading(text, "tag", "on_dark64" if light else "ink72", "p", css=css)


def text(html_, role="body", color="ink72", align=None, max_w=None, css=""):
    s = S(editor=html_).col("text_color", color).ty("typography", role)
    if align:
        s["align"] = align
    if max_w:
        s["_element_width"] = "initial"
        s["_element_custom_width"] = px(max_w)
    if css:
        s["_css_classes"] = css
    return W("text-editor", s)


def paras(items, **kw):
    return text("".join("<p>%s</p>" % p for p in items), **kw)


BTN = {  # style: (background, text, hover background, border)
    "solid": ("ink", "canvas", "#000000", None),
    "scarlet": ("scarlet", "white", "scarlet_hover", None),
    "teal": ("teal", "white", "teal_deep", None),
    "ghost": ("canvas", "ink", "canvas", "line"),
    "light": ("canvas", "ink", "white", None),
    "onmedia": ("#111315", "on_dark", "#111315", "line_dark"),
}


def button(text_, href, style="solid", arrow=True, small=False):
    bg, fg, hov, bd = BTN[style]
    s = S(text=text_, link=link(href), size="sm" if small else "md", button_type="")
    s.ty("typography", "xs" if small else "button")
    if bg.startswith("#"):
        s["background_color"] = bg + ("94" if style == "onmedia" else "")
    else:
        s.col("background_color", bg)
    s.col("button_text_color", fg)
    if hov.startswith("#"):
        s["button_background_hover_color"] = hov
    else:
        s.col("button_background_hover_color", hov)
    s.col("hover_color", fg)
    s["border_radius"] = dim(0)
    s["text_padding"] = dim(11, 20) if small else dim(14, 24)
    if bd:
        s["border_border"] = "solid"
        s["border_width"] = dim(1)
        s.col("border_color", bd)
    if arrow:
        s["selected_icon"] = {"value": "fas fa-arrow-right", "library": "fa-solid"}
        s["icon_align"] = "row-reverse"
        s["icon_indent"] = px(10)
    s["_css_classes"] = "skot-btn"
    return W("button", s)


def alink(text_, href, accent=True, small=False, dark=False):
    """Text link with an arrow: a transparent Button with no padding."""
    s = S(text=text_, link=link(href), size="sm")
    s.ty("typography", "xs" if small else "button")
    s["background_color"] = "#FFFFFF00"
    s["button_background_hover_color"] = "#FFFFFF00"
    if dark:
        s.col("button_text_color", "on_dark").col("hover_color", "on_dark64")
    else:
        s.col("button_text_color", "scarlet" if accent else "ink")
        s.col("hover_color", "ink" if accent else "scarlet")
    s["text_padding"] = dim(0)
    s["border_radius"] = dim(0)
    s["selected_icon"] = {"value": "fas fa-arrow-right", "library": "fa-solid"}
    s["icon_align"] = "row-reverse"
    s["icon_indent"] = px(8)
    s["_css_classes"] = "skot-alink"
    return W("button", s)


def image(path, alt="", *, h=None, w=None, href=None, fit="cover", css=""):
    s = S(image={"url": img_url(path), "id": "", "alt": alt, "source": "library"}, image_size="full")
    if h:
        s["height"] = px(h)
        s["height_tablet"] = px(max(160, int(h * .8)))
        s["height_mobile"] = px(max(140, int(h * .6)))
        s["object-fit"] = fit
    if w:
        s["width"] = px(w, "%")
    if href:
        s["link_to"] = "custom"
        s["link"] = link(href)
    if css:
        s["_css_classes"] = css
    return W("image", s)


def image_box(path, title, desc, href, *, role="h4", alt="", h=None):
    s = S(image={"url": img_url(path), "id": "", "alt": alt, "source": "library"}, image_size="full",
          title_text=title, description_text=desc, link=link(href), title_size="h3",
          image_position="top", text_align="left", image_space=px(24))
    s.col("title_color", "ink").ty("title_typography", role)
    s.col("description_color", "ink72").ty("description_typography", "small")
    s["_css_classes"] = "skot-card"
    return W("image-box", s)


def icon_box(icon, title, desc):
    s = S(selected_icon={"value": icon, "library": "fa-solid"}, title_text=title, description_text=desc,
          title_size="h3", position="top", text_align="left", icon_space=px(24), icon_size=px(44))
    s.col("primary_color", "scarlet").col("title_color", "ink").ty("title_typography", "h3")
    s.col("description_color", "ink72").ty("description_typography", "body")
    s["_css_classes"] = "skot-iconbox"
    return W("icon-box", s)


def counter(value, caption, *, role="h2", dark=False, css="skot-counter"):
    num, unit, plus = re.match(r"^([\d.,]+)([A-Za-z%]*)(\+?)$", value).groups()
    s = S(starting_number=0, duration=2000, thousand_separator="", title=caption,
          ending_number=num.replace(",", ""), prefix="", suffix=unit + plus)
    s.col("number_color", "on_dark" if dark else "ink").ty("typography_number", role)
    s.col("title_color", "on_dark64" if dark else "ink56").ty("typography_title", "xs")
    s["_css_classes"] = css
    return W("counter", s)


def fact(value, caption, *, dark=False, role="h3"):
    """A figure that is a word, not a number ("Free", "6 weeks"): Heading + Text Editor."""
    return [heading(value, role, "on_dark" if dark else "ink", "p"),
            text(escape(caption), "xs", "on_dark64" if dark else "ink56")]


def spectrum():
    cells = [con(w=20, stack=False, bg=k, min_h=5) for k in ("teal_light", "amber", "orange", "scarlet", "crimson")]
    return con(cells, row=True, stack=False, min_h=5, css="skot-spectrum")


def bleed(path, alt, h=540):
    return con([image(path, alt, h=h), spectrum()], gap_=0)


# ── Layout patterns ───────────────────────────────────────────────────────────────────────────
def sec_head(lbl, title_html, link_=None, *, light=False):
    left = con([label(lbl, light=light), heading(title_html, "h2", "on_dark" if light else "ink")], gap_=16, w=68)
    kids = [left]
    if link_:
        kids.append(con([alink(*link_)], w=32, jc="flex-end", ai="flex-end"))
    return con(kids, row=True, jc="space-between", ai="flex-end", gap_=24)


def split(left, right, wl=42):
    return con([con(left, w=wl, gap_=16), con(right, w=100 - wl, gap_=24)], row=True, gap_=64)


def grid(cells, cols, *, pad=(32, 32, 32, 32), color="line", bg=None):
    """Hairline grid: top/left rule on the container, right/bottom rule on every cell, so it closes."""
    w = round(100 / cols, 3)
    kids = [con(c, w=w, pad=pad, gap_=14, border=dict(r=1, b=1, color=color), bg=bg) for c in cells]
    for k in kids:
        if cols > 2:
            k["settings"]["width_tablet"] = px(50, "%")
    return con(kids, row=True, wrap=True, border=dict(t=1, l=1, color=color), gap_=0)


def page_hero(eyebrow, title, lede, cta=None, extra=None):
    left = con([label(eyebrow), heading(title, "title", "ink", "h1")], w=62, jc="flex-end", gap_=28,
               pad={"d": (96, 48, 56, 48), "t": (72, 32, 40, 32), "m": (48, 18, 32, 18)}, min_h=380)
    side = [text(lede, "lead", "ink72")]
    if cta:
        side.append(button(cta[0], cta[1], cta[2] if len(cta) > 2 else "scarlet"))
    side += extra or []
    right = con(side, w=38, jc="flex-end", gap_=28, border=dict(l=1),
                pad={"d": (96, 48, 56, 48), "t": (40, 32, 40, 32), "m": (32, 18, 40, 18)})
    return con([left, right], row=True, border=dict(b=1), gap_=0, boxed=True, css="skot-phero",
               bg="canvas")


def method_section(note=None):
    cards = [icon_box(i, t, b) for i, (t, b) in zip(
        ("fas fa-assistive-listening-systems", "fas fa-comment-dots", "fas fa-bullhorn"),
        ((t, b) for _, t, b in D.METHOD))]
    head = sec_head("How we work", "Advice first.<br>Then we make it happen.")
    return section([head, grid([[c] for c in cards], 3, pad=(40, 32, 40, 32), bg="card")], bg="white", border=False)


def case_card(c):
    logo = B.client_logo(c["slug"])
    kids = [
        label(c["discipline"]),
        (image(logo[0], c["client"], h=96, fit="contain") if logo else heading(c["client"], "h3", "ink", "h3")),
        heading(c["title"], "h4", "ink", "h3", href=B.case_href(c)),
        text(escape(c["summary"]), "small", "ink72"),
        alink("Read the story", B.case_href(c), small=True),
    ]
    return kids


def counters_row(metrics, *, dark=False, role="h2", bg=None):
    cells = [[counter(v, l, role=role, dark=dark)] for v, l in metrics]
    return grid(cells, max(1, min(4, len(metrics))), pad=(32, 32, 32, 32),
                color="line_dark" if dark else "line", bg=bg)


# ══ Pages ═════════════════════════════════════════════════════════════════════════════════════
def home():
    hero = con(
        [heading("Find your voice.<br>Speak to your people&hellip;", "title", "on_dark", "h1"),
         con([button("Speak with our advisory team", "contact.html", "scarlet"),
              button("Explore our expertise", "expertise.html", "onmedia", arrow=False)],
             row=True, stack=False, gap_=12, wrap=True)],
        boxed=True, jc="flex-end", gap_=32, min_h=720, css="skot-hero",
        pad={"d": (96, 48, 72, 48), "t": (72, 32, 56, 32), "m": (56, 18, 48, 18)},
        background_background="classic", background_position="center center", background_size="cover",
        background_image={"url": img_url("assets/img/hero-voice.jpg"), "id": "", "source": "library"},
        background_overlay_background="classic", background_overlay_color="#111315",
        background_overlay_opacity=px(.52))
    rail = con([con([alink(e["title"], B.exp_href(e), accent=False)], w=25, pad=(20, 24, 20, 24), border=dict(r=1))
                for e in D.EXPERTISE], row=True, boxed=True, border=dict(b=1), bg="canvas", gap_=0)

    what = section([
        sec_head("What we do", "We advise organisations on reputation, stakeholders and influence, then deliver "
                 "the communications strategy and execution that make every message count.",
                 ("See our work", "case-studies.html")),
        grid([[image_box(e["image"], e["title"], e["lede"], B.exp_href(e), alt=e["alt"], h=220)]
              for e in D.EXPERTISE], 4, pad=(24, 24, 32, 24)),
    ])

    logos = [con([image(B.client_logo(c["slug"])[0], c["client"], href=B.case_href(c), h=72, fit="contain")],
                 w=100 / 6, pad=(24, 16, 24, 16), ai="center", jc="center")
             for c in D.CASES if B.client_logo(c["slug"])]
    trust = section([con([label("Clients who trust us")], ai="center"),
                     con(logos, row=True, stack=False, wrap=True, jc="center", ai="center", gap_=0)],
                    bg="canvas", gap_=32)

    res = section([con([res_left(), con([counters_row([(v, w) for _, v, w in D.HOME_RESULTS], dark=True)], w=66)],
                       row=True, gap_=48)], bg="ink", border=False)

    lead, _, rest = D.ABOUT["intro"][0].partition(". ")
    who = section([split([label("Who we are")],
                         [heading(lead + ".", "h2", "ink"), text(escape(rest), "body", "ink72", max_w=620),
                          alink("Learn more about us", "about.html")], wl=30)])

    first = next(c for c in D.CASES if c["slug"] == D.HOME_RESULTS[0][0])
    rest_cases = [c for c in D.CASES if c is not first]
    featured = con([
        con([label("%s · %s" % (first["discipline"], first["sector"]), light=True),
             counter(D.HOME_RESULTS[0][1], D.HOME_RESULTS[0][2], role="display", dark=True)],
            w=45, bg="scarlet", jc="space-between", gap_=48, pad=(40, 40, 40, 40)),
        con([label("Featured case study"), heading(first["title"], "h3", "ink", "h3"),
             text(escape(first["summary"]), "body", "ink72"), alink("Read the story", B.case_href(first))],
            w=55, jc="center", gap_=20, pad=(40, 40, 40, 40)),
    ], row=True, gap_=0, border=dict(t=1, l=1, r=1, b=1))
    rows = [con([text("%02d" % (i + 2), "tag", "scarlet"),
                 heading(c["title"], "h3", "ink", "h3", href=B.case_href(c))],
                row=True, stack=False, ai="center", gap_=24, border=dict(b=1), pad=(24, 0, 24, 0))
            for i, c in enumerate(rest_cases)]
    work = section([sec_head("Selected work", "Mandates that moved the conversation.",
                             ("All case studies", "case-studies.html")), featured, con(rows)])

    strip = ["full-room", "cohort-closeup", "guest-speaker", "cohort-applause", "cohort-attentive",
             "cohort-kente", "facilitator-presenting"]
    carousel = W("image-carousel", S(
        carousel=[{"id": "", "url": img_url("assets/img/academy/%s.jpg" % n)} for n in strip],
        slides_to_show="4", slides_to_show_tablet="3", slides_to_show_mobile="2", slides_to_scroll="1",
        autoplay="yes", autoplay_speed=3500, infinite="yes", navigation="none", image_stretch="yes",
        image_spacing="custom", image_spacing_custom=px(0), thumbnail_size="large"))
    programmes = con([
        con([con([text("Through SKOT Impact Academy and SKOT Elevate, we help emerging talent, professionals, "
                       "entrepreneurs and organisations build the practical skills, strategic insight and "
                       "confidence they need to communicate, lead and grow with impact.", "body", "on_dark64")],
                 w=34),
             con([heading("SKOT Programmes brings together SKOT Communications&rsquo; learning, talent "
                          "development and capability-building platforms.", "h2", "on_dark"),
                  button("View our programmes", "programmes.html", "scarlet", arrow=False)], w=66, gap_=32)],
            row=True, boxed=True, gap_=64, pad=pads((112, 80, 60)), bg="teal"),
        con([carousel], bg="teal"),
    ], bg="teal")

    blog = section([
        sec_head("Blog &amp; insights", "See what we&rsquo;ve been up to.", ("Go to insights", "insights.html")),
        posts_widget(3),
    ], bg="panel", border=False)

    return [hero, rail, what, trust, res, who, method_section(), work, programmes, blog]


def res_left():
    return con([label("Recent results", light=True), heading("Proof, not promises.", "h2", "on_dark"),
                text("Measured across print, broadcast, online and social, on live campaigns for our clients.",
                     "body", "on_dark64", max_w=420)], w=34, gap_=16)


def posts_widget(n, exclude_current=False):
    s = S(_skin="classic", posts_post_type="post", posts_per_page=n, classic_posts_per_page=n,
          classic_columns="3", classic_columns_tablet="2", classic_columns_mobile="1",
          classic_show_excerpt="yes", classic_excerpt_length=22, classic_meta_data=["date"],
          classic_show_read_more="yes", classic_read_more_text="Read the article →",
          classic_thumbnail="medium_large", classic_item_ratio=px(.66), classic_title_tag="h3",
          pagination_type="numbers" if n > 6 else "", _css_classes="skot-posts")
    if exclude_current:
        s["posts_exclude"] = ["current_post"]
    s.col("classic_title_color", "ink").ty("classic_title_typography", "h4")
    s.col("classic_excerpt_color", "ink72").ty("classic_excerpt_typography", "small")
    s.col("classic_meta_color", "ink56").ty("classic_meta_typography", "tag")
    s["classic_card_bg_color"] = "#FBFBF9"
    s["classic_card_border_width"] = dim(1)
    s.col("classic_card_border_color", "line")
    return W("posts", s)


def about():
    intro = paras(D.ABOUT["intro"], role="lead", color="ink72")
    vm = grid([[label("Vision"), heading(D.ABOUT["vision"], "h4", "ink", "p")],
               [label("Mission"), heading(D.ABOUT["mission"], "h4", "ink", "p")]], 2, pad=(40, 40, 40, 40))
    duo = con([
        con([image("assets/img/exp-public.jpg", D.EXPERTISE[1]["alt"], h=540)], w=50),
        con([text("Our work sits at the intersection of strategy, communications and reputation — across "
                  "regulators, government, investors, media and the communities our clients operate in. From "
                  "corporate and brand narratives to public affairs, digital influence and reputation under "
                  "pressure.", "lead", "ink72"), alink("See our expertise", "expertise.html")],
            w=50, jc="flex-end", gap_=20, pad=(48, 48, 48, 48)),
    ], row=True, boxed=True, gap_=0, border=dict(t=1, b=1))
    clients = []
    for c in D.CASES:
        logo = B.client_logo(c["slug"])
        clients.append([image(logo[0], c["client"], h=72, fit="contain") if logo else heading(c["client"], "h4"),
                        label(c["sector"]), heading(c["client"], "h4", "ink", "h3", href=B.case_href(c)),
                        alink("Read the story", B.case_href(c), small=True)])
    return [
        page_hero("About", "Shaping how organisations are understood.",
                  "A strategic communications and reputation management consultancy with a strong "
                  "Sub-Saharan Africa focus.", ("Talk to our team", "contact.html")),
        bleed("assets/img/exp-corporate.jpg", D.EXPERTISE[0]["alt"]),
        section([split([label("Who we are")], [intro], wl=30)], border=False),
        con([vm], boxed=True, pad=pads((0, 0, 0), (48, 32, 18)), bg="canvas"),
        duo,
        section([sec_head("Who we work with", "Organisations with<br>something at stake.",
                          ("Read the case studies", "case-studies.html")), grid(clients, 3)]),
        method_section(),
    ]


def expertise_index():
    cards = [[image_box(e["image"], e["title"], e["lede"], B.exp_href(e), alt=e["alt"], h=240),
              alink("Explore", B.exp_href(e))] for e in D.EXPERTISE]
    return [
        page_hero("Expertise", "Define what you stand for. Communicate it with confidence.",
                  "Specialised teams working across strategy, storytelling, stakeholder engagement, digital "
                  "influence and reputation management — delivering advisory support with measurable impact.",
                  ("Talk to our team", "contact.html")),
        section([grid(cards, 2, pad=(24, 24, 32, 24))]),
        method_section(),
    ]


def expertise_page(e):
    rel = [c for c in D.CASES if c["discipline"].split()[0].lower() in e["title"].lower()][:2]
    if len(rel) < 2:
        rel = (rel + [c for c in D.CASES if c not in rel])[:2]
    caps = [con([con([heading(n, "h4", "ink", "h3")], w=35), con([text(d, "body", "ink72")], w=65)],
                row=True, gap_=48, border=dict(b=1), pad=(28, 0, 28, 0)) for n, d in e["capabilities"]]
    sibs = [button(o["short"], B.exp_href(o), "ghost", arrow=True, small=True) for o in D.EXPERTISE
            if o["slug"] != e["slug"]]
    return [
        page_hero("Expertise", e["title"], e["lede"], ("Talk to our team", "contact.html")),
        bleed(e["image"], e["alt"]),
        section([split([label("Our view")], [heading(e["body"], "h4", "ink", "p")], wl=30)]),
        section([sec_head("Capabilities", "What this covers."), con(caps, border=dict(t=1))]),
        section([sec_head("Related work", "This discipline, in practice.", ("All case studies", "case-studies.html")),
                 grid([case_card(c) for c in rel], 2),
                 split([label("More expertise")], [con(sibs, row=True, stack=False, wrap=True, gap_=8)], wl=30)],
                border=False),
    ]


def case_index():
    stats = [("526M+", "Estimated reach"), ("105", "Media mentions"), ("21.87M", "Impressions"),
             ("100%", "Positive sentiment")]
    return [
        page_hero("Our work", "Strategic discipline, applied to the moments that matter.",
                  "We partner with clients to communicate with purpose, act with clarity and build stronger "
                  "relationships with the stakeholders who shape their success.", ("See how we deliver", "#cases")),
        con([counters_row(stats)], boxed=True, border=dict(b=1), bg="canvas"),
        section([heading("Browse the work.", "h3", "ink", "h2"), grid([case_card(c) for c in D.CASES], 3)],
                border=False, css_id="cases"),
    ]


def case_page(c):
    logo = B.client_logo(c["slug"])
    mark = image(logo[0], c["client"], h=220, fit="contain") if logo else heading(c["client"], "display", "ink", "h2")
    metrics = (counters_row(c["metrics"]) if c["metrics"]
               else grid([[label("Impact"), text(escape(c["qualitative"]), "body", "ink72")]], 1))

    def block(title_, kids):
        return con([con([heading(title_, "h3", "ink", "h2")], w=30),
                    con(kids, w=70, gap_=16)], row=True, gap_=64, border=dict(t=1), pad=(48, 0, 48, 0))

    nxt = [o for o in D.CASES if o["slug"] != c["slug"]][:2]
    return [
        page_hero("Case study", c["title"], escape(c["summary"]),
                  extra=[label("Client"), text(escape(c["client"]), "ui", "ink")]),
        con([mark, spectrum()], bg="panel", gap_=0, ai="stretch",
            pad={"d": (64, 32, 0, 32), "m": (40, 18, 0, 18)}, boxed=False),
        con([metrics], boxed=True, border=dict(b=1)),
        section([
            block("The challenge", [text(c["challenge"], "body", "ink72")]),
            block("Our approach", [paras(c["approach"], role="body", color="ink72")]),
            block("The impact", [text(c["impact"], "body", "ink72")]),
            block("The SKOT contribution", [con([text(c["contribution"], "h4", "ink")],
                                               border=dict(l=3, color="scarlet"), pad=(4, 0, 4, 24))]),
        ], border=False, gap_=0),
        section([sec_head("Next", "More selected work.", ("All case studies", "case-studies.html")),
                 grid([case_card(o) for o in nxt], 2)], border=False),
    ]


def insights_index():
    search = W("search-form", S(skin="classic", placeholder="Search insights", _css_classes="skot-search"))
    return [
        page_hero("Insights", "Perspectives on reputation, influence and communications in a changing world.",
                  "We examine reputation, public affairs, crisis preparedness, digital influence, leadership "
                  "communication and the evolving expectations placed on businesses and institutions across "
                  "Sub-Saharan Africa and beyond.", ("Talk to our team", "contact.html")),
        section([con([heading("Browse insights.", "h3", "ink", "h2"), search], row=True, jc="space-between",
                     ai="center", gap_=24), posts_widget(9)], border=False),
    ]


def single_post():
    meta = W("post-info", S(
        icon_list=[{"_id": "pi_date", "type": "date", "text_prefix": "Published ", "date_format": "default",
                    "show_icon": "none"},
                   {"_id": "pi_cat", "type": "terms", "taxonomy": "category", "text_prefix": "Category: ",
                    "show_icon": "none"},
                   {"_id": "pi_time", "type": "time", "show_icon": "none"}],
        view="inline", _css_classes="skot-post-meta").col("text_color", "ink72").ty("text_typography", "tag"))
    share = W("share-buttons", S(share_buttons=[{"button": "linkedin", "_id": "sb_li"}, {"button": "email", "_id": "sb_em"}],
                                 view="text", skin="flat", columns="2", _css_classes="skot-share"))
    title = W("theme-post-title", S(header_size="h1", _css_classes="skot-article-title").col("title_color", "ink")
              .ty("typography", "display"))
    excerpt = W("theme-post-excerpt", S().col("text_color", "ink72").ty("typography", "lead"))
    featured = W("theme-post-featured-image", S(image_size="full", _css_classes="skot-article-image"))
    content = W("theme-post-content", S().col("text_color", "ink").ty("typography", "read"))
    return [
        con([label("Insights"), title, excerpt], boxed=True, gap_=24, border=dict(b=1), bg="canvas",
            pad=pads((96, 64, 48))),
        con([featured, spectrum()], gap_=0),
        section([con([con([label("Share"), share, meta], w=26, gap_=20),
                      con([content], w=74)], row=True, gap_=64)], border=False),
        section([sec_head("Keep reading", "More insights.", ("All insights", "insights.html")),
                 posts_widget(3, exclude_current=True)], border=False, bg="panel"),
    ]


def programmes_index():
    duos = []
    for i, p in enumerate(D.PROGRAMMES):
        facts = grid([fact(v, l, role="h4") for v, l in p["facts"]], len(p["facts"]), pad=(20, 20, 20, 20))
        copy = con([label(p["badge"]), heading(p["name"], "h2"), text(escape(p["lede"]), "lead", "ink72"), facts,
                    con([button("Learn more", B.prog_href(p), "solid", arrow=True),
                         alink(p["cta"], "contact.html")], row=True, stack=False, ai="center", gap_=20)],
                   w=50, gap_=22, jc="center", pad=(56, 48, 56, 48))
        media = con([image(p["image"], p["alt"], h=560)], w=50)
        duos.append(con([media, copy] if i % 2 else [copy, media], row=True, boxed=True, gap_=0,
                        border=dict(b=1)))
    return [
        page_hero("Programmes", "Capability, built deliberately.",
                  "SKOT Programmes brings together our learning, talent development and capability-building "
                  "platforms — for emerging talent, established professionals and the organisations they serve.",
                  ("Register interest", "contact.html")),
        *duos,
        section([split([label("Why we run them")],
                       [heading("The communications talent gap is a reputation risk — for every organisation in "
                                "the market.", "h2"),
                        text("Our programmes exist to close it: practical, accessible, industry-relevant learning "
                             "that gives emerging African communications professionals the skills and the network "
                             "to practise at a high standard.", "body", "ink72", max_w=620)], wl=30)], border=False),
    ]


def programme_page(p):
    academy = p["slug"] == "impact-academy"
    facts = (grid([fact(v, l, dark=True) for v, l in p["facts"]], 2, pad=(28, 28, 28, 28), color="line_dark", bg="teal")
             if academy else grid([fact(v, l) for v, l in p["facts"]], 1, pad=(24, 0, 24, 0)))
    return [
        page_hero("Programmes", p["name"], escape(p["lede"]),
                  (p["cta"], "contact.html", "teal" if academy else "scarlet")),
        bleed(p["image"], p["alt"], h=520),
        section([split([label("About the programme", teal=academy), text(escape(p["body"]), "h4", "ink")],
                       [facts], wl=48)]),
        *(academy_sections() if academy else masterclass_section()),
    ]


def academy_sections():
    mods = [[text("%02d" % (i + 1), "tag", "teal"), heading(t, "h4", "ink", "h3")]
            for i, t in enumerate(D.ACADEMY_LEARN)]
    mods.append([alink("Apply for the next cohort", "contact.html", accent=False)])
    how = [("Practical exercises", "Build strategies and analyse real campaigns.", "cohort-attentive"),
           ("Peer learning", "Guided group discussions with fellow early-career professionals.", "cohort-closeup"),
           ("Interactive workshops", "Led by industry practitioners, with role-play, scenario planning and live feedback.",
            "facilitator-presenting")]
    pillars = [[image("assets/img/academy/%s.jpg" % n, t, h=280), text("%02d" % (i + 1), "tag", "teal"),
                heading(t, "h4", "ink", "h3"), text(d, "small", "ink72")] for i, (t, d, n) in enumerate(how)]
    band = [("full-room", "In session"), ("cohort-applause", "Peer learning"), ("cohort-kente", "Facilitator-led")]
    mosaic = con([con([image("assets/img/academy/%s.jpg" % n, cap, h=320), text(cap, "tag", "on_dark64")], w=100 / 3,
                      gap_=10) for n, cap in band], row=True, gap_=16)
    return [
        section([split([label("Who it’s for", teal=True)], [heading(D.ACADEMY_WHO, "h4", "ink", "p")], wl=30)]),
        section([split([label("What you’ll learn", teal=True)],
                       [heading("The PR Foundation Course.", "h2"), text(escape(D.ACADEMY_COURSE), "body", "ink72",
                                                                       max_w=620)], wl=30),
                 grid(mods, 4, pad=(24, 24, 24, 24))]),
        section([split([label("How you’ll learn", teal=True)],
                       [heading("Practical, shared and led by practitioners.", "h2")], wl=30),
                 grid(pillars, 3, pad=(24, 24, 32, 24))]),
        section([label("Inside the Academy", light=True), heading("Learning. Leading. Growing.", "h2", "on_dark"),
                 mosaic], bg="teal_deep", border=False),
        con([con([image("assets/img/academy/embrace.jpg", "Two members of the Academy community sharing an embrace",
                        h=520)], w=50),
             con([label("Next cohort", light=True),
                  heading("Start your PR journey with <span style=\"color:#D6001C\">SKOT Impact Academy.</span>",
                          "h2", "on_dark"),
                  button("Apply for the next cohort", "contact.html", "light")],
                 w=50, jc="center", gap_=24, pad=(56, 56, 56, 56))],
            row=True, gap_=0, bg="teal_deep", css="skot-acad-cta"),
    ]


def masterclass_section():
    topics = grid([[heading(t, "h4", "ink", "p")] for t in D.MASTERCLASS["topics"]], 3, pad=(28, 28, 28, 28))
    return [section([split([label("Under SKOT Elevate"), heading("Masterclass.", "h2")],
                           [text(D.MASTERCLASS["body"], "lead", "ink72"), alink("Register interest", "contact.html")],
                           wl=30), topics], border=False, css_id="masterclass")]


def contact():
    fields = [
        {"_id": "name", "custom_id": "name", "field_type": "text", "field_label": "Name", "required": "true",
         "width": "50", "placeholder": ""},
        {"_id": "email", "custom_id": "email", "field_type": "email", "field_label": "Email", "required": "true",
         "width": "50", "placeholder": ""},
        {"_id": "company", "custom_id": "company", "field_type": "text", "field_label": "Company", "width": "50",
         "placeholder": ""},
        {"_id": "subject", "custom_id": "subject", "field_type": "select", "field_label": "This is about",
         "required": "true", "width": "50",
         "field_options": "New business enquiry|New business\nMedia & press|Media & press\n"
                          "Programmes & training|Programmes & training\nCrisis support|Crisis support\n"
                          "General enquiry|General enquiry"},
        {"_id": "message", "custom_id": "message", "field_type": "textarea", "field_label": "Message",
         "required": "true", "width": "100", "rows": 5, "placeholder": ""},
    ]
    form = S(form_name="Contact", form_fields=fields, show_labels="true", label_position="above",
             mark_required="", button_text="Send message", button_size="md", button_width="auto",
             submit_actions=["email"], email_to=D.SITE["email"], email_subject="Website enquiry: [field id=\"subject\"]",
             email_content="[all-fields]", email_from_name="SKOT website", email_reply_to="[field id=\"email\"]",
             email_content_type="plain", success_message="Thank you. We will come back to you shortly.",
             field_background_color="#FBFBF9", field_border_color="#E3E0DA", field_border_width=dim(1),
             field_border_radius=dim(0), button_background_color="#111315", button_text_color="#FBFBF9",
             button_border_radius=dim(0), _css_classes="skot-form")
    form.col("label_color", "ink72").ty("label_typography", "tag").col("field_text_color", "ink").ty("field_typography", "body")
    form.ty("button_typography", "button")
    maps = W("google_maps", S(address="NIJ House, 20 Adeyemo Alakija, Victoria Island, Lagos, Nigeria",
                              zoom=px(15), height=px(460), _css_classes="skot-map"))
    return [
        page_hero("Get in touch", "Let's define your voice.",
                  "Tell us what you are facing. We will tell you plainly whether we are the right firm for it."),
        section([split([label("Send a message"), heading("Tell us about the mandate.", "h2"),
                        text("Give us the shape of it — the situation, the stakeholder and the timeline — and "
                             "the right desk will come back to you directly.", "body", "ink72", max_w=420),
                        alink("%s" % D.SITE["email"], "mailto:" + D.SITE["email"]),
                        alink(D.SITE["phone"], "tel:" + D.SITE["phone_href"])],
                       [W("form", form)], wl=40)], border=False),
        con([con([label("Headquarters"), heading("Victoria Island, Lagos.", "h2"),
                  text("<br>".join(D.SITE["address"]) + "<br>Nigeria", "body", "ink72"),
                  alink("Get directions", "https://maps.google.com/?q=NIJ+House,20+Adeyemo+Alakija,Victoria+Island,Lagos,Nigeria")],
                 w=50, jc="center", gap_=20, pad=(56, 48, 56, 48)),
             con([maps], w=50)], row=True, boxed=True, gap_=0, border=dict(t=1)),
    ]


# ══ Theme Builder parts ═══════════════════════════════════════════════════════════════════════
def header():
    logo = image("assets/img/skot-mark.png", "SKOT Communications", href="index.html", w=100)
    logo["settings"]["_element_width"] = "initial"
    logo["settings"]["_element_custom_width"] = px(110)
    nav = W("nav-menu", S(menu="skot-primary", layout="horizontal", align_items="center", pointer="underline",
                          animation_line="fade", submenu_icon={"value": "fas fa-chevron-down", "library": "fa-solid"},
                          toggle="burger", dropdown="tablet", full_width="stretch", _css_classes="skot-nav")
            .col("color_menu_item", "ink72").col("color_menu_item_hover", "ink").col("pointer_color_hover", "scarlet")
            .ty("menu_typography", "ui"))
    cta = button("Talk to our team", "contact.html", "solid", arrow=False, small=True)
    bar = con([con([logo], w=15, ai="flex-start", jc="center"), con([nav], w=65, jc="center"),
               con([cta], w=20, ai="flex-end", jc="center")],
              row=True, stack=False, ai="center", jc="space-between", gap_=16, boxed=True, bg="canvas",
              border=dict(b=1), pad={"d": (10, 48, 10, 48), "t": (10, 32, 10, 32), "m": (10, 18, 10, 18)},
              tag="header", css="skot-header", sticky="top", sticky_on=["desktop", "tablet", "mobile"],
              sticky_offset=0)
    return [bar]


def footer():
    rows = [("New business enquiry", "New%20business%20enquiry"), ("Media & press", "Media%20%26%20press"),
            ("Programmes & training", "Programmes%20%26%20training"), ("Crisis & issues support", "Crisis%20support")]
    triggers = con([con([alink(t, "mailto:%s?subject=%s" % (D.SITE["email"], q), dark=True)],
                        border=dict(b=1, color="line_dark"), pad=(18, 0, 18, 0)) for t, q in rows], w=45)
    top = con([con([label("Get in touch", light=True), heading("Let's define your voice.", "title", "on_dark", "h2")],
                   w=55, gap_=20), triggers], row=True, gap_=48)

    def detail(k, v):
        return [text(k, "tag", "on_dark64"), text(v, "body", "on_dark")]
    details = grid([detail("Headquarters", "<br>".join(D.SITE["address"])),
                    detail("Email", '<a href="mailto:%s">%s</a>' % (D.SITE["email"], D.SITE["email"])),
                    detail("Telephone", '<a href="tel:%s">%s</a>' % (D.SITE["phone_href"], D.SITE["phone"])),
                    detail("Follow", '<a href="%s" target="_blank" rel="noopener">LinkedIn</a><br>'
                                     '<a href="%s" target="_blank" rel="noopener">Instagram</a>' % (D.SITE["linkedin"], D.SITE["instagram"]))],
                   4, pad=(24, 24, 24, 0), color="line_dark")
    contact_band = con([top, details], boxed=True, bg="ink", gap_=64, pad=pads((100, 80, 60)),
                       css="skot-contact-band")

    def col(title_, items):
        links = W("icon-list", S(
            icon_list=[{"_id": "il%d" % i, "text": t, "link": link(h), "selected_icon": {"value": "", "library": ""}}
                       for i, (t, h) in enumerate(items)], view="traditional", space_between=px(10),
            _css_classes="skot-footer-links")
            .col("text_color", "on_dark64").col("text_color_hover", "on_dark").ty("icon_typography", "small"))
        return con([text(title_, "tag", "on_dark64"), links], w=18, gap_=16)

    exp = [(e["short"], B.exp_href(e)) for e in D.EXPERTISE]
    work = [("Our work", "case-studies.html")] + [(c["client"], B.case_href(c)) for c in D.CASES[:3]]
    firm = [("About us", "about.html"), ("Programmes", "programmes.html")] + \
           [(p["name"], B.prog_href(p)) for p in D.PROGRAMMES] + [("Get in touch", "contact.html")]
    brand = con([image("assets/img/skot-logo-light.png", "SKOT Communications", w=60),
                 text("Exclusive Nigerian partner of PROI Worldwide, the fourth largest PR network in the world.",
                      "xs", "on_dark38", max_w=300)], w=46, gap_=18)
    cols = con([brand, col("Expertise", exp), col("Work", work), col("Firm", firm)], row=True, gap_=32)
    base = con([text("© 2026 SKOT Communications. All rights reserved.", "xs", "on_dark38"),
                text("Strategic communications &amp; reputation management · Lagos, Nigeria", "xs", "on_dark38")],
               row=True, jc="space-between", gap_=12, border=dict(t=1, color="line_dark"), pad=(24, 0, 0, 0))
    footer_ = con([cols, base], boxed=True, bg="ink", gap_=48, pad=pads((48, 40, 32)), tag="footer",
                  css="skot-footer")
    return [contact_band, spectrum(), footer_]


# ══ Kit settings (site-settings.json) ═════════════════════════════════════════════════════════
KIT_CSS = """/* SKOT kit: section label ring, hairlines and small interactions (Site Settings > Custom CSS) */
.skot-label .elementor-heading-title{display:flex;align-items:center;gap:.7rem}
.skot-label .elementor-heading-title::before{content:"";flex:none;width:9px;height:9px;border:2px solid var(--e-global-color-primary);border-radius:50%;box-sizing:border-box}
.skot-label--light .elementor-heading-title::before{border-color:var(--e-global-color-on_dark)}
.skot-label--teal .elementor-heading-title::before{border-color:var(--e-global-color-accent)}
.skot-alink .elementor-button{padding:0!important;border:0;box-shadow:none}
.skot-alink .elementor-button-icon,.skot-btn .elementor-button-icon{transition:transform .28s cubic-bezier(.22,.61,.36,1)}
.skot-alink .elementor-button:hover .elementor-button-icon,.skot-btn .elementor-button:hover .elementor-button-icon{transform:translateX(3px)}
.skot-btn .elementor-button{border-radius:0}
.skot-card .elementor-image-box-img img{width:100%;object-fit:cover}
.skot-card:hover{background:var(--e-global-color-panel)}
.skot-card a{color:inherit}
.skot-counter .elementor-counter-number-wrapper{font-variant-numeric:tabular-nums}
.skot-phero>.e-con-inner>.e-con:last-child{border-left:1px solid var(--e-global-color-line)}
.skot-posts .elementor-post{border:1px solid var(--e-global-color-line)}
.skot-header{z-index:50}
.skot-footer-links .elementor-icon-list-icon{display:none}
.skot-form .elementor-field-group .elementor-field{padding:12px 14px}
@media (max-width:1024px){.skot-phero>.e-con-inner>.e-con:last-child{border-left:0;border-top:1px solid var(--e-global-color-line)}}
"""


def site_settings():
    def sys_color(k):
        gid, title_, val = COLOR[k]
        return {"_id": gid, "title": title_.split(" (")[0], "color": val}

    def typo_entry(role):
        gid, title_, fam, wt, sz, lh, ls, tt = TYPE[role]
        e = S(_id=gid, title=title_.split(" (")[0])
        e.ty("typography", role)
        e.pop("__globals__", None)
        return dict(e)

    s = S()
    s["system_colors"] = [sys_color(k) for k in ("scarlet", "ink", "text", "teal")]
    s["custom_colors"] = [{"_id": v[0], "title": v[1], "color": v[2]} for k, v in COLOR.items()
                          if v[0] not in SYSTEM_COLOR_IDS]
    s["system_typography"] = [typo_entry(r) for r, t in TYPE.items() if t[0] in ("primary", "secondary", "text", "accent")]
    s["custom_typography"] = [typo_entry(r) for r, t in TYPE.items() if t[0] not in ("primary", "secondary", "text", "accent")]
    s["default_generic_fonts"] = "Sans-serif"
    s["container_width"] = px(1400)
    s["space_between_widgets"] = gap(0)
    s["viewport_md"] = 768
    s["viewport_lg"] = 1025
    s["page_title_selector"] = "h1.entry-title"
    s["background_background"] = "classic"
    s.col("background_color", "canvas")
    s.col("body_color", "text").ty("body_typography", "body")
    for h, role in (("h1", "title"), ("h2", "h2"), ("h3", "h3"), ("h4", "h4"), ("h5", "h5"), ("h6", "h5")):
        s.col("%s_color" % h, "ink").ty("%s_typography" % h, role)
    s.col("link_normal_color", "ink").col("link_hover_color", "scarlet")
    s.col("button_text_color", "canvas").col("button_background_color", "ink").ty("button_typography", "button")
    s["button_border_radius"] = dim(0)
    s["button_padding"] = dim(14, 24)
    s["custom_css"] = KIT_CSS
    return {"settings": dict(s)}


# ══ Packaging ════════════════════════════════════════════════════════════════════════════════
def doc(title_, kind, content, page_settings=None):
    return {"content": content, "page_settings": page_settings if page_settings is not None else [],
            "version": "0.4", "title": title_, "type": kind}


PAGE_SETTINGS = {"template": "elementor_header_footer", "hide_title": "yes"}


def templates():
    """(key, title, elementor doc type, envato type, content, page_settings)"""
    out = [
        ("header", "Header", "header", "section", header(), None),
        ("footer", "Footer", "footer", "section", footer(), None),
        ("single-post", "Single Post", "single-post", "section", single_post(), None),
        ("home", "Home", "page", "page", home(), PAGE_SETTINGS),
        ("about", "About", "page", "page", about(), PAGE_SETTINGS),
        ("expertise", "Expertise", "page", "page", expertise_index(), PAGE_SETTINGS),
    ]
    out += [(B.exp_href(e)[:-5], e["short"] + " (Expertise)", "page", "page", expertise_page(e), PAGE_SETTINGS)
            for e in D.EXPERTISE]
    out.append(("case-studies", "Case Studies", "page", "page", case_index(), PAGE_SETTINGS))
    out += [(B.case_href(c)[:-5], c["client"] + " (Case study)", "page", "page", case_page(c), PAGE_SETTINGS)
            for c in D.CASES]
    out += [("insights", "Insights", "page", "page", insights_index(), PAGE_SETTINGS),
            ("programmes", "Programmes", "page", "page", programmes_index(), PAGE_SETTINGS)]
    out += [(B.prog_href(p)[:-5], p["name"] + " (Programme)", "page", "page", programme_page(p), PAGE_SETTINGS)
            for p in D.PROGRAMMES]
    out.append(("contact", "Contact", "page", "page", contact(), PAGE_SETTINGS))
    return out


README = """SKOT Communications - Elementor Pro Template Kit v{ver}
=====================================================

Requires: WordPress 6.x, Elementor {elv}+ and Elementor Pro (Theme Builder, Form, Nav Menu,
Posts, Search Form, Post widgets). Flexbox Containers must be on (default from Elementor 3.16).
Recommended theme: Hello Elementor.

Contents
--------
manifest.json        template index (Envato-style `source` entries and Elementor kit fields)
site-settings.json   Global Colors, Global Fonts, theme style and Custom CSS
templates/           one Elementor document per page + Theme Builder parts
images/              every image the templates reference (backup; see "Images")

Install
-------
1. Install and activate Elementor, Elementor Pro and the Hello Elementor theme.
2. Elementor > Tools > Import/Export Kit > Import this zip. (Or import the .json files in
   templates/ individually from Templates > Saved Templates > Import Templates; apply
   site-settings.json through Site Settings.)
3. Create a menu named "SKOT Primary" (slug skot-primary) and assign it to nothing; the Header
   Nav Menu widget uses it. Structure: About / Expertise (4 sub-items) / Case studies / Insights /
   Programmes (SKOT Impact Academy, SKOT Elevate, Masterclass -> /programmes-elevate/#masterclass).
4. Templates > Theme Builder: set display conditions - Header: Entire Site, Footer: Entire Site,
   Single Post: All Posts.
5. Create a WordPress Page for each page template using the same slug as the template file
   (home, about, expertise, expertise-corporate-brand, case-studies, case-gitex-nigeria,
   insights, programmes, programmes-impact-academy, contact, ...), insert the template, and set
   Settings > Reading: Homepage = Home, Posts page = Insights.
6. Import your articles as normal WordPress posts; the Insights page and Single Post template
   read them through the Posts widget.

Images
------
Templates link to {base}.
Elementor downloads these into the Media Library on import. If that URL is not reachable for you,
upload the files in images/ to the Media Library and re-pick them, or rebuild the kit with
python3 elementor-kit/build_kit.py --asset-base https://your-domain.

Mapping notes
-------------
- Typography weights 510/590/680 are 500/600/700 here (Elementor uses whole hundreds).
- The home hero uses the poster image; add the video under Container > Background > Video.
- The expertise tab switcher, case-study filter chips and the hero marquee are not native Elementor
  features; they are a card grid, a plain grid and a link row respectively.
- Contact form posts by e-mail via the Form widget (Actions After Submit > Email).
"""


def main():
    items = templates()
    dist = os.path.join(HERE, "dist")
    os.makedirs(dist, exist_ok=True)
    today = datetime.date.today().isoformat()

    manifest_templates = {}
    files = {}
    for key, title_, dtype, etype, content, ps in items:
        files["templates/%s.json" % key] = doc(title_, dtype, content, ps)
        manifest_templates[key] = {
            "id": key, "name": title_, "title": title_, "doc_type": dtype, "type": etype,
            "source": "templates/%s.json" % key, "screenshot": "", "thumbnail": False, "preview_url": "",
            "date": today, "metadata": {"template_type": dtype, "elementor_pro_required": True},
        }

    manifest = {
        "manifest_version": "1.0.0", "version": "2.0", "kit_version": KIT_VERSION,
        "name": "skot-communications", "title": "SKOT Communications",
        "description": "Strategic communications consultancy kit: home, about, expertise, case studies, insights, "
                       "programmes, contact, header, footer and single post.",
        "author": "SKOT Communications", "page_builder": "elementor", "elementor_version": ELEMENTOR_VERSION,
        "created": today, "thumbnail": False, "site": "https://skotcomms.com",
        "plugins": [
            {"name": "Elementor", "plugin": "elementor/elementor", "pluginUri": "https://elementor.com/", "version": ELEMENTOR_VERSION},
            {"name": "Elementor Pro", "plugin": "elementor-pro/elementor-pro", "pluginUri": "https://elementor.com/pro/", "version": ELEMENTOR_VERSION},
        ],
        "site-settings": {"theme": False, "globalColors": True, "globalFonts": True, "themeStyleSettings": True,
                          "generalSettings": True, "experiments": False},
        "templates": manifest_templates,
    }

    out = os.path.join(dist, "skot-template-kit.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        z.writestr("site-settings.json", json.dumps(site_settings(), indent=2, ensure_ascii=False))
        z.writestr("readme.txt", README.format(ver=KIT_VERSION, elv=ELEMENTOR_VERSION, base=ASSET_BASE))
        for name, d in files.items():
            z.writestr(name, json.dumps(d, indent=2, ensure_ascii=False))
        for rel in sorted(USED_IMAGES):
            z.write(os.path.join(ROOT, rel), "images/" + rel[len("assets/img/"):])
    print("wrote %s (%d templates, %d images, %.1f MB)" % (out, len(files), len(USED_IMAGES),
                                                         os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
