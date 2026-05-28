"""Phishing Studio — visual CSS constructor + dashboard."""
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

BACKEND = "http://127.0.0.1:8000"

app = FastAPI(title="SocialForge Phisher")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class IframeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        r = await call_next(request)
        r.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; frame-ancestors *"
        # CSP already set
        return r


app.add_middleware(IframeMiddleware)

FONTS = [
    ("'Segoe UI',sans-serif", "Corporate (Segoe UI)"),
    ("Arial,sans-serif", "Clean (Arial)"),
    ("Georgia,serif", "Classic (Georgia)"),
    ("'Courier New',monospace", "Technical (Courier New)"),
    ("Verdana,sans-serif", "Rounded (Verdana)"),
    ("'Times New Roman',serif", "Formal (Times New Roman)"),
]


def _esc(t: str) -> str:
    return (str(t)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


STYLE = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

*{margin:0;padding:0;box-sizing:border-box}

:root{
  --bg:#070b12;
  --surface:#0a0e17;
  --panel:#0d1117;
  --border:rgba(255,255,255,0.07);
  --border-active:rgba(0,255,136,0.3);
  --accent:#00ff88;
  --accent-dim:rgba(0,255,136,0.06);
  --accent-mid:rgba(0,255,136,0.12);
  --accent-glow:rgba(0,255,136,0.3);
  --red:#ef4444;
  --red-dim:rgba(239,68,68,0.08);
  --blue:#3b82f6;
  --blue-dim:rgba(59,130,246,0.08);
  --orange:#f59e0b;
  --orange-dim:rgba(245,158,11,0.08);
  --purple:#6366f1;
  --text:#e2e8f0;
  --muted:#94a3b8;
  --dim:#475569;
}

body{
  font-family:'JetBrains Mono',monospace;
  background:var(--bg);
  color:var(--text);
  height:100vh;
  display:flex;
  flex-direction:column;
  overflow:hidden;
  font-size:11px;
}

body::before{
  content:'';
  position:fixed;
  inset:0;
  background:repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent 2px,
    rgba(0,255,136,0.006) 2px,
    rgba(0,255,136,0.006) 3px
  );
  pointer-events:none;
  z-index:999;
}

/* ── HEADER ── */
.sf-header{
  height:40px;
  background:var(--surface);
  border-bottom:1px solid var(--border);
  display:flex;
  align-items:center;
  padding:0 16px;
  gap:12px;
  flex-shrink:0;
  position:relative;
}
.sf-header::after{
  content:'';
  position:absolute;
  bottom:0;left:0;right:0;
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,136,0.4),transparent);
}
.hdr-logo{
  font-size:11px;
  font-weight:700;
  color:var(--accent);
  letter-spacing:3px;
  text-transform:uppercase;
  display:flex;
  align-items:center;
  gap:8px;
}
.hdr-logo-badge{
  font-size:8px;
  font-weight:700;
  letter-spacing:1.5px;
  color:var(--bg);
  background:var(--accent);
  padding:2px 6px;
  border-radius:2px;
}
.hdr-divider{
  width:1px;
  height:16px;
  background:var(--border);
  flex-shrink:0;
}
.hdr-subtitle{
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
}
.hdr-stats{
  margin-left:auto;
  display:flex;
  gap:8px;
  align-items:center;
}
.hdr-stat{
  font-size:9px;
  letter-spacing:1.5px;
  text-transform:uppercase;
  color:var(--dim);
  border:1px solid var(--border);
  border-radius:3px;
  padding:3px 8px;
  background:var(--panel);
  font-weight:700;
}
.hdr-stat span{
  color:var(--accent);
}
.hdr-status-dot{
  width:6px;height:6px;
  border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 6px var(--accent);
  flex-shrink:0;
}

/* ── TAB BAR ── */
.sf-tabs{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:0 16px;
  display:flex;
  gap:0;
  flex-shrink:0;
}
.sf-tab{
  padding:9px 18px;
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
  background:none;
  border:none;
  border-bottom:2px solid transparent;
  cursor:pointer;
  font-family:'JetBrains Mono',monospace;
  transition:color .15s,border-color .15s;
  position:relative;
}
.sf-tab:hover{color:var(--muted)}
.sf-tab.active{
  color:var(--accent);
  border-bottom-color:var(--accent);
}
.sf-tab.active::before{
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:1px;
  background:var(--accent);
  opacity:0.3;
}

.tab-pane{display:none;flex:1;overflow:hidden;min-height:0}
.tab-pane.active{display:flex}

/* ── BANNERS ── */
.sf-msg{
  padding:7px 14px;
  font-size:9px;
  letter-spacing:1px;
  display:none;
  border-top:1px solid transparent;
  border-bottom:1px solid transparent;
  flex-shrink:0;
}
.sf-msg.show{display:block}
.sf-msg.ok{
  background:rgba(0,255,136,0.04);
  border-color:rgba(0,255,136,0.15);
  color:var(--accent);
}
.sf-msg.err{
  background:rgba(239,68,68,0.04);
  border-color:rgba(239,68,68,0.15);
  color:var(--red);
}

/* ── CONSTRUCTOR LAYOUT ── */
.constructor-layout{
  display:flex;
  flex:1;
  overflow:hidden;
  min-height:0;
}

/* ── LEFT PANEL (220px) ── */
.left-panel{
  width:220px;
  flex-shrink:0;
  background:var(--surface);
  border-right:1px solid var(--border);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}
.lp-section{
  border-bottom:1px solid var(--border);
  padding:10px 12px;
  flex-shrink:0;
}
.lp-section.flex-grow{
  flex:1;
  overflow-y:auto;
  flex-shrink:1;
}
.lp-section::-webkit-scrollbar{width:2px}
.lp-section::-webkit-scrollbar-thumb{background:var(--border-active)}

.panel-label{
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
  margin-bottom:8px;
  display:flex;
  align-items:center;
  gap:6px;
}
.panel-label::after{
  content:'';
  flex:1;
  height:1px;
  background:var(--border);
}

/* ── TEMPLATE LIST ── */
.tpl-list{
  display:flex;
  flex-direction:column;
  gap:1px;
}
.tpl-item{
  display:flex;
  align-items:center;
  gap:8px;
  padding:6px 8px;
  border-radius:3px;
  cursor:pointer;
  font-size:10px;
  font-weight:500;
  color:var(--muted);
  transition:all .12s;
  border:1px solid transparent;
  font-family:'JetBrains Mono',monospace;
  letter-spacing:0.3px;
}
.tpl-item:hover{
  background:var(--accent-dim);
  color:var(--text);
}
.tpl-item.active{
  background:var(--accent-dim);
  color:var(--accent);
  border-color:rgba(0,255,136,0.15);
}
.tpl-radio{
  font-size:11px;
  flex-shrink:0;
  width:12px;
  color:var(--dim);
  font-style:normal;
}
.tpl-item.active .tpl-radio{
  color:var(--accent);
}

/* ── QUALITY SCORE ── */
.quality-wrap{
  display:flex;
  flex-direction:column;
  gap:6px;
}
.q-bar-row{
  display:flex;
  align-items:center;
  gap:8px;
}
.q-bar-track{
  flex:1;
  height:4px;
  background:var(--panel);
  border-radius:2px;
  overflow:hidden;
  border:1px solid var(--border);
}
.q-bar-fill{
  height:100%;
  border-radius:2px;
  transition:width .5s ease,background .4s;
  width:0;
}
.q-pct{
  font-size:12px;
  font-weight:700;
  font-family:'JetBrains Mono',monospace;
  min-width:34px;
  text-align:right;
  letter-spacing:-0.5px;
}
.q-label{
  font-size:8px;
  letter-spacing:1.5px;
  text-transform:uppercase;
  color:var(--dim);
  font-weight:700;
}
.q-checks{
  display:flex;
  flex-direction:column;
  gap:3px;
  margin-top:2px;
}
.q-check{
  font-size:9px;
  display:flex;
  align-items:center;
  gap:5px;
  font-family:'JetBrains Mono',monospace;
  padding:3px 5px;
  border-radius:2px;
  border:1px solid transparent;
}
.q-check .qc-sym{
  flex-shrink:0;
  width:12px;
  font-size:10px;
}
.q-check .qc-txt{
  color:var(--dim);
  flex:1;
}
.q-check .qc-score{
  font-size:8px;
  color:var(--dim);
  opacity:0.7;
}
.q-check.pass{background:rgba(0,255,136,0.04);border-color:rgba(0,255,136,0.1)}
.q-check.pass .qc-txt{color:var(--text)}
.q-check.fail{background:rgba(239,68,68,0.04);border-color:rgba(239,68,68,0.08)}
.q-check.fail .qc-txt{color:var(--dim)}
.q-check.pend .qc-txt{color:var(--dim)}

