"""Phone Simulator — dial extensions or send SMS to NPC employees."""
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="SocialForge Phone")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AllowIframeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; frame-ancestors *"
        # CSP already set
        return response


app.add_middleware(AllowIframeMiddleware)

LABS_DIR = Path(__file__).parent.parent.parent / "labs"


def load_directory():
    """Return {lab_id: {ext: contact}}.

    Extensions aren't globally unique across labs — two separate scenarios can
    reuse ext 1001 — so the UI must pick the sub-directory for the active lab.
    """
    directory: dict = {}
    for f in LABS_DIR.glob("*.json"):
        with open(f, encoding="utf-8") as fh:
            lab = json.load(fh)
        company_name = lab["target_company"]["name"]
        if isinstance(company_name, dict):
            company_name = company_name.get("en") or next(iter(company_name.values()), "")
        lab_dir = directory.setdefault(lab["id"], {})
        for pid, p in lab.get("personas", {}).items():
            ext = p.get("phone_ext")
            if ext:
                lab_dir[str(ext)] = {
                    "name": p["name"],
                    "role": p["role"],
                    "company": company_name,
                    "persona_id": pid,
                    "lab_id": lab["id"],
                    "contactable": p.get("contactable", False),
                    "phone": p.get("phone_number") or "",
                    "busy": p.get("phone_busy", False),
                }
            mobile_ext = p.get("phone_mobile_ext")
            if mobile_ext and p.get("phone_busy"):
                lab_dir[str(mobile_ext)] = {
                    "name": p["name"],
                    "role": p["role"],
                    "company": company_name,
                    "persona_id": pid,
                    "lab_id": lab["id"],
                    "contactable": p.get("contactable", False),
                    "phone": p.get("phone_number") or "",
                    "busy": False,
                }
    return directory


PHONE_DIR = load_directory()


def _flatten_dir_for_display() -> dict:
    """Flat view keyed by 'lab_id:ext' for the /directory debug page."""
    flat: dict = {}
    for lab_id, labmap in PHONE_DIR.items():
        for ext, info in labmap.items():
            flat[f"{lab_id}:{ext}"] = info
    return flat


@app.get("/", response_class=HTMLResponse)
async def phone_ui():
    dir_js = json.dumps(PHONE_DIR)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TELEPHONY INTERCEPT TERMINAL</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── RESET & TOKENS ── */
*, *::before, *::after {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}
:root {{
  --bg:        #070b12;
  --surface:   #0a0e17;
  --elevated:  #0d1220;
  --border:    rgba(255,255,255,0.07);
  --accent:    #00ff88;
  --purple:    #6366f1;
  --blue:      #3b82f6;
  --amber:     #f59e0b;
  --red:       #ef4444;
  --orange:    #f97316;
  --text:      #e2e8f0;
  --muted:     #94a3b8;
  --font:      'JetBrains Mono', 'Courier New', monospace;
}}
html, body {{
  height: 100%;
  overflow: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 12px;
}}
::-webkit-scrollbar {{ width: 3px; height: 3px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(0,255,136,0.18); border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(0,255,136,0.38); }}

/* ── LAYOUT SHELL ── */
.shell {{
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}}

/* ── HEADER ── */
.hdr {{
  height: 40px;
  min-height: 40px;
  background: var(--surface);
  border-bottom: 1px solid rgba(0,255,136,0.12);
  display: flex;
  align-items: center;
  padding: 0 14px;
  gap: 12px;
  flex-shrink: 0;
  z-index: 50;
}}
.hdr-brand {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}}
.hdr-icon {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-dot 2s ease-in-out infinite;
  flex-shrink: 0;
}}
@keyframes pulse-dot {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(0,255,136,0.55); opacity: 1; }}
  50%       {{ box-shadow: 0 0 0 5px rgba(0,255,136,0);  opacity: .7; }}
}}
.hdr-icon.amber {{ background: var(--amber); animation: pulse-dot-amber 2s ease-in-out infinite; }}
@keyframes pulse-dot-amber {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(245,158,11,0.55); opacity: 1; }}
  50%       {{ box-shadow: 0 0 0 5px rgba(245,158,11,0);  opacity: .7; }}
}}
.hdr-title {{
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 3px;
  text-transform: uppercase;
  white-space: nowrap;
  text-shadow: 0 0 14px rgba(0,255,136,0.35);
}}
.hdr-sep {{
  width: 1px;
  height: 18px;
  background: var(--border);
  flex-shrink: 0;
}}
.hdr-meta {{
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}}
.hdr-badge {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--muted);
  padding: 2px 6px;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 3px;
  white-space: nowrap;
}}
.hdr-badge.green {{
  color: rgba(0,255,136,0.75);
  border-color: rgba(0,255,136,0.18);
  background: rgba(0,255,136,0.05);
}}
.hdr-uptime {{
  font-size: 9px;
  color: var(--muted);
  letter-spacing: 1px;
  white-space: nowrap;
}}
.hdr-cursor {{
  display: inline-block;
  width: 6px;
  height: 12px;
  background: var(--accent);
  margin-left: 3px;
  vertical-align: middle;
  animation: blink .9s step-end infinite;
  opacity: .8;
}}
@keyframes blink {{ 0%, 100% {{ opacity: .8; }} 50% {{ opacity: 0; }} }}

/* ── SPOOF BANNER ── */
.spoof-banner {{
  display: none;
  background: rgba(245,158,11,0.05);
  border-bottom: 1px solid rgba(245,158,11,0.18);
  color: var(--amber);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1.5px;
  padding: 5px 14px;
  gap: 14px;
  flex-wrap: wrap;
  align-items: center;
  flex-shrink: 0;
  animation: border-pulse-amber 2s ease-in-out infinite;
}}
.spoof-banner.show {{ display: flex; }}
.sb-label {{ opacity: .55; font-size: 8px; letter-spacing: 2px; margin-right: 4px; }}
@keyframes border-pulse-amber {{
  0%, 100% {{ border-bottom-color: rgba(245,158,11,0.18); }}
  50%       {{ border-bottom-color: rgba(245,158,11,0.42); }}
}}

/* ── BODY ── */
.body {{
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}}

/* ════════════════════════════════
   LEFT PANEL — 240px
   ════════════════════════════════ */
.left {{
  width: 240px;
  min-width: 240px;
  background: var(--surface);
  border-right: 1px solid rgba(0,255,136,0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}

/* section labels */
.section-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #475569;
  padding: 8px 12px 6px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}}

/* dir tabs */
.dir-tabs {{
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}}
.dir-tab {{
  flex: 1;
  padding: 7px 2px;
  text-align: center;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color .12s, border-color .12s;
  user-select: none;
  font-family: var(--font);
}}
.dir-tab:hover {{ color: var(--text); }}
.dir-tab.active {{
  color: var(--accent);
  border-bottom-color: var(--accent);
  text-shadow: 0 0 8px rgba(0,255,136,0.3);
}}

/* contact list */
.contact-list {{
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}}
.contact-item {{
  display: flex;
  align-items: flex-start;
  gap: 9px;
  padding: 8px 12px;
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: background .1s;
  position: relative;
}}
.contact-item:hover {{ background: rgba(0,255,136,0.035); }}
.contact-item.active {{
  border-left-color: var(--accent);
  background: rgba(0,255,136,0.05);
}}
.contact-item.inactive {{ opacity: .4; cursor: not-allowed; }}
.c-dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}}
.c-dot.online {{
  background: var(--accent);
  box-shadow: 0 0 5px rgba(0,255,136,0.5);
  animation: pulse-dot 2.5s ease-in-out infinite;
}}
.c-dot.offline {{ background: #1e293b; border: 1px solid #334155; }}
.c-body {{ flex: 1; min-width: 0; }}
.c-name {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.c-role {{
  font-size: 10px;
  color: var(--muted);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.c-ext {{
  font-size: 9px;
  color: rgba(0,255,136,0.5);
  letter-spacing: .5px;
  margin-top: 2px;
}}
.c-sms-tag {{
  display: inline-block;
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--blue);
  border: 1px solid rgba(59,130,246,0.3);
  background: rgba(59,130,246,0.06);
  border-radius: 3px;
  padding: 1px 4px;
  margin-top: 3px;
}}

/* call log */
.calllog-section {{
  flex-shrink: 0;
  max-height: 170px;
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border);
}}
.calllog-list {{
  flex: 1;
  overflow-y: auto;
  padding: 3px 0;
}}
.calllog-empty {{
  font-size: 10px;
  color: var(--muted);
  padding: 10px 12px;
  letter-spacing: .4px;
  font-style: italic;
}}
.calllog-item {{
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px;
  border-bottom: 1px solid var(--border);
  font-size: 10px;
}}
.cl-time {{ color: var(--muted); font-size: 9px; flex-shrink: 0; white-space: nowrap; }}
.cl-name {{ flex: 1; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.cl-status {{ font-size: 7px; font-weight: 700; letter-spacing: .5px; flex-shrink: 0; white-space: nowrap; padding: 2px 6px; border-radius: 3px; }}
.cl-status.ok   {{ color: var(--accent); background: rgba(0,255,136,0.08); border: 1px solid rgba(0,255,136,0.18); }}
.cl-status.miss {{ color: var(--muted);  background: rgba(255,255,255,0.03); border: 1px solid var(--border); }}
.cl-status.sms  {{ color: var(--blue);   background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); }}

/* ════════════════════════════════
   RIGHT PANEL
   ════════════════════════════════ */
.right {{
  flex: 1;
  min-width: 0;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}}

/* channel label strip */
.ch-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #475569;
  padding: 8px 16px 7px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--surface);
}}

/* ── DIALER TAB ── */
.dialer-panel {{
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 14px 16px;
  gap: 11px;
  overflow-y: auto;
  min-height: 0;
}}

/* LCD display */
.lcd {{
  background: #000;
  border: 1px solid rgba(0,255,136,0.14);
  border-radius: 6px;
  padding: 13px 14px;
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 8px;
  color: var(--accent);
  min-height: 54px;
  text-shadow: 0 0 12px rgba(0,255,136,0.45), 0 0 28px rgba(0,255,136,0.15);
  flex-shrink: 0;
  transition: border-color .15s, box-shadow .15s, color .15s, font-size .12s;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.lcd::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0, transparent 3px,
    rgba(0,255,136,0.01) 3px, rgba(0,255,136,0.01) 4px
  );
  pointer-events: none;
}}
.lcd.ringing   {{ color: var(--amber); font-size: 12px; letter-spacing: 2px; border-color: rgba(245,158,11,0.25); }}
.lcd.connected {{ color: var(--accent); font-size: 12px; letter-spacing: 2px; border-color: rgba(0,255,136,0.3); box-shadow: 0 0 14px rgba(0,255,136,0.1); }}
.lcd.voicemail {{ color: var(--blue);  font-size: 12px; letter-spacing: 2px; border-color: rgba(59,130,246,0.25); }}
.lcd.ended     {{ color: var(--muted); font-size: 12px; letter-spacing: 2px; }}

