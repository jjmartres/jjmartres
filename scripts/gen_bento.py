#!/usr/bin/env python3
"""Generate the bento tiles of the profile README (Catppuccin Latte / Macchiato).

Usage: python3 scripts/gen_bento.py
Writes assets/bento/<tile>-<light|dark>.svg from the logos in assets/, then
refreshes the ?v=<hash> suffix of every tile URL in README.md so GitHub and
browsers never show a cached tile after a change.
"""
import base64
import hashlib
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "bento"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def svg_inner(path):
    s = Path(path).read_text()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = re.sub(r"^.*?<svg[^>]*>", "", s, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner)
    inner = re.sub(r"<title[^>]*>.*?</title>", "", inner, flags=re.S)
    inner = re.sub(r'aria-labelledby="[^"]*"', "", inner)
    return vb, inner


# Catppuccin: Latte (light) and Macchiato (dark) — https://catppuccin.com/palette
CATPPUCCIN = {
    "light": dict(base="#eff1f5", mantle="#e6e9ef", crust="#dce0e8", surface0="#ccd0da", surface1="#bcc0cc",
                  overlay0="#9ca0b0", subtext0="#6c6f85", subtext1="#5c5f77", text="#4c4f69",
                  blue="#1e66f5", lavender="#7287fd", sapphire="#209fb5", teal="#179299", green="#40a02b",
                  yellow="#df8e1d", peach="#fe640b", red="#d20f39", mauve="#8839ef", pink="#ea76cb"),
    "dark": dict(base="#24273a", mantle="#1e2030", crust="#181926", surface0="#363a4f", surface1="#494d64",
                 overlay0="#6e738d", subtext0="#a5adcb", subtext1="#b8c0e0", text="#cad3f5",
                 blue="#8aadf4", lavender="#b7bdf8", sapphire="#7dc4e4", teal="#8bd5ca", green="#a6da95",
                 yellow="#eed49f", peach="#f5a97f", red="#ed8796", mauve="#c6a0f6", pink="#f5bde6"),
}


def palette(theme):
    c = CATPPUCCIN[theme]
    return dict(c, card=c["base"], border=c["surface0"], fg=c["text"], dim=c["subtext0"],
                chip=c["mantle"], chipfg=c["text"])


def canvas_path(w, h, corners, r=22):
    """Rectangle with rounded corners only where the tile touches the grid's outer corner."""
    tl, tr, br, bl = (r if c in corners else 0 for c in ("tl", "tr", "br", "bl"))
    return (f"M{tl} 0H{w - tr}" + (f"A{tr} {tr} 0 0 1 {w} {tr}" if tr else "") +
            f"V{h - br}" + (f"A{br} {br} 0 0 1 {w - br} {h}" if br else "") +
            f"H{bl}" + (f"A{bl} {bl} 0 0 1 0 {h - bl}" if bl else "") +
            f"V{tl}" + (f"A{tl} {tl} 0 0 1 {tl} 0" if tl else "") + "Z")


def tile(w, h, theme, body, defs="", corners=""):
    p = palette(theme)
    g = 6  # half gap: the Catppuccin canvas shows 12px between tiles
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>{defs}<clipPath id="card"><rect x="{g}" y="{g}" width="{w - 2 * g}" height="{h - 2 * g}" rx="16"/></clipPath></defs>
  <path d="{canvas_path(w, h, corners)}" fill="{p['crust']}"/>
  <rect x="{g}" y="{g}" width="{w - 2 * g}" height="{h - 2 * g}" rx="16" fill="{p['card']}"/>
  <g font-family="{SANS}" clip-path="url(#card)">{body}</g>
  <rect x="{g + .5}" y="{g + .5}" width="{w - 2 * g - 1}" height="{h - 2 * g - 1}" rx="16" fill="none" stroke="{p['border']}"/>
