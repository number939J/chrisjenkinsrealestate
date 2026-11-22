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
GUIDE_URL = "/blog/hampton-roads-home-buying-and-selling-checklist/"
BRAND = "Better Homes and Gardens Real Estate – Native American Group"
AGENT = "Chris Jenkins"
PHONE_DISPLAY, PHONE_TEL = "(757) 286-7255", "+17572867255"
# Business address and profile links as shown on Chris's Google Business Profile
ADDR = {"@type": "PostalAddress", "streetAddress": "5224 Indian River Rd, Suite 104", "addressLocality": "Virginia Beach", "addressRegion": "VA", "postalCode": "23464", "addressCountry": "US"}
ADDR_LINE = "5224 Indian River Rd, Suite 104, Virginia Beach, VA 23464"
GBP_MAP = "https://www.google.com/maps?cid=8369621191773639772"
ZILLOW = "https://www.zillow.com/profile/Christopher%20Jenkins/"
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
    <span class="nav-name">Chris Jenkins</span>
  </a>
  <ul class="nav-links">
    <li><a href="/#about">About</a></li>
    <li><a href="/neighborhoods/">Neighborhoods</a></li>
    <li><a href="/questions/">Questions</a></li>
    <li><a href="/blog/">Blog</a></li>
    <li><a href="/#testimonials">Reviews</a></li>
    <li><a href="/#contact" class="nav-cta">Free Consultation</a></li>
  </ul>
</nav>"""

GA_TAG = """<!-- Google tag (GA4) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-S1R13TNLR9"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-S1R13TNLR9');</script>
    <script defer src="/assets/chris-track.js"></script>"""

FLOAT = """<a class="talk-float" href="/talk-to-chris/" aria-label="Talk to Chris Jenkins now"><img src="/assets/chris-thumb.jpg" width="56" height="56" alt="" /><span>Talk to Chris Now</span></a>"""
SCRIPT_FONT = '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap" rel="stylesheet" />'

FOOTER = f"""<footer>
  <div class="footer-links">
    <a href="/">Home</a><a href="/neighborhoods/">Hampton Roads Neighborhoods</a><a href="/questions/">Hampton Roads Real Estate Questions</a><a href="/tools/neighborhood-compare/">Compare Neighborhoods</a><a href="/tools/va-loan-payment-calculator/">VA Loan Calculator</a><a href="/we-buy-houses-hampton-roads/">Sell Your House for Cash</a><a href="/videos/">Videos</a><a href="/blog/">Real Estate Blog</a><a href="/talk-to-chris/">Talk to Chris</a><a href="/#contact">Contact Chris Jenkins</a>
  </div>
  <p>© {datetime.date.today().year} Chris Jenkins · {BRAND} · All Rights Reserved</p>
  <p style="margin-top:0.4rem;">{ADDR_LINE} · <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> · <a href="{GBP_MAP}" rel="noopener">Find us on Google Maps</a></p>
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
    "address": ADDR,
    "hasMap": GBP_MAP,
    "sameAs": [GBP_MAP, ZILLOW],
    "worksFor": {"@type": "RealEstateAgent", "name": BRAND, "address": ADDR},
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


def page(path, title, desc, body, ld_graph, og_type="website", published=None, modified=None, contact=None, scripts=None, extra_head="", og_image=None):
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
  <meta property="og:image" content="{og_image or OG_IMAGE}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  {og_extra}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  {FONTS}
  <link rel="stylesheet" href="/assets/site.css" />
  {SCRIPT_FONT}
  <link rel="stylesheet" href="/assets/chris-float.css" />
  {extra_head}
  {GA_TAG}
  {jsonld({"@context": "https://schema.org", "@graph": ld_graph})}