/* keypad */
.keypad {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  flex-shrink: 0;
}}
.key {{
  background: rgba(0,255,136,0.03);
  border: 1px solid rgba(0,255,136,0.09);
  border-radius: 5px;
  height: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  user-select: none;
  transition: background .1s, border-color .1s, transform .07s, box-shadow .1s;
}}
.key:hover {{
  background: rgba(0,255,136,0.07);
  border-color: rgba(0,255,136,0.22);
  box-shadow: 0 0 8px rgba(0,255,136,0.07);
}}
.key:active {{
  transform: scale(.93);
  background: rgba(0,255,136,0.12);
  border-color: var(--accent);
  box-shadow: 0 0 12px rgba(0,255,136,0.18);
}}
.key-d {{
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
  font-family: var(--font);
}}
.key-l {{
  font-size: 7px;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 1px;
  line-height: 1;
  font-family: var(--font);
}}

/* dial actions */
.dial-actions {{
  display: flex;
  gap: 7px;
  flex-shrink: 0;
}}
.btn-call {{
  flex: 1;
  height: 44px;
  background: rgba(0,255,136,0.07);
  color: var(--accent);
  border: 1px solid rgba(0,255,136,0.25);
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  font-family: var(--font);
  transition: background .12s, box-shadow .12s;
}}
.btn-call:hover {{ background: rgba(0,255,136,0.12); box-shadow: 0 0 16px rgba(0,255,136,0.2); }}
.btn-call:active {{ transform: scale(.98); }}
.btn-call.red {{
  background: rgba(239,68,68,0.07);
  color: var(--red);
  border-color: rgba(239,68,68,0.25);
}}
.btn-call.red:hover {{ background: rgba(239,68,68,0.12); box-shadow: 0 0 16px rgba(239,68,68,0.2); }}
.btn-sms-quick {{
  height: 44px;
  padding: 0 13px;
  background: rgba(59,130,246,0.06);
  color: var(--blue);
  border: 1px solid rgba(59,130,246,0.22);
  border-radius: 5px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  font-family: var(--font);
  transition: background .12s, box-shadow .12s;
  white-space: nowrap;
}}
.btn-sms-quick:hover {{ background: rgba(59,130,246,0.1); box-shadow: 0 0 10px rgba(59,130,246,0.18); }}
.btn-clr {{
  height: 44px;
  padding: 0 13px;
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 5px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.5px;
  cursor: pointer;
  font-family: var(--font);
  transition: border-color .12s, color .12s;
}}
.btn-clr:hover {{ border-color: rgba(0,255,136,0.22); color: var(--text); }}
.err-msg {{
  font-size: 10px;
  color: var(--red);
  letter-spacing: .5px;
  text-align: center;
  padding: 3px 0;
  flex-shrink: 0;
}}

/* ── ACTIVE CALL VIEW ── */
.callview-panel {{
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 14px 16px;
  gap: 10px;
  min-height: 0;
}}
.conn-status {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid rgba(0,255,136,0.2);
  border-radius: 5px;
  background: rgba(0,255,136,0.04);
  flex-shrink: 0;
}}
.conn-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-dot 1.5s ease-in-out infinite;
  flex-shrink: 0;
}}
.conn-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
}}
.conn-name {{
  font-size: 12px;
  color: var(--text);
  font-weight: 600;
}}
.conn-sep {{ color: var(--muted); }}

/* call meta row */
.call-meta {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  gap: 10px;
}}
.call-info .ci-role    {{ font-size: 9px;  color: var(--muted);  text-transform: uppercase; letter-spacing: 1px; }}
.call-info .ci-company {{ font-size: 10px; color: var(--accent); margin-top: 2px; letter-spacing: .3px; }}
.call-info .ci-ext     {{ font-size: 9px;  color: var(--muted);  margin-top: 3px; }}
.call-info .ci-ext.spoof-ext {{ color: rgba(252,165,165,0.75); font-size: 9px; line-height: 1.6; word-break: break-word; }}
.call-timer {{
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 4px;
  text-shadow: 0 0 10px rgba(0,255,136,0.38);
  flex-shrink: 0;
  font-family: var(--font);
}}

/* waveform */
.waveform {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 30px;
  flex-shrink: 0;
}}
.wb {{
  width: 3px;
  border-radius: 2px;
  background: rgba(0,255,136,0.45);
  animation: wave-pulse 1s ease-in-out infinite;
}}
.wb:nth-child(1) {{ height: 7px;  animation-delay: 0s; }}
.wb:nth-child(2) {{ height: 16px; animation-delay: .1s; }}
.wb:nth-child(3) {{ height: 26px; animation-delay: .2s; }}
.wb:nth-child(4) {{ height: 20px; animation-delay: .3s; }}
.wb:nth-child(5) {{ height: 12px; animation-delay: .4s; }}
.wb:nth-child(6) {{ height: 24px; animation-delay: .5s; }}
.wb:nth-child(7) {{ height: 9px;  animation-delay: .15s; }}
.wb:nth-child(8) {{ height: 18px; animation-delay: .25s; }}
.wb:nth-child(9) {{ height: 6px;  animation-delay: .35s; }}
@keyframes wave-pulse {{
  0%, 100% {{ transform: scaleY(1);   opacity: .45; }}
  50%       {{ transform: scaleY(1.9); opacity: 1;   }}
}}

/* chat area */
.chat-area {{
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-height: 0;
  padding: 2px 0;
}}
.msg {{
  max-width: 90%;
  padding: 7px 11px;
  border-radius: 5px;
  font-size: 12px;
  line-height: 1.55;
  animation: fade-up .18s ease-out;
  flex-shrink: 0;
  word-wrap: break-word;
  font-family: var(--font);
}}
@keyframes fade-up {{ from {{ opacity:0; transform:translateY(4px); }} to {{ opacity:1; transform:translateY(0); }} }}
.msg-user {{
  align-self: flex-end;
  background: rgba(0,255,136,0.07);
  border: 1px solid rgba(0,255,136,0.18);
  color: var(--text);
  border-radius: 5px 5px 2px 5px;
}}
.msg-npc {{
  align-self: flex-start;
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 5px 5px 5px 2px;
}}
.npc-name {{
  font-size: 8px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 4px;
}}
.msg-system {{
  align-self: center;
  color: var(--muted);
  font-size: 10px;
  font-style: italic;
  letter-spacing: .4px;
}}

/* chat input */
.chat-input-row {{
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  align-items: center;
}}
.chat-input-row input {{
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 9px 11px;
  color: var(--text);
  font-size: 12px;
  outline: none;
  font-family: var(--font);
  transition: border-color .12s;
}}
.chat-input-row input::placeholder {{ color: var(--muted); }}
.chat-input-row input:focus {{ border-color: rgba(0,255,136,0.28); box-shadow: 0 0 8px rgba(0,255,136,0.06); }}
.chat-input-row button {{
  background: rgba(0,255,136,0.07);
  color: var(--accent);
  border: 1px solid rgba(0,255,136,0.22);
  border-radius: 5px;
  padding: 0 13px;
  height: 36px;
  font-weight: 700;
  cursor: pointer;
  font-size: 10px;
  letter-spacing: 1.5px;
  font-family: var(--font);
  text-transform: uppercase;
  transition: box-shadow .12s, background .12s;
  white-space: nowrap;
}}
.chat-input-row button:hover {{ box-shadow: 0 0 10px rgba(0,255,136,0.18); background: rgba(0,255,136,0.11); }}

.btn-hangup {{
  width: 100%;
  height: 42px;
  background: rgba(239,68,68,0.06);
  color: var(--red);
  border: 1px solid rgba(239,68,68,0.22);
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  font-family: var(--font);
  transition: background .12s, box-shadow .12s;
  flex-shrink: 0;
}}
.btn-hangup:hover {{ background: rgba(239,68,68,0.11); box-shadow: 0 0 14px rgba(239,68,68,0.2); }}

