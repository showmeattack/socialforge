"""SF Mail — Email Client Simulator. Three tabs: Compose | Sent | Inbox."""
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SocialForge Email")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LABS_DIR = Path(__file__).parent.parent.parent / "labs"


def load_contacts():
    contacts = {}
    for f in LABS_DIR.glob("*.json"):
        try:
            with open(f, encoding="utf-8") as fh:
                lab = json.load(fh)
            company = (lab.get("target_company") or {}).get("name", lab.get("id", "Unknown"))
            for pid, p in lab.get("personas", {}).items():
                email = p.get("email")
                if email:
                    contacts[email.lower()] = {
                        "name": p["name"],
                        "role": p.get("role", ""),
                        "company": company,
                        "persona_id": pid,
                        "lab_id": lab["id"],
                        "email": email,
                        "gullibility": (p.get("psychology") or {}).get("gullibility", 50),
                    }
        except Exception:
            continue
    return contacts


CONTACTS = load_contacts()

PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SF Mail</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:#070b12;
  --sidebar:#0a0e17;
  --surface:#0d1117;
  --surface2:#111827;
  --border:rgba(255,255,255,0.07);
  --border-soft:rgba(255,255,255,0.04);
  --accent:#00ff88;
  --accent-dim:rgba(0,255,136,0.06);
  --accent-mid:rgba(0,255,136,0.12);
  --accent-glow:rgba(0,255,136,0.3);
  --green:#00ff88;
  --green-dim:rgba(0,255,136,0.08);
  --amber:#f59e0b;
  --amber-dim:rgba(245,158,11,0.08);
  --red:#ef4444;
  --red-dim:rgba(239,68,68,0.08);
  --purple:#6366f1;
  --purple-dim:rgba(99,102,241,0.08);
  --text:#e2e8f0;
  --text-muted:#94a3b8;
  --text-dim:#475569;
  --font:'JetBrains Mono',monospace;
  --font-mono:'JetBrains Mono',monospace;
}}

body{{
  font-family:var(--font);
  background:var(--bg);
  color:var(--text);
  height:100vh;
  display:flex;
  flex-direction:column;
  overflow:hidden;
  font-size:13px;
  line-height:1.5;
}}

/* HIDDEN TAB BAR */
.tab-bar{{display:none}}
.tab{{display:none}}

/* LAYOUT */
.app-layout{{
  display:flex;
  flex:1;
  overflow:hidden;
  min-height:0;
}}

/* ============================================================
   LEFT SIDEBAR (220px)
   ============================================================ */
.nav-sidebar{{
  width:220px;
  flex-shrink:0;
  background:var(--sidebar);
  border-right:1px solid var(--border);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}}

.ns-logo{{
  padding:18px 16px 14px;
  display:flex;
  align-items:center;
  gap:10px;
  border-bottom:1px solid var(--border-soft);
  flex-shrink:0;
}}
.ns-logo-icon{{
  width:32px;height:32px;
  background:var(--accent);
  border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
}}
.ns-logo-icon svg{{display:block}}
.ns-logo-text{{
  font-size:16px;font-weight:700;
  color:var(--text);letter-spacing:-.3px;
}}
.ns-logo-text span{{color:var(--accent)}}