</head>
<body>
{NAV}
"""
    return head + body + "\n" + (contact or CONTACT) + "\n<!-- FOOTER -->\n" + FAIR + "\n" + FOOTER + "\n" + (scripts or SCRIPTS) + "\n" + FLOAT + "\n</body>\n</html>\n"


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
QUESTIONS = load_dir("questions")
Q_BY = {q["slug"]: q for q in QUESTIONS}
POSTS = sorted(load_dir("posts"), key=lambda p: p["date"], reverse=True)
HOOD_BY = {(h["city_slug"], h["slug"]): h for h in HOODS}
CASH = load_dir("cash")  # "we buy houses" / cash-offer landing pages (data/cash/*.json)
CASH_BY = {c["slug"]: c for c in CASH}
CASH_HUB = "we-buy-houses-hampton-roads"
CASH_CITIES = [("virginia-beach", "Virginia Beach"), ("norfolk", "Norfolk"), ("chesapeake", "Chesapeake"), ("newport-news", "Newport News"), ("hampton", "Hampton"), ("portsmouth", "Portsmouth"), ("suffolk", "Suffolk")]
cash_city_slug = lambda cs: f"we-buy-houses-{cs}-va"
urls = []  # (path, lastmod, priority)


# ---------------- cash-offer ("we buy houses") landing pages ----------------
def cash_city_note(cs, name):
    if cash_city_slug(cs) not in CASH_BY:
        return ""
    return (f'<h2>Need to Sell Your {esc(name)} Home Fast?</h2><p>If you would rather skip repairs and showings, {esc(AGENT)} makes '
            f'<a href="/{cash_city_slug(cs)}/">cash offers on {esc(name)} homes</a> and will tell you honestly when listing would net you more. '
            f'See also the guide to <a href="/{CASH_HUB}/">cash home buyers across Hampton Roads</a>.</p>')


def cash_hood_note(cs, hood_name, city_name):
    if cash_city_slug(cs) not in CASH_BY:
        return ""
    return (f'<h2>Selling Fast in {esc(hood_name)}?</h2><p>If you need to sell without repairs or showings, '
            f'<a href="/{cash_city_slug(cs)}/">see how a cash sale works in {esc(city_name)}</a> and compare it with listing.</p>')


CASH_CONTACT = f"""<!-- CONTACT -->
<section id="contact">
  <div class="contact-inner">
    <p class="section-eyebrow">Get Your Cash Offer</p>
    <h2 class="section-title">Tell Me About Your House</h2>
    <div class="section-line center" style="background:var(--gold);"></div>
    <p class="contact-sub">Share the address and a little about your situation. I will review it personally and follow up with a no-obligation offer, or tell you honestly if listing would serve you better. Prefer to talk first? Call or text {PHONE_DISPLAY}.</p>
    <div id="contactSuccess">Thank you! I'll review your property and be in touch within one business day.<br/><small style="font-size:0.8rem;font-family:'Montserrat',sans-serif;color:rgba(255,255,255,0.5);margin-top:0.5rem;display:block;">Or call me directly: {PHONE_DISPLAY}</small></div>
    <form class="contact-form" id="cashForm" onsubmit="handleCashForm(event)">
      <div class="form-group"><label for="k-address">Property Address</label><input type="text" id="k-address" required autocomplete="street-address" placeholder="123 Main St, Norfolk, VA" /></div>
      <div class="form-row">
        <div class="form-group"><label for="k-first">First Name</label><input type="text" id="k-first" required placeholder="Jane" /></div>
        <div class="form-group"><label for="k-last">Last Name</label><input type="text" id="k-last" required placeholder="Smith" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label for="k-phone">Phone Number</label><input type="tel" id="k-phone" required placeholder="(757) 555-0100" /></div>
        <div class="form-group"><label for="k-email">Email Address</label><input type="email" id="k-email" placeholder="jane@email.com" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label for="k-situation">What's Going On?</label><select id="k-situation"><option value="">Select one</option><option>Needs repairs / sell as-is</option><option>Inherited or probate</option><option>Behind on payments / foreclosure</option><option>Divorce or separation</option><option>Relocating or PCS move</option><option>Tired landlord / rental property</option><option>Vacant property</option><option>Other</option></select></div>
        <div class="form-group"><label for="k-timeline">How Soon Do You Need to Sell?</label><select id="k-timeline"><option value="">Select one</option><option>As soon as possible</option><option>Within 30 days</option><option>1 to 3 months</option><option>Just exploring options</option></select></div>
      </div>
      <div class="form-group"><label for="k-message">Anything Else I Should Know? (Optional)</label><textarea id="k-message" placeholder="Condition, tenants, mortgage, timing…"></textarea></div>
      <button type="submit" class="form-submit">Request My Cash Offer</button>
    </form>
    <div class="contact-direct">
      <div class="direct-item"><div class="direct-label">Call or Text</div><a href="tel:{PHONE_TEL}" class="direct-value">{PHONE_DISPLAY}</a></div>
      <div class="direct-item"><div class="direct-label">Email</div><a href="mailto:{EMAIL}" class="direct-value">{EMAIL}</a></div>
    </div>
  </div>