/* ── MESSAGES / INBOX ── */
.inbox-hdr {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}}
.inbox-title {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #475569;
}}
.btn-new {{
  background: rgba(59,130,246,0.07);
  color: var(--blue);
  border: 1px solid rgba(59,130,246,0.22);
  border-radius: 4px;
  width: 26px;
  height: 26px;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: box-shadow .12s;
  font-family: var(--font);
  line-height: 1;
}}
.btn-new:hover {{ box-shadow: 0 0 8px rgba(59,130,246,0.2); }}
.inbox {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; min-height: 0; }}
.thread-item {{
  display: flex;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background .1s;
}}
.thread-item:hover {{ background: rgba(0,255,136,0.03); }}
.avatar {{
  width: 34px;
  height: 34px;
  border-radius: 5px;
  background: var(--elevated);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 11px;
  color: var(--accent);
  letter-spacing: .5px;
  flex-shrink: 0;
  font-family: var(--font);
}}
.thread-body {{ flex: 1; min-width: 0; }}
.thread-row1 {{ display: flex; justify-content: space-between; align-items: baseline; gap: 6px; }}
.thread-name {{ font-size: 11px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.thread-time {{ font-size: 9px; color: var(--muted); flex-shrink: 0; }}
.thread-preview {{ font-size: 10px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }}
.empty-inbox {{ text-align: center; color: var(--muted); font-size: 10px; padding: 36px 20px; line-height: 2; letter-spacing: .5px; }}

/* ── SMS CONVERSATION ── */
.sms-thread-hdr {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}}
.back-btn {{
  background: transparent;
  border: 1px solid var(--border);
  color: var(--blue);
  font-size: 15px;
  cursor: pointer;
  padding: 3px 9px;
  border-radius: 4px;
  transition: border-color .12s;
  font-family: var(--font);
  line-height: 1;
}}
.back-btn:hover {{ border-color: rgba(59,130,246,0.4); }}
.sms-av {{
  width: 32px;
  height: 32px;
  border-radius: 5px;
  background: var(--elevated);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 10px;
  color: var(--accent);
  letter-spacing: .5px;
  flex-shrink: 0;
  font-family: var(--font);
}}
.sms-info .si-name {{ font-size: 12px; font-weight: 600; color: var(--text); }}
.sms-info .si-sub  {{ font-size: 9px;  color: var(--muted); margin-top: 1px; }}
.sms-char-count {{ font-size: 9px; color: var(--muted); text-align: right; letter-spacing: .4px; padding: 0 14px 2px; }}
.sms .chat-input-row input:focus {{ border-color: rgba(59,130,246,0.3); }}
.sms .chat-input-row button {{
  background: rgba(59,130,246,0.07);
  color: var(--blue);
  border-color: rgba(59,130,246,0.22);
}}
.sms .chat-input-row button:hover {{ box-shadow: 0 0 10px rgba(59,130,246,0.18); }}
.sms .msg-user {{
  background: rgba(59,130,246,0.07);
  border-color: rgba(59,130,246,0.2);
}}

/* ── SPOOF TAB ── */
.tool-panel {{
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 0;
}}
.tp-section {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 10px 0 5px;
  flex-shrink: 0;
}}
.tp-section.green  {{ color: var(--accent); }}
.tp-section.amber  {{ color: var(--amber); }}
.tp-section.purple {{ color: var(--purple); }}
.tp-section.blue   {{ color: var(--blue); }}
.tp-sub {{
  font-size: 10px;
  color: var(--muted);
  line-height: 1.7;
  margin-bottom: 10px;
  flex-shrink: 0;
}}
.field-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 8px;
  margin-bottom: 3px;
  display: block;
}}
.tool-panel input[type=text],
.tool-panel select {{
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 8px 10px;
  color: var(--text);
  font-size: 11px;
  outline: none;
  font-family: var(--font);
  transition: border-color .12s;
  -webkit-appearance: none;
  appearance: none;
}}
.tool-panel input[type=text]:focus,
.tool-panel select:focus {{
  border-color: rgba(0,255,136,0.28);
  box-shadow: 0 0 8px rgba(0,255,136,0.06);
}}
.tool-panel input[type=text]::placeholder {{ color: var(--muted); }}
.info-box {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 8px 10px;
  font-size: 10px;
  color: var(--muted);
  line-height: 1.65;
  flex-shrink: 0;
  margin-top: 3px;
}}
.spoof-active-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(245,158,11,0.06);
  border: 1px solid rgba(245,158,11,0.22);
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--amber);
  margin-top: 8px;
}}
.spoof-dot {{
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--amber);
  animation: pulse-dot-amber 1.4s ease-in-out infinite;
}}
.btn-panel {{
  background: rgba(0,255,136,0.06);
  color: var(--accent);
  border: 1px solid rgba(0,255,136,0.22);
  border-radius: 5px;
  padding: 10px;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
  margin-top: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: var(--font);
  transition: box-shadow .12s, background .12s;
}}
.btn-panel:hover {{ box-shadow: 0 0 14px rgba(0,255,136,0.18); background: rgba(0,255,136,0.1); }}
.btn-panel.amber {{
  background: rgba(245,158,11,0.06);
  color: var(--amber);
  border-color: rgba(245,158,11,0.22);
}}
.btn-panel.amber:hover {{ box-shadow: 0 0 14px rgba(245,158,11,0.18); background: rgba(245,158,11,0.1); }}
.btn-panel-reset {{
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 8px;
  font-size: 10px;
  cursor: pointer;
  width: 100%;
  margin-top: 5px;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-family: var(--font);
  transition: border-color .12s, color .12s;
}}
.btn-panel-reset:hover {{ border-color: rgba(0,255,136,0.22); color: var(--text); }}
.voice-drop {{
  border: 1px dashed rgba(99,102,241,0.3);
  border-radius: 5px;
  padding: 14px 10px;
  text-align: center;
  color: var(--muted);
  font-size: 10px;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  flex-shrink: 0;
  letter-spacing: .5px;
}}
.voice-drop:hover {{ border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.04); }}
.voice-drop.has-sample {{ border-color: rgba(0,255,136,0.32); background: rgba(0,255,136,0.04); color: var(--accent); border-style: solid; }}
.risk-meter {{
  height: 3px;
  border-radius: 2px;
  background: var(--elevated);
  overflow: hidden;
  margin: 5px 0 3px;
  flex-shrink: 0;
}}
.risk-fill {{ height: 100%; transition: all .3s; border-radius: 2px; }}
.risk-low  .risk-fill {{ background: var(--accent); width: 20%; }}
.risk-med  .risk-fill {{ background: var(--amber);  width: 55%; }}
.risk-high .risk-fill {{ background: var(--red);    width: 90%; }}
.risk-label {{ font-size: 9px; color: var(--muted); letter-spacing: 1px; flex-shrink: 0; text-transform: uppercase; }}

/* ── GATE OVERLAY ── */
.gate {{
  position: absolute;
  inset: 0;
  background: rgba(7,11,18,0.97);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  z-index: 20;
  pointer-events: none;
}}
.gate.show {{ display: flex; pointer-events: auto; }}
.gate-icon {{
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: rgba(0,255,136,0.05);
  border: 1px solid rgba(0,255,136,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: 16px;
  color: var(--muted);
}}
.gate h2 {{
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
}}
.gate p {{
  font-size: 11px;
  color: var(--muted);
  line-height: 1.8;
  margin-bottom: 20px;
  max-width: 310px;
  letter-spacing: .3px;
}}
.gate .start-btn {{
  background: rgba(0,255,136,0.07);
  color: var(--accent);
  border: 1px solid rgba(0,255,136,0.28);
  border-radius: 5px;
  padding: 11px 26px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  font-family: var(--font);
  transition: box-shadow .15s;
}}
.gate .start-btn:hover {{ box-shadow: 0 0 20px rgba(0,255,136,0.22); }}
.gate .start-btn:disabled {{ opacity: .4; cursor: default; box-shadow: none; }}

/* ── GAME OVER ── */
.gameover {{
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(60,0,0,.97) 0%, rgba(0,0,0,.99) 80%);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  z-index: 30;
  animation: go-fade .4s ease-out;
  pointer-events: none;
}}
.gameover.show {{ display: flex; pointer-events: auto; }}
@keyframes go-fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.go-scan {{
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0, transparent 2px,
    rgba(255,0,0,.035) 2px, rgba(255,0,0,.035) 3px
  );
  pointer-events: none;
  animation: scan-move 4s linear infinite;
}}
@keyframes scan-move {{ from {{ background-position: 0 0; }} to {{ background-position: 0 100px; }} }}
.go-inner {{ position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; }}
.go-bust  {{ font-size: 9px; color: rgba(252,165,165,0.6); letter-spacing: 4px; text-transform: uppercase; margin-bottom: 8px; }}
.go-h1 {{
  font-family: 'Impact', 'Arial Black', sans-serif;
  font-size: 48px;
  font-weight: 900;
  letter-spacing: 4px;
  color: #ff2222;
  text-shadow: 0 0 18px rgba(255,40,40,.9), 0 0 48px rgba(255,0,0,.45), 2px 2px 0 #000;
  line-height: 1;
  animation: gta-bust 1.1s ease-out;
}}
@keyframes gta-bust {{
  0%   {{ transform: scale(3.5); opacity: 0; filter: blur(16px); }}
  60%  {{ transform: scale(.92); opacity: 1; filter: blur(0); }}
  100% {{ transform: scale(1); }}
}}
.go-h2 {{ font-size: 12px; letter-spacing: 3px; color: rgba(252,165,165,0.75); margin: 6px 0 18px; }}
.go-who    {{ font-size: 10px; color: rgba(252,165,165,0.65); margin-bottom: 10px; font-style: italic; }}
.go-reason {{
  font-size: 11px;
  color: rgba(255,220,220,0.9);
  line-height: 1.65;
  margin-bottom: 20px;
  max-width: 280px;
  padding: 9px 13px;
  background: rgba(255,0,0,.06);
  border: 1px solid rgba(239,68,68,.2);
  border-radius: 5px;
}}
.go-btns {{ display: flex; gap: 8px; }}
.go-reset {{
  background: rgba(239,68,68,0.09);
  color: var(--red);
  border: 1px solid rgba(239,68,68,0.32);
  border-radius: 5px;
  padding: 9px 18px;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: var(--font);
  transition: box-shadow .15s;
}}
.go-reset:hover {{ box-shadow: 0 0 14px rgba(239,68,68,0.28); }}
.go-dismiss {{
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 9px 16px;
  font-size: 10px;
  cursor: pointer;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-family: var(--font);
  transition: border-color .12s;
}}
.go-dismiss:hover {{ border-color: rgba(0,255,136,0.22); }}

