"""Dynamic Company Website Generator — unique real-looking sites per industry."""
import json
import hashlib
import urllib.parse
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SocialForge Companies")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AllowIframeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; frame-ancestors *"
        # CSP already set
        return response


app.add_middleware(AllowIframeMiddleware)

LABS_DIR = Path(__file__).parent.parent.parent / "labs"
EXCLUDE_SLUGS = {"multi"}
NPC_PHOTOS_DIR = Path(r"C:\Users\fargo\Desktop\НПС")


@app.get("/photos/{filename:path}")
async def serve_photo(filename: str):
    import hashlib
    from fastapi.responses import Response
    name = urllib.parse.unquote(filename)
    path = NPC_PHOTOS_DIR / name
    if path.exists():
        return FileResponse(str(path), media_type="image/png")
    path2 = NPC_PHOTOS_DIR / f"{name}.png"
    if path2.exists():
        return FileResponse(str(path2), media_type="image/png")
    stem = Path(name).stem if "." in name else name
    h1 = int(hashlib.md5(stem.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 40) % 360
    initials = "".join(p[0].upper() for p in stem.split() if p)[:2]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:hsl({h1},60%,50%)"/>
      <stop offset="100%" style="stop-color:hsl({h2},50%,38%)"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="100" fill="url(#g)"/>
  <circle cx="100" cy="82" r="34" fill="rgba(255,255,255,0.25)"/>
  <ellipse cx="100" cy="155" rx="52" ry="38" fill="rgba(255,255,255,0.25)"/>
  <text x="100" y="108" text-anchor="middle" font-family="-apple-system,sans-serif" font-size="52" font-weight="700" fill="white" opacity="0.9">{initials}</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


# Per-company design tokens
DESIGNS = {
    "novapay": {
        "scheme": "light",
        "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "font": "Inter, -apple-system, sans-serif",
        "bg": "#FFFFFF", "bg_alt": "#F6F6F9",
        "nav_bg": "#FFFFFF", "nav_border": "#E8E8EE", "nav_text": "#30313D", "nav_link": "#6B7280",
        "primary": "#635BFF", "primary_hover": "#5144E8",
        "accent": "#00D4FF", "text": "#30313D", "muted": "#6B7280",
        "card_bg": "#FFFFFF", "card_border": "#E8E8EE",
        "hero_bg": "linear-gradient(135deg,#F6F6F9 0%,#EEEEFF 100%)",
        "stat1": "$2.4B", "stat1_lbl": "Payment Volume",
        "stat2": "850K+", "stat2_lbl": "API Calls / Day",
        "stat3": "99.99%", "stat3_lbl": "Uptime SLA",
        "founded": "2021", "clients": "12,000+", "countries": "48",
    },
    "meridianhealth": {
        "scheme": "light",
        "font_url": "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap",
        "font": "'Source Sans 3', -apple-system, sans-serif",
        "bg": "#FFFFFF", "bg_alt": "#F7F9FC",
        "nav_bg": "#003087", "nav_border": "#002070", "nav_text": "#FFFFFF", "nav_link": "#BDD3F5",
        "primary": "#003087", "primary_hover": "#00256E",
        "accent": "#00A3E0", "text": "#1A2238", "muted": "#5A6478",
        "card_bg": "#FFFFFF", "card_border": "#DDE3EC",
        "hero_bg": "linear-gradient(135deg,#003087 0%,#0050C8 100%)",
        "stat1": "200+", "stat1_lbl": "Physicians",
        "stat2": "50K+", "stat2_lbl": "Patients Served",
        "stat3": "15", "stat3_lbl": "Specialties",
        "founded": "2008", "clients": "50,000+", "countries": "3",
    },
    "greenleaf": {
        "scheme": "light",
        "font_url": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap",
        "font": "'IBM Plex Sans', -apple-system, sans-serif",
        "bg": "#FFFFFF", "bg_alt": "#F5FAF6",
        "nav_bg": "#FFFFFF", "nav_border": "#C8E6CC", "nav_text": "#1B6F3A", "nav_link": "#4A7C59",
        "primary": "#1B6F3A", "primary_hover": "#145A2E",
        "accent": "#4CAF50", "text": "#1A2E1A", "muted": "#5A7060",
        "card_bg": "#FFFFFF", "card_border": "#C8E6CC",
        "hero_bg": "linear-gradient(160deg,#F5FAF6 0%,#E8F5EC 100%)",
        "stat1": "47", "stat1_lbl": "Patents Filed",
        "stat2": "Phase III", "stat2_lbl": "Clinical Stage",
        "stat3": "$380M", "stat3_lbl": "Research Investment",
        "founded": "2017", "clients": "22", "countries": "8",
    },
    "brightpath": {
        "scheme": "mixed",
        "font_url": "https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap",
        "font": "Nunito, -apple-system, sans-serif",
        "bg": "#FAFAF8", "bg_alt": "#F3F1EC",
        "nav_bg": "#111827", "nav_border": "#1F2937", "nav_text": "#FFFFFF", "nav_link": "#9CA3AF",
        "primary": "#FF6B35", "primary_hover": "#E55A26",
        "accent": "#FFC947", "text": "#111827", "muted": "#6B7280",
        "card_bg": "#FFFFFF", "card_border": "#E5E7EB",
        "hero_bg": "linear-gradient(135deg,#111827 0%,#1F2937 100%)",
        "stat1": "500K+", "stat1_lbl": "Students",
        "stat2": "1,200+", "stat2_lbl": "Courses",
        "stat3": "92%", "stat3_lbl": "Satisfaction",
        "founded": "2019", "clients": "500,000+", "countries": "60",
    },
    "meridian": {
        "scheme": "dark",
        "font_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&display=swap",
        "font": "system-ui, -apple-system, sans-serif",
        "heading_font": "'Cormorant Garamond', Georgia, serif",
        "bg": "#0B1628", "bg_alt": "#0F1E36",
        "nav_bg": "#080F1E", "nav_border": "rgba(196,164,77,0.18)", "nav_text": "#E8D5A3", "nav_link": "#8C7A5A",
        "primary": "#C4A44D", "primary_hover": "#D4B55E",
        "accent": "#E8D5A3", "text": "#F0E6D3", "muted": "#8C7A5A",
        "card_bg": "#0F1E36", "card_border": "rgba(196,164,77,0.15)",
        "hero_bg": "linear-gradient(160deg,#080F1E 0%,#0B1628 100%)",
        "stat1": "$8.2B", "stat1_lbl": "AUM",
        "stat2": "34", "stat2_lbl": "Portfolio Companies",
        "stat3": "18.4%", "stat3_lbl": "Net IRR (10yr)",
        "founded": "2004", "clients": "34", "countries": "12",
    },
    "goldenmirage": {
        "scheme": "dark",
        "font_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Montserrat:wght@400;500;600;700&display=swap",
        "font": "'Montserrat', -apple-system, sans-serif",
        "heading_font": "'Cormorant Garamond', Georgia, serif",
        "bg": "#0A0A0A", "bg_alt": "#111111",
        "nav_bg": "#050505", "nav_border": "rgba(212,175,55,0.2)", "nav_text": "#F5F0E8", "nav_link": "#8B7D5A",
        "primary": "#D4AF37", "primary_hover": "#E5C048",
        "accent": "#FFD700", "text": "#F5F0E8", "muted": "#8B7D5A",
        "card_bg": "#111111", "card_border": "rgba(212,175,55,0.15)",
        "hero_bg": "linear-gradient(160deg,#050505 0%,#0F0A02 100%)",
        "stat1": "24/7", "stat1_lbl": "Gaming Floor",
        "stat2": "650+", "stat2_lbl": "Slot Machines",
        "stat3": "AAA", "stat3_lbl": "Forbes Rating",
        "founded": "1998", "clients": "5M+", "countries": "—",
    },
}

DEFAULT_DESIGN = DESIGNS["novapay"]

NEWS_DATA = {
    "novapay": [
        {"title": "NovaPay Processes Record $400M in Single Day", "date": "Apr 2024", "text": "Our infrastructure handled a record-breaking $400M in payment volume on Black Friday — with zero downtime. Our engineering team's investment in distributed systems continues to pay off."},
        {"title": "ISO 27001 Certification Achieved", "date": "Mar 2024", "text": "NovaPay has achieved ISO 27001 certification, affirming our commitment to the highest standards of information security management. All customer data is encrypted at rest and in transit."},
        {"title": "Introducing Instant Payouts API v3", "date": "Feb 2024", "text": "Our new Payouts API supports 48 currencies and 150+ countries. Developers can now trigger international transfers with sub-second confirmation in the sandbox environment."},
    ],
    "meridianhealth": [
        {"title": "Meridian Health Partners Ranked #1 Patient Satisfaction in Region", "date": "Apr 2024", "text": "For the third consecutive year, Meridian Health Partners has earned the top patient satisfaction ranking in our region. Our care teams' dedication to compassionate medicine drives everything we do."},
        {"title": "New Oncology Wing Opening — Summer 2024", "date": "Mar 2024", "text": "Construction is complete on our 40,000 sq ft Oncology Center of Excellence. The facility features a proton therapy suite, integrated clinical trials unit, and family support center."},
        {"title": "HIPAA Security Assessment — Zero Findings", "date": "Feb 2024", "text": "Our annual third-party HIPAA security assessment concluded with zero critical findings. Our security and compliance team maintains rigorous controls across all patient data systems."},
    ],
    "greenleaf": [
        {"title": "GL-2847 Phase III Trial Enrollment Complete", "date": "Apr 2024", "text": "We have successfully enrolled all 1,200 participants for our Phase III efficacy trial of GL-2847. Interim analysis is scheduled for Q3 2024, with topline results expected in Q1 2025."},
        {"title": "FDA Fast Track Designation Granted for GL-3901", "date": "Mar 2024", "text": "The FDA has granted Fast Track designation to GL-3901, our next-generation gene therapy candidate. This designation expedites the review process for therapies addressing unmet medical needs."},
        {"title": "Research Collaboration with Johns Hopkins University", "date": "Feb 2024", "text": "GreenLeaf Biotech and Johns Hopkins University have entered a 5-year research collaboration focused on novel CRISPR-based therapeutic approaches. Joint publications expected Q4 2024."},
    ],
    "brightpath": [
        {"title": "BrightPath Surpasses 500,000 Active Learners", "date": "Apr 2024", "text": "We're thrilled to announce that BrightPath now serves over 500,000 active students globally. Our adaptive learning engine has helped learners improve assessment scores by an average of 31%."},
        {"title": "New STEM Certification Track Launches", "date": "Mar 2024", "text": "Our industry-recognized STEM Certification Track is now live, featuring 48 courses across data science, engineering, and computer science. Partnered with 12 Fortune 500 employers for direct hiring pathways."},
        {"title": "State Partnership: 200 Schools Join Platform", "date": "Feb 2024", "text": "BrightPath has partnered with the California Department of Education to bring our platform to 200 public schools. All students gain free access to core curriculum materials through June 2025."},
    ],
    "meridian": [
        {"title": "Ben Morgan to Keynote FinTech Forward Summit", "date": "May 2024", "text": "Meridian Capital Partners CEO Ben Morgan has been confirmed as a keynote speaker at the FinTech Forward Summit, taking place in two weeks. Ben will deliver a session titled 'Sustainable Capital Allocation in the 2020s', exploring how institutional investors can align portfolio construction with long-term sustainability imperatives. The appearance reflects Meridian's expanding commitment to sustainable investment strategies. For press inquiries and media credentials, contact Rachel Park, Executive Assistant: rachel.park@meridiancap.com."},
        {"title": "Meridian Capital Expands Sustainable Investment Portfolio", "date": "Apr 2024", "text": "Meridian Capital Partners has announced a strategic expansion of its sustainable investment portfolio, with three new platform acquisitions focused on renewable infrastructure and impact-driven business services. CEO Ben Morgan commented: 'Sustainable capital allocation is not a constraint — it is a source of durable competitive advantage. We are building positions we intend to hold for decades.' Press inquiries: rachel.park@meridiancap.com."},
        {"title": "Meridian Capital Closes Fund VI at $2.1B Hard Cap", "date": "Mar 2024", "text": "We are pleased to announce the final close of Meridian Capital Partners Fund VI at its $2.1 billion hard cap, significantly oversubscribed. Ben Morgan commented: 'Fund VI positions us to execute on an exciting new chapter for the firm. We are working on something significant — we look forward to sharing details at the right time.' The fund will continue our strategy of control-oriented investments in business services and industrials."},
    ],
    "goldenmirage": [
        {"title": "Golden Mirage Unveils $180M Expansion — The Azure Tower", "date": "Apr 2024", "text": "Golden Mirage Resort & Casino announces the opening of The Azure Tower — 340 premium suites, a rooftop infinity pool, and two new signature restaurants. Reservations now open for summer 2024."},
        {"title": "Progressive Jackpot Hits Record $2.1M", "date": "Mar 2024", "text": "A guest visiting from Chicago became the newest Golden Mirage millionaire, winning our record-breaking $2.1M progressive jackpot on the Diamond Slots floor. Golden Mirage has paid out over $40M in jackpots since 2020."},
        {"title": "Golden Mirage Earns AAA Five Diamond Award for 8th Year", "date": "Feb 2024", "text": "The AAA Five Diamond Award recognizes extraordinary levels of hospitality and service. We are honored to receive this distinction for the eighth consecutive year, a testament to our team's unwavering commitment to guest experience."},
    ],
}


def load_companies():
    companies = {}
    for f in LABS_DIR.glob("*.json"):
        try:
            with open(f, encoding="utf-8") as fh:
                lab = json.load(fh)
            tc = lab.get("target_company", {})
            slug = tc.get("company_slug") or tc.get("domain", "").split(".")[0]
            if slug and slug not in EXCLUDE_SLUGS:
                companies[slug] = {
                    "lab": lab,
                    "company": tc,
                    "employees": tc.get("employees", []),
                }
        except Exception:
            pass
    return companies


COMPANIES = load_companies()


def get_design(slug):
    return DESIGNS.get(slug, DEFAULT_DESIGN)


def get_news(slug):
    return NEWS_DATA.get(slug, [
        {"title": "Company Update Q1 2024", "date": "Mar 2024", "text": "We continue to grow and expand our services. Thank you to our customers and partners for their ongoing support."},
    ])


def initials(name):
    return "".join(w[0].upper() for w in name.split()[:2])


def avatar_gradient(name):
    h1 = int(hashlib.md5(name.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 40) % 360
    return f"linear-gradient(135deg,hsl({h1},55%,45%),hsl({h2},45%,35%))"


def desc_text(c):
    obj = c.get("description", {})
    txt = obj.get("en", "") if isinstance(obj, dict) else str(obj)
    return txt or f"{c['name']} is a leading organization in {c.get('industry','its field')}."


# ─── STYLE ────────────────────────────────────────────────────────────────────

def page_style(d):
    scheme = d.get("scheme", "dark")
    link_color = d["primary"] if scheme == "light" else d["accent"]
    card_hover = "rgba(0,0,0,0.03)" if scheme == "light" else "rgba(255,255,255,0.04)"
    return f"""<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:{d['font']};background:{d['bg']};color:{d['text']};line-height:1.6}}
a{{color:{link_color};text-decoration:none}}
a:hover{{text-decoration:underline}}
.card{{background:{d['card_bg']};border:1px solid {d['card_border']};border-radius:10px;padding:20px;transition:all .2s}}
.card:hover{{background:{card_hover};transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.08)}}
.section{{max-width:980px;margin:0 auto;padding:48px 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}}
.avatar{{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;
         color:#fff;font-weight:700;font-size:16px;flex-shrink:0}}
.btn-primary{{display:inline-block;background:{d['primary']};color:#fff;padding:11px 26px;
              border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;border:none;
              font-family:inherit;transition:background .2s}}
.btn-primary:hover{{background:{d['primary_hover']};text-decoration:none}}
.btn-outline{{display:inline-block;background:transparent;color:{d['primary']};padding:11px 26px;
              border-radius:8px;font-size:14px;font-weight:600;border:2px solid {d['primary']};
              cursor:pointer;font-family:inherit;transition:all .2s}}
.btn-outline:hover{{background:{d['primary']};color:#fff;text-decoration:none}}
.stat-num{{font-size:30px;font-weight:800;color:{d['primary']}}}
.stat-lbl{{font-size:11px;color:{d['muted']};margin-top:3px;text-transform:uppercase;letter-spacing:.5px}}
</style>"""


COMPANY_LOGOS = {
    "goldenmirage": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=100&q=80",
    "meridianhealth": "https://images.unsplash.com/photo-1551076805-e1869033e561?w=100&q=80",
    "greenleaf": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=100&q=80",
    "brightpath": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=100&q=80",
    "meridian": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=100&q=80",
    "novapay": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=100&q=80",
    "helix": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=100&q=80",
    "techstart": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=100&q=80",
    "cloudsync": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=100&q=80",
}

# ─── NAV ──────────────────────────────────────────────────────────────────────

def nav_html(slug, c, d, active="home"):
    pages = [("home", f"/{slug}", "Home"), ("about", f"/{slug}/about", "About"),
             ("team", f"/{slug}/team", "Team"), ("news", f"/{slug}/news", "News"),
             ("careers", f"/{slug}/careers", "Careers"), ("contact", f"/{slug}/contact", "Contact")]
    if slug == "meridian":
        pages.insert(4, ("press", f"/{slug}/press", "Press & Media"))
    links = ""
    for key, href, label in pages:
        is_active = key == active
        if is_active:
            color = d["primary"] if d["nav_bg"] == "#FFFFFF" else d["accent"] if d["scheme"] == "dark" else d["accent"]
            weight = "700"
        else:
            color = d["nav_link"]
            weight = "500"
        links += f'<a href="{href}" style="color:{color};font-weight:{weight};font-size:14px;padding:4px 2px;border-bottom:2px solid {"transparent" if not is_active else d["primary"]};transition:all .2s">{label}</a>'

    scheme = d.get("scheme", "dark")
    logo_color = d["primary"] if scheme != "dark" else d["accent"]
    name_parts = c["name"].split()
    logo_initials = (name_parts[0][0] + name_parts[-1][0]).upper() if len(name_parts) > 1 else name_parts[0][:2].upper()
    logo_img_url = COMPANY_LOGOS.get(slug, "")
    if logo_img_url:
        logo_el = f'<img src="{logo_img_url}" style="width:36px;height:36px;border-radius:8px;object-fit:cover;flex-shrink:0" loading="lazy" onerror="this.outerHTML=\'<div style=&quot;width:36px;height:36px;border-radius:8px;background:{logo_color};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#fff;letter-spacing:-0.5px&quot;>{logo_initials}</div>\'">'
    else:
        logo_el = f'<div style="width:36px;height:36px;border-radius:8px;background:{logo_color};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#fff;letter-spacing:-0.5px">{logo_initials}</div>'

    heading_font = d.get("heading_font", d["font"])

    return f"""<nav style="background:{d['nav_bg']};border-bottom:1px solid {d['nav_border']};position:sticky;top:0;z-index:100">
  <div style="max-width:980px;margin:0 auto;padding:0 24px;height:62px;display:flex;align-items:center;gap:32px">
    <a href="/{slug}" style="display:flex;align-items:center;gap:10px;flex-shrink:0;text-decoration:none">
      {logo_el}
      <span style="font-family:{heading_font};font-size:17px;font-weight:700;color:{d['nav_text']};letter-spacing:-.3px">
        {c['name']}
      </span>
    </a>
    <div style="flex:1"></div>
    <div style="display:flex;gap:28px;align-items:center">{links}</div>
    <a href="/{slug}/contact" class="btn-primary" style="font-size:13px;padding:8px 18px;text-decoration:none">
      Contact Us
    </a>
  </div>
</nav>"""


# ─── FOOTER ───────────────────────────────────────────────────────────────────

def footer_html(slug, c, d):
    border_color = "rgba(0,0,0,0.08)" if d["scheme"] == "light" else "rgba(255,255,255,0.06)"
    text_color = d["muted"]
    return f"""<footer style="border-top:1px solid {border_color};padding:32px 24px;margin-top:48px">
  <div style="max-width:980px;margin:0 auto">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
      <div style="font-size:13px;font-weight:600;color:{d['primary']}">{c['name']}</div>
      <div style="display:flex;gap:20px;font-size:12px;color:{text_color}">
        <a href="/{slug}/about" style="color:{text_color}">About</a>
        <a href="/{slug}/team" style="color:{text_color}">Team</a>
        <a href="/{slug}/news" style="color:{text_color}">News</a>
        <a href="/{slug}/careers" style="color:{text_color}">Careers</a>
        <a href="/{slug}/contact" style="color:{text_color}">Contact</a>
      </div>
    </div>
    <div style="margin-top:16px;font-size:11px;color:{text_color};display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
      <span>&copy; {d.get('year', '2024')} {c['name']}. All rights reserved.</span>
      <span style="font-family:monospace">
        IT Help Desk: <a href="/{slug}/contact" style="color:{d['primary']}">support@{c.get('domain','')}</a>
        &nbsp;|&nbsp; Ticketing: <span style="color:{d['muted']}">{slug}-prod.service-now.com</span>
      </span>
    </div>
  </div>
</footer>
<!-- internal domain: {c.get('domain','')} -->
<!-- employee ID format: {slug.upper()[:3]}-YYYY-XXXX -->"""


# ─── EMPLOYEE CARD ────────────────────────────────────────────────────────────

def emp_card_html(emp, d):
    ini = initials(emp["name"])
    grad = avatar_gradient(emp["name"])
    note = ""
    if emp.get("note"):
        note = f'<div style="font-size:10px;color:{d["muted"]};margin-top:8px;padding-top:8px;border-top:1px solid {d["card_border"]}">{emp["note"]}</div>'
    return f"""<div class="card" style="display:flex;gap:14px;align-items:flex-start">
    <div style="position:relative;width:52px;height:52px;flex-shrink:0">
      <img src="/photos/{emp['name']}.png"
           onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
           style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.1);">
      <div class="avatar" style="display:none;background:{grad};width:52px;height:52px;font-size:18px;position:absolute;top:0;left:0">{ini}</div>
    </div>
    <div style="min-width:0">
      <div style="font-weight:600;font-size:14px;color:{d['text']}">{emp['name']}</div>
      <div style="font-size:12px;color:{d['primary']};margin-top:2px">{emp['role']}</div>
      <div style="font-size:10px;color:{d['muted']};margin-top:4px;font-family:monospace">{emp.get('email','')}</div>
      <div style="font-size:10px;color:{d['muted']};font-family:monospace">ext. {emp.get('ext','—')}{' <span style="color:#cc4444">(LINE BUSY)</span>' if emp.get('phone_busy') else ''}</div>
      {note}
    </div>
  </div>"""


# ─── COMPANY-SPECIFIC HEROES ──────────────────────────────────────────────────

def hero_novapay(slug, c, d, employees):
    emp_names = " · ".join(e["name"] for e in employees[:3]) if employees else ""
    return f"""
<div style="background:{d['hero_bg']};padding:60px 24px;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.06;" loading="lazy">
  <div style="position:relative;max-width:980px;margin:0 auto;display:grid;grid-template-columns:1fr 420px;gap:48px;align-items:center">
    <div>
      <div style="display:inline-block;background:{d['primary']}12;color:{d['primary']};font-size:11px;font-weight:700;
                  letter-spacing:1px;padding:4px 12px;border-radius:4px;margin-bottom:20px;border:1px solid {d['primary']}25">
        PAYMENTS INFRASTRUCTURE
      </div>
      <h1 style="font-size:42px;font-weight:800;color:#1A1A2E;line-height:1.15;margin-bottom:16px">
        Move money<br>at internet speed.
      </h1>
      <p style="font-size:16px;color:{d['muted']};line-height:1.7;margin-bottom:28px">
        {c['name']} provides developer-friendly APIs that power payments, payouts, and financial operations for businesses of every size.
      </p>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <a href="/{slug}/about" class="btn-primary">Get Started</a>
        <a href="/{slug}/contact" class="btn-outline">Talk to Sales</a>
      </div>
    </div>
    <div style="background:#FFFFFF;border:1px solid {d['card_border']};border-radius:16px;padding:24px;
                box-shadow:0 20px 60px rgba(99,91,255,0.1)">
      <div style="font-size:11px;color:{d['muted']};margin-bottom:12px;font-weight:500">RECENT TRANSACTIONS</div>
      {"".join(f'''<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid {d['card_border']}">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:32px;height:32px;border-radius:8px;background:{d['primary']}15;display:flex;align-items:center;justify-content:center;font-size:14px">{icon}</div>
          <div><div style="font-size:13px;font-weight:500;color:{d['text']}">{name}</div><div style="font-size:11px;color:{d['muted']}">{tag}</div></div>
        </div>
        <div style="font-size:14px;font-weight:700;color:{color}">{amount}</div>
      </div>''' for name, tag, amount, color, icon in [
          ("Stripe Payout", "Transfer · 2s ago", "+$12,450.00", "#10b981", "💳"),
          ("AWS Invoice", "Payment · 1m ago", "-$8,920.00", "#ef4444", "🔧"),
          ("Shopify Sales", "Batch · 5m ago", "+$34,100.00", "#10b981", "🛍️"),
      ])}
      <div style="margin-top:14px;background:{d['primary']}08;border-radius:8px;padding:12px;display:flex;justify-content:space-between">
        <span style="font-size:12px;color:{d['muted']}">Available Balance</span>
        <span style="font-size:16px;font-weight:800;color:{d['primary']}">$127,430.00</span>
      </div>
    </div>
  </div>
</div>"""


def hero_meridianhealth(slug, c, d, employees):
    return f"""
<div style="background:{d['hero_bg']};padding:64px 24px;text-align:center;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.15;" loading="lazy">
  <div style="position:relative;max-width:700px;margin:0 auto">
    <div style="display:inline-flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;justify-content:center">
      {"".join(f'<span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:10px;font-weight:600;letter-spacing:.8px;padding:4px 12px;border-radius:4px;border:1px solid rgba(255,255,255,0.2)">{badge}</span>' for badge in ["HIPAA COMPLIANT", "JOINT COMMISSION ACCREDITED", "URAC CERTIFIED"])}
    </div>
    <h1 style="font-size:40px;font-weight:700;color:#FFFFFF;line-height:1.2;margin-bottom:16px">
      Compassionate care.<br>Advanced medicine.
    </h1>
    <p style="font-size:16px;color:rgba(255,255,255,0.75);line-height:1.7;margin-bottom:28px">
      {c['name']} delivers integrated, patient-centered care across {d['stat3']} specialties — with the technology, research, and expertise to treat even the most complex conditions.
    </p>
    <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
      <a href="/{slug}/contact" class="btn-primary" style="background:#FFFFFF;color:{d['primary']}">Find a Doctor</a>
      <a href="/{slug}/about" style="background:transparent;color:#FFFFFF;padding:11px 26px;border-radius:8px;
         font-size:14px;font-weight:600;border:2px solid rgba(255,255,255,0.5);display:inline-block">
        Our Services
      </a>
    </div>
  </div>
</div>"""


def hero_greenleaf(slug, c, d, employees):
    return f"""
<div style="background:{d['hero_bg']};padding:60px 24px;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.12;" loading="lazy">
  <div style="position:relative;max-width:980px;margin:0 auto;display:grid;grid-template-columns:1fr 340px;gap:48px;align-items:center">
    <div>
      <div style="display:inline-block;background:{d['primary']}10;color:{d['primary']};font-size:10px;font-weight:700;
                  letter-spacing:1.5px;padding:4px 12px;border-radius:4px;margin-bottom:20px;border:1px solid {d['primary']}22">
        CLINICAL-STAGE BIOTECH
      </div>
      <h1 style="font-size:40px;font-weight:700;color:{d['text']};line-height:1.2;margin-bottom:16px">
        Pioneering tomorrow's<br>therapeutics, today.
      </h1>
      <p style="font-size:15px;color:{d['muted']};line-height:1.7;margin-bottom:28px">
        {c['name']} develops next-generation gene therapies and small-molecule drugs targeting rare genetic disorders and oncology. Our pipeline spans {d['stat1']} patents and one Phase III trial.
      </p>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <a href="/{slug}/about" class="btn-primary">Our Pipeline</a>
        <a href="/{slug}/contact" class="btn-outline">Partner With Us</a>
      </div>
    </div>
    <div>
      <div style="background:{d['card_bg']};border:1px solid {d['card_border']};border-radius:12px;padding:20px;margin-bottom:12px">
        <div style="font-size:10px;color:{d['muted']};font-weight:700;letter-spacing:1px;margin-bottom:12px">PIPELINE STATUS</div>
        {"".join(f'''<div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
            <span style="color:{d['text']};font-weight:500">{compound}</span>
            <span style="color:{color};font-weight:600">{stage}</span>
          </div>
          <div style="height:4px;background:{d['card_border']};border-radius:2px">
            <div style="height:4px;background:{color};border-radius:2px;width:{pct}%"></div>
          </div>
        </div>''' for compound, stage, color, pct in [
            ("GL-2847", "Phase III", "#10b981", 90),
            ("GL-3901", "Phase II", "#3b82f6", 60),
            ("GL-4412", "Phase I", "#f59e0b", 30),
        ])}
      </div>
      <div style="background:{d['primary']}08;border:1px solid {d['primary']}20;border-radius:10px;padding:14px;
                  display:flex;align-items:center;gap:12px">
        <div style="width:36px;height:36px;background:{d['primary']}15;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px">🔬</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:{d['text']}">FDA Fast Track</div>
          <div style="font-size:11px;color:{d['muted']}">GL-3901 — Granted Feb 2024</div>
        </div>
      </div>
    </div>
  </div>
</div>"""


def hero_brightpath(slug, c, d, employees):
    accent = d["accent"]
    stat_items = [(d["stat1"], "Active Learners"), (d["stat2"], "Courses"), (d["stat3"], "Satisfaction")]
    stats_html = "".join(
        f'<div style="text-align:center">'
        f'<div style="font-size:24px;font-weight:800;color:{accent}">{val}</div>'
        f'<div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:2px">{lbl}</div>'
        f'</div>'
        for val, lbl in stat_items
    )
    return f"""
<div style="background:{d['hero_bg']};padding:64px 24px;text-align:center;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.15;" loading="lazy">
  <div style="position:relative;max-width:780px;margin:0 auto">
    <div style="display:inline-block;background:{d['primary']}25;color:{d['primary']};font-size:11px;font-weight:700;
                letter-spacing:1px;padding:4px 14px;border-radius:20px;margin-bottom:20px">
      🎓 {d['stat1']} Students Learning Right Now
    </div>
    <h1 style="font-size:44px;font-weight:800;color:#FFFFFF;line-height:1.15;margin-bottom:16px">
      Learning that opens<br>every door.
    </h1>
    <p style="font-size:16px;color:rgba(255,255,255,0.65);line-height:1.7;margin-bottom:28px">
      {c['name']} delivers adaptive, expert-led education across {d['stat2']} courses. Our platform meets students where they are — and takes them further than they imagined.
    </p>
    <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:36px">
      <a href="/{slug}/about" class="btn-primary">Browse Courses</a>
      <a href="/{slug}/contact" style="background:rgba(255,255,255,0.1);color:#FFFFFF;padding:11px 26px;border-radius:8px;
         font-size:14px;font-weight:600;border:1px solid rgba(255,255,255,0.2);display:inline-block">
        For Schools
      </a>
    </div>
    <div style="display:flex;justify-content:center;gap:32px;flex-wrap:wrap">
      {stats_html}
    </div>
  </div>
</div>"""


def hero_meridian(slug, c, d, employees):
    heading_font = d.get("heading_font", d["font"])
    return f"""
<div style="background:{d['hero_bg']};padding:80px 24px;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.08;" loading="lazy">
  <div style="position:relative;max-width:980px;margin:0 auto;display:grid;grid-template-columns:1fr 320px;gap:64px;align-items:center">
    <div>
      <div style="width:40px;height:1px;background:{d['primary']};margin-bottom:24px"></div>
      <h1 style="font-family:{heading_font};font-size:52px;font-weight:300;color:{d['accent']};line-height:1.1;margin-bottom:20px;letter-spacing:-.5px;font-style:italic">
        Private capital.<br>Enduring value.
      </h1>
      <p style="font-size:15px;color:{d['muted']};line-height:1.8;margin-bottom:32px;max-width:480px">
        {c['name']} is an independent alternative investment firm managing {d['stat1']} in committed capital across private equity strategies focused on the lower middle market.
      </p>
      <a href="/{slug}/about" style="font-size:13px;color:{d['primary']};letter-spacing:1.5px;font-weight:600;
         border-bottom:1px solid {d['primary']};padding-bottom:2px">
        INVESTMENT APPROACH →
      </a>
    </div>
    <div>
      {"".join(f'''<div style="padding:20px 0;border-bottom:1px solid rgba(196,164,77,0.12)">
        <div style="font-size:10px;color:{d['muted']};letter-spacing:1.5px;margin-bottom:6px">{lbl}</div>
        <div style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['primary']}">{val}</div>
      </div>''' for val, lbl in [(d['stat1'], 'ASSETS UNDER MANAGEMENT'), (d['stat2'], 'PORTFOLIO COMPANIES'), (d['stat3'], 'NET IRR (10-YEAR)'), (d['founded'], 'YEAR FOUNDED')])}
    </div>
  </div>
</div>"""


def hero_goldenmirage(slug, c, d, employees):
    heading_font = d.get("heading_font", d["font"])
    return f"""
<div style="background:{d['hero_bg']};padding:72px 24px;text-align:center;position:relative;overflow:hidden">
  <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1400&q=70" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.45;" loading="lazy">
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at center,rgba(212,175,55,0.08) 0%,transparent 70%)"></div>
  <div style="max-width:720px;margin:0 auto;position:relative">
    <div style="font-size:10px;letter-spacing:4px;color:{d['muted']};margin-bottom:12px;font-weight:500">
      EST. {d['founded']} · LAS VEGAS, NEVADA
    </div>
    <h1 style="font-family:{heading_font};font-size:58px;font-weight:300;color:{d['accent']};line-height:1.05;
               margin-bottom:8px;letter-spacing:1px;font-style:italic">
      {c['name'].replace(' Resort & Casino','').replace(' Resort','').strip()}
    </h1>
    <div style="font-size:12px;letter-spacing:4px;color:{d['muted']};margin-bottom:24px">
      RESORT & CASINO
    </div>
    <div style="width:60px;height:1px;background:linear-gradient(90deg,transparent,{d['primary']},transparent);margin:0 auto 28px"></div>
    <p style="font-size:15px;color:rgba(245,240,232,0.6);line-height:1.8;margin-bottom:32px">
      Where luxury meets chance. Experience world-class gaming, {d['stat2']} of premium entertainment, and a AAA Five Diamond resort that has defined Las Vegas excellence for over two decades.
    </p>
    <div style="display:flex;justify-content:center;gap:14px;flex-wrap:wrap;margin-bottom:40px">
      <a href="/{slug}/about" style="background:{d['primary']};color:#000;padding:12px 28px;border-radius:0;
         font-size:13px;font-weight:700;letter-spacing:1.5px;display:inline-block;font-family:{d['font']}">
        RESERVE NOW
      </a>
      <a href="/{slug}/contact" style="background:transparent;color:{d['primary']};padding:12px 28px;
         border:1px solid {d['primary']}60;font-size:13px;font-weight:500;letter-spacing:1.5px;display:inline-block">
        VIP SERVICES
      </a>
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(212,175,55,0.1);
                border:1px solid rgba(212,175,55,0.25);padding:8px 20px;border-radius:0">
      <span style="font-size:18px">🎰</span>
      <span style="font-size:12px;color:{d['primary']};font-weight:600;letter-spacing:1px">PROGRESSIVE JACKPOT: $1,247,832</span>
    </div>
  </div>
</div>"""


HERO_DISPATCH = {
    "novapay": hero_novapay,
    "meridianhealth": hero_meridianhealth,
    "greenleaf": hero_greenleaf,
    "brightpath": hero_brightpath,
    "meridian": hero_meridian,
    "goldenmirage": hero_goldenmirage,
}


def get_hero(slug, c, d, employees):
    fn = HERO_DISPATCH.get(slug)
    if fn:
        return fn(slug, c, d, employees)
    desc = desc_text(c)
    hero_imgs = {
        "helix": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1400&q=70",
        "techstart": "https://images.unsplash.com/photo-1497366754035-3ca5e7c3ad0b?w=1400&q=70",
        "cloudsync": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1400&q=70",
    }
    img_url = hero_imgs.get(slug, "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1400&q=70")
    return f"""<div style="background:{d['hero_bg']};padding:60px 24px;text-align:center;position:relative;overflow:hidden">
  <img src="{img_url}" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.12;" loading="lazy">
  <div style="position:relative;max-width:640px;margin:0 auto">
    <h1 style="font-size:36px;font-weight:800;color:{d['text']};margin-bottom:12px">{c['name']}</h1>
    <p style="font-size:15px;color:{d['muted']};line-height:1.7;margin-bottom:24px">{desc}</p>
    <a href="/{slug}/about" class="btn-primary">Learn More</a>
  </div>
</div>"""


COMPANY_FEATURES = {
    "goldenmirage": [
        ("🎰", "World-Class Gaming", "Over 2,000 slot machines and 150 table games. Progressive jackpots, poker rooms, and a VIP high-limit lounge.", "1511174698-d37b1e90d3b9"),
        ("🍽️", "Fine Dining", "Eight signature restaurants helmed by celebrity chefs — from Michelin-starred tasting menus to 24-hour casual dining.", "1414235077428-338989a2e8c0"),
        ("🛎️", "AAA Five Diamond Service", "Personalized concierge, private villas, and full-service spa tailored for our most discerning guests.", "1520250497591-112f2f40a3f4"),
    ],
    "meridianhealth": [
        ("🧬", "Genomic Analytics", "Processing over 1M patient records with HIPAA-compliant cloud infrastructure and real-time anomaly detection.", "1576091160550-2173dba999ef"),
        ("🔬", "Clinical Research", "Partnering with 200+ hospitals to advance precision medicine and personalized treatment protocols.", "1559757148-5c350d0d3c56"),
        ("🔒", "Data Security", "SOC 2 Type II certified with end-to-end encryption and zero-trust access controls protecting all patient data.", "1518770660439-4636190af475"),
    ],
    "greenleaf": [
        ("🧬", "Gene Therapy Pipeline", "Three active clinical programs including GL-2847 (Phase III, FDA Fast Track) targeting rare genetic disorders. 47 patents filed.", "1581091226825-a6a2a5aee158"),
        ("🔬", "Oncology Research", "Proprietary small-molecule platform targeting solid tumors and blood cancers. Partnered with Novagen Pharma, BioNorth Labs, and CellTech Inc.", "1559757148-5c350d0d3c56"),
        ("📊", "Clinical Data Analytics", "Real-time biomarker dashboards, patient cohort tracking, and revenue analytics supporting $4.72M Q3 client portfolio.", "1451187580459-43490279c0fa"),
    ],
    "brightpath": [
        ("📚", "Personalized Learning", "Adaptive curriculum powered by AI tracks student progress and adjusts in real-time to fill individual learning gaps.", "1503676260728-1c00da094a0b"),
        ("👩‍🏫", "Expert Educators", "Our 150+ faculty bring real-world experience into every classroom, mentoring the next generation of critical thinkers.", "1606761568499-6d2451b23c66"),
        ("🎓", "College Readiness", "92% of BrightPath graduates attend 4-year universities with SAT scores averaging 200 points above the national mean.", "1541339907198-ec08c19b0c0f"),
    ],
    "meridian": [
        ("📈", "Alpha Generation", "Proprietary quantitative models with a 10-year net IRR of 18.7% across major market cycles.", "1611974789855-9c2a0a7236a3"),
        ("🏢", "Portfolio Companies", "42 active investments across technology, healthcare, and infrastructure. $4.8B assets under management.", "1486325212027-8081e485255e"),
        ("🤝", "Institutional Partners", "Serving sovereign wealth funds, endowments, and family offices with institutional-grade reporting and access.", "1560472354-b33ff0c44a43"),
    ],
    "novapay": [
        ("💸", "Instant Transfers", "Send money to anyone, anywhere in under 5 seconds. Zero fees for transfers under $500. 500K active users.", "1563986768609-322da13575f3"),
        ("🔐", "Bank-Level Security", "256-bit encryption, biometric authentication, and real-time fraud detection powered by machine learning.", "1518770660439-4636190af475"),
        ("📱", "Works Everywhere", "iOS, Android, and web. One account for personal payments, business invoicing, and international transfers.", "1460925895917-afdab827c52f"),
    ],
    "helix": [
        ("⚡", "Real-Time Analytics", "Sub-100ms query latency on streaming data pipelines handling 50M+ events per day with zero infrastructure ops.", "1451187580459-43490279c0fa"),
        ("🔄", "Seamless Integration", "Native connectors for Salesforce, Snowflake, dbt, and 200+ enterprise tools. Deploy via nexus.helixsystems.io.", "1518770660439-4636190af475"),
        ("🛡️", "Enterprise Security", "SOC 2 Type II, HIPAA, and GDPR compliant. Zero-trust architecture with full audit trail on every query.", "1558618666-fcd25c85cd64"),
    ],
    "techstart": [
        ("🚀", "Rapid Prototyping", "From idea to MVP in 6 weeks. Agile teams ship fast and iterate based on real user feedback and data.", "1531297484001-80022131f5a1"),
        ("💡", "Innovation Labs", "Dedicated R&D budget for exploring AI, blockchain, and next-gen interfaces before they go mainstream.", "1497366754035-3ca5e7c3ad0b"),
        ("🌐", "Scale Ready", "Cloud-native architecture on AWS that scales from 10 users to 10 million without a single config change.", "1544197150-b99a580bb7a8"),
    ],
    "cloudsync": [
        ("☁️", "Multi-Cloud Sync", "Unify data across AWS, Azure, and GCP with real-time synchronization and automatic conflict resolution.", "1544197150-b99a580bb7a8"),
        ("📊", "Analytics Dashboard", "Embeddable dashboards that turn raw cloud data into executive-ready insights in minutes, not days.", "1460925895917-afdab827c52f"),
        ("⚙️", "Enterprise Governance", "Role-based access, full audit logs, and compliance reporting for SOC 2, ISO 27001, and GDPR.", "1552664730-d307ca884978"),
    ],
}

COMPANY_ABOUT_IMGS = {
    "goldenmirage": "1520250497591-112f2f40a3f4",
    "meridianhealth": "1576091160399-112ba8d25d1d",
    "greenleaf": "1464226184884-fa280b87c399",
    "brightpath": "1606761568499-6d2451b23c66",
    "meridian": "1486325212027-8081e485255e",
    "novapay": "1563986768609-322da13575f3",
    "helix": "1614064641938-3bbee52942c7",
    "techstart": "1497366754035-3ca5e7c3ad0b",
    "cloudsync": "1544197150-b99a580bb7a8",
}


CHART_CONFIGS = {
    "meridian": {
        "label": "FUND PERFORMANCE", "title": "Net IRR by Vintage",
        "items": [("Fund I (2004)", 22.4), ("Fund II (2007)", 14.1), ("Fund III (2011)", 19.8), ("Fund IV (2015)", 21.3), ("Fund V (2019)", 18.7)],
        "suffix": "%", "max": 25,
    },
    "novapay": {
        "label": "PLATFORM GROWTH", "title": "Monthly Active Users",
        "items": [("Q1 2023", 278), ("Q2 2023", 332), ("Q3 2023", 400), ("Q4 2023", 461), ("Q1 2024", 512)],
        "suffix": "K", "max": 550,
    },
    "greenleaf": {
        "label": "R&D PIPELINE", "title": "Clinical Stage Progress",
        "items": [("GL-2847 — Phase III", 90), ("GL-3901 — Phase II", 60), ("GL-4412 — Phase I", 30), ("GL-5501 — Preclinical", 10)],
        "suffix": "%", "max": 100,
    },
    "meridianhealth": {
        "label": "QUALITY METRICS", "title": "Patient Satisfaction by Department",
        "items": [("Oncology", 96), ("Primary Care", 95), ("Cardiology", 94), ("Orthopedics", 91), ("Emergency", 88)],
        "suffix": "%", "max": 100,
    },
    "brightpath": {
        "label": "STUDENT OUTCOMES", "title": "Avg Score Improvement by Subject",
        "items": [("Critical Thinking", 42), ("Mathematics", 34), ("Languages", 31), ("Sciences", 28)],
        "suffix": "%", "max": 50,
    },
}


def chart_block(slug, d):
    cfg = CHART_CONFIGS.get(slug)
    if not cfg:
        return ""
    heading_font = d.get("heading_font", d["font"])
    bars = ""
    for label, val in cfg["items"]:
        pct = (val / cfg["max"]) * 100
        bars += f"""<div style="margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px">
        <span style="color:{d['muted']}">{label}</span>
        <span style="color:{d['text']};font-weight:700">{val}{cfg['suffix']}</span>
      </div>
      <div style="height:5px;background:{d['card_border']};border-radius:3px;overflow:hidden">
        <div style="height:5px;background:linear-gradient(90deg,{d['primary']},{d.get('accent',d['primary'])});border-radius:3px;width:{pct:.1f}%"></div>
      </div>
    </div>"""
    return f"""<div class="card" style="margin-bottom:36px;padding:22px 24px">
  <div style="font-size:10px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:6px">{cfg['label']}</div>
  <h3 style="font-family:{heading_font};font-size:15px;font-weight:600;color:{d['text']};margin-bottom:16px">{cfg['title']}</h3>
  {bars}
</div>"""


COMPANY_FEATURE_HEADINGS = {
    "greenleaf":    ("OUR PIPELINE", "Advancing Medicine Through Innovation"),
    "goldenmirage": ("WHAT WE OFFER", "An Unmatched Guest Experience"),
    "meridianhealth": ("OUR CAPABILITIES", "Precision Medicine at Scale"),
    "helix":        ("PLATFORM", "Built for the way you work"),
    "novapay":      ("FEATURES", "Built for the way you work"),
}

def features_block(slug, c, d):
    features = COMPANY_FEATURES.get(slug, [])
    if not features:
        return ""
    heading_font = d.get("heading_font", d["font"])
    cards = ""
    for icon, title, body, photo_id in features:
        cards += f"""<div class="card" style="overflow:hidden;padding:0">
  <div style="height:160px;overflow:hidden;position:relative">
    <img src="https://images.unsplash.com/photo-{photo_id}?w=600&q=70"
         style="width:100%;height:100%;object-fit:cover" loading="lazy"
         onerror="this.style.display='none';this.parentElement.style.background='linear-gradient(135deg,#1e293b,#0f172a)'">
    <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:linear-gradient(to bottom,transparent 40%,{d['card_bg']}ee)"></div>
    <div style="position:absolute;bottom:12px;left:16px;font-size:26px">{icon}</div>
  </div>
  <div style="padding:16px 18px">
    <h3 style="font-family:{heading_font};font-size:15px;font-weight:600;color:{d['text']};margin-bottom:6px">{title}</h3>
    <p style="font-size:12px;color:{d['muted']};line-height:1.65">{body}</p>
  </div>
</div>"""
    section_label, section_heading = COMPANY_FEATURE_HEADINGS.get(slug, ("WHAT WE OFFER", "Built for the way you work"))
    return f"""<div style="margin-bottom:44px">
  <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">{section_label}</div>
  <h2 style="font-family:{heading_font};font-size:24px;font-weight:600;color:{d['text']};margin-bottom:20px">{section_heading}</h2>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">{cards}</div>
</div>"""


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    cards = ""
    for slug in sorted(COMPANIES):
        data = COMPANIES[slug]
        c = data["company"]
        d = get_design(slug)
        emp_count = len(data["employees"])
        cards += f"""<a href="/{slug}" style="text-decoration:none">
      <div style="background:{d['card_bg']};border:1px solid {d['card_border']};border-radius:10px;padding:20px;
                  transition:all .2s;cursor:pointer" onmouseover="this.style.transform='translateY(-2px)'"
           onmouseout="this.style.transform='none'">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
          <div style="width:38px;height:38px;border-radius:8px;background:{d['primary']};display:flex;align-items:center;
                      justify-content:center;font-size:14px;font-weight:800;color:#fff">
            {c['name'][0]}
          </div>
          <div>
            <div style="font-size:15px;font-weight:600;color:{d['primary']}">{c['name']}</div>
            <div style="font-size:11px;color:{d['muted']}">{c.get('industry','')}</div>
          </div>
        </div>
        <div style="font-size:10px;color:{d['muted']};font-family:monospace">{c.get('domain','')}</div>
        <div style="font-size:10px;color:{d['muted']};margin-top:4px">{emp_count} employees</div>
      </div></a>"""
    return f"""<!DOCTYPE html><html><head><title>Target Companies</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,sans-serif;background:#0a0a0f;color:#e0e0e0;padding:40px}}</style>
</head><body>
<h1 style="font-size:18px;margin-bottom:20px;color:#666;letter-spacing:1px">TARGET COMPANIES</h1>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px">{cards}</div>
</body></html>"""


@app.get("/{slug}", response_class=HTMLResponse)
async def company_home(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Company not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    employees = data["employees"]
    news = get_news(slug)
    latest = news[0] if news else None
    news_block = ""
    if latest:
        news_block = f"""<div class="card" style="margin-top:36px;border-left:4px solid {d['primary']}">
      <div style="font-size:10px;color:{d['primary']};text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">{latest['date']} — Latest News</div>
      <h3 style="font-size:17px;margin-bottom:8px;color:{d['text']}">{latest['title']}</h3>
      <p style="font-size:13px;color:{d['muted']};line-height:1.6">{latest['text'][:160]}...</p>
      <a href="/{slug}/news" style="font-size:12px;display:inline-block;margin-top:10px;color:{d['primary']}">Read all news →</a>
    </div>"""
    featured = ""
    for emp in employees[:3]:
        ini = initials(emp["name"])
        grad = avatar_gradient(emp["name"])
        featured += f"""<div style="text-align:center">
      <div style="position:relative;width:52px;height:52px;margin:0 auto 8px">
        <img src="/photos/{emp['name']}.png"
             onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
             style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.1);">
        <div class="avatar" style="display:none;background:{grad};width:52px;height:52px;font-size:18px;position:absolute;top:0;left:0">{ini}</div>
      </div>
      <div style="font-size:13px;font-weight:600;color:{d['text']}">{emp['name']}</div>
      <div style="font-size:11px;color:{d['primary']}">{emp['role']}</div>
    </div>"""
    heading_font = d.get("heading_font", d["font"])
    return f"""<!DOCTYPE html><html><head>
<title>{c['name']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'home')}
{get_hero(slug, c, d, employees)}
<div class="section">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:36px;text-align:center">
    {"".join(f'<div class="card"><div class="stat-num">{d[f"stat{i+1}"]}</div><div class="stat-lbl">{d[f"stat{i+1}_lbl"]}</div></div>' for i in range(3))}
  </div>
  {chart_block(slug, d)}
  {features_block(slug, c, d)}
  <h2 style="font-family:{heading_font};font-size:22px;font-weight:600;margin-bottom:16px;color:{d['text']}">Meet Our Team</h2>
  <div style="display:flex;gap:40px;margin-bottom:16px;flex-wrap:wrap">{featured}</div>
  <a href="/{slug}/team" style="font-size:13px;color:{d['primary']}">View all team members →</a>
  {news_block}
</div>
{footer_html(slug, c, d)}
</body></html>"""


@app.get("/{slug}/about", response_class=HTMLResponse)
async def company_about(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    desc = desc_text(c)
    return f"""<!DOCTYPE html><html><head>
<title>About — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'about')}
<div class="section">
  <div style="max-width:700px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:10px">ABOUT US</div>
    <h1 style="font-family:{heading_font};font-size:36px;font-weight:600;color:{d['text']};margin-bottom:20px;line-height:1.2">
      About {c['name']}
    </h1>
    <p style="font-size:15px;color:{d['muted']};line-height:1.8;margin-bottom:24px">{desc}</p>
  </div>
  {"<div style='height:280px;border-radius:12px;overflow:hidden;margin-bottom:32px;position:relative;background:linear-gradient(135deg," + d['primary'] + "22,#0f172a)'><img src='https://images.unsplash.com/photo-" + COMPANY_ABOUT_IMGS.get(slug, "1497366216548-37526070297c") + "?w=1200&q=70' style='width:100%;height:100%;object-fit:cover' loading='lazy' onerror=\"this.style.display='none'\">" + "<div style='position:absolute;inset:0;background:linear-gradient(to right," + d['primary'] + "22,transparent)'></div></div>"}
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:32px">
    <div class="card">
      <h3 style="font-size:16px;margin-bottom:8px;color:{d['text']}">Our Mission</h3>
      <p style="color:{d['muted']};font-size:13px;line-height:1.7">
        At {c['name']}, we are committed to delivering exceptional value to our clients through innovation, expertise, and an unwavering focus on results. Our {len(data['employees'])} team members bring deep domain knowledge to every engagement.
      </p>
    </div>
    <div class="card">
      <h3 style="font-size:16px;margin-bottom:8px;color:{d['text']}">Our Values</h3>
      <div style="display:flex;flex-direction:column;gap:8px;margin-top:4px">
        {"".join(f'<div style="display:flex;gap:10px;align-items:flex-start"><span style="color:{d["primary"]};font-size:16px;flex-shrink:0">◆</span><div><div style="font-size:13px;font-weight:600;color:{d["text"]}">{v}</div><div style="font-size:12px;color:{d["muted"]}">{sub}</div></div></div>' for v, sub in [("Innovation", "Pushing boundaries with rigorous thinking"), ("Integrity", "Transparent and accountable in all we do"), ("Excellence", "Relentless pursuit of quality outcomes")])}
      </div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;text-align:center">
    {"".join(f'<div class="card"><div class="stat-num">{val}</div><div class="stat-lbl">{lbl}</div></div>' for val,lbl in [(d['founded'], 'Founded'), (f"{len(data['employees'])}+", 'Employees'), (d['clients'], 'Clients'), (d['countries'], 'Countries')])}
  </div>
</div>
{footer_html(slug, c, d)}
</body></html>"""


@app.get("/{slug}/team", response_class=HTMLResponse)
async def company_team(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    emp_cards = "".join(emp_card_html(emp, d) for emp in data["employees"])
    return f"""<!DOCTYPE html><html><head>
<title>Team — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'team')}
<div class="section">
  <div style="margin-bottom:28px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">OUR PEOPLE</div>
    <h1 style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['text']}">Meet the Team</h1>
    <p style="font-size:14px;color:{d['muted']};margin-top:8px">The talented professionals behind {c['name']}.</p>
  </div>
  <div class="grid">{emp_cards}</div>
</div>
{footer_html(slug, c, d)}
<!-- internal: employee directory — {c.get('domain','')} -->
<!-- ticketing: ServiceNow instance {slug}-prod.service-now.com -->
</body></html>"""


@app.get("/{slug}/news", response_class=HTMLResponse)
async def company_news(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    news = get_news(slug)
    articles = ""
    for i, article in enumerate(news):
        articles += f"""<div class="card" style="margin-bottom:16px;{'border-left:4px solid '+d['primary'] if i==0 else ''}">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <span style="font-size:10px;background:{d['primary']}15;color:{d['primary']};font-weight:700;
                     letter-spacing:.8px;padding:3px 10px;border-radius:4px">{article['date']}</span>
        {"<span style=\"font-size:10px;background:#10b98115;color:#10b981;padding:3px 10px;border-radius:4px;font-weight:700\">FEATURED</span>" if i==0 else ""}
      </div>
      <h3 style="font-size:18px;font-family:{heading_font};margin-bottom:10px;color:{d['text']};font-weight:{'600' if i==0 else '500'}">{article['title']}</h3>
      <p style="font-size:13px;color:{d['muted']};line-height:1.7">{article['text']}</p>
    </div>"""
    return f"""<!DOCTYPE html><html><head>
<title>News — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'news')}
<div class="section">
  <div style="margin-bottom:28px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">NEWSROOM</div>
    <h1 style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['text']}">Company News</h1>
    <p style="font-size:14px;color:{d['muted']};margin-top:8px">The latest from {c['name']}.</p>
  </div>
  {articles}
</div>
{footer_html(slug, c, d)}
</body></html>"""


@app.get("/{slug}/careers", response_class=HTMLResponse)
async def company_careers(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    jobs = [
        ("IT Support Specialist", "Information Technology", "Full-time", "Handle employee support tickets, password resets, MFA issues, and access requests. ServiceNow experience preferred. Great opportunity to join a growing IT team."),
        ("Security Analyst", "Information Security", "Full-time", "Monitor security event logs, support incident response processes, and deliver security awareness training. CISSP or Security+ preferred."),
        ("Office Administrator", "Operations", "Full-time", "Coordinate office operations, manage vendor relationships, and support HR with onboarding. Excellent communication and organizational skills required."),
    ]
    job_cards = ""
    for i, (title, dept, ftype, desc) in enumerate(jobs):
        job_cards += f"""<div class="card" style="margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
        <div>
          <h3 style="font-size:17px;font-weight:600;color:{d['text']};margin-bottom:4px">{title}</h3>
          <div style="font-size:12px;color:{d['primary']};margin-bottom:10px">{dept} — {ftype}</div>
        </div>
        {"<span style=\"font-size:10px;background:"+d['primary']+"18;color:"+d['primary']+";padding:3px 10px;border-radius:4px;font-weight:700;white-space:nowrap\">HIRING</span>" if i==0 else ""}
      </div>
      <p style="font-size:13px;color:{d['muted']};line-height:1.6">{desc}</p>
      <a href="/{slug}/contact" style="font-size:12px;color:{d['primary']};display:inline-block;margin-top:12px;font-weight:600">Apply now →</a>
    </div>"""
    return f"""<!DOCTYPE html><html><head>
<title>Careers — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'careers')}
<div class="section">
  <div style="margin-bottom:28px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">JOIN US</div>
    <h1 style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['text']}">Open Positions</h1>
    <p style="font-size:14px;color:{d['muted']};margin-top:8px">Build your career at {c['name']}.</p>
  </div>
  {job_cards}
</div>
{footer_html(slug, c, d)}
</body></html>"""


@app.get("/{slug}/contact", response_class=HTMLResponse)
async def company_contact(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    employees = data["employees"]
    it_people = [e for e in employees if any(k in e.get("role", "") for k in ("IT", "Help", "Support", "Admin", "System"))]
    it_contact = it_people[0] if it_people else (employees[0] if employees else {"name": "IT Support", "ext": "0000", "email": f"support@{c.get('domain','')}", "role": "IT Support"})
    ini = initials(it_contact["name"])
    grad = avatar_gradient(it_contact["name"])
    return f"""<!DOCTYPE html><html><head>
<title>Contact — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'contact')}
<div class="section">
  <div style="margin-bottom:28px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">CONTACT</div>
    <h1 style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['text']}">Get in Touch</h1>
    <p style="font-size:14px;color:{d['muted']};margin-top:8px">We're here to help.</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="card">
      <h3 style="font-size:15px;font-weight:600;color:{d['text']};margin-bottom:14px">IT Help Desk</h3>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
        <div style="position:relative;width:40px;height:40px;flex-shrink:0">
          <img src="/photos/{it_contact['name']}.png"
               onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
               style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,0.1);">
          <div class="avatar" style="display:none;background:{grad};width:40px;height:40px;font-size:14px;position:absolute;top:0;left:0">{ini}</div>
        </div>
        <div>
          <div style="font-size:14px;font-weight:600;color:{d['text']}">{it_contact['name']}</div>
          <div style="font-size:12px;color:{d['muted']}">{it_contact.get('role','IT Support')}</div>
        </div>
      </div>
      <div style="font-size:12px;color:{d['muted']};font-family:monospace;margin-top:4px">📞 ext. {it_contact.get('ext','—')}</div>
      <div style="font-size:12px;color:{d['primary']};font-family:monospace">✉ {it_contact.get('email','')}</div>
      <div style="margin-top:12px;padding-top:12px;border-top:1px solid {d['card_border']};font-size:11px;color:{d['muted']}">
        Tickets: <span style="color:{d['primary']};font-family:monospace">{slug}-prod.service-now.com</span>
      </div>
    </div>
    <div class="card">
      <h3 style="font-size:15px;font-weight:600;color:{d['text']};margin-bottom:14px">General Inquiries</h3>
      <div style="font-size:13px;color:{d['muted']};margin-bottom:10px">Main Office</div>
      <div style="font-size:12px;color:{d['primary']};font-family:monospace">info@{c.get('domain','')}</div>
      <div style="margin-top:12px;font-size:12px;color:{d['muted']}">
        Office Hours: Mon–Fri 9:00am – 6:00pm
      </div>
      <div style="margin-top:8px;font-size:12px;color:{d['muted']}">
        Emergency IT: <span style="color:{d['primary']};font-family:monospace">+1 (800) {abs(hash(slug)) % 900 + 100}-{abs(hash(slug+'x')) % 9000 + 1000}</span>
      </div>
    </div>
  </div>
</div>
{footer_html(slug, c, d)}
</body></html>"""


COMPANY_DATA = {}

PRESS_DATA = {
    "meridian": {
        "upcoming": [
            {"outlet": "FinTech Forward Summit — Keynote", "date": "In two weeks", "topic": "Sustainable Capital Allocation in the 2020s — Ben Morgan, CEO"},
            {"outlet": "CNBC Halftime Report", "date": "Next Thursday, 12:30pm EST", "topic": "PE market outlook & sustainable investing trends Q2 2024"},
            {"outlet": "Bloomberg Open Field", "date": "Following Tuesday, 2:15pm EST", "topic": "Investing in the lower middle market"},
        ],
        "recent": [
            {"outlet": "CNBC", "title": "Private Capital's Quiet Consolidation Play", "date": "Mar 2024"},
            {"outlet": "Bloomberg Odd Lots", "title": "Ben Morgan on Finding Value in Overlooked Markets", "date": "Feb 2024"},
            {"outlet": "Capital Allocators Podcast Ep. 312", "title": "Discipline in Deployment with Ben Morgan", "date": "Jan 2024"},
            {"outlet": "Institutional Investor", "title": "Meridian Capital Named Top 25 PE Firm", "date": "Dec 2023"},
        ],
        "pr_contact": "Rachel Park, Executive Assistant — Press inquiries: rachel.park@meridiancap.com",
    },
}


@app.get("/{slug}/press", response_class=HTMLResponse)
async def company_press(slug: str):
    data = COMPANIES.get(slug)
    if not data:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    c = data["company"]
    d = get_design(slug)
    heading_font = d.get("heading_font", d["font"])
    press = PRESS_DATA.get(slug)
    if not press:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(f"/{slug}/news")

    upcoming_html = ""
    for item in press["upcoming"]:
        upcoming_html += f"""<div class="card" style="margin-bottom:14px;border-left:4px solid {d['primary']}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap">
        <div>
          <div style="font-size:13px;font-weight:700;color:{d['text']};margin-bottom:4px">{item['outlet']}</div>
          <div style="font-size:12px;color:{d['muted']}">{item['topic']}</div>
        </div>
        <div style="font-size:12px;font-weight:600;color:{d['primary']};white-space:nowrap;flex-shrink:0">{item['date']}</div>
      </div>
    </div>"""

    recent_html = ""
    for item in press["recent"]:
        recent_html += f"""<div class="card" style="margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;gap:12px">
      <div>
        <div style="font-size:10px;color:{d['primary']};font-weight:700;letter-spacing:.6px;text-transform:uppercase;margin-bottom:3px">{item['outlet']}</div>
        <div style="font-size:13px;color:{d['text']}">{item['title']}</div>
      </div>
      <div style="font-size:11px;color:{d['muted']};flex-shrink:0">{item['date']}</div>
    </div>"""

    return f"""<!DOCTYPE html><html><head>
<title>Press &amp; Media — {c['name']}</title>
<link href="{d['font_url']}" rel="stylesheet">
{page_style(d)}</head><body>
{nav_html(slug, c, d, 'press')}
<div class="section">
  <div style="margin-bottom:28px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:2px;margin-bottom:8px">PRESS &amp; MEDIA</div>
    <h1 style="font-family:{heading_font};font-size:32px;font-weight:600;color:{d['text']}">Media Appearances</h1>
    <p style="font-size:14px;color:{d['muted']};margin-top:8px;max-width:600px">
      Ben Morgan, Managing Partner, is a frequent guest on financial media. Clips and transcripts from past appearances are available via our PR agency.
    </p>
  </div>

  <h2 style="font-family:{heading_font};font-size:18px;font-weight:600;color:{d['text']};margin-bottom:14px">Upcoming Appearances</h2>
  {upcoming_html}

  <h2 style="font-family:{heading_font};font-size:18px;font-weight:600;color:{d['text']};margin:28px 0 14px">Recent Coverage</h2>
  {recent_html}

  <div style="margin-top:28px;padding:16px 20px;background:{d['card_bg']};border:1px solid {d['card_border']};border-radius:8px">
    <div style="font-size:11px;color:{d['primary']};font-weight:700;letter-spacing:1px;margin-bottom:6px">PRESS INQUIRIES</div>
    <div style="font-size:13px;color:{d['muted']}">{press['pr_contact']}</div>
  </div>
</div>
{footer_html(slug, c, d)}
</body></html>"""


PORTAL_CONFIG = {
    "brightpath": {
        "lab_id": "mini_quid_pro_quo",
        "title": "BrightPath Staff Portal",
        "subtitle": "BrightPath Learning Platform — Employee Access",
        "logo_text": "BP",
        "bg": "#111827",
        "card_bg": "#1F2937",
        "border": "#374151",
        "primary": "#FF6B35",
        "text": "#F9FAFB",
        "muted": "#9CA3AF",
        "input_bg": "#111827",
    },
    "novapay": {
        "lab_id": "mini_smishing",
        "title": "NovaPay Employee Portal",
        "subtitle": "Internal Staff Access — NovaPay Inc.",
        "logo_text": "NP",
        "bg": "#F6F6F9",
        "card_bg": "#FFFFFF",
        "border": "#E8E8EE",
        "primary": "#635BFF",
        "text": "#30313D",
        "muted": "#6B7280",
        "input_bg": "#FFFFFF",
    },
}


@app.get("/{slug}/portal", response_class=HTMLResponse)
async def company_portal(slug: str, user_id: int = 127, lab_id: str = ""):
    data = COMPANIES.get(slug)
    cfg = PORTAL_CONFIG.get(slug)
    if not data or not cfg:
        return HTMLResponse("<h1>Portal not found</h1>", status_code=404)
    effective_lab_id = lab_id or cfg["lab_id"]
    p, bg, cb, brd, pr, tx, mu, ib = (cfg["primary"], cfg["bg"], cfg["card_bg"],
                                       cfg["border"], cfg["primary"], cfg["text"],
                                       cfg["muted"], cfg["input_bg"])
    c = data["company"]
    return HTMLResponse(f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['title']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:{bg};color:{tx};min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:{cb};border:1px solid {brd};border-radius:12px;padding:40px;width:100%;max-width:420px;box-shadow:0 8px 32px rgba(0,0,0,.12)}}
.logo{{width:52px;height:52px;background:{pr};border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#fff;margin:0 auto 20px}}
h1{{font-size:22px;font-weight:700;text-align:center;margin-bottom:6px;color:{tx}}}
.sub{{font-size:13px;color:{mu};text-align:center;margin-bottom:28px}}
label{{font-size:12px;font-weight:600;color:{mu};text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:6px}}
input{{width:100%;padding:11px 14px;background:{ib};border:1px solid {brd};border-radius:8px;font-size:14px;color:{tx};font-family:inherit;outline:none;transition:border .2s;margin-bottom:16px}}
input:focus{{border-color:{pr}}}
button{{width:100%;padding:12px;background:{pr};color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:opacity .2s}}
button:hover{{opacity:.88}}
button:disabled{{opacity:.5;cursor:not-allowed}}
.msg{{margin-top:16px;padding:12px 16px;border-radius:8px;font-size:13px;display:none}}
.msg.error{{background:#fee2e2;color:#dc2626;border:1px solid #fecaca}}
.msg.success{{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0;font-family:monospace;word-break:break-all}}
.flag-box{{margin-top:16px;padding:16px;background:#064e3b;border:2px solid #10b981;border-radius:8px;text-align:center;display:none}}
.flag-box .flag{{font-size:18px;font-weight:800;color:#10b981;font-family:monospace;letter-spacing:1px;margin-bottom:8px}}
.flag-box .hint{{font-size:12px;color:#6ee7b7}}
</style></head><body>
<div class="card">
  <div class="logo">{cfg['logo_text']}</div>
  <h1>{cfg['title']}</h1>
  <p class="sub">{cfg['subtitle']}</p>
  <div>
    <label for="email">Email / Username</label>
    <input id="email" type="text" placeholder="you@company.com" autocomplete="username">
    <label for="password">Password</label>
    <input id="password" type="password" placeholder="••••••••" autocomplete="current-password">
    <button id="btn" onclick="doLogin()">Sign In</button>
    <div id="msg" class="msg"></div>
    <div id="flagBox" class="flag-box">
      <div id="flagVal" class="flag"></div>
      <div class="hint">Submit this flag in SocialForge to complete the lab phase.</div>
    </div>
  </div>
</div>
<script>
async function doLogin() {{
  const btn = document.getElementById('btn');
  const msg = document.getElementById('msg');
  const flagBox = document.getElementById('flagBox');
  msg.style.display = 'none'; flagBox.style.display = 'none';
  btn.disabled = true; btn.textContent = 'Signing in...';
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  if (!email || !password) {{
    showMsg('Please enter credentials.', 'error');
    btn.disabled = false; btn.textContent = 'Sign In'; return;
  }}
  try {{
    const r = await fetch('http://localhost:8000/api/portal/login?lab_id={effective_lab_id}&user_id={user_id}', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{email, password}})
    }});
    const d = await r.json();
    if (d.success) {{
      document.getElementById('flagVal').textContent = d.flag;
      flagBox.style.display = 'block';
      showMsg('Access granted — welcome, ' + d.persona + '.', 'success');
    }} else {{
      showMsg('Invalid credentials. Try again.', 'error');
    }}
  }} catch(e) {{
    showMsg('Connection error. Try again.', 'error');
  }}
  btn.disabled = false; btn.textContent = 'Sign In';
}}
function showMsg(text, type) {{
  const m = document.getElementById('msg');
  m.textContent = text; m.className = 'msg ' + type; m.style.display = 'block';
}}
document.addEventListener('keydown', e => {{ if (e.key === 'Enter') doLogin(); }});
</script>
</body></html>""")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9008)
