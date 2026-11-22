#!/usr/bin/env python3
"""Generate the 1672x941 blog header image for a post.

Usage: python3 _tools/make_image.py data/posts/<file>.json   (or no args = every post missing an image)
Reads the post's "image" spec:
  {"line1": "GREAT BRIDGE", "line2": "1775 -> TODAY", "pill": "CHESAPEAKE, VA",
   "scene": "neighborhood|skyline|bridge|waterfront|sale|military|events|flood|tax|keys",
   "sky": "dusk|day|dawn|night|teal", "alt": "..."}
Writes assets/blog/<slug>.jpg. Chris's real headshot (cut out) sits on the right, same layout every time.
"""
import base64, glob, html, json, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1672, 941

SKY = {
    "dusk": ("#10264f", "#3b5f9a", "#f0a04b"),
    "day": ("#1b6fb8", "#5aa8e0", "#dff0fb"),
    "dawn": ("#27407a", "#d98a6a", "#ffd68a"),
    "night": ("#0a1630", "#1f3a6e", "#4c6fae"),
    "teal": ("#0d4a5c", "#1f8a9a", "#a8e0d8"),
}


def house(x, y, s, body="#e9e3d6", roof="#46546e", door="#8a4b2f"):
    w, h = 190 * s, 120 * s
    return (f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="{-h}" width="{w}" height="{h}" fill="{body}"/>'
            f'<polygon points="{-12*s},{-h} {w/2},{-h-80*s} {w+12*s},{-h}" fill="{roof}"/>'
            f'<rect x="{w*0.42}" y="{-h*0.55}" width="{w*0.16}" height="{h*0.55}" fill="{door}"/>'
            f'<rect x="{w*0.1}" y="{-h*0.7}" width="{w*0.2}" height="{h*0.3}" fill="#9cc7e6"/>'
            f'<rect x="{w*0.7}" y="{-h*0.7}" width="{w*0.2}" height="{h*0.3}" fill="#9cc7e6"/></g>')


def tree(x, y, s, c="#2f7a3e"):
    return (f'<g transform="translate({x},{y})"><rect x="{-6*s}" y="{-60*s}" width="{12*s}" height="{60*s}" fill="#5b3f27"/>'
            f'<circle cx="0" cy="{-95*s}" r="{55*s}" fill="{c}"/><circle cx="{-32*s}" cy="{-70*s}" r="{38*s}" fill="{c}"/>'
            f'<circle cx="{32*s}" cy="{-70*s}" r="{38*s}" fill="{c}"/></g>')


def ground(color="#2c6b34"):
    return f'<rect x="0" y="800" width="1200" height="141" fill="{color}"/>'


