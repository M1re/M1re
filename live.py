"""Live parts of the profile, rebuilt nightly by .github/workflows/live.yml.

- dist/telemetry.svg   HUD panel from the GitHub GraphQL API
- dist/runner-trace.svg gets the profile background (the snake comes from Platane/snk)
- dist/fieldlog-N.svg  FIELD LOG rows: latest notes from the Engineering Vault
- README.md            FIELD LOG block linking each row to its note

Env:
  GITHUB_TOKEN  token for the GraphQL API
  VAULT_DIR     local clone of M1re/EngineeringVault (field log is skipped without it)
  LIVE_SAMPLE   path to a JSON file used instead of the API (local testing)
"""
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from gen import ACID, BG, CYAN, DIM, ORANGE, PINK, WHITE, brackets, esc, grid_pattern, svg

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
LOGIN = "M1re"
VAULT_SITE = "https://m1re.github.io/EngineeringVault"
OUTPUT_URL = "https://raw.githubusercontent.com/M1re/M1re/output"

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_stats():
    sample = os.environ.get("LIVE_SAMPLE")
    if sample:
        return json.loads(Path(sample).read_text(encoding="utf-8"))
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "m1re-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    # Today is not over yet: an empty today does not break the current streak.
    tail = days[:-1] if days and not days[-1]["contributionCount"] else days
    current = 0
    for d in reversed(tail):
        if not d["contributionCount"]:
            break
        current += 1
    return current, best


