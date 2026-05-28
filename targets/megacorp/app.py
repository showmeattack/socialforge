"""Golden Mirage Resort & Casino — fake company website for OSINT reconnaissance."""
import urllib.parse
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

_PORTAL_CREDS = {"marcus.chen", "marcus.chen@goldenmirage.com"}
_PORTAL_PASS  = "G0ld3nM!rag3#Temp92"
_PORTAL_TOKEN = "GM_SESS_44821"
_PORTAL_FLAG  = "SF{h3lpd3sk_pwn3d_2023}"

NPC_PHOTOS_DIR = Path(r"C:\Users\fargo\Desktop\НПС")

_EXTRA_PHOTO_URLS = {
    "Jennifer Walsh":  "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&h=200&fit=crop",
    "Tony Russo":      "https://images.unsplash.com/photo-1566753323558-f4e0952af115?w=200&h=200&fit=crop",
    "Lisa Nakamura":   "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&h=200&fit=crop",
}

app = FastAPI(title="Golden Mirage Resort & Casino")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AllowIframeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; frame-ancestors *"
        # CSP already set
        return response


app.add_middleware(AllowIframeMiddleware)


@app.get("/photos/{filename:path}")
async def serve_photo(filename: str):
    import hashlib
    from fastapi.responses import Response, RedirectResponse
    name = urllib.parse.unquote(filename)
    for p in [NPC_PHOTOS_DIR / name, NPC_PHOTOS_DIR / f"{name}.png"]:
        if p.exists():
            return FileResponse(str(p), media_type="image/png")
    stem = Path(name).stem if "." in name else name
    if stem in _EXTRA_PHOTO_URLS:
        return RedirectResponse(_EXTRA_PHOTO_URLS[stem], status_code=302)
    h1 = int(hashlib.md5(stem.encode()).hexdigest()[:6], 16) % 360
    h2 = (h1 + 40) % 360
    initials = "".join(p[0].upper() for p in stem.split() if p)[:2] or "?"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
           f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
           f'<stop offset="0%" stop-color="hsl({h1},60%,45%)"/>'
           f'<stop offset="100%" stop-color="hsl({h2},60%,30%)"/></linearGradient></defs>'
           f'<circle cx="32" cy="32" r="32" fill="url(#g)"/>'
           f'<text x="32" y="38" text-anchor="middle" font-family="Arial,sans-serif" '
           f'font-size="22" font-weight="700" fill="#fff">{initials}</text></svg>')
    return Response(content=svg, media_type="image/svg+xml")


def photo_card(name, role, bio, detail=""):
    ini = "".join(w[0].upper() for w in name.split()[:2])
    detail_html = f'<div class="detail">{detail}</div>' if detail else ""
    return f"""<div class="team-card" style="display:flex;gap:16px;align-items:flex-start">
  <div style="position:relative;width:64px;height:64px;flex-shrink:0">
    <img src="/photos/{urllib.parse.quote(name)}.png"
         onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
         style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #d4af3740">
    <div style="display:none;width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#b8962e,#8b6914);
                align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#fff;
                position:absolute;top:0;left:0">{ini}</div>
  </div>
  <div style="min-width:0;flex:1">
    <h3>{name}</h3>
    <div class="role">{role}</div>
    <div class="bio">{bio}</div>
    {detail_html}
  </div>
</div>"""