.pulse {{ animation: sys-pulse 1.8s ease-in-out infinite; }}
@keyframes sys-pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .4; }} }}
</style>
</head>
<body>
<div class="shell">

  <!-- ── HEADER ── -->
  <header class="hdr">
    <div class="hdr-brand">
      <span class="hdr-icon" id="hdr-live-dot"></span>
      <span class="hdr-title">TELEPHONY INTERCEPT TERMINAL</span>
    </div>
    <div class="hdr-sep"></div>
    <div class="hdr-meta">
      <span class="hdr-badge green" id="hdr-live-label">LIVE</span>
      <span class="hdr-badge">PHONE MODULE v2.1<span class="hdr-cursor"></span></span>
    </div>
    <span class="hdr-uptime" id="time"></span>
  </header>

  <!-- ── SPOOF BANNER ── -->
  <div class="spoof-banner" id="spoof-banner"></div>

  <!-- ── BODY ── -->
  <div class="body">

    <!-- LEFT PANEL -->
    <aside class="left">
      <div class="dir-tabs" id="dir-tabs">
        <div class="dir-tab active" data-tab="messages" onclick="switchTab('messages')">SMS</div>
        <div class="dir-tab"        data-tab="spoof"    onclick="switchTab('spoof')">SPOOF</div>
        <div class="dir-tab"        data-tab="voice"    onclick="switchTab('voice')">VOICE</div>
      </div>
      <div class="contact-list" id="contact-list" style="display:none"></div>
      <div class="calllog-section">
        <div class="section-label" style="display:flex;justify-content:space-between;align-items:center">
          <span>CALL LOG</span>
          <button onclick="switchTab('dialer')" style="background:rgba(0,255,136,0.08);color:var(--accent);border:1px solid rgba(0,255,136,0.25);border-radius:4px;padding:2px 8px;font-family:var(--font);font-size:8px;font-weight:700;letter-spacing:1px;cursor:pointer">DIAL</button>
        </div>
        <div class="calllog-list" id="calllog-list">
          <div class="calllog-empty">No activity yet.</div>
        </div>
      </div>
    </aside>

    <!-- RIGHT PANEL -->
    <main class="right" id="right-panel" style="position:relative;">

      <!-- hidden tab strip — kept for JS switchTab() compatibility -->
      <div id="tabs" style="display:none">
        <div class="tab" data-tab="dialer"   onclick="switchTab('dialer')"></div>
        <div class="tab" data-tab="voice"    onclick="switchTab('voice')"></div>
        <div class="tab" data-tab="spoof"    onclick="switchTab('spoof')"></div>
        <div class="tab" data-tab="messages" onclick="switchTab('messages')"></div>
      </div>

      <!-- DIALER TAB -->
      <div id="tab-dialer" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="ch-label">ACTIVE CHANNEL &mdash; DIAL MODE</div>
        <div class="dialer-panel">

          <!-- LCD number display -->
          <div class="lcd" id="display">&nbsp;</div>

          <!-- 12-key keypad -->
          <div class="keypad">
            <div class="key" onclick="press('1')"><span class="key-d">1</span><span class="key-l">&nbsp;</span></div>
            <div class="key" onclick="press('2')"><span class="key-d">2</span><span class="key-l">ABC</span></div>
            <div class="key" onclick="press('3')"><span class="key-d">3</span><span class="key-l">DEF</span></div>
            <div class="key" onclick="press('4')"><span class="key-d">4</span><span class="key-l">GHI</span></div>
            <div class="key" onclick="press('5')"><span class="key-d">5</span><span class="key-l">JKL</span></div>
            <div class="key" onclick="press('6')"><span class="key-d">6</span><span class="key-l">MNO</span></div>
            <div class="key" onclick="press('7')"><span class="key-d">7</span><span class="key-l">PQRS</span></div>
            <div class="key" onclick="press('8')"><span class="key-d">8</span><span class="key-l">TUV</span></div>
            <div class="key" onclick="press('9')"><span class="key-d">9</span><span class="key-l">WXYZ</span></div>
            <div class="key" onclick="press('*')"><span class="key-d">*</span><span class="key-l">&nbsp;</span></div>
            <div class="key" onclick="press('0')"><span class="key-d">0</span><span class="key-l">+</span></div>
            <div class="key" onclick="press('#')"><span class="key-d">#</span><span class="key-l">&nbsp;</span></div>
          </div>

          <!-- action row -->
          <div class="dial-actions">
            <button class="btn-clr"      onclick="clearNum()">CLR</button>
            <button class="btn-call"     onclick="dial()">CONNECT</button>
            <button class="btn-sms-quick" onclick="smsFromDialer()">SMS</button>
          </div>
          <div id="error" class="err-msg" style="display:none"></div>

        </div>
      </div>

      <!-- ACTIVE CALL VIEW -->
      <div id="callview" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="ch-label">ACTIVE CHANNEL &mdash; VOICE CALL</div>
        <div class="callview-panel">

          <!-- connection status banner -->
          <div class="conn-status" id="connected-badge">
            <div class="conn-dot"></div>
            <span class="conn-label">CONNECTED</span>
            <span class="conn-sep">&mdash;</span>
            <span class="conn-name" id="call-name"></span>
          </div>

          <!-- meta + timer -->
          <div class="call-meta">
            <div class="call-info">
              <div class="ci-role"    id="call-role"></div>
              <div class="ci-company" id="call-company"></div>
              <div class="ci-ext"     id="call-ext"></div>
            </div>
            <div class="call-timer" id="call-timer">CONNECTING...</div>
          </div>

          <!-- waveform -->
          <div class="waveform" id="waveform" style="display:none;">
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
            <div class="wb"></div>
          </div>

          <!-- transcript -->
          <div class="chat-area" id="chat-area"></div>

          <!-- input -->
          <div class="chat-input-row">
            <input id="chat-input" placeholder="&gt; speak..." onkeydown="if(event.key==='Enter')sendMsg()">
            <button onclick="sendMsg()">SEND</button>
          </div>
          <button class="btn-hangup" onclick="hangup()">END CALL</button>

        </div>
      </div>

      <!-- MESSAGES / INBOX TAB -->
      <div id="tab-messages" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="inbox-hdr">
          <span class="inbox-title">MESSAGES</span>
          <button class="btn-new" onclick="openNewSmsModal()" title="New message">+</button>
        </div>
        <div class="inbox" id="inbox-list">
          <div class="empty-inbox">Loading conversations...</div>
        </div>
      </div>


      <!-- NEW SMS MODAL -->
      <div id="new-sms-modal" style="display:none;position:absolute;inset:0;background:rgba(7,11,18,0.92);z-index:50;flex-direction:column;align-items:center;justify-content:center;padding:16px;">
        <div style="background:#0d1220;border:1px solid rgba(59,130,246,0.25);border-radius:10px;width:100%;max-width:320px;overflow:hidden;">
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.07);">
            <span style="font-size:10px;font-weight:700;letter-spacing:2px;color:#3b82f6;">NEW MESSAGE</span>
            <button onclick="closeNewSmsModal()" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:16px;line-height:1;">&#x2715;</button>
          </div>
          <div style="padding:14px;">
            <div style="font-size:9px;letter-spacing:1px;color:#94a3b8;margin-bottom:6px;">SELECT CONTACT</div>
            <div id="sms-contact-list" style="max-height:200px;overflow-y:auto;border:1px solid rgba(255,255,255,0.07);border-radius:6px;margin-bottom:12px;"></div>
            <div style="font-size:9px;letter-spacing:1px;color:#94a3b8;margin-bottom:6px;">OR ENTER EXTENSION</div>
            <div style="display:flex;gap:8px;">
              <input id="sms-ext-input" type="text" placeholder="ext. 1234"
                style="flex:1;background:#070b12;border:1px solid rgba(255,255,255,0.1);color:#e2e8f0;padding:8px 10px;border-radius:5px;font-family:var(--font);font-size:11px;"
                onkeydown="if(event.key==='Enter')confirmNewSms()">
              <button onclick="confirmNewSms()"
                style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);color:#3b82f6;padding:8px 14px;border-radius:5px;font-family:var(--font);font-size:10px;font-weight:700;cursor:pointer;letter-spacing:1px;">
                MSG
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SMS CONVERSATION VIEW -->
      <div id="smsview" class="sms" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="sms-thread-hdr">
          <button class="back-btn" onclick="backToInbox()">&lsaquo;</button>
          <div class="sms-av" id="sms-avatar"></div>
          <div class="sms-info">
            <div class="si-name" id="sms-name"></div>
            <div class="si-sub"  id="sms-sub"></div>
          </div>
        </div>
        <div class="chat-area" id="sms-chat-area" style="padding:10px 14px;"></div>
        <div class="sms-char-count" id="sms-char-count">0/160</div>
        <div class="chat-input-row" style="padding:0 14px 12px;">
          <input id="sms-chat-input" placeholder="&gt; message..." onkeydown="if(event.key==='Enter')sendSms()" oninput="updateSmsCharCount()">
          <button onclick="sendSms()">&uarr;</button>
        </div>
      </div>

      <!-- SPOOF TAB -->
      <div id="tab-spoof" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="ch-label">CALLER ID SPOOF</div>
        <div class="tool-panel" style="gap:0">

          <span class="field-label" style="margin-top:4px">Show caller as</span>
          <input id="sim-spoof-as" type="text" placeholder='ext. 3041  or  "IT Helpdesk"' maxlength="40" oninput="onSpoofChange()">

          <div id="sim-preview" class="info-box" style="margin-top:8px">Showing as: Unknown caller</div>

          <div id="spoof-active-wrap" style="display:none;margin-top:6px">
            <div class="spoof-active-badge"><span class="spoof-dot"></span>SPOOFING ACTIVE</div>
          </div>
        </div>
      </div>

      <!-- VOICE CLONE TAB -->
      <div id="tab-voice" style="display:none;flex-direction:column;flex:1;min-height:0;">
        <div class="ch-label">VOICE SYNTHESIS</div>
        <div class="tool-panel" style="gap:0">

          <span class="field-label" style="margin-top:4px">Voice Sample (.sfvoice)</span>
          <div id="voice-file-zone" onclick="document.getElementById('voice-file-input').click()" style="border:1px dashed rgba(99,102,241,0.3);border-radius:4px;padding:8px 10px;cursor:pointer;font-size:10px;color:var(--muted);transition:border-color .15s,background .15s">
            Drop .sfvoice or click to browse
          </div>
          <input id="voice-file-input" type="file" accept=".sfvoice" style="display:none" onchange="loadVoiceFile(this.files[0])">
          <input id="voice-engine" type="hidden" value="neuralclone_v3">
          <select id="voice-target" style="display:none"></select>
          <div id="voice-quality-badge" style="display:none;margin-top:4px;font-size:10px;padding:4px 8px;background:var(--surface);border:1px solid var(--border);border-radius:3px"></div>

          <div id="voice-status" class="info-box" style="margin-top:8px">No voice identity active.</div>

          <div style="margin-top:6px">
            <div class="risk-meter risk-low" id="voice-risk-meter"><div class="risk-fill"></div></div>
            <div id="voice-risk-label" class="risk-label" style="margin-top:3px">LOW &mdash; real voice</div>
          </div>

          <div style="display:flex;gap:6px;margin-top:10px">
            <button class="btn-panel"       onclick="applyVoice()" style="flex:1;margin-top:0">Apply</button>
            <button class="btn-panel-reset" onclick="resetVoice()" style="flex:1;margin-top:0">Reset</button>
          </div>
        </div>
      </div>

      <!-- GATE OVERLAY -->
      <div class="gate" id="gate">
        <div class="gate-icon">[LOCK]</div>
        <h2>Simulation Locked</h2>
        <p id="gate-msg">Start the lab simulation from the main app to enable calls and messages. NPC behavior depends on the active lab.</p>
        <button class="start-btn" id="gate-start" onclick="startSimulation()" style="display:none">START SIMULATION</button>
      </div>

      <!-- GAME OVER OVERLAY -->
      <div class="gameover" id="gameover">
        <div class="go-scan"></div>
        <div class="go-inner">
          <div class="go-bust">Operation Compromised</div>
          <div class="go-h1">HACKER</div>
          <div class="go-h1">EXPOSED</div>
          <div class="go-h2">// MISSION FAILED //</div>
          <div class="go-who"   id="go-who"></div>
          <div class="go-reason" id="go-reason">The target recognized the attack.</div>
          <div class="go-btns">
            <button class="go-reset"   onclick="resetLab()">RESET LAB</button>
            <button class="go-dismiss" onclick="hideGameOver()">DISMISS</button>
          </div>
        </div>
      </div>

    </main><!-- /right -->
  </div><!-- /body -->
</div><!-- /shell -->

<script>
const DIR = {dir_js};
const API = 'http://127.0.0.1:8000';
let number = '';
let callActive = false;
let timerInterval = null;
let callSeconds = 0;
let currentContact = null;
let sending = false;
let currentSms = null; // {{ext, contact}}
let smsSending = false;

// SIM / Caller-ID spoof state
const spoofState = {{
  caller_id: '',
  caller_ext: '',
  caller_identity: '',
}};

// Voice-clone state
const voiceState = {{
  has_sample: false,
  sample_name: '',
  sample_url: '',
  quality_score: 0,
  quality_label: '',
  target_persona: '',
  target_name: '',
  engine: 'neuralclone_v3',
}};