.ns-compose-btn{{
  margin:12px 12px 8px;
  padding:10px 0;
  background:var(--accent);
  color:#070b12;
  border:none;
  border-radius:4px;
  font-size:13px;font-weight:600;
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:7px;
  transition:background .15s,box-shadow .15s;
  flex-shrink:0;
}}
.ns-compose-btn:hover{{background:#00cc6a;box-shadow:0 4px 16px var(--accent-glow)}}

.ns-section{{padding:6px 0 2px;flex-shrink:0}}

.ns-nav-item{{
  display:flex;align-items:center;gap:10px;
  padding:8px 16px;
  cursor:pointer;
  border-radius:0 3px 3px 0;
  margin-right:12px;
  transition:background .1s;
  position:relative;
  border:none;background:none;
  width:calc(100% - 12px);
  text-align:left;
  color:var(--text-muted);
  font-size:13px;font-weight:500;
  font-family:var(--font);
}}
.ns-nav-item:hover{{background:rgba(255,255,255,0.05);color:var(--text)}}
.ns-nav-item.active{{background:var(--accent-mid);color:var(--accent);font-weight:600}}
.ns-nav-item .nav-icon{{
  font-size:16px;width:20px;text-align:center;flex-shrink:0;font-style:normal;
}}
.ns-nav-label{{flex:1}}
.ns-badge{{
  font-size:11px;font-weight:700;
  min-width:20px;height:20px;
  border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  padding:0 5px;
}}
.ns-badge.blue{{background:var(--accent);color:#fff}}
.ns-badge.red{{background:var(--red);color:#fff}}
.ns-badge.green{{background:var(--green);color:#fff}}
.ns-badge.amber{{background:var(--amber);color:#111827;font-size:10px}}

.ns-divider{{
  height:1px;background:var(--border-soft);
  margin:10px 16px;flex-shrink:0;
}}

.ns-label-section{{
  padding:4px 0 4px;
  flex-shrink:0;
}}
.ns-label-heading{{
  font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;
  color:var(--text-dim);padding:4px 16px 6px;
}}
.ns-label-item{{
  display:flex;align-items:center;gap:9px;
  padding:6px 16px;cursor:default;
  font-size:12px;color:var(--text-muted);
}}
.label-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}

.ns-profile{{
  margin-top:auto;
  border-top:1px solid var(--border-soft);
  padding:12px 14px;
  display:flex;align-items:center;gap:10px;
  flex-shrink:0;
  position:relative;
  transition:background .15s;
}}
.ns-profile:hover{{background:rgba(0,255,136,0.03)}}
.ns-avatar{{
  width:34px;height:34px;
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;
  background:var(--accent);color:#fff;
  flex-shrink:0;
  cursor:default;
}}
.ns-profile-info{{flex:1;min-width:0}}
.ns-profile-email{{
  font-size:12px;color:var(--text);font-weight:500;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.ns-profile-role{{font-size:11px;color:var(--text-muted)}}

/* ============================================================
   MIDDLE LIST PANE (340px)
   ============================================================ */
.list-pane{{
  width:340px;
  flex-shrink:0;
  border-right:1px solid var(--border);
  display:flex;
  flex-direction:column;
  overflow:hidden;
  background:var(--surface);
}}

.lp-header{{
  padding:14px 16px 10px;
  border-bottom:1px solid var(--border-soft);
  flex-shrink:0;
}}
.lp-title{{
  font-size:18px;font-weight:700;color:var(--text);
  margin-bottom:10px;
}}
.lp-search{{
  position:relative;
}}
.lp-search-icon{{
  position:absolute;left:10px;top:50%;transform:translateY(-50%);
  color:var(--text-dim);font-size:14px;pointer-events:none;
}}
.lp-search input{{
  width:100%;padding:7px 10px 7px 32px;
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border);
  border-radius:6px;
  color:var(--text);font-size:13px;
  font-family:var(--font);
  outline:none;transition:border-color .15s,background .15s;
}}
.lp-search input:focus{{border-color:var(--accent);background:rgba(0,255,136,0.05)}}
.lp-search input::placeholder{{color:var(--text-dim)}}

.lp-body{{flex:1;overflow-y:auto;}}

/* Mail list items */
.mail-list{{flex:1;overflow-y:auto}}
.mail-empty{{
  padding:48px 20px;text-align:center;
  color:var(--text-dim);font-size:13px;
}}
.mail-empty .ico{{font-size:36px;opacity:.3;margin-bottom:12px;display:block}}
.mail-empty-link{{
  color:var(--accent);cursor:pointer;font-size:12px;margin-top:6px;display:inline-block;
}}
.mail-empty-link:hover{{text-decoration:underline}}

.mail-item{{
  padding:12px 16px;
  border-bottom:1px solid var(--border-soft);
  cursor:pointer;
  transition:background .1s;
  display:flex;flex-direction:column;gap:4px;
  border-left:3px solid transparent;
  position:relative;
}}
.mail-item:hover{{background:rgba(255,255,255,0.03)}}
.mail-item.active{{background:var(--accent-dim);border-left-color:var(--accent)}}
.mail-item.unread{{border-left-color:var(--accent)}}
.mail-item.unread .mi-who{{color:var(--text);font-weight:700}}
.mail-item.unread .mi-subj{{color:var(--text-muted)}}

.mail-item-row{{display:flex;align-items:center;gap:10px}}
.sender-avatar{{
  width:36px;height:36px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;flex-shrink:0;
}}
.mi-meta{{flex:1;min-width:0}}
.mi-who{{
  font-size:13px;font-weight:500;color:var(--text-muted);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.mi-time{{font-size:11px;color:var(--text-dim);white-space:nowrap;flex-shrink:0}}
.mi-subj{{
  font-size:12px;color:var(--text-dim);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  padding-left:46px;
}}
.mi-flag{{
  display:inline-block;background:var(--green-dim);color:var(--green);
  font-size:10px;font-weight:700;padding:1px 5px;margin-left:5px;
  border-radius:3px;border:1px solid rgba(0,255,136,0.25);
}}
.ms-ok{{
  display:inline-block;background:var(--green-dim);color:var(--green);
  font-size:10px;font-weight:700;padding:1px 5px;margin-left:4px;
  border-radius:3px;border:1px solid rgba(0,255,136,0.25);
}}
.ms-spam{{
  display:inline-block;background:var(--red-dim);color:var(--red);
  font-size:10px;font-weight:700;padding:1px 5px;margin-left:4px;
  border-radius:3px;border:1px solid rgba(239,68,68,0.25);
}}

/* Contacts list (compose quick targets) */
.contacts-header{{
  padding:10px 16px 6px;
  font-size:11px;font-weight:600;letter-spacing:.4px;text-transform:uppercase;
  color:var(--text-dim);
  border-bottom:1px solid var(--border-soft);
  flex-shrink:0;
}}
.contact-item{{
  display:flex;align-items:center;gap:10px;
  padding:9px 16px;
  border-bottom:1px solid var(--border-soft);
  cursor:pointer;
  transition:background .1s;
}}
.contact-item:hover{{background:rgba(255,255,255,0.04)}}
.contact-avatar{{
  width:32px;height:32px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;flex-shrink:0;
}}
.contact-info{{flex:1;min-width:0}}
.contact-name{{font-size:13px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.contact-email{{font-size:11px;color:var(--text-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.contact-company{{font-size:11px;color:var(--accent);white-space:nowrap;flex-shrink:0}}

/* ============================================================
   RIGHT CONTENT PANE
   ============================================================ */
.content-pane{{
  flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg);min-width:0;
}}

/* PANES */
.pane{{display:none;flex:1;overflow:hidden;flex-direction:column}}
.pane.active{{display:flex}}

/* ---- COMPOSE ---- */
.compose-layout{{display:flex;flex:1;overflow:hidden;min-height:0}}
.compose-main{{flex:1;overflow-y:auto;padding:0;min-width:0;display:flex;flex-direction:column}}

.compose-toolbar{{
  padding:10px 20px;
  border-bottom:1px solid var(--border-soft);
  display:flex;align-items:center;gap:8px;
  flex-shrink:0;
  background:var(--bg);
}}
.compose-title{{font-size:15px;font-weight:600;color:var(--text);flex:1}}

.mode-toggle{{
  display:flex;
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border);
  border-radius:6px;
  overflow:hidden;
  flex-shrink:0;
}}
.mode-btn{{
  padding:6px 14px;font-size:12px;font-weight:600;
  background:none;color:var(--text-muted);border:none;cursor:pointer;
  transition:all .12s;display:flex;align-items:center;gap:5px;
  font-family:var(--font);white-space:nowrap;
}}
.mode-btn:hover{{color:var(--text);background:rgba(255,255,255,0.04)}}
.mode-btn.active{{background:var(--accent);color:#fff}}
.mode-btn+.mode-btn{{border-left:1px solid var(--border)}}

.compose-fields{{padding:0 20px;background:var(--bg);flex-shrink:0}}

.field-row{{
  display:flex;align-items:center;
  border-bottom:1px solid var(--border-soft);
  padding:4px 0;
}}
.field-label{{
  font-size:12px;font-weight:600;color:var(--text-dim);
  width:60px;flex-shrink:0;padding:8px 0;
}}
.field-row input{{
  flex:1;background:transparent;border:none;
  color:var(--text);font-size:14px;
  font-family:var(--font);outline:none;
  padding:8px 0;
}}
.field-row input::placeholder{{color:var(--text-dim)}}
.field-row input.err{{color:var(--red)}}
.field-row input.locked{{color:var(--accent)}}

.from-hint{{
  font-size:11px;padding:4px 0 6px 60px;
  color:var(--text-dim);
  flex-shrink:0;
  padding-left:80px;
}}
.from-hint.warn{{color:var(--amber)}}
.from-hint.bad{{color:var(--red)}}
.from-hint.ok{{color:var(--green)}}
.from-hint.sync{{color:var(--accent)}}

/* Legacy hidden hint element */
.hint{{display:none}}

.tpl-row{{
  display:flex;flex-wrap:wrap;gap:6px;
  padding:10px 20px;
  border-bottom:1px solid var(--border-soft);
  flex-shrink:0;
}}
.tpl-chip{{
  padding:5px 12px;border-radius:16px;
  font-size:11px;font-weight:600;
  border:1px solid var(--border);
  background:rgba(255,255,255,0.04);
  color:var(--text-muted);
  cursor:pointer;transition:all .12s;
  font-family:var(--font);
}}
.tpl-chip:hover{{color:var(--text);border-color:rgba(255,255,255,0.2);background:rgba(255,255,255,0.08)}}
.tpl-chip.it{{border-color:rgba(239,68,68,0.35);color:var(--red)}}
.tpl-chip.it:hover{{background:var(--red-dim)}}
.tpl-chip.hr{{border-color:rgba(245,158,11,0.35);color:var(--amber)}}
.tpl-chip.hr:hover{{background:var(--amber-dim)}}
.tpl-chip.ceo{{border-color:rgba(139,92,246,0.35);color:var(--purple)}}
.tpl-chip.ceo:hover{{background:var(--purple-dim)}}
.tpl-chip.sys{{border-color:rgba(0,255,136,0.35);color:var(--accent)}}
.tpl-chip.sys:hover{{background:var(--accent-dim)}}

.compose-body-wrap{{
  flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;
  padding:12px 20px 0;
}}
textarea.body-field{{
  flex:1;min-height:200px;
  background:transparent;border:none;
  color:var(--text);font-size:14px;line-height:1.75;
  font-family:var(--font-mono);
  resize:none;outline:none;
  padding:0;
}}
textarea.body-field::placeholder{{color:var(--text-dim)}}

/* Legacy hidden spam elements */
.spam-indicator,.si-score,.si-fill,.si-hint,.si-checklist,.si-checks,.si-check-item,.sic-dot,.phish-quality-label,.phish-quality-wrap{{display:none}}

/* Campaign extras (mass mode) */
.campaign-extras{{display:none;flex-direction:column;gap:8px;padding:12px 20px;border-top:1px solid var(--border-soft);flex-shrink:0}}
.campaign-extras.show{{display:flex}}
.ce-label{{
  font-size:12px;font-weight:700;color:var(--amber);
  display:flex;align-items:center;gap:6px;
}}
.ce-sub{{font-size:11px;color:var(--text-dim)}}
.npc-actions{{display:flex;align-items:center;gap:8px}}
.npc-btn{{
  padding:5px 12px;border-radius:5px;
  font-size:11px;font-weight:600;
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;
  transition:all .12s;font-family:var(--font);
}}
.npc-btn:hover{{background:rgba(255,255,255,0.1);color:var(--text)}}
.npc-count{{font-size:12px;color:var(--text-muted);margin-left:auto}}
.npc-list{{
  max-height:140px;overflow-y:auto;
  border:1px solid var(--border);border-radius:6px;
  background:var(--surface);
}}
.npc-item{{display:flex;align-items:center;gap:8px;padding:7px 12px;cursor:pointer;border-bottom:1px solid var(--border-soft);transition:background .1s}}
.npc-item:last-child{{border-bottom:none}}
.npc-item:hover{{background:rgba(255,255,255,0.04)}}
.npc-item input[type=checkbox]{{accent-color:var(--accent);flex-shrink:0;cursor:pointer}}
.npc-name{{font-size:12px;font-weight:600;color:var(--text);white-space:nowrap;flex-shrink:0}}
.npc-email{{font-size:11px;color:var(--text-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}}
.npc-co{{font-size:11px;color:var(--accent);white-space:nowrap;flex-shrink:0}}
.npc-loading{{padding:12px;text-align:center;color:var(--text-dim);font-size:12px}}

.campaign-result{{display:none;padding:12px 20px;border-top:1px solid var(--border-soft);max-height:220px;overflow-y:auto;flex-shrink:0}}
.campaign-result.show{{display:block}}
.cr-stat{{font-size:12px;color:var(--text-muted);margin-bottom:8px}}
.cr-stat span{{color:var(--amber);font-weight:700}}
.flag-pieces{{display:flex;gap:6px;margin-bottom:8px}}
.fp-slot{{flex:1;background:var(--surface);border:1px solid var(--border);padding:5px 6px;font-size:11px;font-family:var(--font-mono);color:var(--text-dim);text-align:center;border-radius:4px}}
.fp-slot.filled{{background:var(--green-dim);border-color:rgba(0,255,136,0.4);color:var(--green)}}
.flag-done{{background:var(--green-dim);border:1px solid rgba(0,255,136,0.4);padding:10px;font-size:12px;color:var(--green);font-family:var(--font-mono);font-weight:700;text-align:center;display:none;margin-bottom:8px;border-radius:5px}}
.flag-done.show{{display:block}}
.cr-table{{width:100%;border-collapse:collapse;font-size:11px;font-family:var(--font)}}
.cr-table th{{background:rgba(255,255,255,0.04);color:var(--text-dim);padding:5px 8px;text-align:left;font-size:10px;font-weight:700;letter-spacing:.5px;text-transform:uppercase}}
.cr-table td{{padding:4px 8px;border-bottom:1px solid var(--border-soft);color:var(--text-muted)}}
.cr-table td:nth-child(3),.cr-table td:nth-child(4){{color:var(--green)}}
.cr-blocked{{font-size:12px;color:var(--red);padding:6px 10px;background:var(--red-dim);border:1px solid rgba(239,68,68,0.2);margin-bottom:8px;border-radius:4px}}

/* Send footer bar */
.compose-footer{{
  padding:12px 20px;
  border-top:1px solid var(--border-soft);
  display:flex;align-items:center;gap:12px;
  flex-shrink:0;
  background:var(--bg);
}}
.btn-send{{
  padding:9px 24px;border-radius:6px;
  font-size:13px;font-weight:700;
  border:none;cursor:pointer;
  display:flex;align-items:center;gap:7px;
  transition:all .15s;
  font-family:var(--font);
}}
.btn-send.single{{background:var(--accent);color:#fff}}
.btn-send.single:hover{{background:#00cc6a;box-shadow:0 4px 14px var(--accent-glow)}}
.btn-send.mass{{background:var(--amber);color:#111827}}
.btn-send.mass:hover{{box-shadow:0 4px 14px rgba(245,158,11,0.4)}}
.btn-send:disabled{{opacity:.4;cursor:default;box-shadow:none}}
.status{{font-size:12px;font-family:var(--font)}}
.status.ok{{color:var(--green)}}
.status.err{{color:var(--red)}}

@keyframes spin{{to{{transform:rotate(360deg)}}}}
.spinner{{display:inline-block;width:12px;height:12px;border:2px solid rgba(255,255,255,0.15);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle}}

/* ---- QUALITY PANEL (right of compose) ---- */
.quality-panel{{
  width:220px;flex-shrink:0;
  border-left:1px solid var(--border);
  background:var(--surface);
  display:flex;flex-direction:column;overflow:hidden;
}}
.qp-header{{
  padding:14px 16px 10px;
  border-bottom:1px solid var(--border-soft);
  font-size:13px;font-weight:700;color:var(--text);
}}
.qp-score-block{{
  padding:16px;
  border-bottom:1px solid var(--border-soft);
  display:flex;flex-direction:column;gap:8px;
}}
.qp-score-row{{display:flex;align-items:baseline;gap:5px}}
.qp-score-num{{font-size:36px;font-weight:700;line-height:1;transition:color .3s;font-family:var(--font)}}
.qp-score-of{{font-size:13px;color:var(--text-dim)}}
.qp-score-label{{font-size:11px;color:var(--text-dim);transition:color .3s;line-height:1.4}}
.qp-bar-track{{height:4px;background:rgba(255,255,255,0.07);border-radius:2px;overflow:hidden}}
.qp-bar-fill{{height:100%;transition:width .35s,background .35s;width:0;border-radius:2px}}
.qp-checks{{padding:12px 16px;display:flex;flex-direction:column;gap:6px;flex:1;overflow-y:auto}}
.qp-check-heading{{font-size:11px;font-weight:700;color:var(--text-dim);letter-spacing:.4px;text-transform:uppercase;margin-bottom:2px}}
.qp-check-item{{display:flex;align-items:flex-start;gap:8px;font-size:12px;line-height:1.5}}
.qp-check-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0;margin-top:4px}}
.qp-check-item.good .qp-check-dot{{background:var(--green)}}
.qp-check-item.good .qp-check-text{{color:var(--green)}}
.qp-check-item.bad .qp-check-dot{{background:var(--red)}}
.qp-check-item.bad .qp-check-text{{color:var(--red)}}
.qp-check-item.neutral .qp-check-dot{{background:var(--text-dim)}}
.qp-check-item.neutral .qp-check-text{{color:var(--text-dim)}}

/* ---- MAIL VIEWER (sent/inbox detail) ---- */
.mail-viewer{{flex:1;display:flex;flex-direction:column;overflow:hidden}}
.mv-toolbar{{
  padding:10px 20px;
  border-bottom:1px solid var(--border-soft);
  display:flex;gap:8px;align-items:center;
  flex-shrink:0;
  background:var(--bg);
}}
.mv-btn{{
  padding:6px 14px;border-radius:6px;
  font-size:12px;font-weight:600;
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border);
  color:var(--text-muted);cursor:pointer;
  transition:all .12s;font-family:var(--font);
}}
.mv-btn:hover{{background:rgba(255,255,255,0.1);color:var(--text)}}
.mv-btn.del:hover{{border-color:var(--red);color:var(--red);background:var(--red-dim)}}
.mv-btn.flag-btn:hover{{border-color:var(--amber);color:var(--amber);background:var(--amber-dim)}}
.mv-ts{{margin-left:auto;font-size:12px;color:var(--text-dim)}}
.mv-head{{
  padding:20px 24px;
  border-bottom:1px solid var(--border-soft);
  background:var(--bg);flex-shrink:0;
}}
.mv-subj{{font-size:18px;font-weight:700;color:var(--text);margin-bottom:12px;line-height:1.3}}
.mv-meta div{{font-size:12px;color:var(--text-dim);line-height:2}}
.mv-meta .lbl{{display:inline-block;width:40px;font-weight:600;color:var(--text-dim);font-size:11px;text-transform:uppercase;letter-spacing:.4px}}
.mv-meta .val{{color:var(--text-muted)}}
.mv-body{{flex:1;overflow-y:auto;padding:20px 24px;font-size:14px;line-height:1.85;color:var(--text-muted);white-space:pre-wrap;font-family:var(--font)}}
.mv-flag{{
  margin:10px 24px;padding:12px 16px;
  background:var(--green-dim);border:1px solid rgba(0,255,136,0.4);
  font-size:13px;font-weight:700;color:var(--green);
  border-radius:6px;flex-shrink:0;display:none;
}}

/* ---- CAMPAIGN PANE ---- */
.campaign-redirect{{padding:32px 24px}}
.campaign-redirect h3{{font-size:16px;font-weight:700;color:var(--text);margin-bottom:8px}}
.campaign-redirect p{{font-size:13px;color:var(--text-muted);line-height:1.7}}
.campaign-redirect-link{{color:var(--accent);cursor:pointer;text-decoration:underline}}

/* ============================================================
   STATUS BAR
   ============================================================ */
.statusbar{{
  height:28px;flex-shrink:0;
  background:var(--sidebar);
  border-top:1px solid var(--border);
  display:flex;align-items:center;padding:0 16px;gap:18px;
}}
.sb-item{{display:flex;align-items:center;gap:6px;font-size:11px}}
.sb-key{{font-weight:700;text-transform:uppercase;color:var(--text-dim);letter-spacing:.4px}}
.sb-v{{color:var(--text-muted)}}
.sb-v.accent{{color:var(--accent)}}
.sb-v.warn{{color:var(--amber)}}
.sb-v.danger{{color:var(--red)}}
.sb-sep{{width:1px;height:14px;background:var(--border)}}
.sb-spacer{{flex:1}}
.sb-version{{font-size:11px;color:var(--text-dim)}}

/* ============================================================
   OVERLAYS
   ============================================================ */
.gate{{
  position:fixed;inset:0;
  background:rgba(17,24,39,0.92);
  backdrop-filter:blur(6px);
  display:none;flex-direction:column;align-items:center;justify-content:center;
  padding:32px;text-align:center;z-index:40;
}}
.gate.show{{display:flex}}
.gate-card{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:4px;
  padding:32px 40px;
  max-width:420px;width:100%;
}}
.gate-icon-wrap{{
  width:56px;height:56px;border-radius:50%;
  background:var(--accent-dim);border:1px solid rgba(0,255,136,0.3);
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 16px;font-size:22px;
}}
.gate h2{{font-size:18px;font-weight:700;color:var(--text);margin-bottom:8px}}
.gate p{{font-size:13px;color:var(--text-muted);line-height:1.7;margin-bottom:24px}}
.gate .gbtn{{
  background:var(--accent);color:#fff;
  border:none;padding:11px 28px;
  border-radius:7px;
  font-size:14px;font-weight:700;font-family:var(--font);
  cursor:pointer;transition:all .18s;
}}
.gate .gbtn:hover{{background:#00cc6a;box-shadow:0 4px 16px var(--accent-glow)}}
.gate .gbtn:disabled{{opacity:.4;cursor:default;box-shadow:none}}

.gameover{{
  position:fixed;inset:0;
  background:rgba(10,5,5,0.97);
  display:none;flex-direction:column;align-items:center;justify-content:center;
  padding:40px;text-align:center;z-index:50;
}}
.gameover.show{{display:flex}}
.gameover-card{{
  background:rgba(239,68,68,0.06);
  border:1px solid rgba(239,68,68,0.25);
  border-radius:12px;
  padding:36px 48px;max-width:500px;width:100%;
}}
.go-icon{{font-size:48px;margin-bottom:12px}}
.go-title{{font-size:28px;font-weight:800;color:var(--red);letter-spacing:-1px;margin-bottom:4px}}
.go-sub{{font-size:14px;color:#f87171;margin-bottom:16px}}
.go-who{{font-size:12px;color:#f87171;margin-bottom:12px;opacity:.8}}
.go-reason{{
  font-size:13px;color:#fecaca;line-height:1.65;margin-bottom:20px;
  padding:12px 16px;background:rgba(239,68,68,0.06);
  border:1px solid rgba(239,68,68,0.15);border-radius:6px;
}}
.go-btns{{display:flex;gap:10px;justify-content:center}}
.go-btns .rbtn{{
  background:var(--red);color:#fff;border:none;
  padding:10px 22px;border-radius:6px;
  font-size:13px;font-weight:700;font-family:var(--font);
  cursor:pointer;transition:all .18s;
}}
.go-btns .rbtn:hover{{box-shadow:0 4px 14px rgba(239,68,68,0.5)}}
.go-btns .dbtn{{
  background:rgba(255,255,255,0.06);color:var(--text-muted);
  border:1px solid var(--border);padding:10px 18px;
  border-radius:6px;font-size:13px;font-family:var(--font);cursor:pointer;transition:all .18s;
}}
.go-btns .dbtn:hover{{background:rgba(255,255,255,0.1)}}

button *{{pointer-events:none}}

::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.1);border-radius:2px}}
::-webkit-scrollbar-thumb:hover{{background:rgba(255,255,255,0.2)}}
</style>
</head>
<body>

<!-- Hidden tab-bar for JS compat -->
<div class="tab-bar" style="display:none">
  <button type="button" class="tab active" id="tab-compose"></button>
  <button type="button" class="tab" id="tab-sent"></button>
  <button type="button" class="tab" id="tab-inbox"></button>
</div>

<div class="app-layout">

  <!-- LEFT NAV SIDEBAR -->
  <nav class="nav-sidebar">

    <!-- Logo -->
    <div class="ns-logo">
      <div class="ns-logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
      </div>
      <div class="ns-logo-text">GHOST<span>_MAIL</span></div>
    </div>

    <!-- Compose button -->
    <button type="button" class="ns-compose-btn" id="nav-compose">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Compose
    </button>

    <!-- Nav items -->
    <div class="ns-section">
      <button type="button" class="ns-nav-item" id="nav-inbox">
        <span class="nav-icon">&#9993;</span>
        <span class="ns-nav-label">Inbox</span>
        <span class="ns-badge red" id="inbox-badge" style="display:none">0</span>
      </button>
      <button type="button" class="ns-nav-item" id="nav-sent">
        <span class="nav-icon">&#10148;</span>
        <span class="ns-nav-label">Sent</span>
        <span class="ns-badge green" id="sent-badge" style="display:none">0</span>
      </button>
      <button type="button" class="ns-nav-item" id="nav-campaign">
        <span class="nav-icon">&#9741;</span>
        <span class="ns-nav-label">Phish Queue</span>
        <span class="ns-badge amber">MASS</span>
      </button>
    </div>

    <div class="ns-divider"></div>

    <!-- Labels -->
    <div class="ns-label-section">
      <div class="ns-label-heading">Labels</div>
      <div class="ns-label-item"><div class="label-dot" style="background:#00ff88"></div>Work</div>
      <div class="ns-label-item"><div class="label-dot" style="background:#3b82f6"></div>Personal</div>
      <div class="ns-label-item"><div class="label-dot" style="background:#ef4444"></div>Phishing</div>
    </div>

    <!-- Profile at bottom -->
    <div class="ns-profile" id="ns-profile-btn" onclick="toggleIdentityPopover()" title="Click to change identity" style="cursor:pointer;position:relative;">
      <div class="ns-avatar" id="sidebar-avatar">AT</div>
      <div class="ns-profile-info">
        <div class="ns-profile-email" id="sidebar-username">attacker@kali.local</div>
        <div class="ns-profile-role">Red Team Operator</div>
      </div>
      <div style="font-size:11px;color:var(--accent);opacity:0.5;flex-shrink:0">✎</div>
    </div>
    <!-- Identity popover -->
    <div id="identity-popover" style="display:none;position:absolute;bottom:64px;left:10px;right:10px;background:#0d1117;border:1px solid rgba(0,255,136,0.3);border-radius:7px;padding:12px;z-index:300;box-shadow:0 0 16px rgba(0,0,0,0.6);">
      <div style="font-size:9px;font-weight:700;color:var(--accent);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">Change Identity</div>
      <input id="identity-input" type="email" placeholder="you@domain.tld" style="width:100%;background:rgba(255,255,255,0.05);border:1px solid rgba(0,255,136,0.25);border-radius:5px;padding:7px 10px;font-family:var(--font);font-size:12px;color:var(--text);outline:none;margin-bottom:8px;" onkeydown="if(event.key==='Enter')applyIdentityFromSidebar();if(event.key==='Escape')closeIdentityPopover();" />
      <div style="display:flex;gap:6px;">
        <button onclick="applyIdentityFromSidebar()" style="flex:1;padding:6px;border-radius:5px;background:rgba(0,255,136,0.12);color:var(--accent);border:1px solid rgba(0,255,136,0.3);font-family:var(--font);font-size:11px;font-weight:700;cursor:pointer;">SAVE</button>
        <button onclick="closeIdentityPopover()" style="padding:6px 12px;border-radius:5px;background:transparent;color:var(--text-muted);border:1px solid var(--border);font-family:var(--font);font-size:11px;cursor:pointer;">✕</button>
      </div>
    </div>

  </nav>

  <!-- MIDDLE LIST PANE -->
  <div class="list-pane" id="list-panel" style="display:none">

    <div class="lp-header">
      <div class="lp-title" id="list-panel-title">Targets</div>
      <div class="lp-search">
        <span class="lp-search-icon">&#128269;</span>
        <input type="text" placeholder="Search..." aria-label="Search">
      </div>
    </div>

    <div class="lp-body">
      <!-- Compose: quick contacts -->
      <div id="list-compose-hint" style="display:flex;flex-direction:column;height:100%">
        <div class="contacts-header">NPC Targets &mdash; <span id="list-panel-count" style="color:var(--accent)">0</span> contacts</div>
        <div id="quick-target-list" style="flex:1;overflow-y:auto">
          <div style="padding:20px 16px;color:var(--text-dim);font-size:12px">Loading contacts...</div>
        </div>
      </div>

      <!-- Sent list -->
      <div class="mail-list" id="sent-list-view" style="display:none">
        <div class="mail-empty" id="sent-empty">
          <span class="ico">&#10148;</span>
          No sent messages<br>
          <span class="mail-empty-link" id="go-compose-link">Compose a new email</span>
        </div>
      </div>

      <!-- Inbox list -->
      <div class="mail-list" id="inbox-list-view" style="display:none">
        <div class="mail-empty" id="inbox-empty">
          <span class="ico">&#9993;</span>
          Inbox is empty<br>
          <span style="color:var(--text-dim);font-size:12px">NPC replies appear here</span>
        </div>
      </div>
    </div>

  </div>

  <!-- RIGHT CONTENT PANE -->
  <div class="content-pane">

    <!-- COMPOSE PANE -->
    <div class="pane active" id="pane-compose">
      <div class="compose-layout">
        <div class="compose-main">

          <!-- Toolbar -->
          <div class="compose-toolbar">
            <span class="compose-title">New Message</span>
            <div class="mode-toggle">
              <button type="button" class="mode-btn active" id="mode-single">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                Single
              </button>
              <button type="button" class="mode-btn" id="mode-mass">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                Mass Campaign
              </button>
            </div>
          </div>

          <!-- Fields -->
          <div class="compose-fields">
            <div class="field-row">
              <span class="field-label">From</span>
              <input id="from-field" value="attacker@kali.local" placeholder="spoof@domain.com" autocomplete="off">
            </div>
            <div class="from-hint" id="from-hint">Tip: spoof a lookalike domain. Real brand domains are rejected by the mail gateway.</div>

            <div id="single-to-row" class="field-row">
              <span class="field-label">To</span>
              <input id="to-field" placeholder="target@company.com" autocomplete="off">
            </div>

            <div class="field-row">
              <span class="field-label">Subject</span>
              <input id="subject-field" placeholder="Email subject...">
            </div>
          </div>

          <!-- Template chips -->
          <div class="tpl-row">
            <button type="button" class="tpl-chip ceo" onclick="applyTemplate('ceo_request')">&#128084; Authority (CEO)</button>
            <button type="button" class="tpl-chip hr" onclick="applyTemplate('hr_announce')">&#128203; HR Update</button>
            <button type="button" class="tpl-chip it" onclick="applyTemplate('it_security')">&#128274; IT Security</button>
            <button type="button" class="tpl-chip sys" onclick="applyTemplate('sys_alert')">&#9888; Security Alert</button>
          </div>

          <!-- Body -->
          <div class="compose-body-wrap">
            <textarea class="body-field" id="body-field"
              placeholder="Write your email body here...&#10;&#10;Tip: paste a phishing URL and the system auto-detects it for credential harvesting."></textarea>
          </div>

          <!-- Legacy hidden spam elements -->
          <div class="spam-indicator" id="spam-indicator" style="display:none">
            <span id="si-score"></span>
            <div id="si-fill"></div>
            <div id="si-hint"></div>
            <div id="si-checklist"></div>
          </div>

          <!-- Mass campaign extras -->
          <div class="campaign-extras" id="campaign-extras">
            <div class="ce-label">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              Campaign Recipients
            </div>
            <div class="ce-sub">Select NPC targets &mdash; include your phishing URL in the body above</div>
            <div class="npc-actions">
              <button type="button" class="npc-btn" id="np-all-btn">Select All</button>
              <button type="button" class="npc-btn" id="np-clear-btn">Clear</button>
              <span class="npc-count" id="npc-count">0 selected</span>
            </div>
            <div class="npc-list" id="npc-list"><div class="npc-loading">Loading contacts...</div></div>
          </div>

          <!-- Send footer -->
          <div class="compose-footer">
            <button type="button" class="btn-send single" id="send-btn">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
              Send
            </button>
            <span class="status" id="status-msg"></span>
          </div>

          <!-- Campaign result -->
          <div class="campaign-result" id="campaign-result"></div>

        </div>

        <!-- PHISH QUALITY SIDEBAR -->
        <div class="quality-panel" id="phish-sidebar">
          <div class="qp-header">Phish Quality</div>
          <div class="qp-score-block">
            <div class="qp-score-row">
              <span class="qp-score-num" id="cs-score-num" style="color:var(--text-dim)">--</span>
              <span class="qp-score-of">/ 100</span>
            </div>
            <div class="qp-score-label" id="cs-score-label">Awaiting input</div>
            <div class="qp-bar-track"><div class="qp-bar-fill" id="cs-bar-fill"></div></div>
          </div>
          <div class="qp-checks" id="cs-checks">
            <div class="qp-check-heading">Checks</div>
            <div class="qp-check-item neutral"><span class="qp-check-dot"></span><span class="qp-check-text">SPF: awaiting sender</span></div>
            <div class="qp-check-item neutral"><span class="qp-check-dot"></span><span class="qp-check-text">DKIM: awaiting sender</span></div>
            <div class="qp-check-item neutral"><span class="qp-check-dot"></span><span class="qp-check-text">Subject tone: awaiting input</span></div>
            <div class="qp-check-item neutral"><span class="qp-check-dot"></span><span class="qp-check-text">Link count: no URLs</span></div>
            <div class="qp-check-item neutral"><span class="qp-check-dot"></span><span class="qp-check-text">Urgency: not detected</span></div>
          </div>
        </div>

      </div>
    </div>

    <!-- SENT PANE -->
    <div class="pane" id="pane-sent">
      <div class="mail-viewer" id="sent-viewer" style="display:none">
        <div class="mv-toolbar">
          <button type="button" class="mv-btn" id="back-sent-btn">&#8592; Back</button>
          <button type="button" class="mv-btn flag-btn">Forward</button>
          <span class="mv-ts" id="sv-ts"></span>
        </div>
        <div class="mv-head">
          <div class="mv-subj" id="sv-subj"></div>
          <div class="mv-meta">
            <div><span class="lbl">From</span><span class="val" id="sv-from"></span></div>
            <div><span class="lbl">To</span><span class="val" id="sv-to"></span></div>
          </div>
        </div>
        <div class="mv-body" id="sv-body"></div>
      </div>
    </div>

    <!-- INBOX PANE -->
    <div class="pane" id="pane-inbox">
      <div class="mail-viewer" id="inbox-viewer" style="display:none">
        <div class="mv-toolbar">
          <button type="button" class="mv-btn" id="back-inbox-btn">&#8592; Back</button>
          <button type="button" class="mv-btn del" id="iv-del-btn">Delete</button>
          <button type="button" class="mv-btn flag-btn">Flag as Phish</button>
          <span class="mv-ts" id="iv-ts"></span>
        </div>
        <div class="mv-head">
          <div class="mv-subj" id="iv-subj"></div>
          <div class="mv-meta">
            <div><span class="lbl">From</span><span class="val" id="iv-from"></span></div>
            <div><span class="lbl">To</span><span class="val" id="iv-to"></span></div>
          </div>
        </div>
        <div class="mv-body" id="iv-body"></div>
        <div class="mv-flag" id="iv-flag"></div>
      </div>
    </div>

    <!-- CAMPAIGN PANE -->
    <div class="pane" id="pane-campaign">
      <div class="campaign-redirect">
        <h3>Mass Phishing Campaign</h3>
        <p>
          Switch to
          <span class="campaign-redirect-link" id="goto-mass-btn">Mass Campaign mode</span>
          in Compose to configure recipients and launch a campaign.
        </p>
      </div>
    </div>

  </div>
</div>

<!-- STATUS BAR -->
<div class="statusbar">
  <div class="sb-item">
    <span class="sb-key">UID</span>
    <span class="sb-v accent" id="stat-uid">--</span>
  </div>
  <div class="sb-sep"></div>
  <div class="sb-item">
    <span class="sb-key">Lab</span>
    <span class="sb-v" id="stat-lab">none</span>
  </div>
  <div class="sb-sep"></div>
  <div class="sb-item">
    <span class="sb-key">Spam Score</span>
    <span class="sb-v" id="stat-spam">--</span>
  </div>
  <div class="sb-sep"></div>
  <div class="sb-item">
    <span class="sb-key">Status</span>
    <span class="sb-v" id="stat-status">Idle</span>
  </div>
  <div class="sb-spacer"></div>
  <div class="sb-version">SF Mail v2 &bull; Port 9004</div>
</div>

<!-- GATE OVERLAY -->
<div class="gate" id="gate">
  <div class="gate-card">
    <div class="gate-icon-wrap">&#128274;</div>
    <h2>Lab Not Started</h2>
    <p id="gate-msg">Start the lab simulation from the main app to enable communication with NPC targets.</p>
    <button type="button" class="gbtn" id="gate-btn" style="display:none">Start Simulation</button>
  </div>
</div>

<!-- GAME OVER -->
<div class="gameover" id="gameover">
  <div class="gameover-card">
    <div class="go-icon">&#128683;</div>
    <div class="go-title">Mission Failed</div>
    <div class="go-sub">Your cover has been blown</div>
    <div class="go-who" id="go-who"></div>
    <div class="go-reason" id="go-reason">The target recognized the attack.</div>
    <div class="go-btns">
      <button type="button" class="rbtn" id="reset-btn">Reset Lab</button>
      <button type="button" class="dbtn" id="dismiss-btn">Dismiss</button>
    </div>
  </div>
</div>

<script>
const API = 'http://127.0.0.1:8000';
const p = new URLSearchParams(location.search);
const userId = parseInt(p.get('uid') || p.get('user') || '1');
let activeLabId = p.get('lab_id') || p.get('lab') || null;
let labStatus = null;
let gameOverDismissed = false;
let attackerEmail = 'attacker@kali.local';
let composeMode = 'single';

let currentTab = 'compose';
let sentEmails = [];
let sentCounter = 1;
let inboxItems = [];
let viewingSentId = null;
let viewingInboxId = null;
let identityOriginal = 'attacker@kali.local';
let allContacts = [];
let lastSpamScore = null;

const BRANDS = new Set(['microsoft.com','outlook.com','office365.com','google.com',
  'gmail.com','apple.com','icloud.com','amazon.com','meta.com','facebook.com',
  'okta.com','slack.com','zoom.us','paypal.com','github.com','linkedin.com',
  'twitter.com','x.com','adobe.com','salesforce.com','dropbox.com']);

function esc(t) {{
  const d = document.createElement('div');
  d.textContent = String(t || '');
  return d.innerHTML;
}}

function avatarColor(name) {{
  const colors = [
    ['rgba(16,185,129,0.2)','#00ff88'],
    ['rgba(0,255,136,0.2)','#3b82f6'],
    ['rgba(245,158,11,0.2)','#f59e0b'],
    ['rgba(139,92,246,0.2)','#8b5cf6'],
    ['rgba(239,68,68,0.2)','#ef4444'],
    ['rgba(148,163,184,0.2)','#94a3b8'],
  ];
  const i = ((name||'?').charCodeAt(0) - 65) % colors.length;
  return colors[Math.max(0,i)];
}}

// ── STATUSBAR ─────────────────────────────────────────────────────────────────
function updateStatusBar(opts) {{
  const uid = document.getElementById('stat-uid');
  const lab = document.getElementById('stat-lab');
  const spam = document.getElementById('stat-spam');
  const status = document.getElementById('stat-status');

  if (uid) uid.textContent = userId;
  if (lab) {{
    lab.textContent = activeLabId || 'none';
    lab.className = 'sb-v ' + (activeLabId ? 'accent' : '');
  }}
  if (spam && lastSpamScore !== null) {{
    spam.textContent = lastSpamScore + '/100';
    spam.className = 'sb-v ' + (lastSpamScore < 35 ? 'accent' : lastSpamScore < 60 ? 'warn' : 'danger');
  }}
  if (status && opts && opts.status) {{
    status.textContent = opts.status;
    status.className = 'sb-v ' + (opts.cls || '');
  }}
}}

function updateToolbarUser() {{
  const el = document.getElementById('hdr-sender');
  if (el) el.textContent = attackerEmail;
  const av = document.getElementById('sidebar-avatar');
  if (av) av.textContent = (attackerEmail||'AT').slice(0,2).toUpperCase();
  const un = document.getElementById('sidebar-username');
  if (un) un.textContent = attackerEmail || 'attacker@kali.local';
}}

// ── TABS ──────────────────────────────────────────────────────────────────────
function showTab(tab) {{
  currentTab = tab;
  ['compose','sent','inbox'].forEach(t => {{
    document.getElementById('tab-' + t).classList.toggle('active', t === tab);
    document.getElementById('pane-' + t).classList.toggle('active', t === tab);
  }});
  ['compose','inbox','sent','campaign'].forEach(t => {{
    const btn = document.getElementById('nav-' + t);
    if (btn) btn.classList.toggle('active', t === tab);
  }});

  const listPanel   = document.getElementById('list-panel');
  const listCompose = document.getElementById('list-compose-hint');
  const listSent    = document.getElementById('sent-list-view');
  const listInbox   = document.getElementById('inbox-list-view');
  const listTitle   = document.getElementById('list-panel-title');

  listCompose.style.display = 'none';
  listSent.style.display    = 'none';
  listInbox.style.display   = 'none';

  if (tab === 'compose' || tab === 'campaign') {{
    listPanel.style.display = 'none';
  }} else if (tab === 'sent') {{
    listPanel.style.display = 'flex';
    listSent.style.display = 'block';
    listTitle.textContent = 'Sent';
    viewingSentId = null; renderSentPane();
  }} else if (tab === 'inbox') {{
    listPanel.style.display = 'flex';
    listInbox.style.display = 'block';
    listTitle.textContent = 'Inbox';
    viewingInboxId = null; renderInboxPane(); loadInbox();
  }}
  updateStatusBar({{status: tab.charAt(0).toUpperCase() + tab.slice(1), cls: 'accent'}});
}}

// ── MODE TOGGLE ───────────────────────────────────────────────────────────────
function setMode(mode) {{
  composeMode = mode;
  document.getElementById('mode-single').classList.toggle('active', mode === 'single');
  document.getElementById('mode-mass').classList.toggle('active', mode === 'mass');
  document.getElementById('single-to-row').style.display = mode === 'single' ? '' : 'none';
  document.getElementById('campaign-extras').classList.toggle('show', mode === 'mass');
  const btn = document.getElementById('send-btn');
  btn.className = 'btn-send ' + (mode === 'mass' ? 'mass' : 'single');
  btn.innerHTML = mode === 'mass'
    ? '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> Deploy Campaign'
    : '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg> Send';
  if (mode === 'mass') document.getElementById('gate').classList.remove('show');
  else refreshLabStatus();
  document.getElementById('campaign-result').classList.remove('show');
  document.getElementById('status-msg').textContent = '';
}}

// ── IDENTITY ──────────────────────────────────────────────────────────────────
async function loadIdentity() {{
  try {{
    const r = await fetch(API + '/api/attacker/profile?user_id=' + userId);
    if (!r.ok) return;
    const d = await r.json();
    if (d.attacker_email) {{ attackerEmail = d.attacker_email; setIdentityDisplay(attackerEmail); }}
  }} catch(e) {{}}
}}

function setIdentityDisplay(email) {{
  document.getElementById('from-field').value = email;
  identityOriginal = email;
  updateToolbarUser();
}}

function toggleIdentityPopover() {{
  const pop = document.getElementById('identity-popover');
  if(pop.style.display === 'none') {{
    document.getElementById('identity-input').value = attackerEmail || '';
    pop.style.display = 'block';
    setTimeout(() => document.getElementById('identity-input').focus(), 50);
  }} else {{
    pop.style.display = 'none';
  }}
}}

function closeIdentityPopover() {{
  document.getElementById('identity-popover').style.display = 'none';
}}

async function applyIdentityFromSidebar() {{
  const v = (document.getElementById('identity-input').value || '').trim().toLowerCase();
  if(!v) return;
  document.getElementById('from-field').value = v;
  await saveIdentity();
  closeIdentityPopover();
}}

async function saveIdentity() {{
  const fld = document.getElementById('from-field');
  const v = (fld.value || '').trim().toLowerCase();
  if (!v || v === attackerEmail) return;
  try {{
    const r = await fetch(API + '/api/attacker/profile', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{user_id: userId, attacker_email: v}})
    }});
    const d = await r.json();
    if (!r.ok) {{
      const msg = (d.detail && d.detail.message) || (typeof d.detail === 'string' ? d.detail : 'Rejected');
      fld.style.borderColor = '#ef4444';
      document.getElementById('status-msg').className = 'status err';
      document.getElementById('status-msg').textContent = msg;
      setTimeout(() => {{ fld.style.borderColor = ''; }}, 2000);
      return;
    }}
    attackerEmail = d.attacker_email;
    identityOriginal = attackerEmail;
    updateToolbarUser();
    fld.style.borderColor = '#00ff88';
    setTimeout(() => {{ fld.style.borderColor = ''; }}, 1500);
  }} catch(e) {{
    document.getElementById('status-msg').className = 'status err';
    document.getElementById('status-msg').textContent = 'Save failed.';
  }}
}}

// ── FROM HINT ─────────────────────────────────────────────────────────────────
function hintFrom() {{
  const v = (document.getElementById('from-field').value || '').trim().toLowerCase();
  const h = document.getElementById('from-hint');
  if (!v) {{ h.className='from-hint'; h.textContent='Tip: spoof a lookalike domain. Real brand domains are rejected by the mail gateway.'; return; }}
  const m = v.match(/^[^@ ]+@([a-z0-9.-]+[.][a-z]{{2,}})$/);
  if (!m) {{ h.className='from-hint bad'; h.textContent='Malformed sender -- use name@domain.tld.'; return; }}
  const domain = m[1];
  if (BRANDS.has(domain)) {{ h.className='from-hint bad'; h.textContent='Protected brand domain -- mail gateway will reject. Use a lookalike.'; return; }}
  const toVal = (document.getElementById('to-field')||{{}}).value||'';
  const tm = toVal.match(/@([a-z0-9.-]+[.][a-z]{{2,}})/i);
  const targetDomain = tm ? tm[1].toLowerCase() : '';
  if (targetDomain && domain === targetDomain) {{ h.className='from-hint ok'; h.textContent='Domain matches target -- low suspicion.'; return; }}
  if (targetDomain && domain !== targetDomain) {{ h.className='from-hint warn'; h.textContent='Domain mismatch -- increases spam score.'; return; }}
  if (/[0-9]/.test(domain.split('.')[0]) || /rn/.test(domain)) {{ h.className='from-hint warn'; h.textContent='Lookalike detected -- vigilant targets may notice.'; return; }}
  h.className='from-hint ok'; h.textContent='Sender looks plausible.';
}}

// ── TEMPLATES ─────────────────────────────────────────────────────────────────
const TEMPLATES = {{
  it_security: {{
    subject: 'ACTION REQUIRED: Password Expiry Notice',
    body: "Dear Employee,\\n\\nOur IT Security team has detected that your account password will expire within the next 24 hours. To avoid losing access to company systems, you must reset your password immediately.\\n\\nClick the link below to verify your identity and set a new password:\\n\\n[INSERT RESET LINK HERE]\\n\\nIf you do not act within 24 hours, your account will be suspended and you will need to contact IT support to regain access.\\n\\nIT Security Team"
  }},
  hr_announce: {{
    subject: 'HR Update: New Benefits Portal',
    body: "Dear Team,\\n\\nHR has migrated our benefits and policy portal to a new system. All employees are required to log in and verify their details by end of business Friday.\\n\\nPlease log in to the new HR portal to complete your acknowledgement:\\n\\n[INSERT HR PORTAL LINK HERE]\\n\\nFailure to complete verification by the deadline may affect your employment record.\\n\\nHuman Resources Department"
  }},
  ceo_request: {{
    subject: 'Urgent: Immediate Action Required',
    body: "Hi,\\n\\nI need you to handle something urgent and confidential for me. I am currently in a meeting and cannot be reached by phone.\\n\\nPlease process an urgent wire transfer as discussed. This needs to be completed today before 3pm. Reply to confirm you received this and I will send account details.\\n\\nDo not discuss this with anyone until I get back to you.\\n\\nThanks"
  }},
  sys_alert: {{
    subject: 'Security Alert: Suspicious Login Detected',
    body: "Security Alert\\n\\nWe detected an unusual sign-in attempt on your account from an unrecognized device.\\n\\nLocation: Eastern Europe\\nDevice: Unknown\\nTime: Today at 02:47 AM\\n\\nIf this was not you, your account may be compromised. Click below immediately to secure your account:\\n\\n[INSERT VERIFY LINK HERE]\\n\\nIf you do not verify within 2 hours, your account will be temporarily suspended for your protection.\\n\\nSecurity Operations Center"
  }}
}};

function applyTemplate(key) {{
  const t = TEMPLATES[key];
  if (!t) return;
  const subj = document.getElementById('subject-field');
  const body = document.getElementById('body-field');
  if (subj) subj.value = t.subject;
  if (body) body.value = t.body;
  updateSpamIndicator();
  hintFrom();
}}

// ── CONTACTS ──────────────────────────────────────────────────────────────────
async function loadContacts() {{
  try {{
    const labParam = activeLabId ? '?lab_id=' + encodeURIComponent(activeLabId) : '';
    const r = await fetch('http://127.0.0.1:9004/api/contacts' + labParam);
    if (!r.ok) return;
    const d = await r.json();
    allContacts = d.contacts || [];
    renderNpcList();
    renderQuickTargets();
  }} catch(e) {{}}
}}

function renderQuickTargets() {{
  const el = document.getElementById('quick-target-list');
  if (!el || !allContacts.length) return;
  el.innerHTML = allContacts.slice(0, 10).map(c => {{
    const [bg, color] = avatarColor(c.name);
    return `<div class="contact-item"
      onclick="document.getElementById('to-field').value='${{esc(c.email)}}';showTab('compose');updateSpamIndicator();">
      <div class="contact-avatar" style="background:${{bg}};color:${{color}}">${{c.name.slice(0,2).toUpperCase()}}</div>
      <div class="contact-info">
        <div class="contact-name">${{esc(c.name)}}</div>
        <div class="contact-email">${{esc(c.email)}}</div>
      </div>
      <div class="contact-company">${{esc(c.company||'')}}</div>
    </div>`;
  }}).join('');
  const lc = document.getElementById('list-panel-count');
  if (lc) lc.textContent = allContacts.length;
}}

function renderNpcList() {{
  const list = document.getElementById('npc-list');
  if (!list) return;
  if (!allContacts.length) {{ list.innerHTML = '<div class="npc-loading">No contacts found.</div>'; return; }}
  list.innerHTML = allContacts.map(c =>
    `<label class="npc-item">
      <input type="checkbox" class="npc-cb" value="${{esc(c.email)}}" data-gullibility="${{c.gullibility || 50}}">
      <span class="npc-name">${{esc(c.name)}}</span>
      <span class="npc-email">${{esc(c.email)}}</span>
      <span class="npc-co">${{esc(c.company)}}</span>
    </label>`
  ).join('');
  updateNpcCount();
}}

function updateNpcCount() {{
  const n = document.querySelectorAll('.npc-cb:checked').length;
  const el = document.getElementById('npc-count');
  if (el) el.textContent = n + ' selected';
}}

// ── SPAM SCORE ────────────────────────────────────────────────────────────────
function calcSpamScore(from, subject, body) {{
  let score = 0;
  const dm = (from||'').match(/@([a-z0-9.-]+\.[a-z]{{2,}})/i);
  const domain = dm ? dm[1].toLowerCase() : '';
  if (BRANDS.has(domain)) {{ score += 80; }}
  else if (!domain) {{ score += 30; }}
  else {{
    if (/[0-9]/.test(domain.split('.')[0])) score += 12;
    if (/rn|vv|cl/.test(domain)) score += 8;
    if (/security|secure|portal|login|microsoft|office|cloud|helpdesk|admin/.test(domain)) score += 18;
    if (/support|it-|noreply|alert/.test(domain)) score += 12;
  }}
  const subj = (subject||'').toLowerCase();
  if (!subj) score += 20;
  if (/[A-Z]{{4,}}/.test(subject||'')) score += 15;
  if (((subject||'').match(/!/g)||[]).length > 1) score += 10;
  if (/free|win|prize|congratul|lottery/.test(subj)) score += 28;
  if (/urgent|action required|verify|locked|suspended|expire|security alert|warning|unusual/.test(subj)) score += 18;
  if (/password|account|sign.?in|login|access/.test(subj)) score += 12;
  const b = (body||'').toLowerCase();
  if (!b || b.length < 40) score += 20;
  const urlCnt = (body||'').match(/https?:\/\//gi)||[];
  if (urlCnt.length === 1) score += 5;
  if (urlCnt.length > 2) score += 18;
  if (/click here now|act immediately|call us now/.test(b)) score += 12;
  if (/urgent|immediately|24 hours|1 hour|2 hours|expire|locked|suspended|verify|confirm your/.test(b)) score += 15;
  if (/dear (user|customer|account holder)/.test(b)) score += 10;
  if (/\bkind regards\b|\bbest regards\b|\bsincerely\b/.test(b)) score -= 8;
  if (/\bplease contact\b|\bfeel free\b|\bthank you for\b/.test(b)) score -= 5;
  score = Math.max(0, Math.min(100, Math.round(score)));
  let color, label;
  if (score < 35)      {{ color='#00ff88'; label='Low -- likely to deliver to most inboxes'; }}
  else if (score < 60) {{ color='#f59e0b'; label='Medium -- gullible targets only'; }}
  else                 {{ color='#ef4444'; label='High -- most spam filters will catch this'; }}
  return {{ score, color, label }};
}}

function updateSpamIndicator() {{
  const from    = (document.getElementById('from-field')||{{}}).value||'';
  const subject = (document.getElementById('subject-field')||{{}}).value||'';
  const body    = (document.getElementById('body-field')||{{}}).value||'';

  const scoreNum   = document.getElementById('cs-score-num');
  const scoreLabel = document.getElementById('cs-score-label');
  const barFill    = document.getElementById('cs-bar-fill');
  const checksEl   = document.getElementById('cs-checks');

  if (!from && !subject && !body) return;
  const r = calcSpamScore(from, subject, body);
  lastSpamScore = r.score;

  if (scoreNum)   {{ scoreNum.textContent = r.score; scoreNum.style.color = r.color; }}
  if (scoreLabel) {{ scoreLabel.textContent = r.label; scoreLabel.style.color = r.color; }}
  if (barFill)    {{ barFill.style.width = r.score + '%'; barFill.style.background = r.color; }}

  if (checksEl) {{
    const checks = [];
    const dm = from.match(/@([a-z0-9.-]+\.[a-z]{{2,}})/i);
    const fromDomain = dm ? dm[1].toLowerCase() : '';
    const toVal = (document.getElementById('to-field')||{{}}).value||'';
    const tm = toVal.match(/@([a-z0-9.-]+\.[a-z]{{2,}})/i);
    if (fromDomain) {{
      if (BRANDS.has(fromDomain)) checks.push({{cls:'bad', text:'SPF: brand domain blocked'}});
      else checks.push({{cls:'good', text:'SPF: custom domain passes'}});
    }} else {{
      checks.push({{cls:'bad', text:'SPF: no sender domain'}});
    }}
    if (fromDomain && !BRANDS.has(fromDomain)) checks.push({{cls:'good', text:'DKIM: not required'}});
    else if (BRANDS.has(fromDomain)) checks.push({{cls:'bad', text:'DKIM: signature mismatch'}});
    else checks.push({{cls:'neutral', text:'DKIM: awaiting sender'}});
    if (/urgent|action required|verify|suspended/.test((subject||'').toLowerCase()))
      checks.push({{cls:'bad', text:'Subject tone: urgency detected'}});
    else if (subject) checks.push({{cls:'good', text:'Subject tone: neutral'}});
    else checks.push({{cls:'neutral', text:'Subject tone: no subject'}});
    const linkCnt = ((body||'').match(/https?:\/\//gi)||[]).length;
    if (linkCnt > 2) checks.push({{cls:'bad', text:'Link count: ' + linkCnt + ' URLs'}});
    else if (linkCnt === 1) checks.push({{cls:'neutral', text:'Link count: 1 URL'}});
    else checks.push({{cls:'good', text:'Link count: no URLs'}});
    if (/immediately|24 hours|expire|locked|suspended/.test((body||'').toLowerCase()))
      checks.push({{cls:'bad', text:'Urgency: keywords detected'}});
    else checks.push({{cls:'good', text:'Urgency: not flagged'}});

    checksEl.innerHTML = '<div class="qp-check-heading">Checks</div>' + checks.map(c =>
      `<div class="qp-check-item ${{c.cls}}"><span class="qp-check-dot"></span><span class="qp-check-text">${{c.text}}</span></div>`
    ).join('');
  }}

  // Legacy hidden elements
  const scoreEl = document.getElementById('si-score');
  const fillEl  = document.getElementById('si-fill');
  const hintEl  = document.getElementById('si-hint');
  if (scoreEl) {{ scoreEl.textContent = r.score; scoreEl.style.color = r.color; }}
  if (fillEl)  {{ fillEl.style.width = r.score + '%'; fillEl.style.background = r.color; }}
  if (hintEl)  {{ hintEl.textContent = r.label; hintEl.style.color = r.color; }}

  updateStatusBar({{status: currentTab.charAt(0).toUpperCase() + currentTab.slice(1), cls: 'accent'}});
}}

// ── LAB STATUS / GATE ─────────────────────────────────────────────────────────
async function refreshLabStatus() {{
  if (!activeLabId || composeMode === 'mass') return;
  try {{
    const r = await fetch(API + '/api/labs/' + encodeURIComponent(activeLabId) + '/progress?user_id=' + userId);
    if (!r.ok) return;
    const d = await r.json();
    labStatus = d.status;
    if (labStatus === 'failed') {{
      if (!gameOverDismissed) showGameOver(d.failure_reason, d.failed_persona);
      document.getElementById('gate').classList.remove('show');
    }} else if (labStatus === 'not_started') {{
      document.getElementById('gate').classList.add('show');
      document.getElementById('gate-btn').style.display = 'block';
      document.getElementById('gate-btn').disabled = false;
      document.getElementById('gate-btn').textContent = 'Start Simulation';
    }} else {{
      document.getElementById('gate').classList.remove('show');
      document.getElementById('gameover').classList.remove('show');
    }}
    updateStatusBar({{status: (labStatus||'unknown').charAt(0).toUpperCase()+(labStatus||'unknown').slice(1), cls: labStatus === 'failed' ? 'danger' : labStatus === 'not_started' ? 'warn' : 'accent'}});
  }} catch(e) {{}}
}}

async function startSimulation() {{
  if (!activeLabId) {{ document.getElementById('gate').classList.remove('show'); return; }}
  const btn = document.getElementById('gate-btn');
  btn.disabled = true; btn.textContent = 'Initializing...';
  try {{
    const r = await fetch(API + '/api/labs/' + encodeURIComponent(activeLabId) + '/start?user_id=' + userId, {{method:'POST'}});
    if (r.ok) {{ labStatus = 'in_progress'; document.getElementById('gate').classList.remove('show'); }}
    else {{ btn.disabled = false; btn.textContent = 'Start Simulation'; }}
  }} catch(e) {{ btn.disabled = false; btn.textContent = 'Start Simulation'; }}
}}

function showGameOver(reason, who) {{
  gameOverDismissed = false;
  document.getElementById('go-reason').textContent = reason || 'The target recognized the attack.';
  document.getElementById('go-who').textContent = who ? 'Detected by ' + who : '';
  document.getElementById('gameover').classList.add('show');
}}

async function resetLab() {{
  if (!activeLabId || !confirm('Reset this lab? All history will be wiped.')) return;
  try {{
    await fetch(API + '/api/labs/' + encodeURIComponent(activeLabId) + '/reset?user_id=' + userId, {{method:'POST'}});
    sentEmails = []; inboxItems = [];
    renderSentPane(); renderInboxPane();
    gameOverDismissed = false;
    document.getElementById('gameover').classList.remove('show');
    await refreshLabStatus();
  }} catch(e) {{ alert('Reset failed.'); }}
}}

// ── SEND ──────────────────────────────────────────────────────────────────────
function handleSend() {{
  if (composeMode === 'mass') launchCampaign();
  else sendEmail();
}}

async function sendEmail() {{
  const toAddr  = (document.getElementById('to-field').value || '').trim().toLowerCase();
  const from    = (document.getElementById('from-field').value || '').trim();
  const subject = (document.getElementById('subject-field').value || '').trim();
  const body    = (document.getElementById('body-field').value || '').trim();
  const statusEl = document.getElementById('status-msg');
  const btn = document.getElementById('send-btn');

  const toInput = document.getElementById('to-field');
  if (!toAddr) {{ toInput.classList.add('err'); statusEl.className='status err'; statusEl.textContent='Enter a recipient address.'; return; }}
  toInput.classList.remove('err');
  if (!body) {{ statusEl.className='status err'; statusEl.textContent='Body cannot be empty.'; return; }}

  btn.disabled = true;
  statusEl.className = 'status'; statusEl.innerHTML = '<span class="spinner"></span> Sending...';
  updateStatusBar({{status: 'Sending', cls: 'warn'}});

  try {{
    const rr = await fetch(API + '/api/email/resolve?email=' + encodeURIComponent(toAddr));
    if (!rr.ok) {{
      statusEl.className='status err'; statusEl.textContent='Delivery failed: address not found.';
      btn.disabled = false; updateStatusBar({{status: 'Blocked', cls: 'danger'}}); return;
    }}
    const contact = await rr.json();

    const spSingle = calcSpamScore(from, subject, body);
    const spThreshold = 50 + (contact.gullibility || 50) * 0.4;
    if (spSingle.score > spThreshold) {{
      const now = new Date().toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}});
      sentEmails.unshift({{id:sentCounter++, to:toAddr, from, subject, body, time:now, status:'blocked'}});
      renderSentPane();
      statusEl.className='status err';
      statusEl.textContent='[BLOCKED] Spam filter ('+spSingle.score+'/100, threshold '+Math.round(spThreshold)+') -- '+spSingle.label;
      btn.disabled = false; updateStatusBar({{status: 'Spam Blocked', cls: 'danger'}}); return;
    }}
    if (!activeLabId) {{ activeLabId = contact.lab_id; updateStatusBar({{}}); refreshLabStatus(); }}

    const res = await fetch(API + '/api/chat', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{user_id: userId, lab_id: contact.lab_id, persona_id: contact.persona_id,
                            message: body, from_email: from, channel: 'email'}})
    }});

    if (res.status === 409) {{
      statusEl.className='status err'; statusEl.textContent="Lab not started -- start the simulation first.";
      labStatus = 'not_started';
      document.getElementById('gate').classList.add('show');
      document.getElementById('gate-btn').style.display = 'block';
      btn.disabled = false; return;
    }}
    if (res.status === 400) {{
      const err = await res.json().catch(()=>({{}}));
      const msg = (err.detail && err.detail.message) || 'Mail gateway rejected sender.';
      statusEl.className='status err'; statusEl.textContent=msg;
      document.getElementById('from-hint').className='from-hint bad';
      document.getElementById('from-hint').textContent=msg;
      btn.disabled = false; return;
    }}

    const data = await res.json();
    const now = new Date().toLocaleTimeString([], {{hour:'2-digit',minute:'2-digit'}});
    const sentId = sentCounter++;
    sentEmails.unshift({{id: sentId, to: toAddr, from, subject, body, time: now, status: 'delivered'}});
    renderSentPane();
    document.getElementById('body-field').value = '';
    document.getElementById('subject-field').value = '';

    if (data.response && !data.voicemail) addVirtualInboxItem(contact, data.response, from, toAddr, subject);
    if (data.mission_failed) {{ showGameOver(data.fail_reason, data.failed_persona || contact.name); btn.disabled = false; return; }}
    if (data.voicemail) addVirtualInboxItem(contact, '(Auto-reply: ' + (data.work_status || 'out of office') + ')', from, toAddr, 'Auto-reply: ' + (subject || '(no subject)'));
    if (data.delivered_email) {{
      await loadInbox();
      const nb = document.getElementById('nav-inbox');
      if (nb) {{ nb.style.background='rgba(0,255,136,0.15)'; setTimeout(()=>{{ nb.style.background=''; }}, 900); }}
    }}

    const siteMatch = body.match(/\/([a-f0-9]{{8}})(?:[?&#\s\/]|$)/);
    if (siteMatch) {{
      try {{
        await fetch(API + '/api/phish/campaign', {{
          method: 'POST', headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{user_id: userId, site_id: siteMatch[1],
                                from_email: from, subject, body,
                                target_emails: [toAddr], targeted: true,
                                lab_id: activeLabId || null}})
        }});
      }} catch(e) {{}}
    }}

    statusEl.className = 'status ok';
    statusEl.textContent = data.voicemail ? 'Sent -- target offline' : 'Sent -- check Inbox for reply';
    updateStatusBar({{status: 'Delivered', cls: 'accent'}});
  }} catch(e) {{
    statusEl.className='status err'; statusEl.textContent='Connection error — ' + (e && e.message ? e.message : 'backend unreachable') + '. Try again.';
    updateStatusBar({{status: 'Error', cls: 'danger'}});
  }}
  btn.disabled = false;
}}

// ── MASS CAMPAIGN ─────────────────────────────────────────────────────────────
async function launchCampaign() {{
  const from    = (document.getElementById('from-field').value || '').trim();
  const subject = (document.getElementById('subject-field').value || '').trim();
  const body    = (document.getElementById('body-field').value || '').trim();
  const statusEl = document.getElementById('status-msg');
  const btn = document.getElementById('send-btn');

  if (!from || !subject || !body) {{
    statusEl.className='status err'; statusEl.textContent='Fill in From, Subject and Body.'; return;
  }}

  const selectedCbs = Array.from(document.querySelectorAll('.npc-cb:checked'));
  if (!selectedCbs.length) {{
    statusEl.className='status err'; statusEl.textContent='Select at least one recipient.'; return;
  }}

  const spam = calcSpamScore(from, subject, body);
  const delivered = [], blocked = [];
  selectedCbs.forEach(cb => {{
    const g = parseInt(cb.dataset.gullibility) || 50;
    const threshold = 50 + g * 0.4;
    (spam.score < threshold ? delivered : blocked).push(cb.value);
  }});

  const now = new Date().toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}});

  if (!delivered.length) {{
    sentEmails.unshift({{id:sentCounter++,
      to:`[Campaign] 0 delivered \xb7 ${{blocked.length}} blocked`,
      from, subject, body, time:now, status:'blocked', deliveredCount:0, blockedCount:blocked.length}});
    renderSentPane();
    statusEl.className='status err';
    statusEl.textContent=`[BLOCKED] All ${{blocked.length}} targets spam-blocked (score ${{spam.score}}/100) -- lower the score.`;
    updateStatusBar({{status: 'All Blocked', cls: 'danger'}});
    return;
  }}

  btn.disabled = true;
  statusEl.className='status'; statusEl.innerHTML='<span class="spinner"></span> Launching campaign...';
  updateStatusBar({{status: 'Deploying', cls: 'warn'}});
  document.getElementById('campaign-result').classList.remove('show');

  const siteMatch = body.match(/\/([a-f0-9]{{8}})(?:[?&#\s\/]|$)/);
  const siteId = siteMatch ? siteMatch[1] : null;

  try {{
    if (siteId) {{
      const r = await fetch(API + '/api/phish/campaign', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{user_id: userId, site_id: siteId, from_email: from,
                              subject, body, target_emails: delivered, targeted: false,
                              lab_id: activeLabId || null}})
      }});
      const d = await r.json();
      if (!r.ok) {{ statusEl.className='status err'; statusEl.textContent=(d.detail||'Campaign error'); btn.disabled=false; return; }}
      sentEmails.unshift({{id:sentCounter++,
        to:`[Campaign] ${{delivered.length}} delivered \xb7 ${{blocked.length}} blocked`,
        from, subject, body, time:now, status:'delivered', deliveredCount:delivered.length, blockedCount:blocked.length}});
      renderSentPane();
      renderCampaignResult(d, blocked.length);
      statusEl.className='status ok';
      statusEl.textContent=`${{delivered.length}} delivered \xb7 ${{blocked.length}} spam-blocked \xb7 ${{d.new_clicks}} hits`;
      updateStatusBar({{status: 'Campaign Sent', cls: 'accent'}});
    }} else {{
      let sent = 0;
      await Promise.all(delivered.map(async email => {{
        try {{
          const rr = await fetch(API + '/api/email/resolve?email=' + encodeURIComponent(email));
          if (!rr.ok) return;
          const contact = await rr.json();
          if (!activeLabId) activeLabId = contact.lab_id;
          const res = await fetch(API + '/api/chat', {{
            method:'POST', headers:{{'Content-Type':'application/json'}},
            body: JSON.stringify({{user_id:userId, lab_id:contact.lab_id,
              persona_id:contact.persona_id, message:body, from_email:from, channel:'email'}})
          }});
          if (!res.ok) return;
          const data = await res.json();
          if (data.response && !data.voicemail) addVirtualInboxItem(contact, data.response, from, email, subject);
          sent++;
        }} catch(e) {{}}
      }}));
      sentEmails.unshift({{id:sentCounter++,
        to:`[Campaign] ${{sent}} delivered \xb7 ${{blocked.length}} blocked`,
        from, subject, body, time:now, status:'delivered', deliveredCount:sent, blockedCount:blocked.length}});
      renderSentPane();
      document.getElementById('campaign-result').classList.remove('show');
      statusEl.className='status ok';
      statusEl.textContent=`${{sent}} delivered \xb7 ${{blocked.length}} spam-blocked`;
      updateStatusBar({{status: 'Campaign Sent', cls: 'accent'}});
    }}
  }} catch(e) {{
    statusEl.className='status err'; statusEl.textContent='Connection error.';
    updateStatusBar({{status: 'Error', cls: 'danger'}});
  }}
  btn.disabled = false;
}}

function renderCampaignResult(d, blockedCount) {{
  const wrap = document.getElementById('campaign-result');
  const showFragments = d.show_flag_fragments !== false;

  let flagSection = '';
  if (showFragments) {{
    const pieces = d.pieces_collected || [];
    const slots = [0,1,2].map(i =>
      `<div class="fp-slot ${{pieces[i] ? 'filled' : ''}}">${{pieces[i] || '[ ' + (i+1) + ' ]'}}</div>`
    ).join('');
    const flagDone = d.flag_complete ? `<div class="flag-done show">FLAG ASSEMBLED: ${{esc(d.full_flag)}}</div>` : '';
    flagSection = `<div class="flag-pieces">${{slots}}</div>${{flagDone}}`;
  }}

  let tableHtml = '';
  if (d.results && d.results.length) {{
    const clickedResults = d.results.filter(r => r.clicked !== false);
    const notClickedResults = d.results.filter(r => r.clicked === false && !(r.visit_story && r.visit_story.includes('[IMMUNE]')));

    if (clickedResults.length > 0) {{
      const hasStory = clickedResults.some(r => r.visit_story);
      const storyCol = hasStory ? '<th>Reaction</th>' : '';
      const rows = clickedResults.map(r =>
        `<tr>
          <td>${{esc(r.persona)}}</td>
          <td>${{esc(r.company)}}</td>
          <td>${{esc(r.email)}}</td>
          <td>${{esc(r.password || '—')}}</td>
          ${{hasStory ? `<td style="color:var(--text-dim);font-size:10px;max-width:200px">${{esc(r.visit_story || '')}}</td>` : ''}}
        </tr>`
      ).join('');
      tableHtml = `<table class="cr-table"><tr><th>NPC</th><th>Company</th><th>Username</th><th>Password</th>${{storyCol}}</tr>${{rows}}</table>`;
    }}

    if (!showFragments && notClickedResults.length > 0) {{
      const rejRows = notClickedResults.slice(0, 5).map(r =>
        `<tr style="opacity:0.5"><td colspan="5" style="font-size:10px;color:var(--text-dim)">${{esc(r.visit_story || r.persona + ': did not click')}}</td></tr>`
      ).join('');
      tableHtml += (tableHtml ? '<br>' : '') + `<table class="cr-table">${{rejRows}}</table>`;
    }}
  }}

  if (!tableHtml) {{
    tableHtml = '<div style="font-size:12px;color:var(--text-dim);text-align:center;padding:8px 0">No new credentials this round -- improve page quality or email urgency.</div>';
  }}

  const blockedHtml = blockedCount ? `<div class="cr-blocked">${{blockedCount}} target${{blockedCount>1?'s':''}} blocked by spam filter before delivery</div>` : '';
  wrap.innerHTML = `
    <div class="cr-stat">Delivered <span>${{d.sent_to}}</span> &middot; <span>${{d.new_clicks}}</span> new credentials &middot; <span>${{d.total_harvests}}</span> total</div>
    ${{blockedHtml}}${{flagSection}}${{tableHtml}}`;
  wrap.classList.add('show');
}}

// ── SENT LIST ─────────────────────────────────────────────────────────────────
function renderSentPane() {{
  const listEl = document.getElementById('sent-list-view');
  const viewEl = document.getElementById('sent-viewer');
  if (viewingSentId !== null) {{
    listEl.style.display = 'none'; viewEl.style.display = 'flex';
    const em = sentEmails.find(e => e.id === viewingSentId);
    if (!em) {{ viewingSentId = null; renderSentPane(); return; }}
    document.getElementById('sv-subj').textContent = em.subject || '(no subject)';
    document.getElementById('sv-from').textContent = em.from;
    document.getElementById('sv-to').textContent = em.to;
    document.getElementById('sv-body').textContent = em.body;
    document.getElementById('sv-ts').textContent = 'Sent ' + em.time;
  }} else {{
    viewEl.style.display = 'none'; listEl.style.display = 'block';
    const empty = document.getElementById('sent-empty');
    if (sentEmails.length === 0) {{ empty.style.display = 'block'; return; }}
    empty.style.display = 'none';
    let html = '';
    sentEmails.forEach(em => {{
      const badge = em.status === 'delivered'
        ? `<span class="ms-ok">Delivered${{em.deliveredCount ? ' '+em.deliveredCount : ''}}</span>`
        : em.status === 'blocked' ? `<span class="ms-spam">Blocked</span>` : '';
      const [bg, color] = avatarColor(em.to || '?');
      html += `<div class="mail-item ${{viewingSentId===em.id?'active':''}}" data-id="${{em.id}}">
        <div class="mail-item-row">
          <div class="sender-avatar" style="background:${{bg}};color:${{color}};font-size:13px;font-weight:700">${{(em.to||'?').slice(0,2).toUpperCase()}}</div>
          <div class="mi-meta">
            <div class="mi-who">${{esc(em.to)}} ${{badge}}</div>
          </div>
          <div class="mi-time">${{esc(em.time)}}</div>
        </div>
        <div class="mi-subj">${{esc(em.subject||'(no subject)')}}</div>
      </div>`;
    }});
    listEl.innerHTML = empty.outerHTML + html;
  }}
  const badge = document.getElementById('sent-badge');
  if (sentEmails.length > 0) {{ badge.style.display='inline-flex'; badge.textContent=sentEmails.length; }}
  else badge.style.display = 'none';
  const lc = document.getElementById('list-panel-count');
  if (lc && currentTab === 'sent') lc.textContent = sentEmails.length;
}}

function openSentMail(id) {{ viewingSentId = id; renderSentPane(); }}

// ── INBOX ─────────────────────────────────────────────────────────────────────
async function loadInbox() {{
  try {{
    const url = API + '/api/attacker/inbox?user_id=' + userId + (activeLabId ? '&lab_id=' + encodeURIComponent(activeLabId) : '');
    const r = await fetch(url);
    if (!r.ok) return;
    const d = await r.json();
    const virtuals = inboxItems.filter(i => i.virtual);
    inboxItems = [...virtuals, ...(d.inbox || d.items || [])];
    renderInboxPane(); updateInboxBadge();
  }} catch(e) {{}}
}}

function updateInboxBadge() {{
  const badge = document.getElementById('inbox-badge');
  const unread = inboxItems.filter(i => !i.read).length;
  if (unread > 0) {{ badge.style.display='inline-flex'; badge.textContent=unread; }}
  else badge.style.display = 'none';
}}

function renderInboxPane() {{
  const listEl = document.getElementById('inbox-list-view');
  const viewEl = document.getElementById('inbox-viewer');
  if (viewingInboxId !== null) {{
    listEl.style.display = 'none'; viewEl.style.display = 'flex';
    const item = inboxItems.find(i => String(i.id) === String(viewingInboxId));
    if (!item) {{ viewingInboxId = null; renderInboxPane(); return; }}
    document.getElementById('iv-subj').textContent = item.subject || '(no subject)';
    document.getElementById('iv-from').textContent = item.from_name ? item.from_name + ' <' + item.from_email + '>' : (item.from_email||'');
    document.getElementById('iv-to').textContent = item.to_email || attackerEmail;
    document.getElementById('iv-body').textContent = item.body || '';
    const flagEl = document.getElementById('iv-flag');
    if (item.flag_value) {{ flagEl.style.display='block'; flagEl.textContent='FLAG: '+item.flag_value; }}
    else flagEl.style.display='none';
    let ts=''; try {{ ts=new Date(item.received_at).toLocaleString(); }} catch(e){{}}
    document.getElementById('iv-ts').textContent='Received '+ts;
  }} else {{
    viewEl.style.display='none'; listEl.style.display='block';
    const empty=document.getElementById('inbox-empty');
    if (inboxItems.length===0) {{ empty.style.display='block'; return; }}
    empty.style.display='none';
    let html='';
    inboxItems.forEach(it => {{
      let ts=''; try {{ ts=new Date(it.received_at).toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}}); }} catch(e){{}}
      const flagBadge = it.flag_value ? '<span class="mi-flag">FLAG</span>' : '';
      const senderName = it.from_name||it.from_email||'?';
      const [bg, color] = avatarColor(senderName);
      html += `<div class="mail-item ${{String(viewingInboxId)===String(it.id)?'active':''}} ${{it.read?'':'unread'}}" data-id="${{it.id}}">
        <div class="mail-item-row">
          <div class="sender-avatar" style="background:${{bg}};color:${{color}};font-size:13px;font-weight:700">${{senderName.slice(0,2).toUpperCase()}}</div>
          <div class="mi-meta">
            <div class="mi-who">${{esc(senderName)}}${{flagBadge}}</div>
          </div>
          <div class="mi-time">${{ts}}</div>
        </div>
        <div class="mi-subj">${{esc(it.subject||'(no subject)')}}</div>
      </div>`;
    }});
    listEl.innerHTML=empty.outerHTML+html;
  }}
  updateInboxBadge();
  const lc = document.getElementById('list-panel-count');
  if (lc && currentTab === 'inbox') lc.textContent = inboxItems.length;
}}

async function openInboxMail(rawId) {{
  viewingInboxId = rawId;
  renderInboxPane();
  const item = inboxItems.find(i => String(i.id) === String(rawId));
  if (item && !item.read) {{
    if (item.virtual) item.read = true;
    else {{ try {{ await fetch(API+'/api/attacker/inbox/'+rawId+'/read?user_id='+userId,{{method:'POST'}}); item.read=true; }} catch(e){{}} }}
    updateInboxBadge();
    renderInboxPane();
  }}
}}

async function deleteInboxMail() {{
  if (viewingInboxId===null||!confirm('Delete this email?')) return;
  const item=inboxItems.find(i=>String(i.id)===String(viewingInboxId));
  if (item&&item.virtual) {{ inboxItems=inboxItems.filter(i=>String(i.id)!==String(viewingInboxId)); viewingInboxId=null; renderInboxPane(); return; }}
  try {{
    await fetch(API+'/api/attacker/inbox/'+viewingInboxId+'?user_id='+userId,{{method:'DELETE'}});
    inboxItems=inboxItems.filter(i=>String(i.id)!==String(viewingInboxId)); viewingInboxId=null; renderInboxPane();
  }} catch(e) {{ alert('Delete failed.'); }}
}}

function backToList(tab) {{
  if (tab==='sent') {{ viewingSentId=null; renderSentPane(); }}
  else {{ viewingInboxId=null; renderInboxPane(); }}
}}

function addVirtualInboxItem(contact, text, fromAddr, toAddr, subject) {{
  inboxItems.unshift({{id:'v_'+Date.now(),from_name:contact.name,from_email:toAddr,
    to_email:fromAddr||attackerEmail,subject:'RE: '+(subject||'(no subject)'),
    body:text,received_at:new Date().toISOString(),read:false,flag_value:null,virtual:true}});
  updateInboxBadge();
  const nb = document.getElementById('nav-inbox');
  if (nb) {{ nb.style.background='rgba(0,255,136,0.2)'; setTimeout(()=>{{ nb.style.background=''; }},700); }}
}}

// ── INIT ──────────────────────────────────────────────────────────────────────
updateStatusBar({{status: 'Idle', cls: ''}});
loadIdentity();
loadInbox();
loadContacts();
updateSpamIndicator();
refreshLabStatus();
setInterval(refreshLabStatus, 9000);
setInterval(() => {{
  if (currentTab==='inbox') loadInbox();
  else {{
    fetch(API+'/api/attacker/inbox?user_id='+userId+(activeLabId?'&lab_id='+encodeURIComponent(activeLabId):''))
      .then(r=>r.ok?r.json():null)
      .then(d=>{{ if(d){{ const v=inboxItems.filter(i=>i.virtual); inboxItems=[...v,...(d.inbox||d.items||[])]; updateInboxBadge(); }} }})
      .catch(()=>{{}});
  }}
}}, 7000);

// ── EVENT DELEGATION ──────────────────────────────────────────────────────────
document.addEventListener('click', function(e) {{
  var id = e.target.id || '';
  switch(id) {{
    case 'tab-compose':   showTab('compose'); break;
    case 'tab-sent':      showTab('sent');    break;
    case 'tab-inbox':     showTab('inbox');   break;
    case 'nav-compose':   showTab('compose'); break;
    case 'nav-sent':      showTab('sent');    break;
    case 'nav-inbox':     showTab('inbox');   break;
    case 'nav-campaign':
      showTab('compose');
      setTimeout(()=>setMode('mass'), 0);
      break;
    case 'goto-mass-btn':
      showTab('compose');
      setTimeout(()=>setMode('mass'), 0);
      break;
    case 'mode-single':   setMode('single'); break;
    case 'mode-mass':     setMode('mass');   break;
    case 'send-btn':      handleSend();      break;
    case 'back-sent-btn': backToList('sent'); break;
    case 'back-inbox-btn':backToList('inbox'); break;
    case 'iv-del-btn':    deleteInboxMail(); break;
    case 'gate-btn':      startSimulation(); break;
    case 'reset-btn':     resetLab();        break;
    case 'dismiss-btn':   gameOverDismissed = true; document.getElementById('gameover').classList.remove('show'); break;
    case 'go-compose-link': showTab('compose'); break;
    case 'np-all-btn':  document.querySelectorAll('.npc-cb').forEach(c=>c.checked=true); updateNpcCount(); break;
    case 'np-clear-btn': document.querySelectorAll('.npc-cb').forEach(c=>c.checked=false); updateNpcCount(); break;
  }}
  var mailItem = e.target.closest('.mail-item[data-id]');
  if (mailItem) {{
    if (e.target.closest('#sent-list-view'))  openSentMail(parseInt(mailItem.dataset.id));
    if (e.target.closest('#inbox-list-view')) openInboxMail(mailItem.dataset.id);
  }}
}});
document.addEventListener('input', function(e) {{
  if (e.target.id === 'from-field') {{ hintFrom(); updateSpamIndicator(); }}
  if (e.target.id === 'to-field') {{ hintFrom(); updateSpamIndicator(); }}
  if (e.target.id === 'subject-field' || e.target.id === 'body-field') updateSpamIndicator();
}});
document.addEventListener('change', function(e) {{
  if (e.target.classList.contains('npc-cb')) updateNpcCount();
}});
document.addEventListener('focusout', function(e) {{
  if (e.target.id === 'from-field') saveIdentity();
}});
document.addEventListener('keydown', function(e) {{
  if (e.target.id === 'from-field' && e.key === 'Enter') {{ e.preventDefault(); saveIdentity(); }}
}});
</script>
</body>
</html>"""


@app.get("/api/contacts")
async def list_contacts_endpoint(lab_id: Optional[str] = Query(default=None)):
    if not lab_id:
        return {"contacts": []}
    if lab_id == "mass_phishing":
        contacts = [
            {"name": c["name"], "email": c["email"], "role": c["role"],
             "company": c["company"], "gullibility": c["gullibility"]}
            for c in CONTACTS.values()
            if c.get("lab_id") != "mass_phishing"
        ]
    else:
        contacts = [
            {"name": c["name"], "email": c["email"], "role": c["role"],
             "company": c["company"], "gullibility": c["gullibility"]}
            for c in CONTACTS.values()
            if c.get("lab_id") == lab_id
        ]
    return {"contacts": contacts}


@app.get("/", response_class=HTMLResponse)
async def email_ui():
    return HTMLResponse(content=PAGE, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9004)
