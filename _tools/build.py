#!/usr/bin/env python3
"""
Static site generator for chrisjenkinsrealestate.com sub-pages.

Reads data/cities/*.json, data/neighborhoods/*.json and data/posts/*.json and writes plain HTML into the
repo root (neighborhoods/, blog/), plus sitemap.xml, robots.txt, llms.txt, 404.html and _redirects.
The homepage (index.html) is NEVER rewritten by this script; its nav/contact/footer markup, phone number and
contact email are read from it so every generated page stays identical to the homepage.

Usage:  python3 _tools/build.py
"""
import html, json, os, re, sys, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://chrisjenkinsrealestate.com"
BRAND = "Better Homes and Gardens Real Estate – Native American Group"
AGENT = "Chris Jenkins"
PHONE_DISPLAY, PHONE_TEL = "(757) 286-7255", "+17572867255"
TODAY = datetime.date.today().isoformat()

esc = lambda s: html.escape(str(s), quote=True)


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(s)


def load_dir(d):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", d, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


HOME = read("index.html")
EMAIL = re.search(r'mailto:([^"]+)"', HOME).group(1)  # read from the homepage, not stored here
OG_IMAGE = BASE + "/headshot.jpg"
CONTACT = re.search(r"<!-- CONTACT -->.*?</section>", HOME, re.S).group(0)
FAIR = re.search(r'<!-- FOOTER -->\s*(<div style="background:#0d0d0d.*?</div>\s*</div>\s*</div>)', HOME, re.S).group(1)
CONTACT_JS = re.search(r"(async function handleContactForm.*?\n  \})\n", HOME, re.S).group(1)
FONTS = re.search(r'<link href="https://fonts.googleapis.com/css2[^>]+>', HOME).group(0)

NAV = f"""<nav id="nav" class="scrolled">
  <a href="/" class="nav-logo" aria-label="{esc(AGENT)} – {esc(BRAND)} – home">
    <img class="nav-logo-img" id="navLogoImg" src="/logo.png" alt="{esc(BRAND)}"
      onload="this.style.display='block'; document.getElementById('navLogoText').style.display='none';"
      onerror="this.style.display='none';" />
    <span class="nav-logo-text" id="navLogoText">Chris Jenkins</span>
  </a>
  <ul class="nav-links">
    <li><a href="/#about">About</a></li>
    <li><a href="/neighborhoods/">Neighborhoods</a></li>
    <li><a href="/blog/">Blog</a></li>
    <li><a href="/#testimonials">Reviews</a></li>
    <li><a href="/#contact" class="nav-cta">Free Consultation</a></li>
  </ul>
</nav>"""

FOOTER = f"""<footer>
  <div class="footer-links">
    <a href="/">Home</a><a href="/neighborhoods/">Hampton Roads Neighborhoods</a><a href="/blog/">Real Estate Blog</a><a href="/#contact">Contact Chris Jenkins</a>
  </div>
  <p>© {datetime.date.today().year} Chris Jenkins · {BRAND} · All Rights Reserved</p>
  <p style="margin-top:0.4rem;">Licensed in the Commonwealth of Virginia · chrisjenkinsrealestate.com</p>
</footer>"""

SCRIPTS = f"""<script>
  document.querySelectorAll('.faq-q').forEach(q => {{
    q.addEventListener('click', () => {{
      const item = q.parentElement, wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    }});
  }});
  {CONTACT_JS}
</script>"""

AGENT_NODE = {
    "@type": ["Person", "RealEstateAgent"],
    "@id": BASE + "/#chris-jenkins",
    "name": AGENT,
    "alternateName": "Christopher Jenkins",
    "jobTitle": "REALTOR®",
    "url": BASE + "/",
    "telephone": PHONE_TEL,
    "email": EMAIL,
    "image": OG_IMAGE,
    "worksFor": {"@type": "RealEstateAgent", "name": BRAND},
    "areaServed": {"@type": "Place", "name": "Hampton Roads, Virginia"},
    "hasCredential": [
        {"@type": "EducationalOccupationalCredential", "name": "HRRA Circle of Excellence Award Winner (2013–present)"},
        {"@type": "EducationalOccupationalCredential", "name": "HRRA Realtor Rookie of the Year 2013"},
    ],
}