/* ── HARVEST LOG ── */
.harvest-log{
  display:flex;
  flex-direction:column;
  gap:2px;
  max-height:140px;
  overflow-y:auto;
}
.harvest-log::-webkit-scrollbar{width:2px}
.harvest-log::-webkit-scrollbar-thumb{background:var(--border-active)}
.hl-row{
  display:flex;
  align-items:center;
  gap:5px;
  font-size:9px;
  font-family:'JetBrains Mono',monospace;
  padding:4px 6px;
  border-radius:2px;
  background:var(--panel);
  border:1px solid var(--border);
}
.hl-time{color:var(--dim);font-size:8px;flex-shrink:0}
.hl-email{color:var(--muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hl-status{font-size:10px;flex-shrink:0}
.hl-empty{
  font-size:9px;
  color:var(--dim);
  text-align:center;
  padding:10px 0;
  letter-spacing:1px;
  font-weight:700;
}

/* ── CENTER PREVIEW ── */
.center-preview{
  flex:1;
  display:flex;
  flex-direction:column;
  background:var(--panel);
  overflow:hidden;
  min-width:0;
  border-right:1px solid var(--border);
}
.cp-header{
  padding:8px 14px;
  border-bottom:1px solid var(--border);
  display:flex;
  align-items:center;
  justify-content:space-between;
  flex-shrink:0;
  background:var(--surface);
}
.cp-title{
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
}
.btn-update{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:3px;
  color:var(--dim);
  font-size:9px;
  font-weight:700;
  padding:3px 9px;
  cursor:pointer;
  font-family:'JetBrains Mono',monospace;
  letter-spacing:1px;
  transition:all .12s;
  text-transform:uppercase;
}
.btn-update:hover{
  border-color:var(--accent);
  color:var(--accent);
  background:var(--accent-dim);
}

/* ── BROWSER CHROME ── */
.browser-chrome{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:7px 12px;
  display:flex;
  align-items:center;
  gap:10px;
  flex-shrink:0;
}
.browser-dots{display:flex;gap:4px}
.browser-dot{
  width:8px;height:8px;
  border-radius:50%;
  opacity:0.7;
}
.browser-urlbar{
  flex:1;
  background:var(--bg);
  border:1px solid var(--border);
  border-radius:3px;
  padding:4px 10px;
  display:flex;
  align-items:center;
  gap:6px;
  font-size:9px;
  font-family:'JetBrains Mono',monospace;
}
.b-lock{
  color:var(--accent);
  font-size:9px;
  font-weight:700;
  flex-shrink:0;
  letter-spacing:0;
}
.b-url{
  color:var(--muted);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  font-size:9px;
}

.preview-frame{
  flex:1;
  width:100%;
  border:none;
  background:#fff;
  min-height:0;
}

/* ── RIGHT PANEL (260px) ── */
.right-panel{
  width:260px;
  flex-shrink:0;
  background:var(--surface);
  display:flex;
  flex-direction:column;
  overflow-y:auto;
}
.right-panel::-webkit-scrollbar{width:2px}
.right-panel::-webkit-scrollbar-thumb{background:var(--border-active)}

.rp-section{
  padding:12px 14px;
  border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.rp-title{
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
  margin-bottom:9px;
  display:flex;
  align-items:center;
  gap:6px;
}
.rp-title::after{
  content:'';
  flex:1;
  height:1px;
  background:var(--border);
}

/* ── FORM FIELDS ── */
.field-group{margin-bottom:8px}
.field-group:last-child{margin-bottom:0}
.field-label{
  font-size:9px;
  font-weight:700;
  color:var(--dim);
  letter-spacing:1px;
  text-transform:uppercase;
  margin-bottom:3px;
  display:block;
}
input[type=text],
input[type=email],
select,
textarea{
  width:100%;
  background:var(--bg);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:3px;
  padding:6px 8px;
  color:var(--text);
  font-size:10px;
  outline:none;
  font-family:'JetBrains Mono',monospace;
  transition:border-color .15s,box-shadow .15s;
}
input[type=text]:focus,
input[type=email]:focus,
select:focus,
textarea:focus{
  border-color:rgba(0,255,136,0.4);
  box-shadow:0 0 0 1px rgba(0,255,136,0.08);
}
input[type=text]::placeholder,
textarea::placeholder{
  color:var(--dim);
  opacity:0.7;
}
textarea{
  resize:vertical;
  min-height:52px;
  line-height:1.5;
}
select{
  cursor:pointer;
  -webkit-appearance:none;
  appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='5' viewBox='0 0 8 5'%3E%3Cpath fill='%23475569' d='M0 0l4 5 4-5z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;
  background-position:right 8px center;
  padding-right:24px;
}
select option{background:var(--surface);color:var(--text)}

/* ── DOMAIN MINI PREVIEW ── */
.domain-mini{
  font-size:9px;
  padding:4px 7px;
  background:var(--bg);
  border:1px solid var(--border);
  border-radius:3px;
  margin-top:4px;
  display:flex;
  align-items:center;
  gap:5px;
  color:var(--muted);
  font-family:'JetBrains Mono',monospace;
  overflow:hidden;
}
.domain-mini .lock{
  color:var(--accent);
  font-size:8px;
  font-weight:700;
  flex-shrink:0;
}
.domain-mini .url{
  color:var(--blue);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  font-size:9px;
}

/* ── COLOR PICKERS ── */
.color-group{
  display:flex;
  gap:7px;
  align-items:center;
}
.color-swatch{
  width:28px;
  height:28px;
  border-radius:3px;
  border:1px solid var(--border);
  cursor:pointer;
  flex-shrink:0;
  position:relative;
  overflow:hidden;
}
.color-swatch input[type=color]{
  position:absolute;
  top:-4px;left:-4px;
  width:calc(100% + 8px);
  height:calc(100% + 8px);
  border:none;
  padding:0;
  cursor:pointer;
  opacity:0;
}
.color-text{flex:1;font-family:'JetBrains Mono',monospace}

/* ── ACTIVE CAMPAIGNS (right panel) ── */
.campaign-list{
  display:flex;
  flex-direction:column;
  gap:4px;
}
.camp-item{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:3px;
  padding:7px 9px;
  font-size:9px;
  font-family:'JetBrains Mono',monospace;
  transition:border-color .12s;
}
.camp-item:hover{border-color:rgba(59,130,246,0.2)}
.camp-domain{
  color:var(--blue);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  margin-bottom:4px;
  font-weight:600;
  font-size:10px;
}
.camp-stats{display:flex;gap:10px}
.camp-stat{font-size:9px;color:var(--dim);letter-spacing:0.5px}
.camp-stat span{color:var(--muted)}
.camp-empty{
  font-size:9px;
  color:var(--dim);
  text-align:center;
  padding:12px 0;
  letter-spacing:1px;
  font-weight:700;
}

/* ── DEPLOY BUTTON ── */
.btn-deploy{
  width:100%;
  background:transparent;
  border:1px solid var(--accent);
  border-radius:3px;
  color:var(--accent);
  font-size:10px;
  font-weight:700;
  letter-spacing:2.5px;
  text-transform:uppercase;
  padding:11px;
  cursor:pointer;
  font-family:'JetBrains Mono',monospace;
  transition:all .2s;
  position:relative;
  overflow:hidden;
}
.btn-deploy::before{
  content:'';
  position:absolute;
  inset:0;
  background:var(--accent);
  opacity:0;
  transition:opacity .2s;
  pointer-events:none;
}
.btn-deploy:hover::before{opacity:0.07}
.btn-deploy:hover{
  box-shadow:0 0 16px rgba(0,255,136,0.2),inset 0 0 16px rgba(0,255,136,0.04);
}
.btn-deploy:active{transform:scale(0.99)}

/* ── DEPLOY URL ── */
.deploy-url-wrap{
  background:var(--bg);
  border:1px solid rgba(0,255,136,0.2);
  border-radius:3px;
  padding:7px 10px;
  display:flex;
  align-items:center;
  gap:8px;
  margin-top:8px;
}
.deploy-url-label{
  font-size:8px;
  font-weight:700;
  color:var(--dim);
  letter-spacing:1.5px;
  flex-shrink:0;
  text-transform:uppercase;
}
.deploy-url-text{
  font-size:9px;
  color:var(--accent);
  flex:1;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  cursor:pointer;
  font-family:'JetBrains Mono',monospace;
  font-weight:600;
}
.deploy-url-text:hover{text-decoration:underline}
.btn-copy{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:2px;
  color:var(--dim);
  font-size:8px;
  font-weight:700;
  padding:3px 7px;
  cursor:pointer;
  font-family:'JetBrains Mono',monospace;
  letter-spacing:1px;
  transition:all .12s;
  flex-shrink:0;
  text-transform:uppercase;
}
.btn-copy:hover{
  border-color:var(--accent);
  color:var(--accent);
  background:var(--accent-dim);
}

/* ── DASHBOARD LAYOUT ── */
.dashboard-layout{
  flex:1;
  overflow-y:auto;
  padding:16px;
  display:flex;
  flex-direction:column;
  gap:14px;
}
.dashboard-layout::-webkit-scrollbar{width:3px}
.dashboard-layout::-webkit-scrollbar-thumb{background:var(--border-active)}

.dash-header-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
}
.dash-title{
  font-size:9px;
  font-weight:700;
  letter-spacing:2px;
  text-transform:uppercase;
  color:var(--dim);
  display:flex;
  align-items:center;
  gap:8px;
}
.dash-title::before{
  content:'';
  display:inline-block;
  width:6px;height:6px;
  border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 6px var(--accent);
}

/* ── SUMMARY STATS ── */
.dash-stats-row{
  display:flex;
  gap:10px;
}
.d-stat{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:4px;
  padding:12px 16px;
  flex:1;
  position:relative;
  overflow:hidden;
}
.d-stat::before{
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:1px;
  background:linear-gradient(90deg,transparent,var(--accent),transparent);
  opacity:0.15;
}
.d-num{
  font-size:24px;
  font-weight:700;
  font-family:'JetBrains Mono',monospace;
  color:var(--accent);
  line-height:1;
  letter-spacing:-1px;
}
.d-num.red{color:var(--red)}
.d-num.blue{color:var(--blue)}
.d-num.gold{color:var(--orange)}
.d-lbl{
  font-size:8px;
  font-weight:700;
  color:var(--dim);
  margin-top:5px;
  letter-spacing:1.5px;
  text-transform:uppercase;
}

/* ── SITE CARDS ── */
.sites-grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:10px;
}
@media(max-width:1000px){.sites-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.sites-grid{grid-template-columns:1fr}}

.site-card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:4px;
  padding:12px;
  display:flex;
  flex-direction:column;
  gap:7px;
  transition:border-color .15s;
  position:relative;
  overflow:hidden;
}
.site-card::before{
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,136,0.2),transparent);
  opacity:0;
  transition:opacity .15s;
}
.site-card:hover{border-color:rgba(0,255,136,0.2)}
.site-card:hover::before{opacity:1}