def scene_svg(name):
    if name == "neighborhood":
        return (ground() + tree(90, 820, 1.2) + house(150, 830, 1.5) + tree(470, 830, 1.0, "#3a8a48")
                + house(520, 838, 1.25, "#d9dfe8", "#5a3d3d") + house(790, 842, 1.1, "#efe0c2", "#35506e") + tree(1040, 850, 1.3))
    if name == "skyline":
        b = ""
        xs = [(40, 120, 330), (170, 100, 460), (280, 130, 380), (420, 90, 560), (520, 140, 420), (670, 110, 500), (790, 150, 360), (950, 100, 440)]
        for x, w, h in xs:
            b += f'<rect x="{x}" y="{800-h}" width="{w}" height="{h}" fill="#1c2a4a" opacity="0.92"/>'
            for yy in range(800 - h + 20, 780, 38):
                for xx in range(x + 14, x + w - 14, 28):
                    b += f'<rect x="{xx}" y="{yy}" width="10" height="16" fill="#ffd88a" opacity="0.75"/>'
        return b + '<rect x="0" y="800" width="1200" height="141" fill="#16223f"/>'
    if name in ("bridge", "waterfront", "flood"):
        water = ('<rect x="0" y="720" width="1200" height="221" fill="#1d5f8f"/>'
                 + "".join(f'<path d="M0 {750+i*34} q60 -18 120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0" stroke="#8cc8ea" stroke-width="4" fill="none" opacity="0.6"/>' for i in range(6)))
        if name == "bridge":
            return (water + '<g fill="#6e4f33"><rect x="60" y="640" width="1000" height="26"/>'
                    + "".join(f'<rect x="{80+i*80}" y="590" width="12" height="50"/>' for i in range(13))
                    + '<rect x="60" y="590" width="1000" height="10"/>'
                    + "".join(f'<rect x="{150+i*240}" y="666" width="26" height="130"/>' for i in range(4)) + '</g>'
                    + house(70, 600, 0.9, "#8a6a47", "#4a3a2a"))
        if name == "flood":
            return (house(250, 790, 1.8) + '<rect x="0" y="760" width="1200" height="181" fill="#1d5f8f" opacity="0.85"/>'
                    + "".join(f'<path d="M0 {780+i*34} q60 -18 120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0" stroke="#bfe4f6" stroke-width="4" fill="none" opacity="0.7"/>' for i in range(5)))
        return (water + '<polygon points="120,720 190,560 260,720" fill="#f4f1ea"/><rect x="186" y="560" width="8" height="170" fill="#444"/>'
                + '<rect x="0" y="780" width="1200" height="161" fill="#e6d3a3"/>' + tree(900, 790, 1.2))
    if name == "sale":
        return (ground() + house(220, 830, 2.3, "#ece6d8", "#3f5675") + tree(110, 830, 1.5) + tree(930, 840, 1.6, "#3a8a48")
                + '<rect x="760" y="650" width="10" height="190" fill="#7a5a3a"/><rect x="690" y="620" width="170" height="90" rx="6" fill="#ffffff"/>'
                + '<rect x="690" y="620" width="170" height="26" rx="6" fill="#d9a41c"/><text x="775" y="685" font-size="34" font-weight="900" text-anchor="middle" fill="#1b2d52" font-family="Fira Sans">SOLD</text>')
    if name == "keys":
        return (ground("#27492e") + house(160, 830, 2.0, "#e3d9c4", "#4a3b5a") + house(640, 840, 1.6, "#dfe6ee", "#3f5675")
                + '<g transform="translate(900,640) rotate(-20)"><circle cx="0" cy="0" r="46" fill="none" stroke="#ffd34d" stroke-width="16"/>'
                '<rect x="40" y="-9" width="170" height="18" fill="#ffd34d"/><rect x="150" y="9" width="14" height="36" fill="#ffd34d"/><rect x="180" y="9" width="14" height="26" fill="#ffd34d"/></g>')
    if name == "military":
        stripes = "".join(f'<rect x="60" y="{530+i*17}" width="760" height="9" fill="{"#c8283c" if i%2==0 else "#f5f5f5"}" opacity="0.92"/>' for i in range(13))
        stars = "".join(f'<circle cx="{80+c*40}" cy="{550+r*26}" r="4" fill="#fff"/>' for r in range(5) for c in range(6))
        return (stripes + '<rect x="60" y="530" width="280" height="140" fill="#233a7a" opacity="0.95"/>' + stars
                + '<rect x="0" y="800" width="1200" height="141" fill="#15243f"/>' + house(700, 830, 1.5, "#d9dfe8", "#35506e")
                + '<polygon points="560,830 620,700 680,830" fill="#5b6a80"/><rect x="595" y="700" width="50" height="130" fill="#6d7d93"/>')
    if name == "events":
        s = ""
        for i, (x, y, c) in enumerate([(250, 330, "#ffd34d"), (520, 240, "#ff6b6b"), (780, 360, "#7ee0ff"), (400, 470, "#b98cff"), (950, 250, "#7dff9a")]):
            for a in range(0, 360, 30):
                import math
                dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
                s += f'<line x1="{x+dx*30}" y1="{y+dy*30}" x2="{x+dx*95}" y2="{y+dy*95}" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
        return (s + '<rect x="0" y="800" width="1200" height="141" fill="#15213f"/>' + house(120, 830, 1.4, "#e9e3d6", "#46546e") + tree(520, 840, 1.2, "#2a6a3a")
                + house(640, 836, 1.6, "#d9dfe8", "#5a3d3d")
                + '<path d="M0 640 Q300 700 600 640 T1200 640" stroke="#ffe9a8" stroke-width="3" fill="none"/>'
                + "".join(f'<circle cx="{40+i*75}" cy="{ (656 if i%2==0 else 682) }" r="9" fill="#ffd34d"/>' for i in range(16)))
    if name == "tax":
        return (ground("#21402b") + house(130, 830, 1.8) + house(640, 836, 1.5, "#dfe6ee", "#3f5675")
                + '<g transform="translate(960,560) rotate(8)"><rect x="-90" y="-120" width="180" height="230" rx="10" fill="#fdfcf7"/>'
                '<rect x="-60" y="-90" width="120" height="14" fill="#9aa8bd"/><rect x="-60" y="-60" width="90" height="10" fill="#c3ccd9"/>'
                '<rect x="-60" y="-38" width="110" height="10" fill="#c3ccd9"/><text x="0" y="60" font-size="84" font-weight="900" text-anchor="middle" fill="#c8283c" font-family="Fira Sans">%</text></g>')
    return ground() + house(200, 830, 1.8)