PAGE_STYLE = """
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Georgia',serif;background:#0a0a0a;color:#d4af37}
.header{background:linear-gradient(135deg,#1a0a2e,#0d0d0d);padding:30px 60px;border-bottom:2px solid #d4af37}
.logo{font-size:32px;font-weight:bold;letter-spacing:3px;color:#d4af37}
.logo span{color:#fff}
.nav{display:flex;gap:30px;margin-top:15px}
.nav a{color:#999;text-decoration:none;font-size:14px;letter-spacing:1px;text-transform:uppercase}
.nav a:hover{color:#d4af37}
.hero{background:linear-gradient(rgba(0,0,0,.7),rgba(0,0,0,.9)),url('');height:400px;display:flex;align-items:center;justify-content:center;text-align:center}
.hero h1{font-size:48px;color:#fff;margin-bottom:10px}
.hero p{font-size:18px;color:#999;max-width:600px}
.section{padding:60px;max-width:1200px;margin:0 auto}
.section h2{font-size:28px;margin-bottom:30px;color:#d4af37;border-bottom:1px solid #333;padding-bottom:10px}
.team-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px}
.team-card{background:#111;border:1px solid #222;border-radius:8px;padding:24px;transition:border-color .2s}
.team-card:hover{border-color:#d4af37}
.team-card h3{color:#fff;font-size:18px;margin-bottom:4px}
.team-card .role{color:#d4af37;font-size:13px;margin-bottom:12px}
.team-card .bio{color:#888;font-size:13px;line-height:1.6}
.team-card .detail{color:#666;font-size:12px;margin-top:8px}
.footer{background:#050505;padding:40px 60px;border-top:1px solid #222;color:#555;font-size:12px}
.footer a{color:#d4af37;text-decoration:none}
/* Responsive grid */
</style>
"""


@app.get("/", response_class=HTMLResponse)
async def homepage():
    return f"""<!DOCTYPE html><html><head><title>Golden Mirage Resort & Casino</title>{PAGE_STYLE}</head><body>
<div class="header">
  <div class="logo">GOLDEN <span>MIRAGE</span></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/team">Our Team</a>
    <a href="/careers">Careers</a>
    <a href="/contact">Contact</a>
  </div>
</div>
<div class="hero">
  <div>
    <h1>Welcome to Golden Mirage</h1>
    <p>Las Vegas' premier luxury resort and casino experience. 3,200 rooms. World-class dining. Unforgettable entertainment.</p>
  </div>
</div>
<div class="section">
  <h2>Experience Luxury</h2>
  <p style="color:#999;line-height:1.8">Golden Mirage Resort & Casino has been the crown jewel of the Las Vegas Strip since 1997. With over 3,200 luxury suites, 15 restaurants, and a 100,000 sq ft casino floor, we deliver an unmatched experience.</p>
</div>
<!-- Flag hint: check /team and view page source -->
<div class="footer">
  <p>&copy; 2024 Golden Mirage Resort & Casino. All rights reserved.</p>
  <p>Internal systems: <a href="/internal">Employee Portal</a> | Ticketing: ServiceNow</p>
</div>
</body></html>"""


@app.get("/team", response_class=HTMLResponse)
async def team():
    return f"""<!DOCTYPE html><html><head><title>Our Team — Golden Mirage</title>{PAGE_STYLE}</head><body>
<div class="header">
  <div class="logo">GOLDEN <span>MIRAGE</span></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/team">Our Team</a>
    <a href="/careers">Careers</a>
    <a href="/contact">Contact</a>
  </div>
</div>
<div class="section">
  <h2>Leadership & Key Staff</h2>
  <div class="team-grid">
    {photo_card("Richard Blackwell", "Chief Executive Officer", "30+ years in hospitality. Previously CEO of Venetian Sands Group. Harvard MBA.")}
    {photo_card("Sarah Mitchell", "Marketing Director", "Leads brand strategy and guest engagement. 15 years in luxury hospitality marketing. Known for data-driven campaigns.", "Team: Marketing (12 members)")}
    {photo_card("David Park", "IT Director", "Oversees all technology infrastructure. Previously at Caesars Entertainment. Manages a team of 45 IT professionals.", "Help Desk: ext. 4357 | ServiceNow ticketing")}
    {photo_card("Elena Rodriguez", "IT Help Desk Lead", "Manages the 24/7 IT support team. Ensures quick resolution of employee technical issues. 4 years at Golden Mirage.", "Direct line: ext. 4358 | elena.rodriguez@goldenmirage.com")}
    {photo_card("Marcus Chen", "Marketing Associate", "New addition to the marketing team! Marcus brings fresh energy from his Boston University communications degree.", "Started: April 2024 | Reports to: Sarah Mitchell")}
    {photo_card("Jennifer Walsh", "HR Director", "Manages talent acquisition and employee relations. 20 years HR experience in gaming industry.")}
    {photo_card("Tony Russo", "Casino Floor Manager", "Oversees all casino operations. Former dealer turned manager. 18 years on the floor.")}
    {photo_card("Lisa Nakamura", "Chief Information Security Officer", "Leads cybersecurity initiatives. MS in Cybersecurity from Stanford. Implemented zero-trust architecture in 2023.", "Security awareness training: mandatory quarterly")}
  </div>
  <!-- new-hire-onboarding: employees receive GM-YYYY-XXXX format IDs, visible on badge photos -->
</div>
<!-- internal-systems: ServiceNow ticketing | Employee Portal: /internal -->
<div class="footer">
  <p>&copy; 2024 Golden Mirage Resort & Casino</p>
</div>
</body></html>"""