.site-card-head{display:flex;flex-direction:column;gap:2px}
.site-card-domain{
  font-size:11px;
  font-weight:700;
  color:var(--text);
  word-break:break-all;
  letter-spacing:-0.3px;
}
.site-card-url{
  font-size:9px;
  color:var(--blue);
  font-family:'JetBrains Mono',monospace;
  opacity:0.8;
}
.site-card-quality{
  font-size:8px;
  font-weight:700;
  color:var(--dim);
  letter-spacing:1px;
  text-transform:uppercase;
}

.sc-stats{
  display:flex;
  gap:5px;
  flex-wrap:wrap;
}
.sc-stat{
  font-size:8px;
  font-weight:700;
  padding:2px 6px;
  border-radius:2px;
  font-family:'JetBrains Mono',monospace;
  letter-spacing:1px;
  text-transform:uppercase;
}
.sc-stat.visits{
  background:var(--blue-dim);
  color:var(--blue);
  border:1px solid rgba(59,130,246,0.15);
}
.sc-stat.creds{
  background:var(--accent-dim);
  color:var(--accent);
  border:1px solid rgba(0,255,136,0.15);
}

/* ── FLAG FRAGMENTS ── */
.frag-row{
  display:flex;
  gap:4px;
}
.frag-slot{
  flex:1;
  background:var(--bg);
  border:1px solid var(--border);
  border-radius:2px;
  padding:5px 3px;
  text-align:center;
  font-size:8px;
  font-family:'JetBrains Mono',monospace;
  color:var(--dim);
  display:flex;
  align-items:center;
  justify-content:center;
  gap:2px;
  overflow:hidden;
  font-weight:700;
  letter-spacing:0.5px;
}
.frag-slot.unlocked{
  background:var(--orange-dim);
  border-color:rgba(245,158,11,0.25);
  color:var(--orange);
}

.flag-complete-banner{
  background:var(--orange-dim);
  border:1px solid rgba(245,158,11,0.3);
  border-radius:3px;
  padding:8px 10px;
  font-size:10px;
  color:var(--orange);
  font-family:'JetBrains Mono',monospace;
  text-align:center;
  font-weight:700;
  letter-spacing:1px;
}
.flag-progress{
  display:flex;
  align-items:center;
  gap:6px;
  font-size:8px;
  font-weight:700;
  color:var(--dim);
  letter-spacing:0.5px;
  text-transform:uppercase;
}
.flag-progress-bar{
  flex:1;
  height:2px;
  background:var(--panel);
  border-radius:1px;
  overflow:hidden;
}
.flag-progress-fill{
  height:100%;
  background:var(--accent);
  border-radius:1px;
  transition:width .4s ease;
}

/* ── EDIT BUTTON ── */
.btn-edit{
  background:transparent;
  border:1px solid rgba(59,130,246,0.2);
  border-radius:3px;
  color:rgba(59,130,246,0.5);
  font-size:10px;
  width:26px;height:26px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;
  transition:all .12s;
  padding:0;
  font-family:'JetBrains Mono',monospace;
  font-weight:700;
  flex-shrink:0;
}
.btn-edit:hover{
  border-color:var(--blue);
  color:var(--blue);
  background:var(--blue-dim);
}

/* ── CREDS TABLE ── */
.site-card-actions{
  display:flex;
  gap:5px;
  align-items:center;
}
.btn-creds{
  background:var(--bg);
  border:1px solid rgba(59,130,246,0.2);
  border-radius:3px;
  color:var(--blue);
  font-size:8px;
  font-weight:700;
  padding:4px 8px;
  cursor:pointer;
  transition:all .12s;
  font-family:'JetBrains Mono',monospace;
  letter-spacing:1px;
  text-transform:uppercase;
  flex:1;
}
.btn-creds:hover{
  border-color:var(--blue);
  background:var(--blue-dim);
}
.btn-creds.active{
  background:var(--blue-dim);
  border-color:var(--blue);
}
.btn-del{
  background:transparent;
  border:1px solid rgba(239,68,68,0.15);
  border-radius:3px;
  color:rgba(239,68,68,0.4);
  font-size:10px;
  width:26px;height:26px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;
  transition:all .12s;
  padding:0;
  font-family:'JetBrains Mono',monospace;
  font-weight:700;
  flex-shrink:0;
}
.btn-del:hover{
  border-color:var(--red);
  color:var(--red);
  background:var(--red-dim);
}

.creds-panel{
  display:none;
  border-top:1px solid var(--border);
  padding-top:8px;
  margin-top:2px;
}
.creds-panel.open{display:block}