</section>"""

CASH_SCRIPTS = """<script>
  document.querySelectorAll('.faq-q').forEach(q => {
    q.addEventListener('click', () => {
      const item = q.parentElement, wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });
  async function handleCashForm(e) {
    e.preventDefault();
    const form = e.target, btn = form.querySelector('button[type="submit"]'), orig = btn.textContent, v = id => document.getElementById(id).value;
    btn.textContent = 'Sending…'; btn.disabled = true;
    const fd = new FormData();
    fd.append('name', v('k-first') + ' ' + v('k-last'));
    fd.append('email', v('k-email'));
    fd.append('phone', v('k-phone'));
    fd.append('type', 'Cash offer request');
    fd.append('address', v('k-address'));
    fd.append('situation', v('k-situation'));
    fd.append('timeline', v('k-timeline'));
    fd.append('message', v('k-message'));
    fd.append('page', location.href);
    fd.append('_subject', 'New CASH OFFER Lead — ' + location.pathname);
    try {
      const res = await fetch('https://formspree.io/f/xykvnplp', { method: 'POST', body: fd, headers: { 'Accept': 'application/json' } });
      if (res.ok) { if (window.gtag) gtag('event','generate_lead',{form_name:'cash_offer',page_path:location.pathname}); document.getElementById('contactSuccess').style.display = 'block'; form.style.display = 'none'; }
      else { alert('Something went wrong. Please call (757) 286-7255.'); btn.textContent = orig; btn.disabled = false; }
    } catch { alert('Network error. Please call (757) 286-7255.'); btn.textContent = orig; btn.disabled = false; }
  }
</script>"""

CASH_CSS = '<link rel="stylesheet" href="/assets/cash.css" />'


def cash_cards(exclude=None):
    out = []
    for cs, nm in CASH_CITIES:
        slug = cash_city_slug(cs)
        if slug in CASH_BY and slug != exclude:
            out.append(f'<a class="link-card" href="/{slug}/"><h3>{esc(nm)}, VA</h3><p>{esc(CASH_BY[slug]["card"])}</p><span class="more">Cash offers in {esc(nm)} →</span></a>')
    return "".join(out)


def cash_shared(p):
    """Shared explainer blocks. Kept short so each page is mostly its own local content."""
    nm = p.get("city_name") or "Hampton Roads"
    steps = (
        f"<h2>How Selling to Chris Works in {esc(nm)}</h2><ol>"
        "<li><strong>Tell me about the house.</strong> Send the address, the condition and your timeline through the form below or call me. A rough description is enough to start.</li>"
        "<li><strong>I review it and put the offer in writing.</strong> I look at the property, recent nearby sales and the work the house needs, then give you a no-obligation written offer. You can compare it with what listing would likely bring.</li>"
        "<li><strong>You decide, and you set the pace.</strong> If you accept, we close through a Virginia title company or attorney on a date that fits your situation. If you decline, you owe nothing.</li></ol>"
    )
    rows = [
        ("Price", "A cash offer usually comes in below what a repaired, well-marketed home can fetch on the open market. You are paying for speed, certainty and convenience."),
        ("Speed", "A cash buyer does not wait on mortgage approval or a lender appraisal. A listing depends on how fast the right buyer and their financing line up."),
        ("Repairs and showings", "Sell as-is with no repairs, staging or open houses, versus preparing and showing the home when you list."),
        ("Certainty", "Fewer contingencies means fewer ways for the deal to fall through, though every sale still depends on clear title and a signed contract."),
        ("Costs", 'No listing commission on a direct sale, but closing costs and taxes still apply. Virginia’s state recordation tax is 25 cents per $100 of the price (<a href="https://law.lis.virginia.gov/vacodefull/title58.1/chapter8/" rel="noopener nofollow" target="_blank">Va. Code § 58.1-801</a>), and other fees can apply. Your settlement agent itemizes all of it.'),
    ]
    compare = (
        f"<h2>Cash Sale vs. Listing With an Agent in {esc(nm)}</h2><table class=\"facts\">"
        + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
        + "</table><p>If your home is in good shape and you are not in a hurry, listing with an agent will often net you more, and I will tell you that straight. I am a full-time REALTOR®, so I can help you either way.</p>"
    )
    disclose = (
        "<h2>Who You Would Be Selling To</h2>"
        f"<p>I am {esc(AGENT)}, a licensed Virginia real estate agent with {esc(BRAND)}. If you sell your home directly to me or to a company I own, I am the buyer, not your agent, and I will tell you so in writing before you sign anything. "
        "You are always free to talk with a REALTOR®, an attorney or a tax advisor first, and to compare my offer with listing the home. "
        f'See my <a href="/#testimonials">client reviews</a> and my <a href="/talk-to-chris/">background</a>.</p>'
    )
    return steps + compare + disclose


def build_cash(p):
    path = f"/{p['slug']}/"
    hub = p["kind"] == "hub"
    nm = p.get("city_name") or "Hampton Roads"
    crumbs = [("Home", "/")]
    if not hub:
        crumbs.append(("We Buy Houses in Hampton Roads", f"/{CASH_HUB}/"))
    crumbs.append((p["crumb"], path))
    cta = f'<p class="cash-cta"><a class="cash-btn" href="#contact">Get My Cash Offer</a><a class="cash-call" href="tel:{PHONE_TEL}">Or call {PHONE_DISPLAY}</a></p>'
    who = (
        '<table class="facts">'
        f'<tr><th>Who you are dealing with</th><td>{esc(AGENT)}, licensed Virginia REALTOR® with {esc(BRAND)}, a Hampton Roads native</td></tr>'
        '<tr><th>Track record as a Realtor</th><td>500+ homes sold and over $100 million in sales; HRRA Circle of Excellence winner every year since 2013; 200+ five-star reviews (<a href="/#testimonials">read them</a>)</td></tr>'
        f'<tr><th>Office</th><td>{ADDR_LINE} · <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></td></tr>'
        f'<tr><th>Areas</th><td>Virginia Beach, Norfolk, Chesapeake, Newport News, Hampton, Portsmouth and Suffolk</td></tr></table>'
    )
    secs = "".join(f"<h2>{esc(s['h2'])}</h2>{s['html']}" for s in p["sections"])
    more = cash_cards(None if hub else cash_city_slug(p.get("city_slug", "")))
    more_h = "Cash Offers Across Hampton Roads" if hub else "We Also Buy Houses in These Hampton Roads Cities"
    guides = "".join(
        f'<a class="link-card" href="{esc(g["href"])}"><h3>{esc(g["title"])}</h3><p>{esc(g["text"])}</p><span class="more">Read →</span></a>' for g in p.get("guides", [])
    )
    guides_html = f'<h2>Helpful Guides</h2><div class="card-grid">{guides}</div>' if guides else ""
    body = (
        hero(p["eyebrow"], p["h1"], p["lede"], byline_html(p["updated"]))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-grid"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">The short answer</span><p>{p["tldr"]}</p></div>'
        + cta + who + secs + cash_shared(p) + guides_html
        + f'<h2>{esc(more_h)}</h2><div class="card-grid">{more}</div>'
        + sources_html(p.get("sources"))
        + f'<p class="post-meta" style="margin-top:2rem;">This page is general information, not legal, tax or financial advice. Talk with a Virginia attorney or tax professional about your specific situation.</p>'
        + "</article>"
        + f'<aside class="side-card"><h3>Want a cash offer on your {esc(nm)} house?</h3><p>Send the address and your timeline. No obligation, and I will tell you honestly if listing would net you more.</p>'
        + f'<a class="hero-btn" href="#contact">Get My Cash Offer</a><div class="side-contact">{esc(AGENT)} · {esc(BRAND)}<br/><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div></aside>'
        + "</div></main>"
        + faq_html(p["faqs"], p.get("faq_heading", f"{nm} Cash Sale Questions, Answered"))
    )
    title = p["title"]
    area = (
        [{"@type": "City", "name": n, "containedInPlace": {"@type": "State", "name": "Virginia"}} for _, n in CASH_CITIES]
        if hub else {"@type": "City", "name": nm, "containedInPlace": {"@type": "State", "name": "Virginia"}}
    )
    ld = [
        AGENT_NODE, crumbs_ld(crumbs),
        {"@type": "WebPage", "@id": BASE + path + "#webpage", "url": BASE + path, "name": title, "description": p["description"],
         "dateModified": p["updated"], "inLanguage": "en-US", "isPartOf": {"@type": "WebSite", "name": f"{AGENT} – {BRAND}", "url": BASE + "/"},
         "author": {"@id": BASE + "/#chris-jenkins"}, "about": {"@id": BASE + path + "#service"}},
        {"@type": "Service", "@id": BASE + path + "#service", "name": p.get("service_name", f"Cash home buying in {nm}, Virginia"),
         "serviceType": "Cash home purchase", "description": p["description"], "url": BASE + path,
         "provider": {"@id": BASE + "/#chris-jenkins"}, "areaServed": area},
        faq_ld(p["faqs"]),
    ]
    write(path.strip("/") + "/index.html", page(path, title, p["description"], body, ld, contact=CASH_CONTACT, scripts=CASH_SCRIPTS, extra_head=CASH_CSS))
    urls.append((path, p["updated"], "0.9" if p["kind"] in ("hub", "city") else "0.8"))


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
        + (lambda cs, sl, rel0: f'<h2>Compare {esc(h["name"])} and Ask Questions</h2><p>See {esc(h["name"])} next to another neighborhood with the <a href="/tools/neighborhood-compare/?a={cs}/{sl}&b={cs}/{rel0 or sl}">free neighborhood compare tool</a>, or read our short answers on <a href="/questions/median-home-price-{cs}-va/">{esc(city["name"])} home prices</a> and <a href="/questions/days-to-sell-a-house-{cs}-va/">how long homes take to sell in {esc(city["name"])}</a>.</p>' if cs in ("chesapeake", "virginia-beach") else "")(h["city_slug"], h["slug"], (h.get("related") or [None])[0])
        + cash_hood_note(h["city_slug"], h["name"], city["name"])
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
        + cash_city_note(c["slug"], c["name"])
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
def post_image(p):
    """Return (root-relative url, absolute url) of the post's header image, or (None, None)."""
    rel = f"/assets/blog/{p['slug']}.jpg"
    if os.path.exists(os.path.join(ROOT, rel.lstrip("/"))):
        return rel, BASE + rel
    return None, None


def build_post(p):
    img, img_abs = post_image(p)
    fig = ""
    if img:
        alt = esc((p.get("image") or {}).get("alt") or f"{p['title']} - {AGENT}, REALTOR")
        fig = f'<figure class="post-figure"><img src="{img}" width="1672" height="941" alt="{alt}" fetchpriority="high" /></figure>'
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
        + fig
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
         "author": {"@id": BASE + "/#chris-jenkins"}, "image": img_abs or OG_IMAGE, "articleSection": p["category"],
         "keywords": ", ".join(p.get("keywords", [])), "inLanguage": "en-US",
         "publisher": {"@type": "RealEstateAgent", "name": f"{AGENT} – {BRAND}", "url": BASE + "/", "telephone": PHONE_TEL, "logo": {"@type": "ImageObject", "url": BASE + "/logo.png"}},
         "citation": [u for _, u in p.get("sources", [])]},
    ]
    if p.get("faqs"):
        ld.append(faq_ld(p["faqs"]))
    write(path.strip("/") + "/index.html", page(path, title, p["description"], body, ld, "article", p["date"], p.get("updated"), og_image=img_abs))
    urls.append((path, p.get("updated", p["date"]), "0.6"))