@app.get("/about", response_class=HTMLResponse)
async def about():
    return f"""<!DOCTYPE html><html><head><title>About — Golden Mirage</title>{PAGE_STYLE}</head><body>
<div class="header">
  <div class="logo">GOLDEN <span>MIRAGE</span></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/team">Our Team</a>
    <a href="/careers">Careers</a>
    <a href="/contact">Contact</a>
  </div>
</div>
<div class="section">
  <h2>About Golden Mirage</h2>
  <p style="color:#999;line-height:1.8;margin-bottom:20px">
    Founded in 1997, Golden Mirage Resort & Casino has grown from a single hotel tower to one of the most
    iconic destinations on the Las Vegas Strip. With over 3,200 luxury suites, 15 world-class restaurants,
    a 100,000 sq ft casino floor, and a 4,000-seat entertainment arena, we redefine hospitality excellence.
  </p>
  <p style="color:#999;line-height:1.8;margin-bottom:20px">
    Our commitment to innovation extends beyond guest experience. Golden Mirage was among the first
    Las Vegas properties to implement contactless check-in, AI-powered concierge services, and a fully
    integrated rewards program — <b style="color:#d4af37">Mirage Gold Rewards</b> — serving over 2 million members.
  </p>
  <h2 style="margin-top:40px">Our Mission</h2>
  <p style="color:#999;line-height:1.8;margin-bottom:20px">
    To deliver unforgettable experiences through world-class hospitality, cutting-edge technology,
    and a team of over 8,500 dedicated professionals.
  </p>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:30px">
    <div class="team-card" style="text-align:center">
      <div style="font-size:36px;color:#d4af37;margin-bottom:8px">3,200+</div>
      <div style="color:#999;font-size:13px">Luxury Suites</div>
    </div>
    <div class="team-card" style="text-align:center">
      <div style="font-size:36px;color:#d4af37;margin-bottom:8px">8,500+</div>
      <div style="color:#999;font-size:13px">Team Members</div>
    </div>
    <div class="team-card" style="text-align:center">
      <div style="font-size:36px;color:#d4af37;margin-bottom:8px">2M+</div>
      <div style="color:#999;font-size:13px">Rewards Members</div>
    </div>
  </div>
</div>
<div class="footer">
  <p>&copy; 2024 Golden Mirage Resort & Casino</p>
  <p>Internal systems: <a href="/internal">Employee Portal</a> | Ticketing: ServiceNow</p>
</div>
</body></html>"""