.creds-table{
  width:100%;
  border-collapse:collapse;
  font-size:9px;
  font-family:'JetBrains Mono',monospace;
}
.creds-table th{
  color:var(--dim);
  font-size:8px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:1px;
  padding:4px 5px;
  text-align:left;
  border-bottom:1px solid var(--border);
}
.creds-table td{
  padding:4px 5px;
  border-bottom:1px solid rgba(255,255,255,0.03);
}
.creds-table tr:last-child td{border-bottom:none}
.creds-npc{color:var(--text);font-weight:600}
.creds-login{color:var(--blue)}
.creds-pw{color:#f9a8d4}
.creds-flag{color:var(--orange);font-size:8px;font-weight:700}

.url-copy{
  font-size:9px;
  color:var(--accent);
  font-family:'JetBrains Mono',monospace;
  cursor:pointer;
  word-break:break-all;
  opacity:0.6;
  font-weight:600;
}
.url-copy:hover{
  opacity:1;
  text-decoration:underline;
}

.empty{
  text-align:center;
  color:var(--dim);
  font-size:10px;
  font-weight:700;
  padding:36px;
  letter-spacing:1.5px;
  text-transform:uppercase;
}

/* ── SCROLLBARS ── */
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border-active);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:rgba(0,255,136,0.5)}
"""


async def _fetch_sites_all(user_id: int) -> list:
    try:
        async with httpx.AsyncClient(timeout=4) as c:
            r = await c.get(f"{BACKEND}/api/phish/sites-all", params={"user_id": str(user_id)})
            return r.json().get("sites", [])
    except Exception:
        return []


def _font_options(selected: str = "") -> str:
    opts = []
    for val, label in FONTS:
        sel = " selected" if val == selected else ""
        opts.append(f'<option value="{_esc(val)}"{sel}>{_esc(label)}</option>')
    return "".join(opts)


@app.get("/", response_class=HTMLResponse)
async def main_ui(request: Request):
    q = dict(request.query_params)
    lab_id = q.get("lab", "mass_phishing")
    user_id = int(q.get("user", "1"))
    active_tab = q.get("tab", "constructor")
    created = q.get("created", "")
    error = q.get("error", "")

    pf_primary = q.get("primary", "#0078d4")
    pf_bg = q.get("bg", "#f3f2f1")
    pf_btn = q.get("btn_color", "#0078d4")
    pf_font = q.get("font", "'Segoe UI',sans-serif")
    pf_domain = q.get("domain", "")
    pf_company = q.get("company", "")
    pf_headline = q.get("headline", "")
    pf_sub = q.get("sub", "")
    pf_button = q.get("button", "Sign in")
    pf_redirect = q.get("redirect", "")

    created_banner = ""
    if created:
        phish_url = f"http://127.0.0.1:8000/p/{_esc(created)}"
        created_banner = (
            f'<div class="sf-msg ok show" id="created-banner">'
            f'[OK] PAGE DEPLOYED — '
            f'<span class="url-copy" onclick="navigator.clipboard.writeText(\'{phish_url}\')" title="Click to copy">'
            f'{_esc(phish_url)}</span>'
            f'</div>'
        )
    error_banner = f'<div class="sf-msg err show">[ERR] {_esc(error)}</div>' if error else ""

    font_opts = _font_options(pf_font)

    return HTMLResponse(f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PHISHER // SITE FACTORY</title>
<style>{STYLE}</style></head><body>

<!-- HEADER -->
<div class="sf-header">
  <div class="hdr-logo">
    <span class="hdr-logo-badge">SF</span>
    PHISHER
  </div>
  <div class="hdr-divider"></div>
  <div class="hdr-subtitle">SITE FACTORY</div>
  <div class="hdr-status-dot"></div>
  <div class="hdr-stats">
    <div class="hdr-stat">CAMPAIGNS <span id="hdr-campaigns">—</span></div>
    <div class="hdr-stat">HARVESTED <span id="hdr-harvested">—</span></div>
  </div>
</div>

<!-- TABS -->
<div class="sf-tabs">
  <button class="sf-tab{' active' if active_tab=='constructor' else ''}" onclick="showTab('constructor',this)">CONSTRUCTOR</button>
  <button class="sf-tab{' active' if active_tab=='dashboard' else ''}" onclick="showTab('dashboard',this)">HARVEST MONITOR</button>
</div>

{error_banner}
{created_banner}

<!-- ═══ CONSTRUCTOR TAB ═══ -->
<div id="tab-constructor" class="tab-pane{' active' if active_tab=='constructor' else ''}">
  <div class="constructor-layout">

    <!-- LEFT: TEMPLATES + QUALITY + HARVEST LOG -->
    <div class="left-panel">

      <div class="lp-section">
        <div class="panel-label">Templates</div>
        <div class="tpl-list">
          <div class="tpl-item active" id="pt-microsoft" onclick="setPageType('microsoft',this)">
            <span class="tpl-radio">●</span>Microsoft 365
          </div>
          <div class="tpl-item" id="pt-google" onclick="setPageType('google',this)">
            <span class="tpl-radio">○</span>Google
          </div>
          <div class="tpl-item" id="pt-linkedin" onclick="setPageType('linkedin',this)">
            <span class="tpl-radio">○</span>LinkedIn
          </div>
          <div class="tpl-item" id="pt-github" onclick="setPageType('github',this)">
            <span class="tpl-radio">○</span>GitHub
          </div>
          <div class="tpl-item" id="pt-dropbox" onclick="setPageType('dropbox',this)">
            <span class="tpl-radio">○</span>Dropbox
          </div>
          <div class="tpl-item" id="pt-docusign" onclick="setPageType('docusign',this)">
            <span class="tpl-radio">○</span>DocuSign
          </div>
          <div class="tpl-item" id="pt-outlook" onclick="setPageType('outlook',this)">
            <span class="tpl-radio">○</span>Outlook
          </div>
          <div class="tpl-item" id="pt-apple" onclick="setPageType('apple',this)">
            <span class="tpl-radio">○</span>Apple ID
          </div>
          <div class="tpl-item" id="pt-office365" onclick="setPageType('office365',this)">
            <span class="tpl-radio">○</span>Office 365
          </div>
          <div class="tpl-item" id="pt-paypal" onclick="setPageType('paypal',this)">
            <span class="tpl-radio">○</span>PayPal
          </div>
          <div class="tpl-item" id="pt-custom" onclick="setPageType('custom',this)">
            <span class="tpl-radio">○</span>Custom
          </div>
        </div>
      </div>

      <div class="lp-section">
        <div class="panel-label">Quality Score</div>
        <div class="quality-wrap">
          <div class="q-bar-row">
            <div class="q-bar-track">
              <div class="q-bar-fill" id="qbar-fill" style="background:var(--red)"></div>
            </div>
            <div class="q-pct" id="qbar-pct" style="color:var(--red)">0%</div>
          </div>
          <div class="q-label" id="q-label">POOR — EASILY DETECTED</div>
          <div class="q-checks">
            <div class="q-check fail" id="qc-domain">
              <span class="qc-sym">✗</span>
              <span class="qc-txt">Domain: plausible</span>
              <span class="qc-score">0/3</span>
            </div>
            <div class="q-check fail" id="qc-logo">
              <span class="qc-sym">✗</span>
              <span class="qc-txt">Brand: consistent</span>
              <span class="qc-score">0/2</span>
            </div>
            <div class="q-check fail" id="qc-urgency">
              <span class="qc-sym">✗</span>
              <span class="qc-txt">Urgency: missing</span>
              <span class="qc-score">-2</span>
            </div>
            <div class="q-check pend" id="qc-https">
              <span class="qc-sym">○</span>
              <span class="qc-txt">SSL: pending</span>
              <span class="qc-score">0/1</span>
            </div>
            <div class="q-check fail" id="qc-redirect">
              <span class="qc-sym">✗</span>
              <span class="qc-txt">Redirect: missing</span>
              <span class="qc-score">0/1</span>
            </div>
          </div>
        </div>
      </div>

      <div class="lp-section flex-grow">
        <div class="panel-label">Harvest Log</div>
        <div class="harvest-log" id="harvest-log">
          <div class="hl-empty">// NO DATA YET</div>
        </div>
      </div>

    </div>

    <!-- CENTER: LIVE PREVIEW -->
    <div class="center-preview">
      <div class="cp-header">
        <div class="cp-title">// LIVE PREVIEW</div>
        <button class="btn-update" onclick="updatePreview()">REFRESH</button>
      </div>

      <div class="browser-chrome">
        <div class="browser-dots">
          <div class="browser-dot" style="background:#ef4444"></div>
          <div class="browser-dot" style="background:#f59e0b"></div>
          <div class="browser-dot" style="background:#22c55e"></div>
        </div>
        <div class="browser-urlbar">
          <span class="b-lock">SSL</span>
          <span class="b-url" id="preview-url-bar">https://secure-login.office365.example.com</span>
        </div>
      </div>

      <iframe id="preview-frame" class="preview-frame" sandbox="allow-scripts allow-same-origin"></iframe>
    </div>

    <!-- RIGHT: CONFIGURATION -->
    <div class="right-panel">

      <div class="rp-section">
        <div class="rp-title">Target Company</div>
        <div class="field-group">
          <label class="field-label">Company Name</label>
          <input type="text" id="f-company" value="{_esc(pf_company)}"
                 placeholder="Microsoft Corporation"
                 oninput="updatePreview()">
        </div>
        <div class="field-group">
          <label class="field-label">Fake Domain</label>
          <input type="text" id="f-domain" value="{_esc(pf_domain)}"
                 placeholder="secure-login.office365.example.com"
                 oninput="updatePreview();updateQuality();updateDomainPreview()">
          <div class="domain-mini" id="domain-preview">
            <span class="lock">SSL</span>
            <span class="url" id="dp-url">https://secure-login.office365.example.com</span>
          </div>
        </div>
        <div class="field-group">
          <label class="field-label">Logo / Brand Text</label>
          <input type="text" id="f-logo" value="" placeholder="Microsoft" oninput="updatePreview()">
        </div>
      </div>

      <div class="rp-section">
        <div class="rp-title">Headline / CTA</div>
        <div class="field-group">
          <label class="field-label">Headline</label>
          <input type="text" id="f-headline" value="{_esc(pf_headline)}"
                 placeholder="Your account security is at risk"
                 oninput="updatePreview();updateQuality()">
        </div>
        <div class="field-group">
          <label class="field-label">Body Text</label>
          <textarea id="f-sub" rows="3"
                    placeholder="Unusual sign-in activity detected. Verify your identity within 1 hour."
                    oninput="updatePreview();updateQuality()">{_esc(pf_sub)}</textarea>
        </div>
        <div class="field-group">
          <label class="field-label">Button Text</label>
          <input type="text" id="f-button" value="{_esc(pf_button)}"
                 placeholder="Sign in" oninput="updatePreview()">
        </div>
        <div class="field-group">
          <label class="field-label">Redirect URL</label>
          <input type="text" id="f-redirect" value="{_esc(pf_redirect)}"
                 placeholder="https://microsoft.com" oninput="updateQuality()">
        </div>
      </div>

      <div class="rp-section">
        <div class="rp-title">Colors</div>
        <div class="field-group">
          <label class="field-label">Primary Color</label>
          <div class="color-group">
            <div class="color-swatch" id="sw-primary" style="background:{_esc(pf_primary)}">
              <input type="color" id="cp-primary" value="{_esc(pf_primary)}"
                     oninput="syncColorText('primary');updatePreview();updateQuality()">
            </div>
            <input type="text" class="color-text" id="ct-primary" value="{_esc(pf_primary)}" placeholder="#0078d4"
                   oninput="syncColorPicker('primary');updatePreview();updateQuality()">
          </div>
        </div>
        <div class="field-group">
          <label class="field-label">Button Color</label>
          <div class="color-group">
            <div class="color-swatch" id="sw-btn" style="background:{_esc(pf_btn)}">
              <input type="color" id="cp-btn" value="{_esc(pf_btn)}"
                     oninput="syncColorText('btn');updatePreview();updateQuality()">
            </div>
            <input type="text" class="color-text" id="ct-btn" value="{_esc(pf_btn)}" placeholder="#0078d4"
                   oninput="syncColorPicker('btn');updatePreview();updateQuality()">
          </div>
        </div>
        <div class="field-group">
          <label class="field-label">Background Color</label>
          <div class="color-group">
            <div class="color-swatch" id="sw-bg" style="background:{_esc(pf_bg)}">
              <input type="color" id="cp-bg" value="{_esc(pf_bg)}"
                     oninput="syncColorText('bg');updatePreview()">
            </div>
            <input type="text" class="color-text" id="ct-bg" value="{_esc(pf_bg)}" placeholder="#f3f2f1"
                   oninput="syncColorPicker('bg');updatePreview()">
          </div>
        </div>
        <div class="field-group">
          <label class="field-label">Font Family</label>
          <select id="f-font" onchange="updatePreview();updateQuality()">{font_opts}</select>
        </div>
      </div>

      <div class="rp-section">
        <form method="POST" action="/create" id="create-form">
          <input type="hidden" name="lab_id" value="{_esc(lab_id)}">
          <input type="hidden" name="user_id" value="{user_id}">
          <button type="button" class="btn-deploy" onclick="deployPhish(event)">
            DEPLOY SITE
          </button>
        </form>
        <div id="deploy-url-wrap" style="display:none" class="deploy-url-wrap">
          <span class="deploy-url-label">URL</span>
          <span class="deploy-url-text" id="deploy-url-text" onclick="copyDeployUrl()"></span>
          <button class="btn-copy" onclick="copyDeployUrl()">COPY</button>
        </div>
      </div>

      <div class="rp-section" style="flex:1;min-height:80px">
        <div class="rp-title">Active Campaigns</div>
        <div class="campaign-list" id="rp-campaigns">
          <div class="camp-empty">// NO CAMPAIGNS YET</div>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- ═══ DASHBOARD TAB ═══ -->
<div id="tab-dashboard" class="tab-pane{' active' if active_tab=='dashboard' else ''}">
  <div class="dashboard-layout">
    <div class="dash-header-row">
      <div class="dash-title">HARVEST MONITOR</div>
    </div>
    <div class="dash-stats-row">
      <div class="d-stat">
        <div class="d-num" id="ds-sites">—</div>
        <div class="d-lbl">Sites Active</div>
      </div>
      <div class="d-stat">
        <div class="d-num red" id="ds-creds">—</div>
        <div class="d-lbl">Credentials</div>
      </div>
    </div>
    <div class="sites-grid" id="dashboard-content">
      <div class="empty" style="grid-column:1/-1">// LOADING...</div>
    </div>
  </div>
</div>

<script>
const LAB_ID = "{_esc(lab_id)}";
const USER_ID = {user_id};
const BACKEND = "http://127.0.0.1:8000";

function showTab(t, btn) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.sf-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + t).classList.add('active');
  btn.classList.add('active');
  if (t === 'dashboard') loadDashboard();
}}

const PAGE_PRESETS = {{
  microsoft: {{ primary:'#0078d4', btn:'#0078d4', headline:'Sign in to your account', sub:'Your session has expired. Please verify your identity to continue.', button:'Sign in', logo:'Microsoft' }},
  google:    {{ primary:'#4285f4', btn:'#4285f4', headline:"Verify it's you", sub:'Unusual sign-in activity detected on your Google Account.', button:'Continue', logo:'Google' }},
  linkedin:  {{ primary:'#0077b5', btn:'#0077b5', headline:'Sign in to LinkedIn', sub:'Your account requires verification. Please confirm your credentials.', button:'Sign in', logo:'LinkedIn' }},
  github:    {{ primary:'#24292f', btn:'#2da44e', headline:'Sign in to GitHub', sub:'We detected a new sign-in to your account. Please verify your identity.', button:'Sign in', logo:'GitHub' }},
  dropbox:   {{ primary:'#0061ff', btn:'#0061ff', headline:'Sign in to Dropbox', sub:'Your Dropbox account requires immediate verification.', button:'Sign in', logo:'Dropbox' }},
  docusign:  {{ primary:'#ffb600', btn:'#ffb600', headline:'Complete Document Signing', sub:'A document is awaiting your signature. Verify your identity to proceed.', button:'View Document', logo:'DocuSign' }},
  outlook:   {{ primary:'#0078d4', btn:'#0078d4', headline:'Sign in to Outlook', sub:'Your Outlook session has expired. Sign in again to access your email.', button:'Sign in', logo:'Outlook' }},
  apple:     {{ primary:'#1d1d1f', btn:'#0071e3', headline:'Apple ID Verification Required', sub:'Your Apple ID has been locked for security reasons. Verify your identity.', button:'Continue', logo:'Apple' }},
  office365: {{ primary:'#d83b01', btn:'#d83b01', headline:'Sign in to Office 365', sub:'Your Office 365 account requires re-authentication to continue.', button:'Sign in', logo:'Office 365' }},
  paypal:    {{ primary:'#003087', btn:'#0070ba', headline:'Confirm Your PayPal Account', sub:'We noticed unusual activity. Please verify your account to restore access.', button:'Confirm Account', logo:'PayPal' }},
  custom:    {{ primary:'#374151', btn:'#374151', headline:'', sub:'', button:'Submit', logo:'' }},
}};

function setPageType(type, el) {{
  document.querySelectorAll('.tpl-item').forEach(i => {{
    i.classList.remove('active');
    i.querySelector('.tpl-radio').textContent = '○';
  }});
  el.classList.add('active');
  el.querySelector('.tpl-radio').textContent = '●';
  const preset = PAGE_PRESETS[type];
  if (!preset) return;
  document.getElementById('ct-primary').value = preset.primary;
  document.getElementById('cp-primary').value = preset.primary;
  document.getElementById('sw-primary').style.background = preset.primary;
  document.getElementById('ct-btn').value = preset.btn;
  document.getElementById('cp-btn').value = preset.btn;
  document.getElementById('sw-btn').style.background = preset.btn;
  if (preset.headline) document.getElementById('f-headline').value = preset.headline;
  if (preset.sub) document.getElementById('f-sub').value = preset.sub;
  if (preset.button) document.getElementById('f-button').value = preset.button;
  if (preset.logo) document.getElementById('f-logo').value = preset.logo;
  updatePreview(); updateQuality();
}}

function syncColorText(id) {{
  const val = document.getElementById('cp-' + id).value;
  document.getElementById('ct-' + id).value = val;
  document.getElementById('sw-' + id).style.background = val;
}}
function syncColorPicker(id) {{
  const val = document.getElementById('ct-' + id).value.trim();
  if (/^#[0-9a-fA-F]{{6}}$/.test(val)) {{
    document.getElementById('cp-' + id).value = val;
    document.getElementById('sw-' + id).style.background = val;
  }}
}}

function updateDomainPreview() {{
  const d = document.getElementById('f-domain').value || 'secure-login.office365.example.com';
  const url = 'https://' + d;
  document.getElementById('dp-url').textContent = url;
  document.getElementById('preview-url-bar').textContent = url;
}}

function luma(hex) {{
  try {{
    const h = hex.replace('#','');
    const r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16);
    return (r*299 + g*587 + b*114) / 1000;
  }} catch(e) {{ return 200; }}
}}

function buildPreviewHtml() {{
  const primary = document.getElementById('ct-primary').value || '#0078d4';
  const btn     = document.getElementById('ct-btn').value || primary;
  const bg      = document.getElementById('ct-bg')?.value || '#f3f2f1';
  const font    = document.getElementById('f-font').value || "'Segoe UI',sans-serif";
  const company = document.getElementById('f-company').value || 'Secure Portal';
  const logo    = document.getElementById('f-logo').value || company;
  const headline= document.getElementById('f-headline').value || 'Verify your identity';
  const sub     = document.getElementById('f-sub').value || 'Unusual sign-in activity detected.';
  const btnText = document.getElementById('f-button').value || 'Sign in';
  const darkBtn = luma(btn) < 128;
  const btnTx   = darkBtn ? '#ffffff' : '#111827';
  const darkBg  = luma(bg) < 128;
  const cardBg  = darkBg ? '#1f2937' : '#ffffff';
  const textCol = darkBg ? '#e5e7eb' : '#111827';
  const subCol  = darkBg ? '#9ca3af' : '#6b7280';
  const inpBg   = darkBg ? '#374151' : '#ffffff';
  const inpBdr  = darkBg ? '#4b5563' : '#d1d5db';
  const inpTxt  = darkBg ? '#f9fafb' : '#111827';

  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:${{font}};background:${{bg}};min-height:100vh;display:flex;flex-direction:column}}
.topbar{{background:${{primary}};padding:12px 24px;color:#fff;font-size:18px;font-weight:700;display:flex;align-items:center;gap:8px}}
.content{{flex:1;display:flex;align-items:center;justify-content:center;padding:40px 16px}}
.card{{background:${{cardBg}};border-radius:4px;padding:32px;width:100%;max-width:380px;box-shadow:0 2px 12px rgba(0,0,0,.12)}}
.logo{{font-size:22px;font-weight:700;color:${{primary}};margin-bottom:4px}}
h2{{font-size:17px;font-weight:600;color:${{textCol}};margin-bottom:6px}}
.sub{{font-size:13px;color:${{subCol}};margin-bottom:22px;line-height:1.5}}
label{{font-size:12px;font-weight:600;color:${{subCol}};display:block;margin-bottom:4px;margin-top:14px}}
input{{width:100%;padding:10px 12px;border:1px solid ${{inpBdr}};border-radius:4px;font-size:14px;background:${{inpBg}};color:${{inpTxt}};outline:none;font-family:inherit}}
input:focus{{border-color:${{primary}};box-shadow:0 0 0 2px ${{primary}}22}}
.submit{{width:100%;margin-top:20px;padding:11px;background:${{btn}};color:${{btnTx}};border:none;border-radius:4px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}}
.submit:hover{{opacity:.9}}
.footer{{font-size:10px;color:#9ca3af;text-align:center;margin-top:12px}}
.footer-link{{color:${{primary}};text-decoration:none;font-size:10px}}
</style></head><body>
<div class="topbar"><span style="font-size:22px">&#128274;</span> ${{logo}}</div>
<div class="content">
  <div class="card">
    <div class="logo">${{company}}</div>
    <h2>${{headline}}</h2>
    <div class="sub">${{sub}}</div>
    <label>Email address</label>
    <input type="text" placeholder="user@example.com">
    <label>Password</label>
    <input type="password" placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;">
    <button class="submit">${{btnText}}</button>
    <div class="footer">
      <a href="#" class="footer-link">Forgot password?</a> &nbsp;&middot;&nbsp;
      <a href="#" class="footer-link">Terms of use</a> &nbsp;&middot;&nbsp;
      <a href="#" class="footer-link">Privacy</a>
    </div>
  </div>
</div></body></html>`;
}}

function updatePreview() {{
  document.getElementById('preview-frame').srcdoc = buildPreviewHtml();
  updateDomainPreview();
}}

function updateQuality() {{
  let score = 0.20;
  const domain   = document.getElementById('f-domain').value;
  const headline = document.getElementById('f-headline').value;
  const sub      = document.getElementById('f-sub').value;
  const redirect = document.getElementById('f-redirect').value;
  const primary  = document.getElementById('ct-primary').value;
  const btn      = document.getElementById('ct-btn').value;
  const font     = document.getElementById('f-font').value;

  const hasDomain = domain && domain !== 'secure-login.example.com';
  if (hasDomain) score += 0.12;
  const spoofs = ['microsoft','google','amazon','apple','slack','office','secure','login','account','portal','auth'];
  const d = domain.toLowerCase();
  for (const s of spoofs) if (d.includes(s)) {{ score += 0.12; break; }}
  if (d.includes('-') || d.split('.').length > 2) score += 0.05;
  const hasHeadline = headline && headline.length > 5;
  if (hasHeadline) score += 0.10;
  const hasSub = sub && sub.length > 20;
  if (hasSub) score += 0.10;
  const urgency = ['urgent','locked','1 hour','expire','suspend','unusual','action required','immediately'];
  const bodyLow = (headline + ' ' + sub).toLowerCase();
  let hasUrgency = false;
  for (const u of urgency) if (bodyLow.includes(u)) {{ hasUrgency = true; score += 0.08; break; }}
  const hasRedirect = !!redirect;
  if (hasRedirect) score += 0.07;
  if (primary && primary !== '#0078d4') score += 0.06;
  if (btn && btn !== '#0078d4' && btn !== primary) score += 0.03;
  const hasCustomFont = font && !font.includes('Segoe');
  if (hasCustomFont) score += 0.03;
  score = Math.min(score, 0.97);
  const pct = Math.round(score * 100);

  const color = score < 0.4 ? '#ef4444' : score < 0.7 ? '#f59e0b' : '#00ff88';

  const qbarFill = document.getElementById('qbar-fill');
  const qbarPct  = document.getElementById('qbar-pct');
  qbarFill.style.width = pct + '%';
  qbarFill.style.background = color;
  qbarPct.textContent = pct + '%';
  qbarPct.style.color = color;

  const lbl = score < 0.4 ? 'POOR — EASILY DETECTED' : score < 0.65 ? 'AVERAGE — SOME WILL FALL' : score < 0.80 ? 'GOOD — MOST TARGETS CLICK' : 'EXCELLENT — HIGHLY CONVINCING';
  const lblEl = document.getElementById('q-label');
  lblEl.textContent = lbl;
  lblEl.style.color = color;

  function setQCheck(id, state, text, score_txt) {{
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'q-check ' + state;
    el.querySelector('.qc-sym').textContent = state === 'pass' ? '✓' : state === 'fail' ? '✗' : '○';
    el.querySelector('.qc-sym').style.color = state === 'pass' ? '#00ff88' : state === 'fail' ? '#ef4444' : 'rgba(212,245,226,0.25)';
    if (text) el.querySelector('.qc-txt').textContent = text;
    if (score_txt !== undefined) el.querySelector('.qc-score').textContent = score_txt;
  }}
  setQCheck('qc-domain', hasDomain ? 'pass' : 'fail', hasDomain ? 'Domain: plausible' : 'Domain: missing', hasDomain ? '3/3' : '0/3');
  setQCheck('qc-logo', !!(document.getElementById('f-logo').value || document.getElementById('f-company').value) ? 'pass' : 'fail', 'Brand: consistent', undefined);
  setQCheck('qc-urgency', hasUrgency ? 'pass' : 'fail', hasUrgency ? 'Urgency: detected' : 'Urgency: missing', undefined);
  setQCheck('qc-https', hasDomain ? 'pass' : 'pend', 'SSL: ' + (hasDomain ? 'active' : 'pending'), hasDomain ? '1/1' : '0/1');
  setQCheck('qc-redirect', hasRedirect ? 'pass' : 'fail', hasRedirect ? 'Redirect: set' : 'Redirect: missing', undefined);

  window._qualityScore = score;
}}

function syncHidden(e) {{
  const form = document.getElementById('create-form');
  const fields = {{
    domain:        'f-domain',
    company_name:  'f-company',
    headline:      'f-headline',
    subheadline:   'f-sub',
    button_text:   'f-button',
    redirect_url:  'f-redirect',
    primary_color: 'ct-primary',
    bg_color:      'ct-bg',
    btn_color:     'ct-btn',
  }};
  for (const [name, id] of Object.entries(fields)) {{
    let inp = form.querySelector(`input[name="${{name}}"]`);
    if (!inp) {{ inp = document.createElement('input'); inp.type = 'hidden'; inp.name = name; form.appendChild(inp); }}
    inp.value = document.getElementById(id) ? document.getElementById(id).value : '';
  }}
  let fi = form.querySelector('input[name="font_family"]');
  if (!fi) {{ fi = document.createElement('input'); fi.type = 'hidden'; fi.name = 'font_family'; form.appendChild(fi); }}
  fi.value = document.getElementById('f-font').value;
  let qs = form.querySelector('input[name="quality_score"]');
  if (!qs) {{ qs = document.createElement('input'); qs.type = 'hidden'; qs.name = 'quality_score'; form.appendChild(qs); }}
  qs.value = (window._qualityScore || 0.3).toFixed(3);
}}

async function deployPhish(e) {{
  if (e) e.preventDefault();
  syncHidden(null);
  const domain       = document.getElementById('f-domain')?.value?.trim() || 'secure-login.example.com';
  const company_name = document.getElementById('f-company')?.value?.trim() || '';
  const logo_text    = document.getElementById('f-logo')?.value?.trim() || '';
  const headline     = document.getElementById('f-headline')?.value?.trim() || '';
  const subheadline  = document.getElementById('f-sub')?.value?.trim() || '';
  const button_text  = document.getElementById('f-button')?.value?.trim() || 'Sign in';
  const redirect_url = document.getElementById('f-redirect')?.value?.trim() || '';
  const primary_color= document.getElementById('ct-primary')?.value?.trim() || '#0078d4';
  const bg_color     = document.getElementById('ct-bg')?.value?.trim() || '#f3f2f1';
  const btn_color    = document.getElementById('ct-btn')?.value?.trim() || '#0078d4';
  const font_family  = document.getElementById('f-font')?.value || "'Segoe UI',sans-serif";
  const quality_score= (window._qualityScore || 0.3).toFixed(3);

  const btn = document.querySelector('.btn-deploy');
  const origText = btn ? btn.textContent : 'DEPLOY SITE';
  if (btn) {{ btn.textContent = 'DEPLOYING...'; btn.disabled = true; }}

  try {{
    const r = await fetch(BACKEND + '/api/phish/create', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{
        lab_id: LAB_ID, user_id: USER_ID,
        template: 'custom', domain, company_name, logo_text, headline, subheadline,
        button_text, redirect_url, quality_score: parseFloat(quality_score),
        primary_color, bg_color, btn_color, font_family
      }})
    }});
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Deploy failed');
    const siteId = data.site_id || '';
    const url = BACKEND + '/p/' + siteId;
    const wrap = document.getElementById('deploy-url-wrap');
    const urlEl = document.getElementById('deploy-url-text');
    if (wrap && urlEl) {{ urlEl.textContent = url; wrap.style.display = 'flex'; }}
    updateRpCampaigns();
    showTab('dashboard', document.querySelector('.sf-tab:nth-child(2)'));
  }} catch(err) {{
    alert('[DEPLOY ERROR] ' + err.message);
  }} finally {{
    if (btn) {{ btn.textContent = origText; btn.disabled = false; }}
  }}
}}

function copyDeployUrl() {{
  const url = document.getElementById('deploy-url-text').textContent;
  navigator.clipboard.writeText(url).then(() => {{
    const btn = document.querySelector('.btn-copy');
    if (btn) {{ btn.textContent = 'COPIED'; setTimeout(() => btn.textContent = 'COPY', 1500); }}
  }});
}}

function toggleCreds(siteId) {{
  const panel = document.getElementById('cp-' + siteId);
  const btn   = document.getElementById('cb-' + siteId);
  if (!panel) return;
  const open = panel.classList.toggle('open');
  if (btn) btn.classList.toggle('active', open);
}}

function _buildCredsPanel(siteId, fd) {{
  const harvests = fd.harvests || [];
  const pieces   = fd.pieces   || [];
  const fullFlags = fd.full_flags || [];

  let rows = harvests.length
    ? harvests.map(h => `
        <tr>
          <td class="creds-npc">${{h.persona_name}}</td>
          <td class="creds-login">${{h.username}}</td>
          <td class="creds-pw">${{h.password}}</td>
        </tr>`).join('')
    : `<tr><td colspan="3" style="color:var(--dim);padding:10px 6px;text-align:center;font-size:9px;letter-spacing:1px;font-weight:700">NO CREDENTIALS HARVESTED YET</td></tr>`;

  const out = `
    <table class="creds-table">
      <thead><tr>
        <th>NPC</th><th>LOGIN</th><th>PASSWORD</th>
      </tr></thead>
      <tbody>${{rows}}</tbody>
    </table>`;

  return out;
}}

async function loadDashboard() {{
  const container = document.getElementById('dashboard-content');
  container.innerHTML = '<div class="empty" style="grid-column:1/-1">// SCANNING HARVEST NODES...</div>';
  try {{
    const r = await fetch(BACKEND + '/api/phish/sites-all?user_id=' + USER_ID);
    const data = await r.json();
    const sites = data.sites || [];

    if (!sites.length) {{
      container.innerHTML = '<div class="empty" style="grid-column:1/-1">// NO PHISHING PAGES DEPLOYED — CREATE ONE IN THE CONSTRUCTOR TAB</div>';
      updateHeaderStats(0, 0);
      return;
    }}

    const totalHarvests = sites.reduce((s, x) => s + x.harvest_count, 0);
    document.getElementById('ds-sites').textContent = sites.length;
    document.getElementById('ds-creds').textContent = totalHarvests;

    const flagData = await Promise.all(sites.map(async site => {{
      try {{
        const fr = await fetch(`${{BACKEND}}/api/phish/flag-status?user_id=${{USER_ID}}&site_id=${{site.site_id}}`);
        return fr.ok ? await fr.json() : {{}};
      }} catch(e) {{ return {{}}; }}
    }}));

    let html = '';
    window._siteData = {{}};

    for (let i = 0; i < sites.length; i++) {{
      const site = sites[i];
      window._siteData[site.site_id] = site;
      const fd   = flagData[i] || {{}};
      const url  = `http://127.0.0.1:8000/p/${{site.site_id}}`;
      const cnt  = site.harvest_count || 0;

      const credsPanel = _buildCredsPanel(site.site_id, fd);
      const credsBtnLabel = cnt ? `${{cnt}} CRED${{cnt !== 1 ? 'S' : ''}}` : '0 CREDS';

      html += `<div class="site-card">
        <div class="site-card-head">
          <div class="site-card-domain">${{site.domain || site.site_id}}</div>
          <div class="site-card-url">${{site.domain || site.site_id}}</div>
          <div class="site-card-quality">QUALITY: ${{Math.round((site.quality_score||0.3)*100)}}%</div>
        </div>
        <div class="sc-stats">
          <span class="sc-stat visits">${{site.visit_count || 0}} VISITS</span>
          <span class="sc-stat creds">${{cnt}} CREDS</span>
        </div>
        <span class="url-copy" onclick="navigator.clipboard.writeText('${{url}}')" title="Click to copy">${{url}}</span>
        <div class="site-card-actions">
          <button id="cb-${{site.site_id}}" class="btn-creds" onclick="toggleCreds('${{site.site_id}}')">${{credsBtnLabel}}</button>
          <button class="btn-edit" onclick="editSite('${{site.site_id}}')" title="Edit page">✎</button>
          <button class="btn-del" onclick="deleteSite('${{site.site_id}}','${{site.domain||site.site_id}}')" title="Delete page">✕</button>
        </div>
        <div id="cp-${{site.site_id}}" class="creds-panel${{cnt > 0 ? ' open' : ''}}">
          ${{credsPanel}}
        </div>
      </div>`;
    }}

    updateHeaderStats(sites.length, totalHarvests);
    container.innerHTML = html;

  }} catch(e) {{
    container.innerHTML = '<div class="empty" style="grid-column:1/-1">[ERR] FAILED TO LOAD: ' + e.message + '</div>';
  }}
}}

function updateHeaderStats(sites, creds) {{
  const hc = document.getElementById('hdr-campaigns');
  const hh = document.getElementById('hdr-harvested');
  if (hc) hc.textContent = sites;
  if (hh) hh.textContent = creds;
}}

async function updateRpCampaigns() {{
  try {{
    const r = await fetch(BACKEND + '/api/phish/sites-all?user_id=' + USER_ID);
    const data = await r.json();
    const sites = (data.sites || []).slice(0, 4);
    const wrap = document.getElementById('rp-campaigns');
    if (!wrap) return;
    const totalHarvests = (data.sites||[]).reduce((s,x)=>s+x.harvest_count,0);
    updateHeaderStats((data.sites||[]).length, totalHarvests);
    if (!sites.length) {{
      wrap.innerHTML = '<div class="camp-empty">// NO CAMPAIGNS YET</div>';
      return;
    }}
    wrap.innerHTML = sites.map(s =>
      `<div class="camp-item">
        <div class="camp-domain">${{s.domain || s.site_id}}</div>
        <div class="camp-stats">
          <span class="camp-stat">VISITS: <span>${{s.visit_count||0}}</span></span>
          <span class="camp-stat">CREDS: <span>${{s.harvest_count||0}}</span></span>
        </div>
      </div>`
    ).join('');
  }} catch(e) {{}}
}}

async function deleteSite(siteId, label) {{
  if (!confirm('Delete phishing page "' + label + '"?\\nAll harvested credentials will be lost.')) return;
  try {{
    const r = await fetch(BACKEND + '/api/phish/' + siteId, {{method: 'DELETE'}});
    if (r.ok) loadDashboard();
    else alert('Delete failed.');
  }} catch(e) {{ alert('Delete failed: ' + e.message); }}
}}

function editSite(siteId) {{
  const site = (window._siteData || {{}})[siteId];
  if (!site) return;
  const constructorTab = document.querySelector('.sf-tab:first-child');
  showTab('constructor', constructorTab);
  const set = (id, val) => {{ const el = document.getElementById(id); if (el && val != null) el.value = val; }};
  set('f-domain',   site.domain || '');
  set('f-company',  site.company_name || '');
  set('f-logo',     site.logo_text || '');
  set('f-headline', site.headline || '');
  set('f-sub',      site.subheadline || '');
  set('f-button',   site.button_text || 'Sign in');
  set('f-redirect', site.redirect_url || '');
  if (site.primary_color) {{
    set('ct-primary', site.primary_color);
    const cp = document.getElementById('cp-primary');
    const sw = document.getElementById('sw-primary');
    if (cp) cp.value = site.primary_color;
    if (sw) sw.style.background = site.primary_color;
  }}
  if (site.btn_color) {{
    set('ct-btn', site.btn_color);
    const cp = document.getElementById('cp-btn');
    const sw = document.getElementById('sw-btn');
    if (cp) cp.value = site.btn_color;
    if (sw) sw.style.background = site.btn_color;
  }}
  if (site.bg_color) {{
    set('ct-bg', site.bg_color);
    const cp = document.getElementById('cp-bg');
    const sw = document.getElementById('sw-bg');
    if (cp) cp.value = site.bg_color;
    if (sw) sw.style.background = site.bg_color;
  }}
  if (site.font_family) set('f-font', site.font_family);
  updatePreview(); updateQuality(); updateDomainPreview();
}}

updatePreview();
updateQuality();
updateDomainPreview();
updateRpCampaigns();
{f"loadDashboard();" if active_tab == "dashboard" else ""}
</script>
</body></html>""")