def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False) + "\n</script>"


def crumbs_html(items):
    parts = []
    for i, (name, url) in enumerate(items):
        parts.append(esc(name) if i == len(items) - 1 else f'<a href="{url}">{esc(name)}</a>')
    return '<div class="breadcrumbs">' + '<span class="sep">/</span>'.join(parts) + "</div>"


def crumbs_ld(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u}
            for i, (n, u) in enumerate(items)
        ],
    }


def faq_html(faqs, heading="Frequently Asked Questions"):
    if not faqs:
        return ""
    items = "".join(
        f'<div class="faq-item"><div class="faq-q">{esc(q)}</div><div class="faq-a">{a}</div></div>' for q, a in faqs
    )
    return (
        f'<section id="faq" class="band-cream faq-sub"><div class="faq-inner"><div class="faq-header">'
        f'<p class="section-eyebrow">Common Questions</p><h2 class="section-title">{esc(heading)}</h2>'
        f'<div class="section-line center"></div></div>{items}</div></section>'
    )


def faq_ld(faqs):
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faqs
        ],
    }


def sources_html(sources):
    if not sources:
        return ""
    lis = "".join(
        f'<li><a href="{esc(u)}" rel="noopener nofollow" target="_blank">{esc(t)}</a></li>' for t, u in sources
    )
    return f'<div class="sources"><h2>Sources</h2><ul>{lis}</ul></div>'


def side_card(title, text):
    return (
        f'<aside class="side-card"><h3>{esc(title)}</h3><p>{esc(text)}</p>'
        f'<a class="hero-btn" href="#contact">Schedule a Free Consultation</a>'
        f'<div class="side-contact">{esc(AGENT)} · {esc(BRAND)}<br/>'
        f'<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div></aside>'
    )


def page(path, title, desc, body, ld_graph, og_type="website", published=None, modified=None):
    url = BASE + path
    og_extra = ""
    if og_type == "article":
        og_extra = (
            f'<meta property="article:published_time" content="{published}" />'
            f'<meta property="article:modified_time" content="{modified or published}" />'
            f'<meta property="article:author" content="{esc(AGENT)}" />'
        )
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <meta name="author" content="{esc(AGENT)}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <link rel="canonical" href="{url}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="{esc(AGENT)} – {esc(BRAND)}" />
  <meta property="og:image" content="{OG_IMAGE}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  {og_extra}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  {FONTS}
  <link rel="stylesheet" href="/assets/site.css" />
  {jsonld({"@context": "https://schema.org", "@graph": ld_graph})}