@app.get("/contact", response_class=HTMLResponse)
async def contact():
    return f"""<!DOCTYPE html><html><head><title>Contact — Golden Mirage</title>{PAGE_STYLE}</head><body>
<div class="header">
  <div class="logo">GOLDEN <span>MIRAGE</span></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/team">Our Team</a>
    <a href="/careers">Careers</a>
    <a href="/contact">Contact</a>
  </div>
</div>
<div class="section">
  <h2>Contact Us</h2>
  <div class="team-grid">
    <div class="team-card">
      <h3>General Inquiries</h3>
      <div class="role">Front Desk</div>
      <div class="detail">Phone: +1 (702) 555-0100</div>
      <div class="detail">Email: info@goldenmirage.com</div>
    </div>
    <div class="team-card">
      <h3>IT Help Desk</h3>
      <div class="role">Internal Support (Employees Only)</div>
      <div class="detail">Extension: 4358</div>
      <div class="detail">Email: helpdesk@goldenmirage.com</div>
      <div class="detail">ServiceNow: gm-prod.service-now.com</div>
    </div>
    <div class="team-card">
      <h3>Human Resources</h3>
      <div class="role">Jennifer Walsh — HR Director</div>
      <div class="detail">Email: hr@goldenmirage.com</div>
      <div class="detail">Careers: <a href="/careers">Open Positions</a></div>
    </div>
    <div class="team-card">
      <h3>Reservations</h3>
      <div class="role">24/7 Booking</div>
      <div class="detail">Phone: +1 (702) 555-0200</div>
      <div class="detail">Email: reservations@goldenmirage.com</div>
    </div>
  </div>
</div>
<div class="footer"><p>&copy; 2024 Golden Mirage Resort & Casino</p></div>
</body></html>"""


@app.get("/careers", response_class=HTMLResponse)
async def careers():
    return f"""<!DOCTYPE html><html><head><title>Careers — Golden Mirage</title>{PAGE_STYLE}</head><body>
<div class="header">
  <div class="logo">GOLDEN <span>MIRAGE</span></div>
  <div class="nav"><a href="/">Home</a><a href="/team">Our Team</a><a href="/careers">Careers</a></div>
</div>
<div class="section">
  <h2>Join Our Team</h2>
  <p style="color:#999;margin-bottom:30px">Golden Mirage is always looking for talented individuals to join our world-class team.</p>
  <div class="team-card" style="margin-bottom:16px">
    <h3>IT Support Specialist</h3>
    <div class="role">IT Department — Full Time</div>
    <div class="bio">Join Elena Rodriguez's help desk team! Handle employee support tickets via ServiceNow, assist with password resets, MFA issues, and hardware provisioning. Must be comfortable with high-pressure situations.</div>
  </div>
  <div class="team-card" style="margin-bottom:16px">
    <h3>Marketing Coordinator</h3>
    <div class="role">Marketing — Full Time</div>
    <div class="bio">Work with Sarah Mitchell's team on luxury brand campaigns. Support Marcus Chen and the team with social media strategy and content creation.</div>
  </div>
</div>
<div class="footer"><p>&copy; 2024 Golden Mirage Resort & Casino</p></div>
</body></html>"""


