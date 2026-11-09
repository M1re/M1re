"""Generates the animated SVG assets for the M1re profile README.

Run:  python gen.py      -> writes assets/*.svg and preview.html
"""
import random
from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#0A0A0B"
GRID = "#17171A"
ACID = "#C8FF00"
PINK = "#FF2E88"
ORANGE = "#FF5A1F"
CYAN = "#00E5FF"
WHITE = "#E8E8E2"
DIM = "#7C7C78"
MONO = "'JetBrains Mono','Cascadia Mono',Consolas,'DejaVu Sans Mono',Menlo,monospace"

GLYPHS = {
    "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def block_text(text, x, y, cell, gap=2, advance=6):
    """Blocky stencil lettering built from rects, so no font is needed."""
    out = []
    for i, ch in enumerate(text):
        for r, row in enumerate(GLYPHS[ch]):
            for c, v in enumerate(row):
                if v == "X":
                    out.append(
                        f'<rect x="{x + (i * advance + c) * cell}" y="{y + r * cell}" '
                        f'width="{cell - gap}" height="{cell - gap}"/>'
                    )
    return "".join(out)


def barcode(x, y, w, h, seed, color):
    rnd = random.Random(seed)
    out, cx = [], x
    while cx < x + w:
        bw = rnd.choice([1, 1, 2, 2, 3, 4])
        if rnd.random() > 0.35:
            out.append(f'<rect x="{cx}" y="{y}" width="{bw}" height="{h}" fill="{color}"/>')
        cx += bw + rnd.choice([1, 2, 2, 3])
    return "".join(out)


def brackets(x, y, w, h, l=18, color=ACID, sw=2):
    p = [
        f"M{x},{y + l}V{y}H{x + l}",
        f"M{x + w - l},{y}H{x + w}V{y + l}",
        f"M{x + w},{y + h - l}V{y + h}H{x + w - l}",
        f"M{x + l},{y + h}H{x}V{y + h - l}",
    ]
    return f'<path d="{" ".join(p)}" fill="none" stroke="{color}" stroke-width="{sw}"/>'


def svg(w, h, body, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<style>text{{font-family:{MONO}}}{css}</style>{body}</svg>"
    )


def grid_pattern(pid, size=40):
    return (
        f'<pattern id="{pid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">'
        f'<path d="M{size} 0H0V{size}" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>'
    )


def hazard_pattern(pid, color=ACID):
    return (
        f'<pattern id="{pid}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="7" height="14" fill="{color}"/></pattern>'
    )


# ---------------------------------------------------------------- banner
def banner():
    W, H = 1200, 440
    cell = 22
    title = block_text("M1RE", 70, 92, cell)
    stack = "C# /// .NET /// ASP.NET CORE /// REACT /// TYPESCRIPT /// DOCKER /// KAFKA /// RABBITMQ /// REDIS /// MONGODB /// MS SQL /// "
    ticker = esc(stack * 3)
    css = f"""
    .blink{{animation:blink 1.1s steps(2,start) infinite}}
    @keyframes blink{{to{{visibility:hidden}}}}
    .scan{{animation:scan 5s linear infinite}}
    @keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY({H}px)}}}}
    .ticker{{animation:tick 28s linear infinite}}
    @keyframes tick{{from{{transform:translateX(0)}}to{{transform:translateX(-{len(stack) * 9.6:.1f}px)}}}}
    .g1{{animation:g1 3.2s steps(1) infinite}}
    .g2{{animation:g2 3.2s steps(1) infinite}}
    @keyframes g1{{0%,86%,100%{{transform:translate(0,0);opacity:0}}87%{{transform:translate(-7px,2px);opacity:.9}}90%{{transform:translate(5px,-3px);opacity:.9}}93%{{transform:translate(-3px,0);opacity:.9}}96%{{opacity:0}}}}
    @keyframes g2{{0%,86%,100%{{transform:translate(0,0);opacity:0}}88%{{transform:translate(6px,-2px);opacity:.9}}91%{{transform:translate(-5px,3px);opacity:.9}}94%{{transform:translate(4px,1px);opacity:.9}}97%{{opacity:0}}}}
    .main{{animation:jit 3.2s steps(1) infinite}}
    @keyframes jit{{0%,86%,100%{{transform:none}}89%{{transform:translateX(3px)}}92%{{transform:translateX(-2px)}}}}
    .bar{{animation:fill 2.4s cubic-bezier(.2,.8,.2,1) both}}
    @keyframes fill{{from{{transform:scaleX(0)}}}}
    .beam{{animation:beam 2.6s ease-in-out infinite alternate}}
    @keyframes beam{{from{{transform:translateX(0)}}to{{transform:translateX(300px)}}}}
    """
    bars = []
    stats = [("C#/.NET", 0.92, ACID), ("BACKEND", 0.85, ACID), ("REACT/TS", 0.62, PINK), ("DEVOPS", 0.48, ORANGE)]
    for i, (name, v, col) in enumerate(stats):
        y = 190 + i * 30
        bars.append(
            f'<text x="800" y="{y + 10}" font-size="12" fill="{DIM}" letter-spacing="2">{esc(name)}</text>'
            f'<rect x="920" y="{y}" width="220" height="12" fill="#1C1C20"/>'
            f'<rect class="bar" style="transform-origin:920px 0;animation-delay:{0.3 + i * 0.25}s" '
            f'x="920" y="{y}" width="{220 * v:.0f}" height="12" fill="{col}"/>'
        )
    body = f"""
    <defs>{grid_pattern("g")}{hazard_pattern("hz")}
      <clipPath id="reveal"><rect x="60" y="80" width="0" height="170">
        <animate attributeName="width" from="0" to="620" dur="1.1s" begin="0.2s" fill="freeze"
          calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect></clipPath>
      <linearGradient id="sl" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0" stop-color="{ACID}" stop-opacity="0"/><stop offset="1" stop-color="{ACID}" stop-opacity=".16"/></linearGradient>
    </defs>
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#g)"/>
    <rect x="0" y="0" width="12" height="{H}" fill="{ACID}"/>

    <text x="40" y="44" font-size="13" fill="{DIM}" letter-spacing="3">SECTOR 04 // KYIV-UA // 50.4501N 30.5234E</text>
    <text x="1160" y="44" font-size="13" fill="{DIM}" letter-spacing="3" text-anchor="end">RUNNER-ID: M1RE-2020-0917</text>
    <rect x="40" y="58" width="1120" height="1" fill="#2A2A2F"/>

    <g clip-path="url(#reveal)">
      <g class="g1" fill="{PINK}">{title}</g>
      <g class="g2" fill="{CYAN}">{title}</g>
      <g class="main" fill="{ACID}">{title}</g>
    </g>

    <text x="72" y="292" font-size="30" font-weight="700" fill="{WHITE}" letter-spacing="8">VLADYSLAV KONOKH</text>
    <rect x="72" y="310" width="330" height="34" fill="{PINK}"/>
    <text x="86" y="333" font-size="16" font-weight="700" fill="{BG}" letter-spacing="3">.NET SOFTWARE ENGINEER</text>
    <text x="72" y="370" font-size="13" fill="{DIM}" letter-spacing="2">// BACKEND · DISTRIBUTED SYSTEMS · REACT</text>

    {brackets(780, 84, 380, 270)}
    <text x="800" y="116" font-size="12" fill="{ACID}" letter-spacing="3">RUNNER PROFILE</text>
    <g class="blink"><circle cx="1050" cy="112" r="5" fill="{ACID}"/></g>
    <text x="1140" y="116" font-size="12" fill="{ACID}" letter-spacing="3" text-anchor="end">ONLINE</text>
    <text x="800" y="146" font-size="12" fill="{DIM}" letter-spacing="2">CLASS</text>
    <text x="920" y="146" font-size="12" fill="{WHITE}" letter-spacing="2">.NET ENGINEER</text>
    <text x="800" y="168" font-size="12" fill="{DIM}" letter-spacing="2">BASE</text>
    <text x="920" y="168" font-size="12" fill="{WHITE}" letter-spacing="2">KYIV // UA</text>
    {"".join(bars)}
    <g>{barcode(800, 316, 300, 26, 41, WHITE)}</g>
    <rect class="beam" x="800" y="312" width="3" height="34" fill="{PINK}"/>
    <text x="1140" y="338" font-size="10" fill="{DIM}" text-anchor="end">0917</text>

    <rect x="0" y="384" width="{W}" height="40" fill="{ACID}"/>
    <rect x="12" y="384" width="110" height="40" fill="{BG}"/>
    <rect x="18" y="390" width="98" height="28" fill="url(#hz)"/>
    <svg x="130" y="384" width="{W - 130}" height="40">
      <g class="ticker"><text x="0" y="27" font-size="16" font-weight="700" fill="{BG}" letter-spacing="0">{ticker}</text></g>
    </svg>

    <g class="scan"><rect x="12" y="0" width="{W}" height="40" fill="url(#sl)"/></g>
    """
    return svg(W, H, body, css)


# ---------------------------------------------------------------- section dividers
def divider(idx, label, code, accent):
    W, H = 1200, 64
    css = """
    .run{animation:run 3.4s linear infinite}
    @keyframes run{from{transform:translateX(0)}to{transform:translateX(560px)}}
    .blink{animation:blink 1.1s steps(2,start) infinite}
    @keyframes blink{to{visibility:hidden}}
    """
    body = f"""
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect x="0" y="12" width="64" height="40" fill="{accent}"/>
    <text x="32" y="40" font-size="22" font-weight="700" fill="{BG}" text-anchor="middle">{idx:02d}</text>
    <text x="84" y="42" font-size="26" font-weight="700" fill="{WHITE}" letter-spacing="6">// {esc(label)}</text>
    <rect x="420" y="31" width="560" height="2" fill="#2A2A2F"/>
    <rect class="run" x="420" y="29" width="60" height="6" fill="{accent}"/>
    <rect x="980" y="24" width="2" height="16" fill="{accent}"/>
    <text x="1000" y="30" font-size="11" fill="{DIM}" letter-spacing="2">{esc(code)}</text>
    {barcode(1000, 38, 140, 12, idx, DIM)}
    <rect class="blink" x="1150" y="38" width="10" height="12" fill="{accent}"/>
    """
    return svg(W, H, body, css)


# ---------------------------------------------------------------- contract cards
def contract(num, name, desc_lines, tags, status, accent, progress):
    W, H = 580, 250
    css = f"""
    .blink{{animation:blink 1.1s steps(2,start) infinite}}
    @keyframes blink{{to{{visibility:hidden}}}}
    .prog{{animation:prog 4s ease-in-out infinite}}
    @keyframes prog{{0%{{transform:scaleX(0)}}60%,100%{{transform:scaleX(1)}}}}
    """
    desc = "".join(
        f'<text x="28" y="{122 + i * 20}" font-size="13" fill="{DIM}">{esc(l)}</text>' for i, l in enumerate(desc_lines)
    )
    tx, chips = 28, []
    for t in tags:
        w = len(t) * 8 + 18
        chips.append(
            f'<rect x="{tx}" y="178" width="{w}" height="22" fill="none" stroke="{accent}"/>'
            f'<text x="{tx + w / 2}" y="193" font-size="11" fill="{accent}" text-anchor="middle" letter-spacing="1">{esc(t)}</text>'
        )
        tx += w + 8
    body = f"""
    <defs>{hazard_pattern("hz" + num, accent)}</defs>
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="none" stroke="#2A2A2F"/>
    <rect x="0" y="0" width="{W}" height="36" fill="{accent}"/>
    <text x="20" y="24" font-size="13" font-weight="700" fill="{BG}" letter-spacing="3">CONTRACT // {num}</text>
    <rect x="{W - 150}" y="8" width="130" height="20" fill="{BG}"/>
    <rect class="blink" x="{W - 142}" y="14" width="8" height="8" fill="{accent}"/>
    <text x="{W - 128}" y="23" font-size="11" fill="{accent}" letter-spacing="2">{esc(status)}</text>
    <text x="28" y="86" font-size="30" font-weight="700" fill="{WHITE}" letter-spacing="2">{esc(name)}</text>
    {desc}
    {"".join(chips)}
    <text x="28" y="232" font-size="10" fill="{DIM}" letter-spacing="2">SYNC</text>
    <rect x="70" y="224" width="380" height="8" fill="#1C1C20"/>
    <rect class="prog" style="transform-origin:70px 0" x="70" y="224" width="{380 * progress:.0f}" height="8" fill="{accent}"/>
    <rect x="470" y="214" width="90" height="22" fill="url(#hz{num})"/>
    """
    return svg(W, H, body, css)


# ---------------------------------------------------------------- loadout
def loadout():
    slots = [
        ("PRIMARY", [("C#", ACID), (".NET", ACID), ("ASP.NET CORE", ACID)]),
        ("FRONTEND", [("REACT", CYAN), ("TYPESCRIPT", CYAN)]),
        ("DATA", [("MS SQL", ORANGE), ("MONGODB", ORANGE), ("REDIS", ORANGE)]),
        ("MESSAGING", [("KAFKA", PINK), ("RABBITMQ", PINK)]),
        ("INFRA", [("DOCKER", WHITE), ("POWERSHELL", WHITE)]),
    ]
    W, rowh = 1200, 60
    H = 40 + len(slots) * rowh + 20
    css = """
    .in{animation:in .5s cubic-bezier(.2,.8,.2,1) both}
    @keyframes in{from{opacity:0;transform:translateX(-24px)}}
    .sweep{animation:sweep 4.5s linear infinite}
    @keyframes sweep{from{transform:translateY(0)}to{transform:translateY(300px)}}
    """
    rows, n = [], 0
    for r, (cat, items) in enumerate(slots):
        y = 30 + r * rowh
        rows.append(
            f'<text x="24" y="{y + 30}" font-size="12" fill="{DIM}" letter-spacing="3">{cat}</text>'
            f'<rect x="180" y="{y + 26}" width="20" height="1" fill="#2A2A2F"/>'
        )
        x = 210
        for name, col in items:
            n += 1
            w = 300
            rows.append(
                f'<g class="in" style="animation-delay:{0.08 * n:.2f}s">'
                f'<rect x="{x}" y="{y + 6}" width="{w}" height="42" fill="#121215" stroke="#2A2A2F"/>'
                f'<rect x="{x}" y="{y + 6}" width="5" height="42" fill="{col}"/>'
                f'<text x="{x + 18}" y="{y + 33}" font-size="15" font-weight="700" fill="{WHITE}" letter-spacing="2">{esc(name)}</text>'
                f'<text x="{x + w - 10}" y="{y + 20}" font-size="9" fill="{DIM}" text-anchor="end">S{n:02d}</text>'
                f"</g>"
            )
            x += w + 14
    body = f"""
    <defs><linearGradient id="sw" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="{ACID}" stop-opacity="0"/><stop offset="1" stop-color="{ACID}" stop-opacity=".08"/></linearGradient></defs>
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {brackets(6, 6, W - 12, H - 12, 22, "#3A3A40")}
    {"".join(rows)}
    <g class="sweep"><rect x="0" y="-30" width="{W}" height="30" fill="url(#sw)"/></g>
    """
    return svg(W, H, body, css)


files = {
    "banner.svg": banner(),
    "div-about.svg": divider(1, "ABOUT", "SEC.01 — PROFILE.DAT", ACID),
    "div-contracts.svg": divider(2, "CONTRACTS", "SEC.02 — ACTIVE OPS", PINK),
    "div-loadout.svg": divider(3, "LOADOUT", "SEC.03 — GEAR.CFG", CYAN),
    "div-telemetry.svg": divider(4, "TELEMETRY", "SEC.04 — SIGNAL.LOG", ORANGE),
    "contract-vault.svg": contract(
        "0x01", "ENGINEERING VAULT",
        ["Public knowledge base on what a staff engineer", "should understand deeply. Obsidian → Quartz."],
        ["OBSIDIAN", "QUARTZ", "GH PAGES"], "ACTIVE", ACID, 0.78,
    ),
    "contract-priority.svg": contract(
        "0x02", "HIGH PRIORITY",
        ["Pins HighPriority CPU class to a chosen app", "and keeps it there. Set once, forget."],
        ["POWERSHELL", "WINDOWS"], "SHIPPED", PINK, 1.0,
    ),
    "loadout.svg": loadout(),
}
for name, content in files.items():
    (ASSETS / name).write_text(content, encoding="utf-8")

# Local preview: README is plain HTML, so wrap it in GitHub-dark chrome.
readme = (ROOT / "README.md").read_text(encoding="utf-8")
(ROOT / "preview.html").write_text(
    "<!doctype html><meta charset=utf-8><title>README preview</title>"
    "<style>body{background:#0d1117;color:#e6edf3;font:16px -apple-system,Segoe UI,sans-serif;margin:0}"
    "main{max-width:980px;margin:24px auto;padding:32px;border:1px solid #30363d;border-radius:6px}"
    "img{max-width:100%}a{color:#4493f8}</style><main>" + readme + "</main>",
    encoding="utf-8",
)
print("ok:", ", ".join(files))