@app.post("/create")
async def create_phish(
    request: Request,
    lab_id: str = Form("mass_phishing"),
    user_id: int = Form(1),
    domain: str = Form(""),
    company_name: str = Form(""),
    headline: str = Form(""),
    subheadline: str = Form(""),
    button_text: str = Form("Sign in"),
    redirect_url: str = Form(""),
    quality_score: float = Form(0.3),
    primary_color: str = Form("#0078d4"),
    bg_color: str = Form("#f3f2f1"),
    btn_color: str = Form("#0078d4"),
    font_family: str = Form("'Segoe UI',sans-serif"),
):
    domain = domain.strip() or "secure-login.example.com"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(f"{BACKEND}/api/phish/create", json={
                "lab_id": lab_id,
                "user_id": user_id,
                "template": "custom",
                "domain": domain,
                "company_name": company_name.strip(),
                "headline": headline.strip(),
                "subheadline": subheadline.strip(),
                "button_text": button_text.strip() or "Sign in",
                "redirect_url": redirect_url.strip(),
                "quality_score": max(0.0, min(1.0, quality_score)),
                "primary_color": primary_color.strip() or "#0078d4",
                "bg_color": bg_color.strip() or "#f3f2f1",
                "btn_color": btn_color.strip() or "#0078d4",
                "font_family": font_family or "'Segoe UI',sans-serif",
            })
            r.raise_for_status()
            site_id = r.json().get("site_id", "")
    except Exception as e:
        err = str(e)[:120]
        return RedirectResponse(
            f"/?lab={lab_id}&user={user_id}&tab=constructor&error={err}",
            status_code=303,
        )
    return RedirectResponse(
        f"/?lab={lab_id}&user={user_id}&tab=constructor&created={site_id}",
        status_code=303,
    )


@app.post("/delete/{site_id}")
async def delete_phish(
    site_id: str,
    lab_id: str = Form("mass_phishing"),
    user_id: int = Form(1),
):
    try:
        async with httpx.AsyncClient(timeout=6) as c:
            await c.delete(f"{BACKEND}/api/phish/{site_id}")
    except Exception:
        pass
    return RedirectResponse(f"/?lab={lab_id}&user={user_id}&tab=dashboard", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9006)