const params = new URLSearchParams(location.search);
const labId = params.get('lab');
const userId = parseInt(params.get('user') || '1');
let labStatus = null;  // not_started | in_progress | completed | failed
let labDismissed = false;  // user dismissed gameover — suppress re-show until next action
let localBustPending = false;  // bust triggered locally before server reflects it

async function refreshLabStatus() {{
  if(!labId) {{
    hideGate();
    return;
  }}
  try {{
    const res = await fetch(API + '/api/labs/' + encodeURIComponent(labId) + '/progress?user_id=' + userId);
    if(!res.ok) return;
    const p = await res.json();
    labStatus = p.status;
    if(labStatus === 'failed') {{
      if(!labDismissed) showGameOver(p.failure_reason, p.failed_persona);
      else labStatus = null;
      hideGate();
    }} else {{
      labDismissed = false;
      if(!localBustPending) hideGameOver();
      hideGate();
    }}
  }} catch(e) {{ /* ignore */ }}
}}

function showGate(mode) {{
  const g = document.getElementById('gate');
  const btn = document.getElementById('gate-start');
  const msg = document.getElementById('gate-msg');
  if(mode === 'start') {{
    btn.style.display = 'block';
    btn.disabled = false;
    btn.textContent = 'START SIMULATION';
    msg.textContent = "NPC life (schedules, moods, detection) only runs while the lab is active. Start the simulation when you are ready to begin the attack.";
  }} else {{
    btn.style.display = 'none';
  }}
  g.classList.add('show');
}}

function hideGate() {{
  document.getElementById('gate').classList.remove('show');
}}

async function startSimulation() {{
  if(!labId) return;
  const btn = document.getElementById('gate-start');
  btn.disabled = true;
  btn.textContent = 'STARTING...';
  try {{
    const res = await fetch(API + '/api/labs/' + encodeURIComponent(labId) + '/start?user_id=' + userId, {{method:'POST'}});
    if(res.ok) {{
      labStatus = 'in_progress';
      hideGate();
    }} else {{
      btn.disabled = false;
      btn.textContent = 'START SIMULATION';
      alert('Could not start simulation.');
    }}
  }} catch(e) {{
    btn.disabled = false;
    btn.textContent = 'START SIMULATION';
  }}
}}

function showGameOver(reason, who) {{
  document.getElementById('go-reason').textContent = reason || 'The target recognized the attack.';
  document.getElementById('go-who').textContent = who ? ('Detected by ' + who) : '';
  document.getElementById('gameover').classList.add('show');
  hideGate();
}}
function hideGameOver() {{
  document.getElementById('gameover').classList.remove('show');
  localBustPending = false;
  if(labStatus === 'failed') {{
    labStatus = null;
    labDismissed = true;
  }}
}}

async function resetLab() {{
  if(!labId) return;
  const ok = confirm('Reset this lab? All progress and conversations will be wiped.');
  if(!ok) return;
  try {{
    await fetch(API + '/api/labs/' + encodeURIComponent(labId) + '/reset?user_id=' + userId, {{method:'POST'}});
    await fetch(API + '/api/labs/' + encodeURIComponent(labId) + '/start?user_id=' + userId, {{method:'POST'}});
    labStatus = 'in_progress';
    labDismissed = false;
    hideGameOver();
    if(callActive) hangup();
    if(currentSms) backToInbox();
    number = '';
    const disp = document.getElementById('display');
    if(disp) disp.innerHTML = '&nbsp;';
    await refreshLabStatus();
  }} catch(e) {{ alert('Reset failed.'); }}
}}

refreshLabStatus();
setInterval(refreshLabStatus, 8000);

let uptimeSeconds = 0;
function updateTime() {{
  uptimeSeconds++;
  const h = String(Math.floor(uptimeSeconds / 3600)).padStart(2,'0');
  const m = String(Math.floor((uptimeSeconds % 3600) / 60)).padStart(2,'0');
  const s = String(uptimeSeconds % 60).padStart(2,'0');
  const el = document.getElementById('time');
  if(el) el.textContent = '[UPTIME: ' + h + ':' + m + ':' + s + ']';
}}
setInterval(updateTime, 1000);
updateTime();

function buildContactList() {{
  return;
  const list = document.getElementById('contact-list');
  if(!list) return;
  const labMap = (labId && DIR[labId]) || {{}};
  const entries = Object.entries(labMap).sort((a,b) => a[1].name.localeCompare(b[1].name));
  if(!entries.length) {{
    list.innerHTML = '<div style="padding:14px;font-size:10px;color:var(--muted);letter-spacing:.5px">No contacts loaded.<br>Select a lab first.</div>';
    return;
  }}
  list.innerHTML = '';
  for(const [ext, c] of entries) {{
    const div = document.createElement('div');
    div.className = 'contact-item' + (c.contactable ? '' : ' inactive');
    div.dataset.ext = ext;
    div.innerHTML =
      '<div class="c-dot ' + (c.contactable ? 'online' : 'offline') + '"></div>' +
      '<div class="c-body">' +
        '<div class="c-name">' + esc(c.name) + '</div>' +
        '<div class="c-ext">ext. ' + esc(ext) + '</div>' +
        (c.contactable ? '<span class="c-sms-tag">SMS</span>' : '') +
      '</div>';
    if(c.contactable) {{
      div.onclick = () => {{
        number = ext;
        document.getElementById('display').textContent = ext;
        document.getElementById('error').style.display = 'none';
        document.querySelectorAll('.contact-item').forEach(el => el.classList.remove('active'));
        div.classList.add('active');
        switchTab('dialer');
      }};
    }}
    list.appendChild(div);
  }}
}}

function addCallLog(name, status) {{
  const list = document.getElementById('calllog-list');
  const empty = list.querySelector('.calllog-empty');
  if(empty) empty.remove();
  const now = new Date().toLocaleTimeString([], {{hour:'2-digit',minute:'2-digit'}});
  const statusClass = status === 'CONNECTED' ? 'ok' : status === 'SMS SENT' ? 'sms' : 'miss';
  const item = document.createElement('div');
  item.className = 'calllog-item';
  item.innerHTML =
    '<span class="cl-time">' + esc(now) + '</span>' +
    '<span class="cl-name">' + esc(name) + '</span>' +
    '<span class="cl-status ' + statusClass + '">' + esc(status) + '</span>';
  list.insertBefore(item, list.firstChild);
}}

(function() {{
  buildContactList();
  const initTab = params.get('tab');
  if(initTab && ['dialer','messages','spoof','voice'].includes(initTab)) {{
    switchTab(initTab);
  }} else {{
    switchTab('messages');
  }}
}})();