</svg>"""


def label(x, y, text, color):
    return f'<text x="{x}" y="{y}" font-size="12" font-family="{MONO}" fill="{color}" letter-spacing="1.5">{text}</text>'


def bento(theme):
    p = palette(theme)
    out = {}
    dark = theme == "dark"

    # Hero 560x260 — AIOps front and centre, regulated environments
    chips, x = [], 34
    for txt, col in (("AI agents for ops", "mauve"), ("self-service", "blue"), ("guard-rails", "teal"), ("regulated · DORA", "peach")):
        cw = len(txt) * 7.2 + 16
        chips.append(f'<rect x="{x}" y="168" width="{cw:.0f}" height="24" rx="12" fill="{p[col]}" fill-opacity=".14" stroke="{p[col]}" stroke-opacity=".5"/>'
                     f'<text x="{x + cw / 2:.0f}" y="184" text-anchor="middle" font-size="12" font-family="{MONO}" fill="{p[col]}">{txt}</text>')
        x += cw + 8
    out["hero"] = tile(560, 260, theme, f"""
      <circle cx="520" cy="30" r="130" fill="{p['mauve']}" opacity=".10"/>
      <circle cx="560" cy="0" r="80" fill="{p['blue']}" opacity=".10"/>
      {label(34, 48, "HELLO, I'M", p['teal'])}
      <text x="34" y="86" font-size="31" font-weight="700" fill="{p['fg']}" letter-spacing="-.5">Jean-Jacques Martrès</text>
      <text x="34" y="113" font-size="15" fill="{p['dim']}">Senior Platform, Cloud &amp; AI Engineering Lead · 25 years</text>
      <text x="34" y="150" font-size="22" font-weight="700" fill="url(#aiops)">AIOps · GenAI that runs the platform</text>
      {''.join(chips)}
      <text x="34" y="228" font-size="11.5" font-family="{MONO}" fill="{p['dim']}">● full remote   ● FR · EN   ● resilience &amp; FinOps</text>""", corners="tl",
        defs=f'<linearGradient id="aiops" x1="0" x2="1"><stop offset="0" stop-color="{p["mauve"]}"/><stop offset=".55" stop-color="{p["pink"]}"/><stop offset="1" stop-color="{p["peach"]}"/></linearGradient>')

    # Certs 280x260
    certs = [("Cloud Architect", True), ("Cloud Security Engineer", True), ("ML Engineer", False)]
    rows = "".join(
        f'<circle cx="38" cy="{104 + i * 32}" r="8" fill="{p["green"] if ok else "none"}" stroke="{p["green"] if ok else p["overlay0"]}" stroke-width="1.5"/>'
        + (f'<path d="M34 {104 + i * 32}l3 3 5-6" stroke="{p["base"]}" stroke-width="1.8" fill="none"/>' if ok else "")
        + f'<text x="56" y="{108 + i * 32}" font-size="13" fill="{p["fg"] if ok else p["dim"]}">{n}{"" if ok else " · soon"}</text>'
        for i, (n, ok) in enumerate(certs))
    out["certs"] = tile(280, 260, theme, f"""
      {label(30, 48, "CERTIFIED", p['teal'])}
      <text x="30" y="74" font-size="15" font-weight="600" fill="{p['fg']}">Google Cloud Professional</text>
      {rows}
      <line x1="30" y1="206" x2="250" y2="206" stroke="{p['border']}"/>
      <text x="30" y="232" font-size="12.5" fill="{p['dim']}">🎓 Executive MBA · Epitech</text>""", corners="tr")

    # Career timeline 560x210
    stops = [("1998", "Network", "engineer"), ("2001", "IP/MPLS", "engineer"), ("2005", "Deputy", "CTO"),
             ("2009", "Cloud", "tech lead"), ("2018", "Head of", "infra"), ("2020", "DevSecOps", "lead"),
             ("2021", "Platform &amp;", "AI lead")]
    x0, x1, ly = 52, 486, 104
    step = (x1 - x0) / (len(stops) - 1)
    eras = [(0, 3, "blue", "networks &amp; telecom"), (3, 5, "teal", "cloud"), (5, 6, "mauve", "Kubernetes → AIOps")]
    tl = []
    for i0, i1, col, name in eras:
        xa, xb = x0 + i0 * step, x0 + i1 * step + (24 if i1 == 6 else 0)
        tl.append(f'<line x1="{xa:.0f}" y1="{ly}" x2="{xb:.0f}" y2="{ly}" stroke="{p[col]}" stroke-width="4" stroke-linecap="round"/>')
        anchor, tx = ("end", xb) if i1 == 6 else ("middle", (xa + xb) / 2)
        tl.append(f'<text x="{tx:.0f}" y="188" text-anchor="{anchor}" font-size="11" font-family="{MONO}" fill="{p[col]}">{name}</text>')
        tl.append(f'<line x1="{xa + 4:.0f}" y1="172" x2="{xb - 4:.0f}" y2="172" stroke="{p[col]}" stroke-opacity=".4" stroke-width="1.5"/>')
    for i, (yr, t1, t2) in enumerate(stops):
        cx = x0 + i * step
        col = "blue" if i < 3 else ("teal" if i < 5 else "mauve")
        last = i == len(stops) - 1
        tl.append(f'<circle cx="{cx:.0f}" cy="{ly}" r="{7 if last else 5}" fill="{p["base"]}" stroke="{p[col]}" stroke-width="3"/>')
        if last:
            tl.append(f'<circle cx="{cx:.0f}" cy="{ly}" r="7" fill="none" stroke="{p[col]}" stroke-width="2">'
                      f'<animate attributeName="r" values="7;14;7" dur="2.4s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values=".8;0;.8" dur="2.4s" repeatCount="indefinite"/></circle>')
        tl.append(f'<text x="{cx:.0f}" y="{ly - 16}" text-anchor="middle" font-size="11.5" font-family="{MONO}" fill="{p["dim"]}">{yr}</text>'
                  f'<text x="{cx:.0f}" y="{ly + 26}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{p["fg"]}">{t1}</text>'
                  f'<text x="{cx:.0f}" y="{ly + 42}" text-anchor="middle" font-size="11.5" fill="{p["dim"]}">{t2}</text>')
    out["timeline"] = tile(560, 210, theme, f"""
      {label(30, 46, "25 YEARS, ONE THREAD: KEEP IT RUNNING", p['teal'])}
      {''.join(tl)}""")

    # Impact 280x210
    metrics = [("−60%", "ops overhead", "AI automation", "mauve"), ("−80%", "deploy complexity", "k8s Operator", "blue"),
               ("−30%", "infra cost", "cloud FinOps", "green"), ("DORA", "compliance", "delivered", "peach")]
    mt = []
    for i, (big, l1, l2, col) in enumerate(metrics):
        cx, cy = 30 + (i % 2) * 118, 84 + (i // 2) * 64
        mt.append(f'<text x="{cx}" y="{cy}" font-size="24" font-weight="700" fill="{p[col]}">{big}</text>'
                  f'<text x="{cx}" y="{cy + 18}" font-size="11.5" fill="{p["fg"]}">{l1}</text>'
                  f'<text x="{cx}" y="{cy + 33}" font-size="10.5" font-family="{MONO}" fill="{p["dim"]}">{l2}</text>')
    out["impact"] = tile(280, 210, theme, f"""
      {label(30, 46, "IMPACT", p['teal'])}
      {''.join(mt)}""")

    def project(key, title, tag, tagcol, lines, icon):
        tw = len(tag) * 7.2 + 16
        out[key] = tile(280, 190, theme, icon + f"""
      <text x="30" y="118" font-size="18" font-weight="700" fill="{p['fg']}">{title}</text>
      <text x="30" y="142" font-size="12.5" fill="{p['dim']}">{lines[0]}</text>
      <text x="30" y="160" font-size="12.5" fill="{p['dim']}">{lines[1]}</text>
      <rect x="{258 - tw:.0f}" y="28" width="{tw:.0f}" height="22" rx="11" fill="{p[tagcol]}" fill-opacity=".14" stroke="{p[tagcol]}" stroke-opacity=".45"/>
      <text x="250" y="43" text-anchor="end" font-size="11" font-family="{MONO}" fill="{p[tagcol]}">{tag}</text>""")

    def badge(col, inner):
        return (f'<rect x="26" y="26" width="52" height="52" rx="14" fill="{p[col]}" fill-opacity=".16"/>'
                f'<g stroke="{p[col]}" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')

    vb, inner = svg_inner(ROOT / "assets" / ("farnswrth-symbol-dark.svg" if dark else "farnswrth-symbol.svg"))
    project("farnswrth", "farnswrth", "soon", "mauve", ["The coding agent that knows", "when to stop and ask."],
            f'<svg x="22" y="22" width="60" height="60" viewBox="{vb}">{inner}</svg>')
    vb, inner = svg_inner(ROOT / "assets" / ("astroagent-symbol-reversed.svg" if dark else "astroagent-symbol.svg"))
    project("astroagent", "astroagent", "python", "blue", ["Raw subs to finished astrophoto,", "an approval at every stage."],
            f'<svg x="26" y="26" width="52" height="52" viewBox="{vb}">{inner}</svg>')
    png = base64.b64encode((ROOT / "assets/nebulis.png").read_bytes()).decode()
    project("nebulis", "Nebulis", "contrib", "peach", ["Sky forecast, imaging-site", "windows, frame analysis."],
            f'<image x="26" y="26" width="52" height="52" href="data:image/png;base64,{png}"/>')
    # stacked layers: one config shared by many agents
    project("agents", "ai-coding-agents", "48★", "yellow", ["One configuration — skills, rules,", "commands — for every agent."],
            badge("teal", '<path d="M52 36l-14 7 14 7 14-7z"/><path d="M38 51l14 7 14-7"/><path d="M38 58l14 7 14-7"/>'))
    # gauge with a needle near the red zone
    project("costguard", "opencode-cost-guard", "9★", "yellow", ["Real-time session cost guard,", "warns or stops at your limit."],
            badge("peach", '<path d="M36 62a16 16 0 1 1 32 0"/><path d="M52 62l9-11"/><circle cx="52" cy="62" r="2.5"/>'))
    # small robot head with antennas
    project("reachy", "Reachy Mini", "10★", "yellow", ["SDK agent skill and mini-apps", "for an expressive robot."],
            badge("pink", '<rect x="37" y="42" width="30" height="22" rx="9"/><circle cx="46" cy="53" r="2.2"/><circle cx="58" cy="53" r="2.2"/>'
                          '<path d="M44 42l-4-8M60 42l4-8"/><circle cx="40" cy="33" r="1.6"/><circle cx="64" cy="33" r="1.6"/>'))

    # Stack 560x180
    chips_list = [("Kubernetes", "blue"), ("Operators", "blue"), ("Google Cloud", "sapphire"), ("AWS", "peach"),
                  ("Azure", "sapphire"), ("Terraform", "mauve"), ("Go", "teal"), ("Python", "yellow"),
                  ("Vertex AI", "pink"), ("MCP", "pink"), ("OpenTelemetry", "lavender"), ("FinOps", "green"),
                  ("SRE", "green"), ("Pi", "mauve")]
    x, y, parts = 30, 70, []
    for ch, col in chips_list:
        cw = len(ch) * 7.1 + 22
        if x + cw > 530:
            x, y = 30, y + 34
        parts.append(f'<rect x="{x}" y="{y}" width="{cw:.0f}" height="26" rx="13" fill="{p[col]}" fill-opacity=".12" stroke="{p[col]}" stroke-opacity=".4"/>'
                     f'<text x="{x + cw / 2:.0f}" y="{y + 17}" text-anchor="middle" font-size="12.5" fill="{p["fg"]}">{ch}</text>')
        x += cw + 8
    out["stack"] = tile(560, 180, theme, f"""
      {label(30, 50, "TOOLBOX", p['teal'])}
      {''.join(parts)}""")

    # Dithered galaxy 280x180, coloured by intensity
    rnd = random.Random(3)
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    cells, cs = {"core": [], "mid": [], "arm": []}, 3
    cx0, cy0 = 140, 92
    for j in range(12, 170, cs):
        for i in range(12, 268, cs):
            dx, dy = (i - cx0), (j - cy0) * 2.1
            ca, sa = math.cos(-.5), math.sin(-.5)
            rx, ry = dx * ca - dy * sa, dx * sa + dy * ca
            r = math.hypot(rx, ry * 1.9) + 1e-6
            th = math.atan2(ry * 1.9, rx)
            arm = (math.cos(2 * th - 0.075 * r) + 1) / 2
            v = math.exp(-r / 18) * 2.2 + arm ** 2 * math.exp(-r / 55) * 1.3
            v += 1.2 if rnd.random() < .006 else 0
            if v * 16 > bayer[(j // cs) % 4][(i // cs) % 4] + 0.5:
                grp = "core" if r < 22 else ("mid" if r < 50 else "arm")
                cells[grp].append(f'<rect x="{i}" y="{j}" width="2" height="2"/>')
    out["galaxy"] = tile(280, 180, theme, f"""
      <rect x="0" y="0" width="280" height="180" fill="{p['crust']}"/>
      <g fill="{p['lavender']}">{''.join(cells['arm'])}</g>
      <g fill="{p['pink']}">{''.join(cells['mid'])}</g>
      <g fill="{p['peach']}">{''.join(cells['core'])}</g>
      <rect x="20" y="138" width="124" height="24" rx="12" fill="{p['base']}" stroke="{p['border']}"/>
      <text x="82" y="154" text-anchor="middle" font-size="11.5" font-family="{MONO}" fill="{p['fg']}">✦ my AstroBin</text>""")

    # Legacy 420x120, Also 420x120
    out["legacy"] = tile(420, 120, theme, f"""
      {label(30, 46, "SINCE 2012", p['teal'])}
      <text x="30" y="82" font-size="30" font-weight="700" fill="{p['yellow']}">886★</text>
      <text x="128" y="70" font-size="13.5" fill="{p['fg']}">Zabbix templates &amp; scripts</text>
      <text x="128" y="90" font-size="12.5" fill="{p['dim']}">archived · featured in a Packt book</text>""", corners="bl")
    out["also"] = tile(420, 120, theme, f"""
      {label(30, 46, "ALSO", p['teal'])}
      <text x="30" y="74" font-size="13.5" fill="{p['fg']}">Smartplaylist <tspan fill="{p['dim']}">— playlists from plain language (MCP)</tspan></text>
      <text x="30" y="96" font-size="13.5" fill="{p['fg']}">dotfiles <tspan fill="{p['dim']}">— fish, Herdr workspaces, macOS &amp; Linux</tspan></text>""", corners="br")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        for name, svg in bento(theme).items():
            (OUT / f"{name}-{theme}.svg").write_text(svg.strip() + "\n")
    readme = ROOT / "README.md"
    text = readme.read_text()

    def version(m):
        digest = hashlib.sha1((ROOT / m.group(1)).read_bytes()).hexdigest()[:8]
        return f'{m.group(1)}?v={digest}"'

    text = re.sub(r'(assets/bento/[a-z]+-(?:light|dark)\.svg)(?:\?v=[0-9a-f]+)?"', version, text)
    readme.write_text(text)
    print("ok")


if __name__ == "__main__":
    main()