@app.get("/linkedin/marcus-chen", response_class=HTMLResponse)
async def marcus_linkedin():
    """Simulated LinkedIn profile page."""
    return f"""<!DOCTYPE html><html><head><title>Marcus Chen — LinkedIn</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:#f3f2ef;color:#000}}
.profile-header{{background:#fff;max-width:800px;margin:20px auto;border-radius:8px;border:1px solid #ddd;overflow:hidden}}
.banner{{height:120px;background:linear-gradient(135deg,#0a66c2,#004182)}}
.profile-info{{padding:20px 24px;position:relative}}
.avatar{{width:100px;height:100px;border-radius:50%;background:#d4af37;border:4px solid #fff;position:absolute;top:-50px;display:flex;align-items:center;justify-content:center;font-size:36px;color:#fff;font-weight:bold}}
.name{{margin-top:60px;font-size:24px;font-weight:600}}
.headline{{color:#666;font-size:14px;margin-top:4px}}
.location{{color:#999;font-size:13px;margin-top:4px}}
.section{{background:#fff;max-width:800px;margin:12px auto;border-radius:8px;border:1px solid #ddd;padding:20px 24px}}
.section h3{{font-size:16px;margin-bottom:12px}}
.post{{border-top:1px solid #eee;padding:12px 0}}
.post .text{{font-size:14px;line-height:1.5;color:#333}}
.post .date{{font-size:12px;color:#999;margin-top:4px}}
.badge-photo{{background:#ffe;border:1px solid #ddd;border-radius:4px;padding:8px;font-size:11px;color:#666;margin-top:8px}}
</style></head><body>
<div class="profile-header">
  <div class="banner"></div>
  <div class="profile-info">
    <div class="avatar">MC</div>
    <div class="name">Marcus Chen</div>
    <div class="headline">Marketing Associate at Golden Mirage Resort & Casino 🎰</div>
    <div class="location">Las Vegas, Nevada • From Boston, MA</div>
    <p style="margin-top:12px;font-size:14px;color:#333">
      Excited to join Golden Mirage Resort & Casino as Marketing Associate! 🎰
      Living my Vegas dream. Boston &rarr; Las Vegas. Dog dad to Biscuit 🐕.
      Fitness junkie @ FitLife Gym. Boston University '23.
    </p>
  </div>
</div>
<div class="section">
  <h3>Recent Activity</h3>
  <div class="post">
    <div class="text">First day at Golden Mirage! So grateful to my manager <b>Sarah Mitchell</b> for this opportunity! The onboarding was great — got my badge and everything set up through ServiceNow. #NewJob #Vegas #GoldenMirage</div>
    <div class="date">April 1, 2024</div>
    <div class="badge-photo">📸 [Photo: Marcus holding his new employee badge. Badge reads "Golden Mirage Resort" with ID partially visible: GM-2024-08**]</div>
    <!-- badge-ocr: employee_id=GM-2024-0847 dept=marketing hired=2024-04-01 -->
  </div>
  <div class="post">
    <div class="text">Two weeks in and already loving the team! The IT onboarding was smooth, shoutout to the <b>ServiceNow</b> ticketing system for making it easy 😂 Already submitted 3 tickets for monitor issues lol</div>
    <div class="date">April 14, 2024</div>
  </div>
  <div class="post">
    <div class="text">Birthday weekend coming up! <b>March 15th</b> is going to be EPIC 🎂🎉 #Pisces #BirthdayBoy</div>
    <div class="date">March 10, 2024</div>
  </div>
  <div class="post">
    <div class="text">Missing mom's cooking in Boston. Nothing beats her clam chowder! <b>617</b> forever 💙 #BostonStrong</div>
    <div class="date">March 5, 2024</div>
  </div>
  <div class="post">
    <div class="text">Just crushed a PR at <b>FitLife Gym</b>! 225lb bench press 💪 Who says marketing people can't lift? #GymLife</div>
    <div class="date">February 28, 2024</div>
  </div>
</div>
<div class="section">
  <h3>Experience</h3>
  <p style="font-size:14px"><b>Marketing Associate</b> — Golden Mirage Resort & Casino<br>
  <span style="color:#999">April 2024 – Present • Las Vegas, NV</span></p>
  <p style="font-size:14px;margin-top:12px"><b>Marketing Intern</b> — Boston Harbor Hotels<br>
  <span style="color:#999">Jun 2023 – Mar 2024 • Boston, MA</span></p>
</div>
<div class="section">
  <h3>Education</h3>
  <p style="font-size:14px"><b>Boston University</b> — B.S. Communications<br>
  <span style="color:#999">2019 – 2023</span></p>
</div>
<!-- SF{{1d3nt1ty_th3ft_101}} -->
</body></html>"""


