#!/usr/bin/env python3
"""Render the profile README cards as animated SVGs.

    python scripts/build_cards.py      animated cards        -> cards/
    STATIC=1 (same command)            final frame, no motion -> preview/static/

Both modes also write a local preview page (preview/index.html or
preview/static.html) that lays the cards out exactly like README.md.

Input:  data/github.json, refreshed daily by .github/workflows/cards.yml
Needs:  pip install fonttools brotli
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC", "") not in ("", "0")
OUT = ROOT / ("preview/static" if STATIC else "cards")

# --------------------------------------------------------------------------
# Content. Edit here.
# --------------------------------------------------------------------------
NAME = "Sam Obila Allela"
GREETING = "Hi, I am"
LOGO = "[S.A]"
LINE = "Data scientist and AI engineer from Nairobi, Kenya, who learns by building things."
PORTRAIT = ROOT / "data/portrait.jpg"  # optional: delete the file to drop it

TILES = [  # one tile per entry, file name cards/tile-<slug>.svg
    dict(slug="portfolio", kicker="Website", title="Portfolio", detail="sam-obila-allela.vercel.app"),
    dict(slug="linkedin", kicker="Network", title="LinkedIn", detail="in/sam-allela"),
    dict(slug="medium", kicker="Writing", title="Medium", detail="@obilasam3"),
]

FEATURED = [  # one card per entry, file name cards/repo-<slug>.svg
    dict(slug="solagent", repo="SolAgent", title="SolAgent",
         blurb="Autonomous AI agent designed to manage Solana crypto wallets using natural language processing."),
    dict(slug="meshfix", repo="MeshFix", title="MeshFix",
         blurb="Intelligent automated tool optimization pipeline for data restructuring and geometric normalization."),
    dict(slug="studybot", repo="pyforge-labs", path="studybot", title="Study Bot",
         blurb="Intelligent assistant built with Google SDK for AI-driven insights."),
]

# Colours and fonts, taken from sam-obila-allela.vercel.app
INK = "#111111"
PAPER = "#f5f4f0"
GRAY = "#e8e7e3"
TAUPE = "#d4cfc9"
MUTED = "#555555"
BRAND = INK  # the contribution graph ramps from paper to this colour

FACES = {  # key: (family, weight, file in fonts/)
    "syne600": ("Syne", 600, "Syne-600.ttf"),
    "syne800": ("Syne", 800, "Syne-800.ttf"),
    "dm300": ("DM Sans", 300, "DMSans-300.ttf"),
    "dm400": ("DM Sans", 400, "DMSans-400.ttf"),
    "dm500": ("DM Sans", 500, "DMSans-500.ttf"),
}

# Seconds before each card starts, so the page plays top to bottom.
T_HERO, T_TILES, T_ACTIVITY, T_REPOS, T_GRAPH = 0.0, 0.6, 1.1, 1.9, 2.5

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
EASE = "cubic-bezier(.16,1,.3,1)"  # the site's easing

ANIM_CSS = (
    f".a{{animation:.8s {EASE} both}}"
    ".up{animation-name:up}.lf{animation-name:lf}.rt{animation-name:rt}"
    ".fd{animation-name:fd}.gy{animation-name:gy}.ro{animation-name:ro}"
    ".dr{animation-name:dr;stroke-dasharray:1}"
    ".nd{animation:nd 5s ease-in-out infinite}"
    # Every keyframe only says where an element comes *from*; its resting
    # state is the plain markup, which is exactly what STATIC=1 emits.
    "@keyframes up{from{opacity:0;transform:translateY(16px)}}"
    "@keyframes lf{from{opacity:0;transform:translateX(-40px)}}"
    "@keyframes rt{from{opacity:0;transform:translateX(40px)}}"
    "@keyframes fd{from{opacity:0}}"
    "@keyframes gy{from{transform:scaleY(0)}}"
    "@keyframes ro{from{transform:translateY(var(--o))}}"
    "@keyframes dr{from{stroke-dashoffset:1}}"
    "@keyframes nd{0%,80%,to{transform:translate(0,0)}90%{transform:translate(2px,-2px)}}"
    # SMIL cannot be switched off from CSS, so SMIL-animated shapes (.mo)
    # ship with a still twin (.st) and reduced motion swaps them.
    ".st{display:none}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
    ".mo{display:none}.st{display:inline}}"
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def n(v: float) -> str:
    """Short number for SVG attributes."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def mix(a: str, b: str, t: float) -> str:
    """Blend hex colour a towards b by t (0..1)."""
    pa, pb = (int(a[i:i + 2], 16) for i in (1, 3, 5)), (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


_metrics: dict[str, tuple[dict, dict, int]] = {}


def advance(ch: str, face: str) -> float:
    """Advance width of one character, in em."""
    if face not in _metrics:
        font = TTFont(ROOT / "fonts" / FACES[face][2])
        _metrics[face] = (font.getBestCmap(), font["hmtx"].metrics, font["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[face]
    if ord(ch) not in cmap:
        sys.exit(f"{FACES[face][2]} has no glyph for {ch!r}")
    return hmtx[cmap[ord(ch)]][0] / upm


def width(s: str, face: str, size: float, ls: float = 0) -> float:
    """Rendered width of a string in px (ls = letter-spacing in em)."""
    return sum(advance(c, face) + ls for c in s) * size


def wrap(s: str, face: str, size: float, max_w: float, max_lines: int = 2) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and width(trial, face, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        while width(last + "…", face, size) > max_w:
            last = last.rsplit(" ", 1)[0]
        lines = lines[:max_lines - 1] + [last.rstrip(",.;") + "…"]
    return lines


_subset_cache: dict[tuple[str, str], str] = {}


def subset_woff2(face: str, chars: str) -> str:
    """Subset one font to the given characters with pyftsubset -> base64 WOFF2."""
    key = (face, chars)
    if key not in _subset_cache:
        exe = shutil.which("pyftsubset")
        cmd = [exe] if exe else [sys.executable, "-m", "fontTools.subset"]  # same program
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "subset.woff2"
            subprocess.run(
                cmd + [
                    str(ROOT / "fonts" / FACES[face][2]),
                    "--unicodes=" + ",".join(f"U+{ord(c):04X}" for c in chars),
                    "--flavor=woff2",
                    "--no-hinting",
                    "--no-recalc-timestamp",  # keeps output identical between runs
                    f"--output-file={out}",
                ],
                check=True,
            )
            _subset_cache[key] = base64.b64encode(out.read_bytes()).decode()
    return _subset_cache[key]


class Card:
    """Collects SVG markup plus the characters each font needs."""

    def __init__(self, name: str, w: int, h: int, bg: str, t0: float, label: str):
        self.name, self.w, self.h, self.bg, self.t0, self.label = name, w, h, bg, t0, label
        self.body: list[str] = []
        self.defs: list[str] = []
        self.used: dict[str, set[str]] = defaultdict(set)

    def add(self, *markup: str) -> None:
        self.body.extend(markup)

    def text(self, x, y, s, face, size, fill, ls=0.0, anchor="start", attrs="") -> str:
        self.used[face].update(s)
        out = f'<text class="{face}" x="{n(x)}" y="{n(y)}" font-size="{n(size)}" fill="{fill}"'
        if ls:
            out += f' letter-spacing="{n(ls * size)}"'
        if anchor != "start":
            out += f' text-anchor="{anchor}"'
        return f"{out}{attrs}>{escape(s)}</text>"

    def g(self, inner: str, anim: str, delay: float, dur: float | None = None, style: str = "") -> str:
        """Wrap markup in an animated group. In STATIC mode it is returned bare."""
        if STATIC:
            return inner
        css = f"animation-delay:{n(self.t0 + delay)}s"
        if dur:
            css += f";animation-duration:{n(dur)}s"
        return f'<g class="a {anim}" style="{css}{style}">{inner}</g>'

    def smil(self, still: str, moving: str) -> str:
        """SMIL-animated markup with the still twin shown under reduced motion."""
        if STATIC:
            return still
        return f'<g class="mo">{moving}</g><g class="st">{still}</g>'

    def arrow(self, cx: float, cy: float, delay: float, stroke: str = INK) -> str:
        """The site's round icon button, holding a north-east arrow."""
        ring = (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="15" fill="none" stroke="{stroke}" '
                f'stroke-opacity=".35" stroke-width="1.5" pathLength="1" '
                f'transform="rotate(-90 {n(cx)} {n(cy)})"/>')
        head = (f'<path d="M{n(cx - 4.5)} {n(cy + 4.5)}L{n(cx + 4.5)} {n(cy - 4.5)}M{n(cx - 2.5)} {n(cy - 4.5)}'
                f'H{n(cx + 4.5)}V{n(cy + 2.5)}" fill="none" stroke="{stroke}" stroke-width="1.6" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
        if STATIC:
            return ring + head
        ring = ring.replace("<circle", f'<circle class="a dr" style="animation-delay:{n(self.t0 + delay)}s"')
        nudge = f'<g class="nd" style="animation-delay:{n(self.t0 + delay + 2)}s">{head}</g>'
        return ring + self.g(nudge, "fd", delay + 0.3)

    def odometer(self, x, y, value: str, face, size, fill, delay, ls=-0.02) -> float:
        """A number whose digits roll up from 0. Returns the width it takes."""
        cid = f"od{len(self.defs)}"
        pitch = size * 1.15
        self.defs.append(f'<clipPath id="{cid}"><rect x="{n(x - 4)}" y="{n(y - size * 0.86)}" '
                         f'width="{n(width(value, face, size, ls) + 8)}" height="{n(size * 1.1)}"/></clipPath>')
        cols, cx = [], x
        for i, ch in enumerate(value):
            w = (advance(ch, face) + ls) * size
            mid = cx + w / 2
            final = self.text(mid, y, ch, face, size, fill, anchor="middle")
            if ch.isdigit() and int(ch) and not STATIC:
                d = int(ch)
                strip = "".join(self.text(mid, y + (d - j) * pitch, str(j), face, size, fill, anchor="middle")
                                for j in range(d + 1))
                final = self.g(strip, "ro", delay + i * 0.08, 1.2, style=f";--o:{n(-d * pitch)}px")
            cols.append(final)
            cx += w
        self.add(f'<g clip-path="url(#{cid})">{"".join(cols)}</g>')
        return cx - x

    def render(self) -> str:
        css = ""
        for face in sorted(self.used):
            family, weight, _ = FACES[face]
            b64 = subset_woff2(face, "".join(sorted(self.used[face])))
            css += (f"@font-face{{font-family:'{family}';font-weight:{weight};"
                    f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
                    f".{face}{{font-family:'{family}',Arial,sans-serif;font-weight:{weight}}}")
        if not STATIC:
            css += ANIM_CSS
        label = escape(self.label)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-label="{label}">'
            f"<title>{label}</title><style>{css}</style>"
            f'<defs><clipPath id="card"><rect width="{self.w}" height="{self.h}" rx="4"/></clipPath>'
            f'{"".join(self.defs)}</defs>'
            f'<g clip-path="url(#card)"><rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>'
            f'{"".join(self.body)}</g></svg>\n'
        )


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def load() -> dict:
    path = ROOT / "data/github.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cal = data["contributionsCollection"]["contributionCalendar"]
    except (OSError, ValueError, TypeError, KeyError) as err:
        sys.exit(f"{path} is missing or not the expected shape ({err!r}); nothing rendered.")
    weeks = [[dict(date=date.fromisoformat(d["date"]), count=d["contributionCount"],
                   level=LEVELS.index(d["contributionLevel"])) for d in w["contributionDays"]]
             for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    if not days:
        sys.exit(f"{path} holds no contribution days; nothing rendered.")

    # Streaks. A day that is still in progress does not break the current one.
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    tail = days[:-1] if days[-1]["count"] == 0 else days
    current = 0
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1

    months: dict[tuple[int, int], int] = {}
    for d in days:
        key = (d["date"].year, d["date"].month)
        months[key] = months.get(key, 0) + d["count"]
    if days[0]["date"].day != 1 and len(months) > 12:
        del months[next(iter(months))]  # the window opens mid-month: drop that stub

    return dict(
        login=data["login"], total=cal["totalContributions"], weeks=weeks, days=days,
        months=months, current=current, longest=longest,
        active=sum(1 for d in days if d["count"]),
        busiest=max(days, key=lambda d: d["count"]),
        repos={r["name"]: r for r in data["repositories"]["nodes"]},
    )


# --------------------------------------------------------------------------
# Cards
# --------------------------------------------------------------------------
def hero() -> Card:
    W, H = 840, 320
    c = Card("hero", W, H, INK, T_HERO, f"{NAME}. {LINE}")

    # Right, dark half: the portrait, or the site's ghost word when there is none.
    if not PORTRAIT.exists():
        c.add(c.g(c.text(W + 26, H + 24, "DATA", "syne800", 150, "#ffffff", ls=-0.05, anchor="end",
                         attrs=' fill-opacity=".04"'), "rt", 0.1))
    else:
        pw, ph = 204, 272
        px, py = 675 - pw / 2, H - ph
        b64 = base64.b64encode(PORTRAIT.read_bytes()).decode()
        c.defs.append(f'<clipPath id="photo"><path d="M{n(px)} {H}V{n(py + 4)}a4 4 0 0 1 4-4h{pw - 8}'
                      f'a4 4 0 0 1 4 4V{H}z"/></clipPath>')
        c.add(c.g(f'<g clip-path="url(#photo)"><rect x="{n(px)}" y="{n(py)}" width="{pw}" height="{ph}" '
                  f'fill="#222222"/><image href="data:image/jpeg;base64,{b64}" x="{n(px)}" y="{n(py)}" '
                  f'width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin slice"/></g>', "up", 0.3, 1.0))

    # Left, light half with the site's slanted edge.
    c.add(c.g(f'<polygon points="0,0 548,0 470,{H} 0,{H}" fill="{GRAY}"/>', "lf", 0))
    c.add(c.g(c.text(44, 62, LOGO, "syne800", 25, INK, ls=-0.04), "fd", 0.3))
    c.add(c.g(c.text(44, 162, GREETING, "dm300", 19, MUTED), "up", 0.25))
    size = min(46, 400 / width(NAME, "syne800", 1, -0.03))
    c.add(c.g(c.text(43, 210, NAME, "syne800", size, INK, ls=-0.03), "up", 0.35))
    for i, line in enumerate(wrap(LINE, "dm400", 15, 395)):
        c.add(c.g(c.text(44, 246 + i * 22, line, "dm400", 15, MUTED), "up", 0.5 + i * 0.08))
    return c


def tile(i: int, t: dict) -> Card:
    W, H = 280, 108
    c = Card(f"tile-{t['slug']}", W, H, TAUPE, T_TILES + i * 0.12, f"{t['title']}: {t['detail']}")
    c.add(c.g(c.text(22, 34, t["kicker"].upper(), "dm500", 10.5, "#444444", ls=0.18), "up", 0))
    c.add(c.g(c.text(21, 68, t["title"], "syne800", 23, INK, ls=-0.02), "up", 0.08))
    c.add(c.g(c.text(22, 89, t["detail"], "dm400", 12.5, "#444444"), "up", 0.16))
    c.add(c.arrow(W - 37, 37, 0.25))
    return c


def activity(d: dict) -> Card:
    W, H = 840, 320
    soft = ' fill-opacity=".6"'
    busy = d["busiest"]
    c = Card("activity", W, H, INK, T_ACTIVITY,
             f"Contributions per month. Current streak {d['current']} days, longest {d['longest']}. "
             f"{d['active']} active days of {len(d['days'])}. Busiest day {busy['count']} contributions "
             f"on {busy['date'].day} {MONTHS[busy['date'].month - 1]} {busy['date'].year}.")
    c.add(c.g(c.text(44, 50, "CONTRIBUTIONS PER MONTH", "syne600", 11.5, PAPER, ls=0.18), "up", 0))

    when = f"{busy['date'].day} {MONTHS[busy['date'].month - 1]} {busy['date'].year}"
    rows = [
        (str(d["current"]), "day" if d["current"] == 1 else "days", f"Current streak · longest {d['longest']}"),
        (str(d["active"]), f"of {len(d['days'])}", "Active days"),
        (str(busy["count"]), "contributions", f"Busiest day · {when}"),
    ]
    for i, (value, unit, label) in enumerate(rows):
        y, delay = 118 + i * 72, 0.15 + i * 0.12
        c.body.append("" if STATIC else f'<g class="a fd" style="animation-delay:{n(c.t0 + delay)}s">')
        w = c.odometer(44, y, value, "syne800", 36, PAPER, delay)
        c.add(c.text(44 + w + 8, y, unit, "dm400", 14, PAPER, attrs=soft))
        c.add(c.text(44, y + 21, label.upper(), "dm500", 10.5, PAPER, ls=0.14, attrs=soft))
        c.body.append("" if STATIC else "</g>")

    # Monthly bars: one series, so one colour, every bar labelled with its value.
    months = list(d["months"].items())
    x0, x1, base, hmax, bw = 336, 796, 262, 148, 22
    step = (x1 - x0) / len(months)
    top = max(max(v for _, v in months), 1)
    still, moving, labels = "", "", ""
    for i, ((year, month), total) in enumerate(months):
        x = x0 + i * step + (step - bw) / 2
        h = max(total / top * hmax, 2) if total else 0
        rect = f'<rect x="{n(x)}" y="{n(base - h)}" width="{bw}" height="{n(h)}" rx="2" fill="{PAPER}"'
        still += rect + "/>"
        wait, dur = c.t0 + 0.3 + i * 0.05, 0.9
        timing = (f'dur="{n(wait + dur)}s" keyTimes="0;{n(wait / (wait + dur))};1" calcMode="spline" '
                  f'keySplines="0 0 1 1;.16 1 .3 1" fill="freeze"')
        moving += (f'{rect}><animate attributeName="height" values="0;0;{n(h)}" {timing}/>'
                   f'<animate attributeName="y" values="{base};{base};{n(base - h)}" {timing}/></rect>')
        mid = x + bw / 2
        labels += c.g(c.text(mid, base - h - 8, str(total), "dm500", 11.5, PAPER, anchor="middle"),
                      "fd", 0.75 + i * 0.05, 0.5)
        tick = c.text(mid, base + 20, MONTHS[month - 1], "dm500", 11, PAPER, anchor="middle", attrs=soft)
        if i == 0 or month == 1:
            tick += c.text(mid, base + 35, str(year), "dm400", 10.5, PAPER, anchor="middle", attrs=soft)
        labels += c.g(tick, "fd", 0.2 + i * 0.03, 0.5)
    c.add(f'<rect x="{x0}" y="{base}" width="{x1 - x0}" height="1" fill="{PAPER}" fill-opacity=".25"/>')
    c.add(c.smil(still, moving), labels)
    return c


def repo(i: int, f: dict, d: dict) -> Card:
    W, H = 840, 140
    info = d["repos"].get(f["repo"]) or sys.exit(f"Featured repo {f['repo']!r} is not in data/github.json")
    blurb = f.get("blurb") or info["description"] or ""
    c = Card(f"repo-{f['slug']}", W, H, GRAY, T_REPOS + i * 0.15, f"{f['title']}. {blurb}")
    c.add(c.g(f'<rect width="6" height="{H}" fill="{INK}"/>', "gy", 0, 0.9))
    trail = " / ".join(filter(None, [d["login"], f["repo"], f.get("path")])).upper()
    c.add(c.g(c.text(44, 40, trail, "dm500", 10.5, MUTED, ls=0.16), "lf", 0.05))
    c.add(c.g(c.text(43, 76, f["title"], "syne800", 27, INK, ls=-0.03), "lf", 0.12))
    lines = "".join(c.text(44, 102 + j * 20, line, "dm400", 14, MUTED)
                    for j, line in enumerate(wrap(blurb, "dm400", 14, 540)))
    c.add(c.g(lines, "lf", 0.2))
    c.add(c.arrow(W - 44 - 15, 40, 0.3))

    # The site's role pill, holding the language; stars only once there are some.
    lang = (info["primaryLanguage"] or {}).get("name")
    meta, right = "", W - 44
    if lang:
        pw = width(lang.upper(), "dm500", 10.5, 0.1) + 26
        meta += (f'<rect x="{n(right - pw)}" y="97" width="{n(pw)}" height="24" rx="12" fill="{INK}"/>'
                 + c.text(right - pw / 2 + 0.5, 113, lang.upper(), "dm500", 10.5, "#ffffff", ls=0.1, anchor="middle"))
        right -= pw + 14
    if info["stargazerCount"]:
        stars = info["stargazerCount"]
        meta += c.text(right, 113.5, f"{stars} star{'s' * (stars != 1)}", "dm500", 12, MUTED, anchor="end")
    c.add(c.g(meta, "fd", 0.4))
    return c


def graph(d: dict) -> Card:
    W, H, x0, y0, pitch, cell = 840, 206, 24, 80, 15, 12
    c = Card("graph", W, H, PAPER, T_GRAPH, f"{d['total']:,} contributions in the last year")
    ramp = [mix(PAPER, BRAND, t) for t in (0.09, 0.3, 0.52, 0.76, 1)]
    c.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="3.5" fill="none" stroke="{ramp[0]}"/>')
    c.add(c.g(c.text(x0, 43, f"{d['total']:,} CONTRIBUTIONS IN THE LAST YEAR", "syne600", 11.5, INK, ls=0.18),
              "up", 0))

    legend, lx = "", W - x0
    legend += c.text(lx, 43, "More", "dm500", 11, MUTED, anchor="end")
    lx -= width("More", "dm500", 11) + 8
    for colour in reversed(ramp):
        lx -= cell
        legend += f'<rect x="{n(lx)}" y="33" width="{cell}" height="{cell}" rx="2.5" fill="{colour}"/>'
        lx -= 3
    legend += c.text(lx - 5, 43, "Less", "dm500", 11, MUTED, anchor="end")
    c.add(c.g(legend, "fd", 0.1))

    last_label = -9
    for w, week in enumerate(d["weeks"]):
        x = x0 + w * pitch
        col = ""
        first = week[0]["date"]
        if w and first.month != d["weeks"][w - 1][0]["date"].month and w - last_label >= 3:
            col += c.text(x, 70, MONTHS[first.month - 1], "dm500", 11, MUTED)
            last_label = w
        for day in week:
            row = (day["date"].weekday() + 1) % 7  # weeks start on Sunday
            col += (f'<rect x="{x}" y="{y0 + row * pitch}" width="{cell}" height="{cell}" rx="2.5" '
                    f'fill="{ramp[day["level"]]}"/>')
        c.add(c.g(col, "up", 0.15 + w * 0.02, 0.6))
    return c


# --------------------------------------------------------------------------
def write_preview() -> None:
    """README.md is plain HTML, so the preview is the README itself."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    src = "static/" if STATIC else "../cards/"
    page = ROOT / "preview" / ("static.html" if STATIC else "index.html")
    page.parent.mkdir(exist_ok=True)
    page.write_text(
        '<!doctype html><meta charset="utf-8"><title>Profile preview</title>'
        "<style>body{margin:0;padding:32px 16px;background:#fff;font:16px/1.5 sans-serif}"
        "main{max-width:846px;margin:auto}img{max-width:100%}</style><main>"
        + readme.replace('src="cards/', f'src="{src}') + "</main>\n", encoding="utf-8")
    print(f"preview  {page.relative_to(ROOT).as_posix()}")


def main() -> None:
    d = load()
    cards = [hero(), *(tile(i, t) for i, t in enumerate(TILES)), activity(d),
             *(repo(i, f, d) for i, f in enumerate(FEATURED)), graph(d)]
    OUT.mkdir(parents=True, exist_ok=True)
    keep = set()
    for card in cards:
        path = OUT / f"{card.name}.svg"
        path.write_text(card.render(), encoding="utf-8", newline="\n")
        keep.add(path.name)
        print(f"{path.stat().st_size / 1024:6.1f} kB  {path.relative_to(ROOT).as_posix()}")
    for stale in OUT.glob("*.svg"):  # e.g. a repo removed from FEATURED
        if stale.name not in keep:
            stale.unlink()
            print(f"removed  {stale.relative_to(ROOT).as_posix()}")
    missing = sorted(set(re.findall(r'src="cards/([^"]+)"', (ROOT / "README.md").read_text(encoding="utf-8"))) ^ keep)
    if missing:
        print("warning: README.md and the rendered cards disagree on:", ", ".join(missing))
    write_preview()


if __name__ == "__main__":
    main()