def page(spec, cut_b64):
    c1, c2, c3 = SKY.get(spec.get("sky", "dusk"), SKY["dusk"])
    scene = scene_svg(spec.get("scene", "neighborhood"))
    l1 = html.escape(spec["line1"])
    l2 = html.escape(spec["line2"])
    pill = html.escape(spec.get("pill", "HAMPTON ROADS, VA"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#000}}
.c{{position:relative;width:{W}px;height:{H}px;overflow:hidden;font-family:'Fira Sans','Arial Black',sans-serif;
 background:linear-gradient(115deg,{c1} 0%,{c2} 48%,{c3} 62%,#7cc3ee 63%,#5aa8e0 100%)}}
.bg{{position:absolute;left:0;top:0;width:1200px;height:{H}px}}
.sun{{position:absolute;left:640px;top:-120px;width:900px;height:900px;background:radial-gradient(circle,rgba(255,236,170,.55),rgba(255,236,170,0) 62%)}}
.right{{position:absolute;left:1020px;top:0;width:652px;height:{H}px;background:linear-gradient(180deg,#58a7e6 0%,#a9d6f5 100%)}}
.right:before{{content:'';position:absolute;left:-60px;top:0;width:120px;height:100%;background:linear-gradient(90deg,rgba(255,215,120,0),rgba(255,230,150,.9),rgba(255,215,120,0));transform:skewX(-6deg)}}
.tint{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.28),rgba(0,0,0,0) 35%)}}
.chris{{position:absolute;right:-20px;bottom:-26px;height:1010px;filter:drop-shadow(0 0 0 #fff) drop-shadow(0 0 5px rgba(255,255,255,.95)) drop-shadow(0 10px 24px rgba(0,0,0,.35))}}
.t1,.t2{{position:absolute;left:62px;font-weight:900;font-style:italic;text-transform:uppercase;line-height:.95;letter-spacing:-2px;white-space:nowrap}}
.t1{{top:50px;color:#fff;text-shadow:0 7px 0 rgba(0,0,0,.28),0 0 30px rgba(0,0,0,.35);}}
.t2{{color:#ffe21a;text-shadow:0 7px 0 rgba(0,0,0,.30),0 0 28px rgba(0,0,0,.35)}}
.pill{{position:absolute;left:250px;background:#173a66;border:3px solid #cfe1f5;color:#fff;font-weight:800;font-style:italic;
 text-transform:uppercase;font-size:50px;padding:10px 46px;transform:skewX(-10deg);white-space:nowrap;box-shadow:0 8px 20px rgba(0,0,0,.35)}}
.pill span{{display:inline-block;transform:skewX(10deg)}}
.name{{position:absolute;left:38px;bottom:42px;color:#fff;font-weight:900;font-style:italic;text-transform:uppercase;font-size:50px;letter-spacing:-1px;text-shadow:0 4px 0 rgba(0,0,0,.45),0 0 14px rgba(0,0,0,.5)}}
.name:after{{content:'';display:block;height:7px;width:112%;background:#ffe21a;transform:skewX(-20deg);margin-top:2px;box-shadow:0 3px 8px rgba(0,0,0,.4)}}
</style></head><body><div class="c">
<div class="right"></div><div class="sun"></div>
<svg class="bg" viewBox="0 0 1200 {H}">{scene}</svg><div class="tint"></div>
<div class="t1" id="t1">{l1}</div><div class="t2" id="t2">{l2}</div><div class="pill" id="pill"><span>{pill}</span></div>
<img class="chris" src="data:image/png;base64,{cut_b64}"/>
<div class="name">Chris Jenkins</div></div>
<script>
function fit(el,maxw,start){{let s=start;el.style.fontSize=s+'px';while(el.scrollWidth>maxw&&s>40){{s-=4;el.style.fontSize=s+'px';}}return s;}}
const t1=document.getElementById('t1'),t2=document.getElementById('t2'),p=document.getElementById('pill');
const s1=fit(t1,1000,210);t2.style.top=(50+s1*0.93)+'px';const s2=fit(t2,1000,190);
p.style.top=(50+s1*0.93+s2*0.97+28)+'px';
</script></body></html>"""


def render(specs):
    cut = base64.b64encode(open(os.path.join(ROOT, "_tools/imgassets/chris-cutout.png"), "rb").read()).decode()
    os.makedirs(os.path.join(ROOT, "assets/blog"), exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for slug, spec in specs:
            pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pg.set_content(page(spec, cut))
            pg.wait_for_timeout(400)
            out = os.path.join(ROOT, f"assets/blog/{slug}.jpg")
            pg.screenshot(path=out, type="jpeg", quality=88)
            pg.close()
            print("wrote", out)
        br.close()


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "data/posts/*.json")))
    specs = []
    for f in files:
        d = json.load(open(f))
        if d.get("image") and (sys.argv[1:] or not os.path.exists(os.path.join(ROOT, f"assets/blog/{d['slug']}.jpg"))):
            specs.append((d["slug"], d["image"]))
    render(specs)