# ---------------- questions (answer-first pages) ----------------
def build_question(q):
    path = f"/questions/{q['slug']}/"
    crumbs = [("Home", "/"), ("Questions", "/questions/"), (q["question"], path)]
    rel_q = [Q_BY[x] for x in q.get("related", []) if x in Q_BY]
    rel_html = ""
    if rel_q:
        rel_html = "<h2>Related Questions</h2><ul class=\"qlist\">" + "".join(f'<li><a href="/questions/{r["slug"]}/">{esc(r["question"])}</a></li>' for r in rel_q) + "</ul>"
    links = [HOOD_BY[tuple(x)] for x in q.get("related_neighborhoods", []) if tuple(x) in HOOD_BY]
    hood_html = ""
    if links:
        cards = "".join(f'<a class="link-card" href="/neighborhoods/{r["city_slug"]}/{r["slug"]}/"><h3>{esc(r["name"])}</h3><p>{esc(r["card"])}</p><span class="more">Explore →</span></a>' for r in links)
        hood_html = f'<h2>Neighborhood Guides Mentioned</h2><div class="card-grid">{cards}</div>'
    body = (
        hero(q["category"], q["question"], esc(q["description"]), byline_html(q["updated"]))
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-grid"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">Short answer</span><p>{q["answer"]}</p></div>'
        + q["body"] + hood_html + rel_html + sources_html(q.get("sources"))
        + f'<p class="post-meta" style="margin-top:2rem;">Answered by {esc(AGENT)}, REALTOR® with {esc(BRAND)}. General information, not legal, tax or financial advice, and not an appraisal.</p>'
        + "</article>"
        + side_card(f"Questions? Ask {AGENT}.", f"{AGENT} helps Hampton Roads buyers, sellers and military families with {BRAND}.")
        + "</div></main>"
        + faq_html(q.get("faqs", []), "More Quick Answers")
    )
    title = f"{q['question']} | {AGENT}"
    ld = [
        AGENT_NODE, crumbs_ld(crumbs),
        {"@type": "WebPage", "@id": BASE + path + "#webpage", "url": BASE + path, "name": q["question"], "description": q["description"],
         "datePublished": q.get("date", q["updated"]), "dateModified": q["updated"], "inLanguage": "en-US",
         "author": {"@id": BASE + "/#chris-jenkins"}, "isPartOf": {"@type": "WebSite", "url": BASE + "/", "name": f"{AGENT} – {BRAND}"},
         "citation": [u for _, u in q.get("sources", [])]},
        faq_ld([(q["question"], q["answer"])] + [tuple(x) for x in q.get("faqs", [])]),
    ]
    write(path.strip("/") + "/index.html", page(path, title, q["description"], body, ld, "article", q.get("date", q["updated"]), q["updated"]))
    urls.append((path, q["updated"], "0.7"))