function switchTab(name) {{
  if(callActive) return;
  document.querySelectorAll('.dir-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.getElementById('tab-dialer').style.display   = (name === 'dialer')   ? 'flex' : 'none';
  document.getElementById('tab-messages').style.display = (name === 'messages') ? 'flex' : 'none';
  document.getElementById('tab-spoof').style.display    = (name === 'spoof')    ? 'flex' : 'none';
  document.getElementById('tab-voice').style.display    = (name === 'voice')    ? 'flex' : 'none';
  document.getElementById('callview').style.display = 'none';
  document.getElementById('smsview').style.display  = 'none';
  if(name === 'messages') loadInbox();
  if(name === 'voice') populatePanelDropdowns();
}}

function onSpoofChange() {{
  const val = (document.getElementById('sim-spoof-as').value || '').trim();
  spoofState.caller_id = '';
  spoofState.caller_ext = '';
  spoofState.caller_identity = '';
  let previewLabel = 'Showing as: Unknown caller';
  if(val) {{
    if(/^\\d+$/.test(val)) {{
      spoofState.caller_ext = val;
      const labMap = (labId && DIR[labId]) || {{}};
      const contact = labMap[val];
      if(contact) {{
        spoofState.caller_id = contact.name;
        spoofState.caller_identity = contact.persona_id;
        previewLabel = 'Showing as: ext. ' + val + ' — ' + contact.name;
      }} else {{
        previewLabel = 'Showing as: ext. ' + val + ' (unknown)';
      }}
    }} else {{
      spoofState.caller_id = val;
      previewLabel = 'Showing as: ' + val;
    }}
  }}
  document.getElementById('sim-preview').textContent = previewLabel;
  const wrap = document.getElementById('spoof-active-wrap');
  if(wrap) wrap.style.display = val ? 'block' : 'none';
  renderSpoofBanner();
}}

function renderSpoofBanner() {{
  const b = document.getElementById('spoof-banner');
  const rows = [];
  if(spoofState.caller_id) rows.push('<span><span class="sb-label">FROM</span> ' + esc(spoofState.caller_id) + '</span>');
  if(voiceState.target_persona) rows.push('<span><span class="sb-label">VOICE</span> ' + esc(voiceState.target_name) + '</span>');
  if(!rows.length) {{ b.classList.remove('show'); b.innerHTML = ''; return; }}
  b.innerHTML = rows.join('');
  b.classList.add('show');
}}

let _panelDropdownsPopulated = false;
function populatePanelDropdowns() {{
  if(_panelDropdownsPopulated) return;
  _panelDropdownsPopulated = true;
  const voiceSel = document.getElementById('voice-target');
  const labMap = (labId && DIR[labId]) || {{}};
  const entries = Object.entries(labMap)
    .filter(([, c]) => c.contactable)
    .sort((a,b) => a[0].localeCompare(b[0]));
  for(const [ext, c] of entries) {{
    const o = document.createElement('option');
    o.value = c.persona_id; o.dataset.name = c.name;
    o.textContent = ext + ' -- ' + c.name + ' (' + c.role + ')';
    voiceSel.appendChild(o);
  }}
}}

function loadVoiceFile(file) {{
  if(!file) return;
  const reader = new FileReader();
  reader.onload = e => {{
    try {{
      const data = JSON.parse(e.target.result);
      if(data.type !== 'sf_voice_sample') {{ _voiceFileError('Not a valid .sfvoice file'); return; }}
      const q = data.quality || 0;
      let tier, col;
      if(q >= 0.95)      {{ tier = 'EXCEPTIONAL'; col = '#9f7aea'; }}
      else if(q >= 0.80) {{ tier = 'EXCELLENT';   col = '#22c55e'; }}
      else if(q >= 0.60) {{ tier = 'PARTIAL';     col = '#eab308'; }}
      else               {{ tier = 'POOR';        col = '#ef4444'; }}
      voiceState.has_sample = true;
      voiceState.quality_score = q;
      voiceState.quality_label = tier;
      voiceState.sample_source = data.source || '';
      const targetSel = document.getElementById('voice-target');
      for(let i = 0; i < targetSel.options.length; i++) {{
        if(targetSel.options[i].value === data.persona) {{ targetSel.value = data.persona; break; }}
      }}
      document.getElementById('voice-engine').value = 'neuralclone_v3';
      voiceState.engine = 'neuralclone_v3';
      const pct = Math.round(q * 100);
      const zone = document.getElementById('voice-file-zone');
      zone.style.borderColor = col;
      zone.style.color = col;
      zone.textContent = '✓ ' + file.name + (data.source ? ' · ' + data.source : '');
      const badge = document.getElementById('voice-quality-badge');
      badge.style.display = 'block';
      badge.innerHTML = '<span style="color:' + col + '">[' + tier + ']</span> Private voice note &mdash; <strong>' + pct + '%</strong> quality'
        + ' &mdash; <span style="opacity:.7;font-size:9px">source: ' + esc(data.source || 'unknown') + '</span>';
      updateVoicePreview();
    }} catch(err) {{ _voiceFileError('Could not parse voice sample file'); }}
  }};
  reader.readAsText(file);
}}

function _voiceFileError(msg) {{
  const badge = document.getElementById('voice-quality-badge');
  badge.style.display = 'block';
  badge.innerHTML = '<span style="color:#ef4444">[ERROR]</span> ' + esc(msg);
}}

function updateVoicePreview() {{
  const targetSel = document.getElementById('voice-target');
  const targetVal = targetSel.value;
  let status, risk, riskLabel;
  if(!targetVal) {{
    status = 'No voice identity active. Calls use your real voice.';
    risk = 'low'; riskLabel = 'LOW — real voice';
  }} else if(voiceState.has_sample && voiceState.quality_score > 0) {{
    const opt = targetSel.options[targetSel.selectedIndex];
    const pct = Math.round(voiceState.quality_score * 100);
    status = 'Cloning: ' + opt.dataset.name + ' — ' + voiceState.quality_label + ' (' + pct + '%)';
    risk = voiceState.quality_score >= 0.80 ? 'med' : 'high';
    riskLabel = (risk === 'med' ? 'MEDIUM' : 'HIGH') + ' — ' + pct + '% match';
  }} else {{
    const opt = targetSel.options[targetSel.selectedIndex];
    status = opt.dataset.name + ' selected — load .sfvoice to activate';
    risk = 'high'; riskLabel = 'HIGH — no sample loaded';
  }}
  document.getElementById('voice-status').textContent = status;
  document.getElementById('voice-risk-meter').className = 'risk-meter risk-' + risk;
  document.getElementById('voice-risk-label').textContent = riskLabel;
}}

function applyVoice() {{
  const targetSel = document.getElementById('voice-target');
  const opt = targetSel.options[targetSel.selectedIndex];
  voiceState.target_persona = targetSel.value || '';
  voiceState.target_name = targetSel.value ? (opt.dataset.name || '') : '';
  voiceState.engine = 'neuralclone_v3';
  updateVoicePreview();
  renderSpoofBanner();
}}

function resetVoice() {{
  voiceState.has_sample = false;
  voiceState.quality_score = 0; voiceState.quality_label = '';
  voiceState.sample_source = '';
  voiceState.target_persona = ''; voiceState.target_name = '';
  voiceState.engine = 'neuralclone_v3';
  document.getElementById('voice-target').value = '';
  document.getElementById('voice-file-input').value = '';
  document.getElementById('voice-quality-badge').style.display = 'none';
  const zone = document.getElementById('voice-file-zone');
  zone.style.borderColor = 'rgba(99,102,241,0.3)';
  zone.style.background = '';
  zone.style.color = 'var(--muted)';
  zone.textContent = 'Drop .sfvoice or click to browse';
  updateVoicePreview();
  renderSpoofBanner();
}}

document.addEventListener('change', (ev) => {{
  if(ev.target && (ev.target.id === 'voice-target' || ev.target.id === 'voice-engine')) updateVoicePreview();
}});

function spoofPayload() {{
  const p = {{}};
  if(spoofState.caller_ext) {{
    p.caller_spoofed_ext = spoofState.caller_ext;
    p.caller_profile = 'spoof_internal';
    if(spoofState.caller_id) p.caller_id = spoofState.caller_id;
  }} else if(spoofState.caller_id) {{
    p.caller_id = spoofState.caller_id;
    p.caller_profile = 'custom';
  }}
  if(spoofState.caller_identity) {{
    p.caller_identity = spoofState.caller_identity;
    if(!p.caller_profile) p.caller_profile = 'spoof_internal';
  }}
  if(voiceState.target_persona) {{
    p.voice_identity = voiceState.target_persona;
    p.voice_engine = voiceState.engine;
    p.voice_has_sample = voiceState.has_sample;
    if(voiceState.quality_score > 0) p.voice_quality_override = voiceState.quality_score;
    if(voiceState.sample_source) p.voice_sample_source = voiceState.sample_source;
  }}
  return p;
}}

function setDisplayState(state, text) {{
  const el = document.getElementById('display');
  el.className = 'lcd' + (state ? ' ' + state : '');
  if(state === 'ringing') {{
    el.textContent = 'RINGING...';
  }} else if(state === 'connected') {{
    el.textContent = text || 'CONNECTED';
  }} else if(state === 'voicemail') {{
    el.textContent = 'VOICEMAIL';
  }} else if(state === 'ended') {{
    el.textContent = 'CALL ENDED';
  }} else if(state === 'busy') {{
    el.textContent = 'LINE BUSY';
  }} else {{
    el.textContent = text || '';
    if(!text) el.innerHTML = text === '' ? number || '&nbsp;' : '&nbsp;';
  }}
}}

function press(d) {{
  if(number.length < 10) {{
    number += d;
    const el = document.getElementById('display');
    el.className = 'lcd';
    el.textContent = number;
    document.getElementById('error').style.display = 'none';
  }}
}}

function clearNum() {{
  number = '';
  const el = document.getElementById('display');
  el.className = 'lcd';
  el.innerHTML = '&nbsp;';
  document.getElementById('error').style.display = 'none';
}}

function resolveExt(ext) {{
  const labMap = labId && DIR[labId];
  const c = labMap && labMap[ext];
  if(!c) return {{err: 'Extension not found. Dial a valid internal extension.'}};
  if(!c.contactable) return {{err: c.name + ' is not available for contact.'}};
  if(c.busy) return {{busy: true, contact: c}};
  return {{contact: c}};
}}

function showDialerError(msg) {{
  const el = document.getElementById('error');
  el.textContent = msg;
  el.style.display = 'block';
}}

async function dial() {{
  if(!number) return;
  if(labStatus === 'failed') {{ showGameOver(); return; }}
  if(labStatus === null && labId) {{ await refreshLabStatus(); }}
  const r = resolveExt(number);
  if(r.err) return showDialerError(r.err);
  if(r.busy) {{ showBusyTone(r.contact, number); return; }}
  startCall(r.contact);
}}

function showBusyTone(contact, ext) {{
  document.getElementById('tab-dialer').style.display = 'none';
  const cv = document.getElementById('callview');
  cv.style.display = 'flex';
  document.getElementById('call-name').textContent = contact.name;
  document.getElementById('call-role').textContent = contact.role;
  document.getElementById('call-company').textContent = contact.company;
  document.getElementById('call-ext').textContent = 'ext. ' + ext;
  document.getElementById('waveform').style.display = 'none';
  setDisplayState('ringing');
  const area = document.getElementById('chat-area');
  const timerEl = document.getElementById('call-timer');
  timerEl.textContent = 'CONNECTING...';
  area.innerHTML = '<div class="msg msg-system">Ringing...</div>';
  setTimeout(() => {{
    timerEl.textContent = 'LINE BUSY';
    timerEl.style.color = '#ef4444';
    area.innerHTML += '<div class="msg msg-system" style="color:#ef4444">── BUSY SIGNAL ──  ·  ·  ·</div>';
    area.innerHTML += '<div class="msg msg-npc" style="border-left-color:#ef4444;color:#ef4444">This extension is currently unavailable. The line is busy.</div>';
    area.innerHTML += '<div class="msg msg-system" style="color:#94a3b8;font-size:9px">Try contacting a colleague to get an alternate number.</div>';
    area.scrollTop = area.scrollHeight;
    setDisplayState('busy');
    document.getElementById('waveform').style.display = 'none';
  }}, 2000);
}}

function startCall(contact) {{
  currentContact = contact;
  callActive = true;
  callSeconds = 0;
  sending = false;

  document.getElementById('tab-dialer').style.display = 'none';
  const cv = document.getElementById('callview');
  cv.style.display = 'flex';
  document.getElementById('call-name').textContent = contact.name;
  document.getElementById('call-role').textContent = contact.role;
  document.getElementById('call-company').textContent = contact.company;
  const extEl = document.getElementById('call-ext');
  const phoneLine = contact.phone
    ? (esc(contact.phone) + ' <span style="opacity:.55">&middot; ext. ' + esc(number) + '</span>')
    : ('ext. ' + esc(number));
  if(spoofState.caller_id || voiceState.target_persona) {{
    const bits = [];
    if(spoofState.caller_id) bits.push('FROM&rarr; ' + esc(spoofState.caller_id));
    if(voiceState.target_persona) bits.push('VOICE&rarr; ' + esc(voiceState.target_name));
    extEl.innerHTML = '<div>' + phoneLine + '</div><div class="spoof-ext">' + bits.join(' &middot; ') + '</div>';
    extEl.classList.add('spoof-ext-wrap');
  }} else {{
    extEl.innerHTML = phoneLine;
    extEl.classList.remove('spoof-ext-wrap');
  }}
  const area = document.getElementById('chat-area');
  area.innerHTML = '<div class="msg msg-system">Ringing...</div>';
  const timerEl = document.getElementById('call-timer');
  timerEl.textContent = 'CONNECTING...';
  const badge = document.getElementById('connected-badge');
  if(badge) badge.style.borderColor = 'rgba(245,158,11,0.3)';
  document.getElementById('waveform').style.display = 'none';
  setDisplayState('ringing');

  setTimeout(() => {{
    if(!callActive) return;
    timerEl.textContent = '00:00';
    if(badge) badge.style.borderColor = 'rgba(0,255,136,0.2)';
    document.getElementById('waveform').style.display = 'flex';
    setDisplayState('connected', contact.name);
    area.scrollTop = area.scrollHeight;
    timerInterval = setInterval(() => {{
      callSeconds++;
      const m = String(Math.floor(callSeconds/60)).padStart(2,'0');
      const s = String(callSeconds%60).padStart(2,'0');
      timerEl.textContent = m + ':' + s;
    }}, 1000);
    autoConnect();
  }}, 1500);

  addCallLog(contact.name, 'CONNECTED');
}}

async function autoConnect() {{
  if(!callActive || !currentContact || sending) return;
  sending = true;
  const area = document.getElementById('chat-area');
  const lab = labId || currentContact.lab_id;
  try {{
    const res = await fetch(API + '/api/chat', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(Object.assign({{
        user_id: userId, lab_id: lab,
        persona_id: currentContact.persona_id,
        message: '[ring]', channel: 'phone'
      }}, spoofPayload()))
    }});
    const data = await res.json().catch(() => ({{}}));
    if(!res.ok) {{
      area.innerHTML += '<div class="msg msg-system" style="opacity:.6">Connected — say something to start.</div>';
      sending = false; return;
    }}
    if(data.no_answer) {{
      area.innerHTML += '<div class="msg msg-system" style="color:var(--muted);line-height:1.5">' + esc(data.response || 'No answer.') + '</div>';
      area.scrollTop = area.scrollHeight;
      sending = false;
      setTimeout(() => hangup(), 3000);
      return;
    }}
    if(data.response) {{
      if(data.response.startsWith('[System:')) {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--amber);font-size:11px">' + esc(data.response) + '</div>';
      }} else {{
        area.innerHTML += '<div class="msg msg-npc"><div class="npc-name">' + esc(currentContact.name) + '</div>' + esc(data.response) + '</div>';
      }}
    }}
    if(data.voicemail) {{
      area.innerHTML += '<div class="msg msg-system" style="color:var(--amber)">(Voicemail — ' + esc(data.work_status || 'after hours') + ')</div>';
    }}
    if(data.mission_failed) {{
      labStatus = 'failed';
      localBustPending = true;
      showGameOver(data.fail_reason, data.failed_persona || (currentContact && currentContact.name));
      if(callActive) hangup();
    }}
  }} catch(e) {{
    area.innerHTML += '<div class="msg msg-system" style="opacity:.6">Connected — say something to start.</div>';
  }}
  area.scrollTop = area.scrollHeight;
  sending = false;
  document.getElementById('chat-input').focus();
}}