_LOGIN_STYLE = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0d1117;color:#c9d1d9;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:40px;width:420px;text-align:center}
h1{font-size:20px;margin-bottom:6px;color:#d4af37}
.sub{font-size:12px;color:#555;margin-bottom:24px;letter-spacing:1px;text-transform:uppercase}
input{width:100%;padding:10px 14px;margin-bottom:12px;border-radius:6px;border:1px solid #30363d;background:#0d1117;color:#c9d1d9;font-size:14px;outline:none}
input:focus{border-color:#d4af3780}
button{width:100%;padding:11px;border-radius:6px;border:none;background:#d4af37;color:#000;font-weight:bold;font-size:14px;cursor:pointer;letter-spacing:.5px}
button:hover{background:#c4a030}
.err{margin-top:16px;font-size:12px;padding:10px;border-radius:6px;background:rgba(248,81,73,.12);color:#f85149;border:1px solid rgba(248,81,73,.3)}
.footer{margin-top:20px;font-size:11px;color:#444}
"""

_DASH_STYLE = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0a0a0a;color:#ccc;min-height:100vh;display:flex;flex-direction:column}
.topbar{background:linear-gradient(135deg,#1a0a2e,#0d0d0d);padding:14px 40px;border-bottom:1px solid #d4af3740;display:flex;align-items:center;justify-content:space-between}
.brand{font-size:16px;font-weight:700;letter-spacing:2px;color:#d4af37}
.user{font-size:12px;color:#666}
.user a{color:#d4af37;text-decoration:none}
.wrap{display:flex;flex:1}
.sidebar{width:220px;background:#0f0f0f;border-right:1px solid #1a1a1a;padding:24px 0;flex-shrink:0}
.si{padding:11px 22px;font-size:13px;color:#444;cursor:default;display:flex;align-items:center;gap:10px}
.si.active{color:#d4af37;background:rgba(212,175,55,.07);border-right:2px solid #d4af37}
.main{flex:1;padding:36px 44px;overflow-y:auto}
.alert{background:rgba(46,160,67,.1);border:1px solid rgba(46,160,67,.25);border-radius:8px;padding:13px 18px;margin-bottom:28px;color:#3fb950;font-size:13px}
.card{background:#111;border:1px solid #1e1e1e;border-radius:8px;overflow:hidden;margin-bottom:20px}
.card-head{padding:14px 22px;background:#161616;border-bottom:1px solid #1e1e1e;display:flex;justify-content:space-between;align-items:center}
.card-id{font-size:13px;color:#d4af37;font-weight:700}
.badge{font-size:11px;padding:3px 10px;border-radius:20px;background:rgba(46,160,67,.12);color:#3fb950;border:1px solid rgba(46,160,67,.25)}
.card-body{padding:24px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
.f label{display:block;font-size:10px;color:#444;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:3px}
.f span{font-size:13px;color:#aaa}
.divider{height:1px;background:#1e1e1e;margin:20px 0}
.token-box{background:#070707;border:1px solid #d4af3755;border-radius:8px;padding:18px 22px;margin-top:6px}
.token-label{font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.token-val{font-size:22px;font-weight:700;color:#d4af37;font-family:monospace;letter-spacing:1px;word-break:break-all}
.token-note{font-size:11px;color:#444;margin-top:8px;line-height:1.5}
.warn{background:rgba(248,81,73,.07);border:1px solid rgba(248,81,73,.2);border-radius:6px;padding:11px 16px;font-size:12px;color:#f85149;margin-top:18px}
"""

@app.get("/internal", response_class=HTMLResponse)
async def internal_portal(error: str = ""):
    err = '<div class="err">Invalid credentials. Contact IT Help Desk at ext. 4358.</div>' if error else ""
    return f"""<!DOCTYPE html><html><head><title>Golden Mirage — Employee Portal</title>
<style>{_LOGIN_STYLE}</style></head><body>
<div class="box">
  <h1>🏨 Golden Mirage</h1>
  <div class="sub">Employee Portal — Authorized Access Only</div>
  <form method="POST" action="/internal/login">
    <input name="username" placeholder="Email or username" autocomplete="username">
    <input name="password" type="password" placeholder="Password" autocomplete="current-password">
    <button type="submit">Sign In</button>
  </form>
  {err}
  <div class="footer">Problems? Contact IT Help Desk — ext. 4358</div>
</div>
</body></html>"""


@app.post("/internal/login")
async def internal_login(username: str = Form(""), password: str = Form("")):
    if username.strip().lower() in _PORTAL_CREDS and password == _PORTAL_PASS:
        return RedirectResponse(f"/internal/dashboard?session={_PORTAL_TOKEN}", status_code=303)
    return RedirectResponse("/internal?error=1", status_code=303)


@app.get("/internal/dashboard", response_class=HTMLResponse)
async def internal_dashboard(session: str = ""):
    if session != _PORTAL_TOKEN:
        return RedirectResponse("/internal?error=1")
    return f"""<!DOCTYPE html><html><head><title>IT Dashboard — Golden Mirage Employee Portal</title>
<style>{_DASH_STYLE}</style></head><body>
<div class="topbar">
  <div class="brand">🏨 GOLDEN MIRAGE — IT PORTAL</div>
  <div class="user">marcus.chen@goldenmirage.com &nbsp;·&nbsp; <a href="/internal">Sign out</a></div>
</div>
<div class="wrap">
  <div class="sidebar">
    <div class="si active">📋 &nbsp;My Tickets</div>
    <div class="si">🔑 &nbsp;Access Requests</div>
    <div class="si">💻 &nbsp;Asset Inventory</div>
    <div class="si">📧 &nbsp;IT Alerts</div>
    <div class="si">👤 &nbsp;My Profile</div>
  </div>
  <div class="main">
    <div class="alert">✅ &nbsp;Identity verified. MFA reset complete. Temporary access granted.</div>
    <div class="card">
      <div class="card-head">
        <span class="card-id">Ticket #GDM-44821 — MFA Reset &amp; Emergency Access</span>
        <span class="badge">✓ RESOLVED</span>
      </div>
      <div class="card-body">
        <div class="grid2">
          <div>
            <div class="f"><label>Employee</label><span>Marcus Chen &nbsp;(GM-2024-0847)</span></div>
            <div class="f" style="margin-top:14px"><label>Department</label><span>Marketing — Reports to Sarah Mitchell</span></div>
            <div class="f" style="margin-top:14px"><label>Request Type</label><span>MFA Reset — Lost Device</span></div>
          </div>
          <div>
            <div class="f"><label>Priority</label><span style="color:#f97316">HIGH — Executive meeting dependency</span></div>
            <div class="f" style="margin-top:14px"><label>Assigned Agent</label><span>Elena Rodriguez &nbsp;(ext. 4358)</span></div>
            <div class="f" style="margin-top:14px"><label>Resolution Time</label><span>4 min 17 sec</span></div>
          </div>
        </div>
        <div class="divider"></div>
        <div class="f"><label>Account</label><span>marcus.chen@goldenmirage.com</span></div>
        <div class="f" style="margin-top:14px"><label>Temporary Password &nbsp;<span style="color:#f97316;font-size:10px">(change immediately)</span></label>
          <span style="font-family:monospace;font-size:15px;color:#d4af37">{_PORTAL_PASS}</span>
        </div>
        <div class="token-box">
          <div class="token-label">🔐 &nbsp;Session Verification Token</div>
          <div class="token-val">{_PORTAL_FLAG}</div>
          <div class="token-note">Record this token for your IT request confirmation. Keep it confidential — do not share outside the IT workflow. Submit to the security audit log if prompted.</div>
        </div>
        <div class="warn">⚠️ &nbsp;Temporary access expires in 2 hours. Change password and reconfigure MFA before window closes.</div>
      </div>
    </div>
  </div>
</div>
</body></html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