</head>
<body>
{NAV}
"""
    return head + body + "\n" + CONTACT + "\n<!-- FOOTER -->\n" + FAIR + "\n" + FOOTER + "\n" + SCRIPTS + "\n</body>\n</html>\n"


def hero(eyebrow, h1, lede, byline=""):
    by = f'<p class="byline">{byline}</p>' if byline else ""
    return (
        f'<header class="page-hero"><p class="hero-eyebrow">{esc(eyebrow)}</p><h1>{esc(h1)}</h1>'
        f'<p class="lede">{lede}</p>{by}</header>'
    )


def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")


def byline_html(updated):
    return f'By <a href="/">{esc(AGENT)}</a> · {esc(BRAND)} · Updated {fmt_date(updated)}'


CITIES = {c["slug"]: c for c in load_dir("cities")}
HOODS = load_dir("neighborhoods")
POSTS = sorted(load_dir("posts"), key=lambda p: p["date"], reverse=True)
HOOD_BY = {(h["city_slug"], h["slug"]): h for h in HOODS}
urls = []  # (path, lastmod, priority)


# ---------------- neighborhood pages ----------------
def build_hood(h):
    city = CITIES[h["city_slug"]]
    path = f"/neighborhoods/{h['city_slug']}/{h['slug']}/"
    crumbs = [("Home", "/"), ("Neighborhoods", "/neighborhoods/"), (f"{city['name']}, VA", f"/neighborhoods/{city['slug']}/"), (h["name"], path)]
    facts = "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in h["facts"])
    secs = "".join(f"<h2>{esc(s['h2'])}</h2>{s['html']}" for s in h["sections"])
    related = ""
    rel = [HOOD_BY[(h["city_slug"], r)] for r in h.get("related", []) if (h["city_slug"], r) in HOOD_BY]
    if rel:
        cards = "".join(
            f'<a class="link-card" href="/neighborhoods/{r["city_slug"]}/{r["slug"]}/"><h3>{esc(r["name"])}</h3>'
            f'<p>{esc(r["card"])}</p><span class="more">Explore →</span></a>' for r in rel
        )
        related = f'<h2>More {esc(city["name"])} Neighborhoods</h2><div class="card-grid">{cards}</div>'
    body = (
        hero(f"{city['name']}, Virginia · Neighborhood Guide", f"{h['name']}, {city['name']} VA – Homes & Community Guide", h["lede"], byline_html(h["updated"]))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-grid"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">At a glance</span><p>{h["tldr"]}</p></div>'
        + f'<h2>{esc(h["name"])} Quick Facts</h2><table class="facts">{facts}</table>'
        + secs
        + related
        + sources_html(h.get("sources"))
        + "</article>"
        + side_card(f"Buying or selling in {h['name']}?", f"{AGENT} with {BRAND} can walk you through {h['name']} and the rest of {city['name']}.")
        + "</div></main>"
        + faq_html(h["faqs"], f"{h['name']} Questions, Answered")
    )
    title = f"{h['name']}, {city['name']} VA Homes for Sale & Guide | {AGENT}"
    ld = [
        AGENT_NODE,
        crumbs_ld(crumbs),
        {
            "@type": "WebPage", "@id": BASE + path + "#webpage", "url": BASE + path, "name": title,
            "description": h["description"], "dateModified": h["updated"], "inLanguage": "en-US",
            "isPartOf": {"@type": "WebSite", "name": f"{AGENT} – {BRAND}", "url": BASE + "/"},
            "author": {"@id": BASE + "/#chris-jenkins"}, "about": {"@id": BASE + path + "#place"},
        },
        {
            "@type": "Place", "@id": BASE + path + "#place", "name": f"{h['name']}, {city['name']}, Virginia",
            "description": h["description"],
            "address": {"@type": "PostalAddress", "addressLocality": city["name"], "addressRegion": "VA", "addressCountry": "US"},
            "containedInPlace": {"@type": "City", "name": city["name"], "containedInPlace": {"@type": "State", "name": "Virginia"}},
        },
        faq_ld(h["faqs"]),
    ]
    place = ld[3]
    if h.get("lat") is not None and h.get("lng") is not None:
        place["geo"] = {"@type": "GeoCoordinates", "latitude": h["lat"], "longitude": h["lng"]}
    if h.get("zip"):
        place["address"]["postalCode"] = h["zip"]
    write(path.strip("/") + "/index.html", page(path, title, h["description"], body, ld))
    urls.append((path, h["updated"], "0.7"))


# ---------------- city hubs ----------------
def build_city(c):
    path = f"/neighborhoods/{c['slug']}/"
    hoods = [h for h in HOODS if h["city_slug"] == c["slug"]]
    crumbs = [("Home", "/"), ("Neighborhoods", "/neighborhoods/"), (f"{c['name']}, VA", path)]
    cards = "".join(
        f'<a class="link-card" href="/neighborhoods/{h["city_slug"]}/{h["slug"]}/"><h3>{esc(h["name"])}</h3><p>{esc(h["card"])}</p><span class="more">Explore →</span></a>'
        for h in hoods
    )
    grid = f'<div class="card-grid">{cards}</div>' if hoods else ""
    body = (
        hero(f"Hampton Roads, Virginia · {c['name']}", f"{c['name']} VA Neighborhoods & Real Estate Guide", c["lede"], byline_html(c["updated"]))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-grid"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">At a glance</span><p>{c["tldr"]}</p></div>'
        + "".join(f"<h2>{esc(s['h2'])}</h2>{s['html']}" for s in c["sections"])
        + f"<h2>{esc(c['name'])} Neighborhood Guides</h2>"
        + (grid or "<p>Neighborhood guides for this city are being added. Call or text Chris Jenkins for a personal walkthrough of any community.</p>")
        + sources_html(c.get("sources"))
        + "</article>"
        + side_card(f"Thinking about {c['name']}?", f"{AGENT} helps buyers and sellers across {c['name']} and the rest of Hampton Roads.")
        + "</div></main>"
        + faq_html(c["faqs"], f"{c['name']} Real Estate FAQ")
    )
    title = f"{c['name']} VA Neighborhoods & Homes for Sale | {AGENT}"
    ld = [
        AGENT_NODE, crumbs_ld(crumbs),
        {"@type": "CollectionPage", "@id": BASE + path + "#webpage", "url": BASE + path, "name": title, "description": c["description"],
         "dateModified": c["updated"], "author": {"@id": BASE + "/#chris-jenkins"},
         "about": {"@type": "City", "name": c["name"], "containedInPlace": {"@type": "State", "name": "Virginia"}}},
        faq_ld(c["faqs"]),
    ]
    write(path.strip("/") + "/index.html", page(path, title, c["description"], body, ld))
    urls.append((path, c["updated"], "0.8"))


# ---------------- neighborhoods index ----------------
def build_hood_index():
    path = "/neighborhoods/"
    crumbs = [("Home", "/"), ("Neighborhoods", path)]
    cards = "".join(
        f'<a class="link-card" href="/neighborhoods/{c["slug"]}/"><h3>{esc(c["name"])}, VA</h3><p>{esc(c["card"])}</p><span class="more">Explore {esc(c["name"])} →</span></a>'
        for c in CITIES.values()
    )
    desc = f"Hampton Roads neighborhood guides by {AGENT} of {BRAND}, starting with Chesapeake. Communities, home types, HOA dues and what to check before you buy or sell."
    body = (
        hero("Hampton Roads, Virginia", "Hampton Roads Neighborhood Guides", f"Community-by-community guides to buying and selling a home across Hampton Roads, written by {AGENT} of {BRAND}.", byline_html(TODAY))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-wide prose">'
        + f"<h2>Explore Hampton Roads by City</h2><p>Every guide covers one community in detail: where it is, what kinds of homes it has, what the dues and amenities look like, and what to check before you buy or sell there. {esc(AGENT)} has helped buyers, sellers and military families move across Hampton Roads for over a decade, and new neighborhood guides are added regularly.</p>"
        + f'<div class="card-grid">{cards}</div>'
        + "</div></main>"
    )
    title = f"Hampton Roads Neighborhood Guides | {AGENT} – {BRAND}"
    ld = [AGENT_NODE, crumbs_ld(crumbs),
          {"@type": "CollectionPage", "@id": BASE + path + "#webpage", "url": BASE + path, "name": title, "description": desc, "author": {"@id": BASE + "/#chris-jenkins"}}]
    write("neighborhoods/index.html", page(path, title, desc, body, ld))
    urls.append((path, TODAY, "0.8"))


# ---------------- blog ----------------
def build_post(p):
    path = f"/blog/{p['slug']}/"
    crumbs = [("Home", "/"), ("Blog", "/blog/"), (p["title"], path)]
    rel = ""
    links = [HOOD_BY[tuple(x)] for x in p.get("related_neighborhoods", []) if tuple(x) in HOOD_BY]
    if links:
        cards = "".join(
            f'<a class="link-card" href="/neighborhoods/{r["city_slug"]}/{r["slug"]}/"><h3>{esc(r["name"])}</h3><p>{esc(r["card"])}</p><span class="more">Explore →</span></a>' for r in links
        )
        rel = f'<h2>Neighborhood Guides Mentioned</h2><div class="card-grid">{cards}</div>'
    body = (
        hero(p["category"], p["title"], esc(p["description"]),
             f'By <a href="/">{esc(AGENT)}</a> · {esc(BRAND)} · Published {fmt_date(p["date"])}' + (f' · Updated {fmt_date(p["updated"])}' if p.get("updated") and p["updated"] != p["date"] else ""))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-grid"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">Quick answer</span><p>{p["tldr"]}</p></div>'
        + p["body"] + rel + sources_html(p.get("sources"))
        + f'<p class="post-meta" style="margin-top:2rem;">Written by {esc(AGENT)}, REALTOR® with {esc(BRAND)}. This article is general information, not legal or financial advice.</p>'
        + "</article>"
        + side_card(f"Questions? Ask {AGENT}.", f"{AGENT} helps Hampton Roads buyers, sellers and military families with {BRAND}.")
        + "</div></main>"
        + faq_html(p.get("faqs", []), "Quick Answers")
    )
    title = f"{p['title']} | {AGENT}"
    ld = [
        AGENT_NODE, crumbs_ld(crumbs),
        {"@type": "BlogPosting", "@id": BASE + path + "#article", "mainEntityOfPage": BASE + path, "headline": p["title"],
         "description": p["description"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
         "author": {"@id": BASE + "/#chris-jenkins"}, "image": OG_IMAGE, "articleSection": p["category"],
         "keywords": ", ".join(p.get("keywords", [])), "inLanguage": "en-US",
         "publisher": {"@type": "RealEstateAgent", "name": f"{AGENT} – {BRAND}", "url": BASE + "/", "telephone": PHONE_TEL, "logo": {"@type": "ImageObject", "url": BASE + "/logo.png"}},
         "citation": [u for _, u in p.get("sources", [])]},
    ]
    if p.get("faqs"):
        ld.append(faq_ld(p["faqs"]))
    write(path.strip("/") + "/index.html", page(path, title, p["description"], body, ld, "article", p["date"], p.get("updated")))
    urls.append((path, p.get("updated", p["date"]), "0.6"))


def build_blog_index():
    path = "/blog/"
    crumbs = [("Home", "/"), ("Blog", path)]
    cards = "".join(
        f'<a class="link-card" href="/blog/{p["slug"]}/"><div class="post-meta">{esc(p["category"])} · {fmt_date(p["date"])}</div><h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p><span class="more">Read →</span></a>'
        for p in POSTS
    )
    desc = f"The {AGENT} real estate blog: Hampton Roads buying and selling guides, military PCS and VA loan tips, and Chesapeake, Virginia Beach and Norfolk insight from {BRAND}."
    body = (
        hero("The Chris Jenkins Real Estate Blog", "Hampton Roads Real Estate Blog", f"Practical guides for buying, selling and relocating in Chesapeake, Virginia Beach, Norfolk and all of Hampton Roads, from {AGENT} of {BRAND}.")
        + crumbs_html(crumbs)
        + f'<main class="sub"><div class="sub-wide"><div class="card-grid">{cards}</div></div></main>'
    )
    title = f"Hampton Roads Real Estate Blog | {AGENT} – {BRAND}"
    ld = [AGENT_NODE, crumbs_ld(crumbs),
          {"@type": "Blog", "@id": BASE + path + "#blog", "url": BASE + path, "name": title, "description": desc, "author": {"@id": BASE + "/#chris-jenkins"},
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": BASE + f"/blog/{p['slug']}/", "datePublished": p["date"]} for p in POSTS[:20]]}]
    write("blog/index.html", page(path, title, desc, body, ld))
    urls.append((path, POSTS[0]["date"] if POSTS else TODAY, "0.8"))
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{BASE}/blog/{p['slug']}/</link><guid>{BASE}/blog/{p['slug']}/</guid>"
        f"<pubDate>{datetime.datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y 12:00:00 +0000')}</pubDate><description>{esc(p['description'])}</description></item>"
        for p in POSTS[:50]
    )
    write("blog/feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(AGENT)} Real Estate Blog</title><link>{BASE}/blog/</link><description>{esc(desc)}</description>{items}</channel></rss>')


# ---------------- site files ----------------
def build_site_files():
    rows = [("/", TODAY, "1.0")] + sorted(urls, key=lambda x: x[0])
    sm = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{m}</lastmod><priority>{pr}</priority></url>" for p, m, pr in rows)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot", "Bingbot", "Googlebot"]
    robots = "User-agent: *\nAllow: /\nDisallow: /_tools/\nDisallow: /data/\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in ai_bots) + f"Sitemap: {BASE}/sitemap.xml\n"
    write("robots.txt", robots)
    lines = [f"# {AGENT} – {BRAND}", "",
             f"> {AGENT} is a full-time REALTOR® serving Chesapeake, Virginia Beach, Norfolk and all of Hampton Roads, Virginia. Over $100M in sales, 500+ homes sold, HRRA Circle of Excellence 2013–present. Specializes in home buyers, home sellers and military PCS relocation. Phone {PHONE_DISPLAY}.", "",
             "## Core pages", f"- [Home]({BASE}/): About {AGENT}, services, client reviews, FAQ and contact", f"- [Neighborhood guides]({BASE}/neighborhoods/): Community-by-community Hampton Roads guides", f"- [Blog]({BASE}/blog/): Buying, selling, VA loan and relocation guides", "", "## Cities"]
    lines += [f"- [{c['name']}, VA]({BASE}/neighborhoods/{c['slug']}/): {c['card']}" for c in CITIES.values()]
    lines += ["", "## Neighborhood guides"] + [f"- [{h['name']}, {CITIES[h['city_slug']]['name']}]({BASE}/neighborhoods/{h['city_slug']}/{h['slug']}/): {h['card']}" for h in HOODS]
    lines += ["", "## Latest blog posts"] + [f"- [{p['title']}]({BASE}/blog/{p['slug']}/): {p['description']}" for p in POSTS[:30]]
    write("llms.txt", "\n".join(lines) + "\n")
    write("_redirects", "/_tools/*  /404.html  404!\n/data/*  /404.html  404!\n/README.md  /404.html  404!\n")
    nf = hero("Page Not Found", "That page isn't here", f"Try the <a href='/neighborhoods/' style='color:var(--gold-lt)'>neighborhood guides</a>, the <a href='/blog/' style='color:var(--gold-lt)'>blog</a>, or call {esc(AGENT)} at {PHONE_DISPLAY}.")
    nf_page = page("/404.html", f"Page Not Found | {AGENT}", "Page not found.", nf, [AGENT_NODE]).replace('content="index, follow, max-image-preview:large, max-snippet:-1"', 'content="noindex"')
    write("404.html", nf_page)


for c in CITIES.values():
    build_city(c)
for h in HOODS:
    build_hood(h)
build_hood_index()
for p in POSTS:
    build_post(p)
build_blog_index()
build_site_files()
print(f"built {len(CITIES)} city hubs, {len(HOODS)} neighborhoods, {len(POSTS)} posts, {len(urls)+1} sitemap urls")