async function sendMsg() {{
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if(!text || !callActive || !currentContact || sending) return;
  if(labStatus === 'failed') {{ showGameOver(); return; }}
  labDismissed = false;
  sending = true;
  input.value = '';

  const area = document.getElementById('chat-area');
  area.innerHTML += '<div class="msg msg-user">' + esc(text) + '</div>';
  area.scrollTop = area.scrollHeight;

  const typingId = 'typing-' + Date.now();
  area.innerHTML += '<div class="msg msg-system pulse" id="' + typingId + '">...</div>';
  area.scrollTop = area.scrollHeight;

  try {{
    const lab = labId || currentContact.lab_id;
    const res = await fetch(API + '/api/chat', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(Object.assign({{
        user_id: userId, lab_id: lab,
        persona_id: currentContact.persona_id,
        message: text, channel: 'phone'
      }}, spoofPayload()))
    }});
    const data = await res.json().catch(() => ({{}}));
    const el = document.getElementById(typingId);
    if(el) el.remove();

    if(res.status === 409) {{
      area.innerHTML += '<div class="msg msg-system" style="color:var(--amber)">Lab not started. Start the simulation first.</div>';
      sending = false; return;
    }}
    if(!res.ok) {{
      const detail = (data && data.detail && (data.detail.message || data.detail)) || ('HTTP ' + res.status);
      area.innerHTML += '<div class="msg msg-system" style="color:var(--red)">' + esc(typeof detail === 'string' ? detail : JSON.stringify(detail)) + '</div>';
      sending = false; return;
    }}

    if(data.no_answer) {{
      area.innerHTML += '<div class="msg msg-system" style="color:var(--muted);line-height:1.5">' + esc(data.response || 'No answer.') + '</div>';
      area.scrollTop = area.scrollHeight;
      sending = false;
      setTimeout(() => hangup(), 3000);
      return;
    }}

    if(data.response) {{
      if(data.response.startsWith('[System:')) {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--amber);font-size:11px">' + esc(data.response) + '</div>';
      }} else {{
        area.innerHTML += '<div class="msg msg-npc"><div class="npc-name">' + esc(currentContact.name) + '</div>' + esc(data.response) + '</div>';
      }}
    }}

    if(data.voicemail) {{
      area.innerHTML += '<div class="msg msg-system" style="color:var(--amber)">(Voicemail -- ' + esc(data.work_status || 'after hours') + ')</div>';
    }}
    if(data.flag_found) {{
      if(data.delivered_email) {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--accent);font-weight:600">📧 Email delivered — check SF Mail inbox</div>';
      }} else {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--accent);font-weight:600">FLAG: ' + esc(data.flag_found) + '</div>';
      }}
    }}
    if(data.mission_failed) {{
      labStatus = 'failed';
      localBustPending = true;
      showGameOver(data.fail_reason, data.failed_persona || (currentContact && currentContact.name));
      if(callActive) hangup();
    }} else if(data.caught) {{
      labStatus = 'failed';
      localBustPending = true;
      area.innerHTML += '<div class="msg msg-system" style="color:var(--red);font-weight:600">CAUGHT! The target has become suspicious.</div>';
      showGameOver('The target identified you as a social engineer.', currentContact && currentContact.name);
      if(callActive) hangup();
    }}

    if(data.followup_hint && !data.mission_failed && !data.voicemail && callActive) {{
      chainFollowup({{
        contact: currentContact,
        channel: 'phone',
        hint: data.followup_hint,
        remaining: 2,
      }});
    }}
  }} catch(e) {{
    const el = document.getElementById(typingId);
    if(el) el.remove();
    area.innerHTML += '<div class="msg msg-system" style="color:var(--red)">Connection error.</div>';
  }}
  area.scrollTop = area.scrollHeight;
  sending = false;
  input.focus();
}}

async function chainFollowup(ctx) {{
  if(!ctx || !ctx.hint || !ctx.hint.delay_seconds) return;
  if(ctx.remaining == null || ctx.remaining <= 0) return;
  const delay = Math.max(3, Math.min(30, Math.round(ctx.hint.delay_seconds)));
  const phrase = ctx.hint.phrase || 'hold on';

  const isPhone = ctx.channel === 'phone';
  const areaId = isPhone ? 'chat-area' : 'sms-chat-area';

  setTimeout(async () => {{
    if(labStatus === 'failed') return;
    if(isPhone && (!callActive || !currentContact || currentContact.persona_id !== ctx.contact.persona_id)) return;
    if(!isPhone && (!currentSms || currentSms.contact.persona_id !== ctx.contact.persona_id)) return;

    const area = document.getElementById(areaId);
    if(!area) return;
    const typingId = 'typing-fu-' + Date.now();
    area.innerHTML += '<div class="msg msg-npc pulse" id="' + typingId + '"><div class="npc-name">' + esc(ctx.contact.name) + '</div>...</div>';
    area.scrollTop = area.scrollHeight;

    try {{
      const lab = labId || ctx.contact.lab_id;
      const body = Object.assign({{
        user_id: userId,
        lab_id: lab,
        persona_id: ctx.contact.persona_id,
        channel: ctx.channel,
        phrase: phrase,
        elapsed_seconds: delay,
      }}, spoofPayload());
      const res = await fetch(API + '/api/chat/followup', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(body),
      }});
      const data = await res.json().catch(() => ({{}}));
      const tn = document.getElementById(typingId);
      if(tn) tn.remove();

      if(!res.ok) {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--red);font-size:11px">(follow-up failed)</div>';
        return;
      }}

      if(data.response) {{
        if(data.response.startsWith('[System:')) {{
          area.innerHTML += '<div class="msg msg-system" style="color:var(--amber);font-size:11px">' + esc(data.response) + '</div>';
        }} else if(isPhone) {{
          area.innerHTML += '<div class="msg msg-npc"><div class="npc-name">' + esc(ctx.contact.name) + '</div>' + esc(data.response) + '</div>';
        }} else {{
          const chunks = (data.response || '').split(/\\n{{2,}}/).filter(s => s.trim().length);
          if(!chunks.length) chunks.push(data.response);
          for(let i = 0; i < chunks.length; i++) {{
            setTimeout(() => appendSmsBubble('assistant', chunks[i].trim()), i * 400);
          }}
        }}
      }}

      if(data.flag_found) {{
        if(data.delivered_email) {{
          area.innerHTML += '<div class="msg msg-system" style="color:var(--accent);font-weight:600">📧 Email delivered — check SF Mail inbox</div>';
        }} else {{
          area.innerHTML += '<div class="msg msg-system" style="color:var(--accent);font-weight:600">FLAG: ' + esc(data.flag_found) + '</div>';
        }}
      }}
      if(data.mission_failed) {{
        labStatus = 'failed';
        showGameOver(data.fail_reason, data.failed_persona || ctx.contact.name);
        return;
      }} else if(data.caught) {{
        area.innerHTML += '<div class="msg msg-system" style="color:var(--red);font-weight:600">CAUGHT! The target has become suspicious.</div>';
        return;
      }}

      area.scrollTop = area.scrollHeight;

      if(data.followup_hint && ctx.remaining > 1) {{
        chainFollowup({{
          contact: ctx.contact,
          channel: ctx.channel,
          hint: data.followup_hint,
          remaining: ctx.remaining - 1,
        }});
      }}
    }} catch(e) {{
      const tn = document.getElementById(typingId);
      if(tn) tn.remove();
    }}
  }}, delay * 1000);
}}

function hangup() {{
  const _hangupName = currentContact ? currentContact.name : null;
  callActive = false;
  currentContact = null;
  if(timerInterval) clearInterval(timerInterval);
  timerInterval = null;
  document.getElementById('callview').style.display = 'none';
  document.getElementById('waveform').style.display = 'none';
  document.getElementById('tab-dialer').style.display = 'flex';
  number = '';
  setDisplayState('ended');
  if(_hangupName) {{
    const lastItem = document.querySelector('.calllog-item');
    if(lastItem) {{
      const st = lastItem.querySelector('.cl-status');
      if(st && st.textContent === 'CONNECTED') {{ st.textContent = 'ENDED'; st.className = 'cl-status miss'; }}
    }}
  }}
  setTimeout(() => {{
    const el = document.getElementById('display');
    if(el && el.className.includes('ended')) {{
      el.className = 'lcd';
      el.innerHTML = '&nbsp;';
    }}
  }}, 2000);
  document.querySelectorAll('.contact-item').forEach(el => el.classList.remove('active'));
}}

async function smsFromDialer() {{
  if(!number) return;
  if(labStatus === 'failed') {{ showGameOver(); return; }}
  if(labStatus === null && labId) {{ await refreshLabStatus(); }}
  const r = resolveExt(number);
  if(r.err) return showDialerError(r.err);
  openSms(number, r.contact);
}}