def telemetry(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, best = streaks(days)
    repos = user["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)

    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

    counters = [
        ("CONTRIBUTIONS // 1Y", cal["totalContributions"], ACID),
        ("COMMITS // 1Y", user["contributionsCollection"]["totalCommitContributions"], WHITE),
        ("STREAK // NOW", current, PINK),
        ("STREAK // BEST", best, CYAN),
        ("STARS", stars, ORANGE),
    ]
    W, H = 1200, 340
    css = """
    .blink{animation:blink 1.1s steps(2,start) infinite}
    @keyframes blink{to{visibility:hidden}}
    .b{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1.2s cubic-bezier(.2,.8,.2,1) both}
    @keyframes grow{from{transform:scaleY(0)}}
    .l{transform-box:fill-box;transform-origin:0 50%;animation:fill 1.6s cubic-bezier(.2,.8,.2,1) both}
    @keyframes fill{from{transform:scaleX(0)}}
    .c{animation:in .6s ease-out both}
    @keyframes in{from{opacity:0;transform:translateY(8px)}}
    """
    synced = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [
        f'<defs>{grid_pattern("g")}</defs>',
        f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#g)"/>',
        brackets(6, 6, W - 12, H - 12, 22, "#3A3A40"),
        f'<text x="28" y="38" font-size="12" fill="{ACID}" letter-spacing="3">SIGNAL // GITHUB TELEMETRY</text>',
        f'<rect class="blink" x="926" y="29" width="8" height="8" fill="{ACID}"/>',
        f'<text x="1172" y="38" font-size="12" fill="{DIM}" letter-spacing="2" text-anchor="end">LAST SYNC {synced}</text>',
    ]
    for i, (label, value, col) in enumerate(counters):
        x = 28 + i * 232
        out.append(
            f'<g class="c" style="animation-delay:{0.1 * i:.1f}s">'
            f'<rect x="{x}" y="56" width="216" height="92" fill="#121215" stroke="#2A2A2F"/>'
            f'<rect x="{x}" y="56" width="4" height="92" fill="{col}"/>'
            f'<text x="{x + 18}" y="80" font-size="11" fill="{DIM}" letter-spacing="2">{label}</text>'
            f'<text x="{x + 18}" y="130" font-size="40" font-weight="700" fill="{col}">{value:,}</text></g>'
        )

    # Weekly activity, last 26 weeks.
    sums = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks[-26:]]
    peak = max(sums) or 1
    out.append(f'<text x="28" y="186" font-size="11" fill="{DIM}" letter-spacing="2">ACTIVITY // 26 WEEKS</text>')
    for i, s in enumerate(sums):
        h = max(2, round(110 * s / peak))
        col = PINK if s == peak and s else (ACID if s else "#2A2A2F")
        out.append(
            f'<rect class="b" style="animation-delay:{0.03 * i:.2f}s" x="{28 + i * 25}" y="{310 - h}" '
            f'width="19" height="{h}" fill="{col}"/>'
        )

    # Language mix across own repos.
    out.append(f'<text x="720" y="186" font-size="11" fill="{DIM}" letter-spacing="2">LANGUAGE MIX // BY CODE SIZE</text>')
    for i, ((name, size), col) in enumerate(zip(top, [ACID, PINK, CYAN, ORANGE, WHITE])):
        y = 206 + i * 22
        pct = 100 * size / total
        out.append(
            f'<text x="720" y="{y + 10}" font-size="12" fill="{WHITE}" letter-spacing="1">{esc(name.upper())}</text>'
            f'<rect x="860" y="{y}" width="250" height="10" fill="#1C1C20"/>'
            f'<rect class="l" style="animation-delay:{0.15 * i:.2f}s" x="860" y="{y}" '
            f'width="{max(2, 250 * pct / 100):.0f}" height="10" fill="{col}"/>'
            f'<text x="1172" y="{y + 10}" font-size="11" fill="{DIM}" text-anchor="end">{pct:.0f}%</text>'
        )
    return svg(W, H, "".join(out), css)


def restyle_snake(path):
    """Platane/snk leaves the background transparent; paint ours under it."""
    if not path.exists():
        return
    s = path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', s)
    if not m or "data-bg" in s:
        return
    x, y, w, h = m.groups()
    rect = f'<rect data-bg="1" x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}"/>'
    path.write_text(re.sub(r"(<svg[^>]*>)", lambda mm: mm.group(1) + rect, s, count=1), encoding="utf-8")


def field_log(vault_dir, limit=6):
    with urllib.request.urlopen(f"{VAULT_SITE}/static/contentIndex.json", timeout=30) as r:
        index = json.load(r)
    by_path = {v["filePath"]: v for v in index.values()}
    log = subprocess.run(
        ["git", "-C", vault_dir, "-c", "core.quotepath=off", "log",
         "--format=@%cs", "--name-only", "--diff-filter=AM", "--", "Vault"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    rows, seen, day = [], set(), ""
    for line in log.splitlines():
        if line.startswith("@"):
            day = line[1:]
            continue
        rel = line.removeprefix("Vault/")
        note = by_path.get(rel)
        if not note or rel in seen or note["slug"].endswith("index"):
            continue
        seen.add(rel)
        rows.append((day, note))
        if len(rows) == limit:
            break

    # One SVG per row, each wrapped in its own link, so rows stay clickable.
    html = []
    for i, (day, note) in enumerate(rows):
        url = f"{VAULT_SITE}/{urllib.parse.quote(note['slug'], safe='/')}"
        sector = " / ".join(Path(note["filePath"]).parent.parts) or "ROOT"
        (DIST / f"fieldlog-{i + 1}.svg").write_text(log_row(i, day, note["title"], sector), encoding="utf-8")
        html.append(
            f'<a href="{url}"><img src="{OUTPUT_URL}/fieldlog-{i + 1}.svg" '
            f'alt="{day} {esc(note["title"])}" width="100%"/></a>'
        )
    return "\n".join(html)


def log_row(i, day, title, sector):
    W, H = 1200, 60
    col = [ACID, PINK, CYAN, ORANGE, WHITE, ACID][i % 6]
    if len(title) > 44:
        title = title[:43] + "…"
    css = f"""
    .in{{animation:in .5s cubic-bezier(.2,.8,.2,1) {0.12 * i:.2f}s both}}
    @keyframes in{{from{{opacity:0;transform:translateX(-30px)}}}}
    .go{{animation:go 1.6s ease-in-out infinite alternate}}
    @keyframes go{{to{{transform:translateX(6px)}}}}
    """
    body = f"""
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <g class="in">
      <rect x="0" y="6" width="{W}" height="{H - 12}" fill="#121215" stroke="#2A2A2F"/>
      <rect x="0" y="6" width="56" height="{H - 12}" fill="{col}"/>
      <text x="28" y="37" font-size="16" font-weight="700" fill="{BG}" text-anchor="middle">{i + 1:02d}</text>
      <text x="80" y="36" font-size="13" fill="{DIM}" letter-spacing="1">{day}</text>
      <text x="230" y="37" font-size="19" font-weight="700" fill="{WHITE}" letter-spacing="1">{esc(title)}</text>
      <text x="1130" y="35" font-size="11" fill="{DIM}" letter-spacing="2" text-anchor="end">{esc(sector.upper())}</text>
      <text class="go" x="1150" y="36" font-size="15" font-weight="700" fill="{col}">&gt;&gt;</text>
    </g>
    """
    return svg(W, H, body, css)


def update_readme(block):
    readme = ROOT / "README.md"
    s = readme.read_text(encoding="utf-8")
    new = re.sub(
        r"(<!-- FIELD-LOG:START -->).*?(<!-- FIELD-LOG:END -->)",
        lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}",
        s, flags=re.S,
    )
    if new != s:
        readme.write_text(new, encoding="utf-8")
        print("README field log updated")


def main():
    DIST.mkdir(exist_ok=True)
    (DIST / "telemetry.svg").write_text(telemetry(fetch_stats()), encoding="utf-8")
    restyle_snake(DIST / "runner-trace.svg")
    if os.environ.get("VAULT_DIR"):
        update_readme(field_log(os.environ["VAULT_DIR"]))
    print("live: done")


if __name__ == "__main__":
    main()