def build_questions_index():
    path = "/questions/"
    crumbs = [("Home", "/"), ("Questions", path)]
    cats = []
    for q in QUESTIONS:
        if q["category"] not in cats: cats.append(q["category"])
    sec = ""
    for c in cats:
        items = "".join(f'<li><a href="/questions/{q["slug"]}/"><strong>{esc(q["question"])}</strong></a><br/>{q["answer_short"]}</li>' for q in QUESTIONS if q["category"] == c)
        sec += f'<h2>{esc(c)}</h2><ul class="qlist">{items}</ul>'
    desc = f"Straight answers to Hampton Roads home buying and selling questions, with REIN MLS data for Chesapeake and Virginia Beach, from {AGENT}."
    body = (
        hero("Ask Chris Jenkins", "Hampton Roads Real Estate Questions, Answered", f"Short, sourced answers to the questions buyers and sellers ask most, built on closed-sale data from REIN MLS. From {esc(AGENT)}, {esc(BRAND)}.")
        + crumbs_html(crumbs)
        + f'<main class="sub"><div class="sub-wide"><article class="prose">{sec}'
        + f'<p>Have a question that is not here? Call or text <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or <a href="#contact">send it through the form</a> and it may become the next answer.</p></article></div></main>'
    )
    title = f"Hampton Roads Real Estate Questions Answered | {AGENT}"
    ld = [AGENT_NODE, crumbs_ld(crumbs),
          {"@type": "CollectionPage", "@id": BASE + path + "#page", "url": BASE + path, "name": title, "description": desc, "author": {"@id": BASE + "/#chris-jenkins"},
           "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + f"/questions/{q['slug']}/", "name": q["question"]} for i, q in enumerate(QUESTIONS)]}}]
    write("questions/index.html", page(path, title, desc, body, ld))
    urls.append((path, max([q["updated"] for q in QUESTIONS] + [TODAY]) if QUESTIONS else TODAY, "0.8"))


# ---------------- free tool: neighborhood compare ----------------
def build_tool():
    stats = json.load(open(os.path.join(ROOT, "assets", "neighborhood-stats.json"), encoding="utf-8"))
    hs = stats["hoods"]; names = stats["city_names"]
    path = "/tools/neighborhood-compare/"
    crumbs = [("Home", "/"), ("Tools", path), ("Neighborhood Compare Tool", path)]
    crumbs = [("Home", "/"), ("Compare Hampton Roads Neighborhoods", path)]
    rows = ""
    for h in sorted(hs, key=lambda x: (x["c"], -x["m"])):
        rows += (f'<tr><th scope="row"><a href="/neighborhoods/{h["c"]}/{h["s"]}/">{esc(h["n"])}</a></th><td>{esc(names[h["c"]])}</td><td class="num">{h["k"]}</td>'
                 f'<td class="num">${h["m"]:,}</td><td class="num">${h["p"]:,}</td><td class="num">{h["d"]}</td><td class="num">{h["y"] or ""}</td></tr>')
    full = (f'<div class="table-wrap"><table class="data-table"><caption>All {len(hs)} neighborhoods, REIN MLS closed sales {esc(stats["window"])}</caption><thead><tr><th scope="col">Neighborhood</th><th scope="col">City</th><th scope="col" class="num">Sales</th>'
            f'<th scope="col" class="num">Median sold price</th><th scope="col" class="num">Price per sq ft</th><th scope="col" class="num">Median days on market</th><th scope="col" class="num">Median year built</th></tr></thead><tbody>{rows}</tbody></table></div>')
    embed_code = f'&lt;iframe src="{BASE}/tools/neighborhood-compare/embed/" width="100%" height="640" style="border:0" title="Hampton Roads neighborhood comparison"&gt;&lt;/iframe&gt;'
    faqs = [
        ("What does the neighborhood compare tool show?", "It puts two Chesapeake or Virginia Beach neighborhoods side by side using REIN MLS closed sales: median sold price, price per square foot, days on market, home size, year built and sale-to-list ratio, with multiples showing how far apart they are."),
        ("Where does the data come from?", f"REIN MLS closed residential sales between {stats['window'].replace(' to ', ' and ')}. Medians are used so a few unusual sales do not skew the numbers, and neighborhoods follow MLS subdivision names."),
        ("Is the tool free to use or embed?", f"Yes. It is free, and you can embed it on your own site with the code on this page. The embed links back to {AGENT} at {BRAND}."),
    ]
    desc = f"Free tool: compare two Chesapeake or Virginia Beach neighborhoods side by side with REIN MLS median prices, price per square foot, days on market and more. By {AGENT}."
    body = (
        hero("Free Tool", "Compare Hampton Roads Neighborhoods Side by Side", f"Pick any two of {len(hs)} Chesapeake and Virginia Beach neighborhoods to compare closed-sale prices, price per square foot, pace and home age. Built by {esc(AGENT)} from REIN MLS data.")
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-wide"><article class="prose">'
        + f'<div class="tldr"><span class="tldr-label">What this does</span><p>Choose two neighborhoods and see their median sold price, price per square foot, days on market, home size and age next to each other, with a multiple showing the gap. Figures come from REIN MLS closed sales between {esc(stats["window"].replace(" to ", " and "))}.</p></div>'
        + '<div id="compare-tool"><div class="cmp-controls"><div><label for="cmp-a">First neighborhood</label><select id="cmp-a"></select></div><div><label for="cmp-b">Second neighborhood</label><select id="cmp-b"></select></div></div><div id="cmp-out" aria-live="polite"></div></div>'
        + f'<h2>All {len(hs)} Neighborhoods at a Glance</h2>{full}'
        + f'<h2>How to Read the Comparison</h2><p>The multiple column shows how the second neighborhood compares with the first: 1.4x means 1.4 times as much. Medians describe typical past sales, not any one home, and neighborhoods follow the names agents use in the MLS. Read <a href="{GUIDE_URL}#methodology">how these statistics are calculated</a>, and see our <a href="/questions/">answers to common questions</a> for more.</p>'
        + f'<h2>Embed This Tool on Your Site</h2><p>Copy this code to add the comparison to your own page:</p><p><textarea class="embed-code" rows="3" readonly>{embed_code}</textarea></p>'
        + sources_html([["REIN MLS closed residential sales, Chesapeake and Virginia Beach VA", "https://www.reinmls.com"], ["Hampton Roads Home Buying and Selling Checklist (methodology)", GUIDE_URL]])
        + '</article></div></main>' + faq_html(faqs, "About the Compare Tool")
        + '<script src="/assets/compare.js" defer></script>'
    )
    title = f"Compare Hampton Roads Neighborhoods: Free Tool | {AGENT}"
    ld = [AGENT_NODE, crumbs_ld(crumbs),
          {"@type": "WebApplication", "@id": BASE + path + "#tool", "name": "Hampton Roads Neighborhood Compare Tool", "url": BASE + path, "description": desc,
           "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
           "author": {"@id": BASE + "/#chris-jenkins"}, "dateModified": stats["updated"], "inLanguage": "en-US"},
          faq_ld(faqs)]
    write("tools/neighborhood-compare/index.html", page(path, title, desc, body, ld))
    urls.append((path, stats["updated"], "0.8"))
    emb = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><meta name="robots" content="noindex, follow"/>
<title>Hampton Roads Neighborhood Compare (embed)</title><link rel="canonical" href="{BASE}{path}"/>{FONTS}<link rel="stylesheet" href="/assets/site.css"/></head>
<body style="background:#fff;padding:1rem"><div class="prose"><div id="compare-tool" data-embed="1"><div class="cmp-controls"><div><label for="cmp-a">First neighborhood</label><select id="cmp-a"></select></div><div><label for="cmp-b">Second neighborhood</label><select id="cmp-b"></select></div></div><div id="cmp-out" aria-live="polite"></div></div></div><script src="/assets/compare.js"></script></body></html>"""
    write("tools/neighborhood-compare/embed/index.html", emb)


def build_va_calc():
    path = "/tools/va-loan-payment-calculator/"
    crumbs = [("Home", "/"), ("VA Loan Payment Calculator", path)]
    faqs = [
        ("What is the VA funding fee?", "It is a one-time fee on VA purchase loans. For a first use it is 2.15% with less than 5% down, 1.5% with 5% to under 10% down, and 1.25% with 10% or more down. For subsequent use with less than 5% down it is 3.3%. Veterans receiving VA disability compensation and certain surviving spouses are exempt, so confirm your status with your lender."),
        ("Can I roll the VA funding fee into the loan?", "Yes, the funding fee can generally be financed, which raises the loan amount. This calculator lets you choose either way so you can see the effect on the monthly payment and on cash at closing."),
        ("Is the property tax figure exact?", "No. It multiplies the purchase price by the city's rate per $100 of assessed value, which is a simplification. Your actual bill uses the city's assessed value and may include special district charges, so check the specific property."),
        ("Does this include flood insurance?", "Only if you enter it. Flood insurance varies by address in Hampton Roads, so get a quote for the specific home and enter the yearly premium."),
        ("How should I use the BAH field?", f"Enter your monthly Basic Allowance for Housing from your official pay information. The calculator then shows your estimated payment as a multiple of your BAH. {AGENT} can help you compare homes against that number."),
    ]
    desc = f"Free VA loan payment calculator for Hampton Roads: estimate your monthly payment with the VA funding fee, city property tax, insurance, flood insurance and your BAH. By {AGENT}."
    cities = '<option value="chesapeake">Chesapeake</option><option value="virginia-beach">Virginia Beach</option><option value="other">Other (edit the rate)</option>'
    form = (f'<form id="va-calc" onsubmit="return false"><div class="calc-grid">'
        '<div><label for="price">Purchase price ($)</label><input id="price" type="number" min="0" step="1000" value="400000"></div>'
        '<div><label for="down">Down payment (%)</label><input id="down" type="number" min="0" max="100" step="0.5" value="0"></div>'
        '<div><label for="rate">Interest rate (%) \u2013 use your lender\u2019s quote</label><input id="rate" type="number" min="0" step="0.125" value="6"></div>'
        '<div><label for="term">Loan term (years)</label><select id="term"><option value="30" selected>30</option><option value="15">15</option></select></div>'
        '<div><label for="use">VA loan use</label><select id="use"><option value="first" selected>First use</option><option value="subsequent">Subsequent use</option></select></div>'
        f'<div><label for="city">City (sets the tax rate)</label><select id="city">{cities}</select></div>'
        '<div><label for="taxrate">Real estate tax rate per $100</label><input id="taxrate" type="number" min="0" step="0.01" value="1.01"></div>'
        '<div><label for="ins">Homeowner\u2019s insurance per year ($)</label><input id="ins" type="number" min="0" step="50" value="0"></div>'
        '<div><label for="flood">Flood insurance per year ($)</label><input id="flood" type="number" min="0" step="50" value="0"></div>'
        '<div><label for="hoa">HOA or condo dues per month ($)</label><input id="hoa" type="number" min="0" step="10" value="0"></div>'
        '<div><label for="bah">Your monthly BAH ($, optional)</label><input id="bah" type="number" min="0" step="10" value="0"></div></div>'
        '<label class="calc-check"><input id="finance" type="checkbox" checked> Roll the funding fee into the loan</label>'
        '<label class="calc-check"><input id="exempt" type="checkbox"> I am exempt from the funding fee (for example, VA disability compensation)</label></form>'
        '<div id="va-out" aria-live="polite"></div>')
    body = (
        hero("Free Tool for Military Buyers", "VA Loan Payment Calculator for Hampton Roads", f"Estimate your monthly payment on a VA loan in Chesapeake, Virginia Beach and the rest of Hampton Roads, with the funding fee, property tax, insurance and your BAH. Built by {esc(AGENT)}.")
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-wide"><article class="prose">'
        + '<div class="tldr"><span class="tldr-label">What this does</span><p>Enter a price, down payment and your lender\u2019s rate to see an estimated monthly payment including the VA funding fee, city property tax, insurance and flood insurance, and how it compares with your BAH. The interest rate, insurance and BAH fields are yours to fill in; nothing here is a rate quote.</p></div>'
        + form
        + '<h2>How This Is Calculated</h2><ul><li><strong>Funding fee:</strong> the published VA purchase-loan chart: first use 2.15% (under 5% down), 1.5% (5% to under 10%), 1.25% (10% or more); subsequent use 3.3% under 5% down, then the same 1.5% and 1.25%. Exempt borrowers pay none.</li>'
        + '<li><strong>Property tax:</strong> price times the city rate per $100, divided by 12. Virginia Beach\u2019s general rate is $0.97 per $100 per the city assessor, and Chesapeake is set to $1.01 per $100, the rate Virginia Beach\u2019s city blog cited in February 2025. Confirm the current rate with the city, and note special service districts can add charges.</li>'
        + '<li><strong>Principal and interest:</strong> a standard fixed-rate payment for the term you choose.</li></ul>'
        + f'<p>For flood zones, HOA packets and military noise zones, use our <a href="{GUIDE_URL}">Hampton Roads buying checklist</a>, and see <a href="/questions/do-i-need-flood-insurance-hampton-roads/">whether you need flood insurance</a>. Compare areas with the <a href="/tools/neighborhood-compare/">neighborhood compare tool</a>. This is an estimate for planning, not a loan offer or financial advice; ask a VA-approved lender for exact figures.</p>'
        + sources_html([["VA funding fee rates for purchase loans (summary of the VA chart effective April 7, 2023)", "https://valoannetwork.com/va-loans/va-funding-fee"], ["VA loan funding fee explained (NerdWallet)", "https://www.nerdwallet.com/article/va-loan-funding-fee-explained"], ["City of Virginia Beach: current real estate tax rate ($0.97 per $100)", "https://assessor.virginiabeach.gov/tax-rates"], ["Virginia Beach: real estate tax rate and Chesapeake comparison (Feb. 2025)", "https://virginiabeach.gov/connect/blog/seven-key-takeaways-from-the-real-estate-assessors-annual-report"]])
        + '</article></div></main>' + faq_html(faqs, "About the VA Loan Calculator")
        + '<script src="/assets/va-calc.js" defer></script>'
    )
    title = f"VA Loan Payment Calculator for Hampton Roads | {AGENT}"
    ld = [AGENT_NODE, crumbs_ld(crumbs),
          {"@type": "WebApplication", "@id": BASE + path + "#tool", "name": "VA Loan Payment Calculator for Hampton Roads", "url": BASE + path, "description": desc,
           "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
           "author": {"@id": BASE + "/#chris-jenkins"}, "dateModified": "2026-11-15", "inLanguage": "en-US"},
          faq_ld(faqs)]
    write("tools/va-loan-payment-calculator/index.html", page(path, title, desc, body, ld))
    urls.append((path, "2026-11-15", "0.8"))


VIDEOS = [
 ("flood-insurance", "Do You Need Flood Insurance in Hampton Roads?", "Three steps to check flood risk before you buy a Hampton Roads home: the FEMA flood map, your lender, and a real insurance quote.", "/questions/do-i-need-flood-insurance-hampton-roads/", "Read the full answer"),
 ("va-appraisal-vs-inspection", "VA Appraisal vs. Home Inspection", "What a VA appraisal checks, what it does not, and what to ask your lender before you write an offer.", "/questions/va-loan-appraisal-and-inspection-hampton-roads/", "Read the full answer"),
 ("va-loan-calculator", "VA Loan Payment Calculator for Hampton Roads", "How the free VA loan payment calculator works, with the funding fee, taxes, insurance and your BAH.", "/tools/va-loan-payment-calculator/", "Use the calculator"),
 ("most-active-neighborhoods", "Most Active Neighborhoods in Virginia Beach and Chesapeake", "Which neighborhoods had the most closed home sales in the last two years, from REIN MLS data.", "/questions/most-active-neighborhoods-chesapeake-virginia-beach/", "Read the full answer"),
 ("price-your-home", "How to Price Your Hampton Roads Home to Sell", "Price from closed sales, check speed and discounts, and aim for week one.", "/questions/how-to-price-your-home-to-sell-hampton-roads/", "Read the full answer"),
 ("test-your-commute", "How to Test Your Commute Before You Buy", "Drive it at real hours, include water crossings, and time it to the gate.", "/questions/how-to-test-your-commute-hampton-roads/", "Read the full answer"),
]


YT_IDS = {"flood-insurance": "ZZDO8HTdCks", "va-appraisal-vs-inspection": "0cjqa2CqZB4", "va-loan-calculator": "sJ8aQIkW4-4",
          "most-active-neighborhoods": "_wWQyjndJOA", "price-your-home": "rvK5YHIQOqM", "test-your-commute": "XsdlMNSB7ik"}
YT_CHANNEL = "https://www.youtube.com/channel/UCTdLsGuLyNam8Ybjm1wxr1Q"


def build_videos():
    path = "/videos/"
    tr = json.load(open(os.path.join(ROOT, "data", "video-transcripts.json")))
    du = json.load(open(os.path.join(ROOT, "data", "video-durations.json")))
    crumbs = [("Home", "/"), ("Videos", path)]
    desc = f"Short Hampton Roads real estate videos from {AGENT}: flood insurance, VA loans, pricing your home, neighborhoods and commutes, each with a transcript."
    items, ld_nodes = "", []
    for slug, title, d, link, cta in VIDEOS:
        text = " ".join(tr[slug])
        yid = YT_IDS[slug]
        items += (f'<section class="vid" id="{slug}"><h2>{esc(title)}</h2>'
                  f'<div style="max-width:360px;aspect-ratio:9/16;margin:0 0 1rem"><iframe src="https://www.youtube-nocookie.com/embed/{yid}" title="{esc(title)}" loading="lazy" style="width:100%;height:100%;border:0" allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>'
                  f'<p>{esc(d)} <a href="{link}">{cta}</a>. <a href="https://www.youtube.com/shorts/{yid}" rel="noopener">Watch on YouTube</a>.</p><details><summary>Read the transcript</summary><p>{esc(text)}</p></details></section>')
        ld_nodes.append({"@type": "VideoObject", "@id": BASE + path + "#" + slug, "name": title, "description": d,
                         "thumbnailUrl": BASE + f"/assets/video/{slug}.jpg", "contentUrl": BASE + f"/assets/video/{slug}.mp4", "embedUrl": f"https://www.youtube.com/embed/{yid}",
                         "uploadDate": "2026-11-15", "duration": f"PT{du[slug]}S", "transcript": text,
                         "author": {"@id": BASE + "/#chris-jenkins"}, "publisher": {"@id": BASE + "/#chris-jenkins"}, "inLanguage": "en-US"})
    body = (hero("Videos", "Hampton Roads Real Estate Videos", f"Short answers to common buying and selling questions from {esc(AGENT)}, {esc(BRAND)}. Each video has a transcript and links to the full guide.")
            + crumbs_html(crumbs)
            + '<main class="sub"><div class="sub-wide"><article class="prose">'
            + '<p>The narration in these videos is an AI-generated voice reading scripts written for Chris Jenkins. The facts match the linked pages. This is general information, not legal or financial advice. Subscribe on <a href="' + YT_CHANNEL + '" rel="noopener">YouTube</a>.</p>'
            + items + '</article></div></main>')
    title = f"Hampton Roads Real Estate Videos | {AGENT}"
    ld = [AGENT_NODE, crumbs_ld(crumbs), {"@type": "CollectionPage", "@id": BASE + path + "#page", "name": "Hampton Roads Real Estate Videos", "url": BASE + path, "description": desc}] + ld_nodes
    write("videos/index.html", page(path, title, desc, body, ld))
    urls.append((path, "2026-11-15", "0.7"))


def build_talk():
    path = "/talk-to-chris/"
    crumbs = [("Home", "/"), ("Talk to Chris", path)]
    desc = f"Talk to {AGENT}, REALTOR® with {BRAND}. Call (757) 286-7255 or email with your Hampton Roads buying, selling or relocation questions."
    body = (
        hero("Let's Talk", "Talk to Chris Jenkins", "Questions about buying, selling or moving to Hampton Roads? I would love to hear from you.")
        + crumbs_html(crumbs)
        + '<main class="sub"><div class="sub-wide"><article class="prose">'
        + '<div class="talk-grid"><img class="talk-photo" src="/headshot.jpg" width="280" height="340" alt="Chris Jenkins, REALTOR® with Better Homes and Gardens Real Estate – Native American Group" />'
        + '<div><p>I am Chris Jenkins, a full-time REALTOR® with ' + esc(BRAND) + ' in Chesapeake, Virginia. I help buyers, sellers and military families in Chesapeake, Virginia Beach, Norfolk and across Hampton Roads.</p>'
        + '<p>I would love to talk with you and answer your questions. Maybe you are just starting to look, getting ready to sell, or planning a PCS move and trying to figure out where to begin. Call, text or email me, and I will get back to you as soon as I can.</p>'
        + '<p>A little about my background: HRRA Circle of Excellence award winner (2013 to present), 2013 HRRA Rookie of the Year, over $100M in sales and 500+ homes sold.</p></div></div>'
        + f'<div class="talk-cards"><a class="talk-card" href="tel:{PHONE_TEL}"><strong>Call or text</strong><span>{PHONE_DISPLAY}</span></a>'
        + f'<a class="talk-card" href="mailto:{EMAIL}"><strong>Email</strong><span>{esc(EMAIL)}</span></a>'
        + '<a class="talk-card" href="#contact"><strong>Send a message</strong><span>Use the form below</span></a></div>'
        + '<h2>Not Sure What to Ask?</h2><ul>'
        + '<li><a href="/questions/">Read answers to common Hampton Roads real estate questions</a></li>'
        + '<li><a href="/tools/va-loan-payment-calculator/">Estimate a VA loan payment</a></li>'
        + '<li><a href="/tools/neighborhood-compare/">Compare two neighborhoods</a></li>'
        + '<li><a href="/neighborhoods/">Browse Hampton Roads neighborhoods</a></li></ul>'
        + '</article></div></main>')
    title = f"Talk to {AGENT} | {BRAND}"
    ld = [AGENT_NODE, crumbs_ld(crumbs), {"@type": "ContactPage", "@id": BASE + path + "#page", "name": f"Talk to {AGENT}", "url": BASE + path, "description": desc, "mainEntity": {"@id": BASE + "/#chris-jenkins"}}]
    write("talk-to-chris/index.html", page(path, title, desc, body, ld))
    urls.append((path, "2026-11-15", "0.8"))


def card_img(p):
    img, _ = post_image(p)
    if not img:
        return ""
    return f'<img class="post-card-img" src="{img}" width="1672" height="941" loading="lazy" alt="{esc((p.get("image") or {}).get("alt") or p["title"])}" />'


def build_blog_index():
    path = "/blog/"
    crumbs = [("Home", "/"), ("Blog", path)]
    cards = "".join(
        f'<a class="link-card post-card" href="/blog/{p["slug"]}/">{card_img(p)}<div class="post-meta">{esc(p["category"])} · {fmt_date(p["date"])}</div><h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p><span class="more">Read →</span></a>'
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
             "## Core pages", f"- [Home]({BASE}/): About {AGENT}, services, client reviews, FAQ and contact", f"- [Neighborhood guides]({BASE}/neighborhoods/): Community-by-community Hampton Roads guides", f"- [Blog]({BASE}/blog/): Buying, selling, VA loan and relocation guides", f"- [Questions]({BASE}/questions/): Short, sourced answers to Hampton Roads buying and selling questions", f"- [Talk to Chris]({BASE}/talk-to-chris/): Phone, email and a short introduction", f"- [Videos]({BASE}/videos/): Short Hampton Roads real estate videos with transcripts", f"- [VA loan payment calculator]({BASE}/tools/va-loan-payment-calculator/): Free Hampton Roads VA loan payment estimate with funding fee, taxes and BAH", f"- [Neighborhood compare tool]({BASE}/tools/neighborhood-compare/): Free side-by-side comparison of Hampton Roads neighborhoods", "", "## Cities"]
    lines += [f"- [{c['name']}, VA]({BASE}/neighborhoods/{c['slug']}/): {c['card']}" for c in CITIES.values()]
    if CASH:
        lines += ["", "## Cash offers (we buy houses)"] + [f"- [{p['h1']}]({BASE}/{p['slug']}/): {p['description']}" for p in CASH]
    lines += ["", "## Neighborhood guides"] + [f"- [{h['name']}, {CITIES[h['city_slug']]['name']}]({BASE}/neighborhoods/{h['city_slug']}/{h['slug']}/): {h['card']}" for h in HOODS]
    lines += ["", "## Questions answered"] + [f"- [{q['question']}]({BASE}/questions/{q['slug']}/): {q['description']}" for q in QUESTIONS]
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
for q in QUESTIONS:
    build_question(q)
if QUESTIONS:
    build_questions_index()
for cp in CASH:
    build_cash(cp)
build_tool()
build_va_calc()
build_videos()
build_talk()
build_site_files()
print(f"built {len(CITIES)} city hubs, {len(HOODS)} neighborhoods, {len(POSTS)} posts, {len(CASH)} cash pages, {len(urls)+1} sitemap urls")