function openNewSmsModal() {{
  const modal = document.getElementById('new-sms-modal');
  modal.style.display = 'flex';
  const list = document.getElementById('sms-contact-list');
  list.innerHTML = '';
  const contacts = labId && DIR[labId] ? Object.entries(DIR[labId]) : [];
  if(contacts.length) {{
    contacts.forEach(([ext, c]) => {{
      const row = document.createElement('div');
      row.style.cssText = 'display:flex;align-items:center;gap:10px;padding:9px 10px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.05);transition:background .12s';
      row.onmouseenter = () => row.style.background = 'rgba(59,130,246,0.07)';
      row.onmouseleave = () => row.style.background = '';
      const ini = (c.name||'?').split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase();
      row.innerHTML = `<div style="width:30px;height:30px;border-radius:50%;background:rgba(59,130,246,0.18);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#3b82f6;flex-shrink:0">${{ini}}</div>
        <div style="min-width:0"><div style="font-size:11px;font-weight:600;color:#e2e8f0">${{c.name}}</div><div style="font-size:9px;color:#94a3b8">ext. ${{ext}} &middot; ${{c.role||''}}</div></div>`;
      row.onclick = () => {{ closeNewSmsModal(); openSms(ext, c); }};
      list.appendChild(row);
    }});
  }} else {{
    list.innerHTML = '<div style="padding:14px;text-align:center;color:#94a3b8;font-size:10px">No contacts found</div>';
  }}
  document.getElementById('sms-ext-input').value = '';
  setTimeout(() => document.getElementById('sms-ext-input').focus(), 100);
}}

function closeNewSmsModal() {{
  document.getElementById('new-sms-modal').style.display = 'none';
}}

function confirmNewSms() {{
  const ext = document.getElementById('sms-ext-input').value.trim();
  if(!ext) return;
  const r = resolveExt(ext);
  if(r.err) {{ document.getElementById('sms-ext-input').style.borderColor='rgba(239,68,68,0.5)'; return; }}
  closeNewSmsModal();
  openSms(ext, r.contact);
}}

async function loadInbox() {{
  const list = document.getElementById('inbox-list');
  list.innerHTML = '<div class="empty-inbox">Loading...</div>';
  try {{
    const res = await fetch(API + '/api/chat/threads?user_id=' + userId + '&channel=sms');
    const data = await res.json();
    if(!data.threads || !data.threads.length) {{
      list.innerHTML = '<div class="empty-inbox">No messages yet.<br>Tap + to start a conversation.</div>';
      return;
    }}
    list.innerHTML = '';
    for(const t of data.threads) {{
      const ext = t.phone_ext || '';
      const contact = ext ? (labId && DIR[labId] && DIR[labId][String(ext)]) : null;
      if(!contact) continue;
      const initials = (t.name || '?').split(' ').map(s => s[0]).slice(0,2).join('').toUpperCase();
      const when = formatWhen(t.last_at);
      const preview = (t.last_role === 'user' ? 'You: ' : '') + (t.last_message || '');
      const div = document.createElement('div');
      div.className = 'thread-item';
      div.innerHTML =
        '<div class="avatar">' + esc(initials) + '</div>' +
        '<div class="thread-body">' +
          '<div class="thread-row1">' +
            '<span class="thread-name">' + esc(t.name) + '</span>' +
            '<span class="thread-time">' + esc(when) + '</span>' +
          '</div>' +
          '<div class="thread-preview">' + esc(preview) + '</div>' +
        '</div>';
      div.onclick = () => openSms(String(ext), contact);
      list.appendChild(div);
    }}
  }} catch(e) {{
    list.innerHTML = '<div class="empty-inbox" style="color:var(--red)">Failed to load inbox.</div>';
  }}
}}

function formatWhen(iso) {{
  if(!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  if(sameDay) return d.toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}});
  const diffDays = Math.floor((now - d) / 86400000);
  if(diffDays < 7) return d.toLocaleDateString([], {{weekday:'short'}});
  return d.toLocaleDateString([], {{month:'numeric', day:'numeric'}});
}}

async function openSms(ext, contact) {{
  currentSms = {{ext: ext, contact: contact}};
  document.getElementById('tab-messages').style.display = 'none';
  document.getElementById('tab-dialer').style.display = 'none';
  const sv = document.getElementById('smsview');
  sv.style.display = 'flex';

  const initials = (contact.name || '?').split(' ').map(s => s[0]).slice(0,2).join('').toUpperCase();
  document.getElementById('sms-avatar').textContent = initials;
  document.getElementById('sms-name').textContent = contact.name;
  document.getElementById('sms-sub').textContent = contact.role + ' · ext. ' + ext;

  const area = document.getElementById('sms-chat-area');
  area.innerHTML = '<div class="msg msg-system">Loading...</div>';

  try {{
    const lab = labId || contact.lab_id;
    const res = await fetch(API + '/api/chat/history?user_id=' + userId +
      '&lab_id=' + encodeURIComponent(lab) +
      '&persona_id=' + encodeURIComponent(contact.persona_id) +
      '&channel=sms');
    const data = await res.json();
    area.innerHTML = '';
    if(!data.messages || !data.messages.length) {{
      area.innerHTML = '<div class="msg msg-system">Send a message to start the conversation</div>';
    }} else {{
      for(const m of data.messages) appendSmsBubble(m.role, m.content);
    }}
    area.scrollTop = area.scrollHeight;
  }} catch(e) {{
    area.innerHTML = '<div class="msg msg-system" style="color:var(--red)">Failed to load history</div>';
  }}

  document.getElementById('sms-chat-input').focus();
  addCallLog(contact.name, 'SMS SENT');
}}

function backToInbox() {{
  currentSms = null;
  document.getElementById('smsview').style.display = 'none';
  document.getElementById('tab-messages').style.display = 'flex';
  loadInbox();
}}

function appendSmsBubble(role, content, opts) {{
  const area = document.getElementById('sms-chat-area');
  if(role === 'user') {{
    area.innerHTML += '<div class="msg msg-user">' + esc(content) + '</div>';
  }} else if(role === 'assistant') {{
    area.innerHTML += '<div class="msg msg-npc">' + esc(content) + '</div>';
  }} else {{
    const color = opts && opts.color ? opts.color : 'var(--muted)';
    const weight = opts && opts.bold ? '600' : '400';
    area.innerHTML += '<div class="msg msg-system" style="color:' + color + ';font-weight:' + weight + '">' + esc(content) + '</div>';
  }}
  area.scrollTop = area.scrollHeight;
}}

function updateSmsCharCount() {{
  const input = document.getElementById('sms-chat-input');
  const counter = document.getElementById('sms-char-count');
  if(!input || !counter) return;
  const len = input.value.length;
  const limit = 160;
  counter.textContent = len + '/' + limit;
  counter.style.color = len >= 141 ? 'var(--red)' : 'var(--muted)';
}}

async function sendSms() {{
  const input = document.getElementById('sms-chat-input');
  const text = input.value.trim();
  if(!text || !currentSms || smsSending) return;
  if(labStatus === 'failed') {{ showGameOver(); return; }}
  labDismissed = false;
  smsSending = true;
  const smsExt = currentSms.ext;
  input.value = '';
  updateSmsCharCount();

  appendSmsBubble('user', text);

  const area = document.getElementById('sms-chat-area');
  const typingId = 'typing-' + Date.now();
  area.innerHTML += '<div class="msg msg-npc pulse" id="' + typingId + '">. . .</div>';
  area.scrollTop = area.scrollHeight;

  try {{
    const lab = labId || currentSms.contact.lab_id;
    const res = await fetch(API + '/api/chat', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(Object.assign({{
        user_id: userId, lab_id: lab,
        persona_id: currentSms.contact.persona_id,
        message: text, channel: 'sms'
      }}, spoofPayload()))
    }});
    const data = await res.json().catch(() => ({{}}));
    const el = document.getElementById(typingId);
    if(el) el.remove();

    if(res.status === 409) {{
      appendSmsBubble('system', 'Lab not started. Start the simulation first.', {{color:'var(--amber)'}});
      smsSending = false; return;
    }}
    if(!res.ok) {{
      const detail = (data && data.detail && (data.detail.message || data.detail)) || ('HTTP ' + res.status);
      appendSmsBubble('system', typeof detail === 'string' ? detail : JSON.stringify(detail), {{color:'var(--red)'}});
      smsSending = false; return;
    }}

    const chunks = (data.response || '').split(/\\n{{2,}}/).filter(s => s.trim().length);
    if(!chunks.length && data.response) chunks.push(data.response);
    for(let i = 0; i < chunks.length; i++) {{
      setTimeout(() => {{ if(currentSms && currentSms.ext === smsExt) appendSmsBubble('assistant', chunks[i].trim()); }}, i * 400);
    }}

    const tailDelay = Math.max(chunks.length, 1) * 400;
    if(data.channel_event) {{
      const _evtColor = data.channel_event === 'sms_clicked' ? 'var(--accent)'
                      : data.channel_event === 'sms_reported' ? 'var(--red)'
                      : 'var(--muted)';
      const _evtMsg = data.channel_event_description || data.channel_event;
      setTimeout(() => appendSmsBubble('system', '⚡ ' + _evtMsg, {{color: _evtColor, bold: data.channel_event === 'sms_clicked'}}), tailDelay);
    }}
    if(data.voicemail) {{
      setTimeout(() => appendSmsBubble('system', '(Target is offline -- ' + (data.work_status || 'after hours') + ')', {{color:'var(--amber)'}}), tailDelay);
    }}
    if(data.flag_found) {{
      const _flagMsg = data.delivered_email
        ? '📧 Email delivered — check SF Mail inbox'
        : 'FLAG: ' + data.flag_found;
      setTimeout(() => appendSmsBubble('system', _flagMsg, {{color:'var(--accent)', bold:true}}), tailDelay);
    }}
    if(data.mission_failed) {{
      labStatus = 'failed';
      setTimeout(() => showGameOver(data.fail_reason, data.failed_persona || (currentSms && currentSms.contact.name)), tailDelay + 200);
    }} else if(data.caught) {{
      setTimeout(() => appendSmsBubble('system', 'CAUGHT! Target is suspicious.', {{color:'var(--red)', bold:true}}), tailDelay + 100);
    }}

    if(data.followup_hint && !data.mission_failed && !data.voicemail && currentSms) {{
      chainFollowup({{
        contact: currentSms.contact,
        channel: 'sms',
        hint: data.followup_hint,
        remaining: 2,
      }});
    }}
  }} catch(e) {{
    const el = document.getElementById(typingId);
    if(el) el.remove();
    appendSmsBubble('system', 'Delivery failed', {{color:'var(--red)'}});
  }}
  smsSending = false;
  input.focus();
}}

function esc(t) {{
  const d = document.createElement('div');
  d.textContent = t == null ? '' : String(t);
  return d.innerHTML;
}}
</script>
</body>
</html>"""


@app.get("/directory", response_class=HTMLResponse)
async def directory_page():
    return HTMLResponse(content="<html><body>403 Forbidden</body></html>", status_code=403)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9007)
