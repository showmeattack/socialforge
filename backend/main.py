"""SocialForge — Social Engineering CTF Platform."""  # v2
import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text as _text

from config import settings
from models import (
    User, LabProgress, ChatMessage, FlagSubmission, AttackerInbox,
    PhishSite, PhishHarvest, PhishCampaign, GameSession, NpcSessionState,
)
from npc_browser import npc_click_link
from ai_engine import (
    chat_with_persona,
    check_flag_in_response,
    check_caught_in_response,
    continue_persona_followup,
    evaluate_phish_page,
    _security_expertise,
    generate_daily_context,
    compute_fraud_delta,
    compute_channel_transition,
    build_org_context_block,
    build_daily_context_block,
    build_fraud_state_block,
    build_cross_channel_block,
    build_phone_phase_block,
    sms_classify,
    sms_deterministic_outcome,
)

# Database
engine: AsyncEngine = create_async_engine(settings.database_url, echo=settings.debug)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


async def _npc_browse_sms(
    message: str, persona: dict, lab: dict,
    lab_id: str, persona_id: str, user_id: int
) -> None:
    """Background task: NPC visits phishing URL from SMS via Playwright MCP.
    If form submitted, writes PhishHarvest record to DB.
    """
    try:
        result = await npc_click_link(message, persona, lab)
        # Try to resolve site_id from URL (e.g. localhost:9006/p/<id>)
        url = result.get("url") or ""
        _sid_m = re.search(r"/p/([A-Za-z0-9_-]+)", url)
        site_id = _sid_m.group(1) if _sid_m else "npc_direct"
        async with AsyncSession(engine) as sess:
            # Always increment visit_count when NPC lands on the page
            if site_id != "npc_direct":
                await sess.execute(
                    _text("UPDATE phishsite SET visit_count = COALESCE(visit_count, 0) + 1 WHERE id = :sid"),
                    {"sid": site_id},
                )
            if result.get("submitted") and result.get("credentials"):
                creds = result["credentials"]
                _existing_sms = (await sess.exec(
                    select(PhishHarvest)
                    .where(PhishHarvest.site_id == site_id)
                    .where(PhishHarvest.persona_id == persona_id)
                    .where(PhishHarvest.user_id == user_id)
                )).first()
                if not _existing_sms:
                    harvest = PhishHarvest(
                        site_id=site_id,
                        lab_id=lab_id,
                        user_id=user_id,
                        persona_id=persona_id,
                        username=creds["username"],
                        password=creds["password"],
                        npc_company=(lab.get("target_company") or {}).get("name", ""),
                        campaign_id="npc_sms_click",
                    )
                    sess.add(harvest)
            await sess.commit()
    except Exception:
        pass


async def _migrate_labprogress(conn):
    """SQLite-friendly additive migration for LabProgress."""
    from sqlalchemy import text
    res = await conn.execute(text("PRAGMA table_info(labprogress)"))
    cols = {row[1] for row in res.fetchall()}
    new_cols = [
        ("failure_reason", "TEXT"),
        ("failed_persona", "TEXT"),
        ("failed_at", "DATETIME"),
    ]
    for name, sql_type in new_cols:
        if name not in cols:
            await conn.execute(text(f"ALTER TABLE labprogress ADD COLUMN {name} {sql_type}"))


async def _migrate_user(conn):
    from sqlalchemy import text
    res = await conn.execute(text("PRAGMA table_info(user)"))
    cols = {row[1] for row in res.fetchall()}
    if "attacker_email" not in cols:
        await conn.execute(text("ALTER TABLE user ADD COLUMN attacker_email TEXT DEFAULT ''"))


async def _migrate_phish_tables(conn):
    from sqlalchemy import text
    # PhishHarvest extra columns
    res = await conn.execute(text("PRAGMA table_info(phishharvest)"))
    cols = {row[1] for row in res.fetchall()}
    for col, sql in [("campaign_id", "TEXT"), ("npc_company", "TEXT DEFAULT ''"), ("flag_piece", "TEXT")]:
        if col not in cols:
            await conn.execute(text(f"ALTER TABLE phishharvest ADD COLUMN {col} {sql}"))
    # PhishSite extra columns
    res = await conn.execute(text("PRAGMA table_info(phishsite)"))
    cols = {row[1] for row in res.fetchall()}
    for col, sql in [
        ("headline", "TEXT DEFAULT ''"), ("subheadline", "TEXT DEFAULT ''"),
        ("button_text", "TEXT DEFAULT 'Sign in'"), ("redirect_url", "TEXT DEFAULT ''"),
        ("quality_score", "REAL DEFAULT 0.6"),
        ("primary_color", "TEXT DEFAULT '#0078d4'"),
        ("bg_color", "TEXT DEFAULT '#f3f2f1'"),
        ("btn_color", "TEXT DEFAULT '#0078d4'"),
        ("font_family", "TEXT DEFAULT '''Segoe UI'',sans-serif'"),
        ("logo_text", "TEXT DEFAULT ''"),
        ("ssl_type", "TEXT DEFAULT 'valid'"),
        ("visit_count", "INTEGER DEFAULT 0"),
    ]:
        if col not in cols:
            await conn.execute(text(f"ALTER TABLE phishsite ADD COLUMN {col} {sql}"))




@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await _migrate_labprogress(conn)
        await _migrate_user(conn)
        await _migrate_phish_tables(conn)
    yield


app = FastAPI(title="SocialForge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load labs
LABS_DIR = Path(__file__).parent.parent / "labs"
def load_labs() -> dict:
    labs = {}
    for f in LABS_DIR.glob("*.json"):
        try:
            with open(f, encoding="utf-8-sig") as fh:
                lab = json.load(fh)
            labs[lab["id"]] = lab
        except Exception:
            continue
    return labs


def get_lab(lab_id: str) -> dict:
    labs = load_labs()
    if lab_id not in labs:
        raise HTTPException(404, "Lab not found")
    return labs[lab_id]


# --- Auth (simple for MVP) ---
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: str = ""
    locale: str = "en"


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/auth/register")
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    import bcrypt as _bcrypt
    existing = await session.exec(select(User).where(User.username == req.username))
    if existing.first():
        raise HTTPException(400, "Username taken")
    hashed = _bcrypt.hashpw(req.password.encode(), _bcrypt.gensalt()).decode()
    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hashed,
        display_name=req.display_name or req.username,
        locale=req.locale,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"ok": True, "user_id": user.id, "username": user.username}


@app.post("/api/auth/login")
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    import bcrypt as _bcrypt
    result = await session.exec(select(User).where(User.username == req.username))
    user = result.first()
    if not user or not _bcrypt.checkpw(req.password.encode(), user.hashed_password.encode()):
        raise HTTPException(401, "Invalid credentials")
    # Simple token (for MVP — just user_id, no JWT)
    return {"ok": True, "user_id": user.id, "username": user.username, "locale": user.locale}


# --- Labs ---
@app.get("/api/labs")
async def list_labs():
    labs = load_labs()
    return {
        "labs": [
            {
                "id": l["id"],
                "title": l["title"],
                "description": l["description"],
                "difficulty": l["difficulty"],
                "category": l["category"],
                "points": l["points"],
                "estimated_time": l["estimated_time"],
                "real_case": l.get("real_case"),
                "type": l.get("type", "lab"),
                "operation_flag": l.get("operation_flag"),
                "operation_flag_id": l.get("operation_flag_id"),
            }
            for l in labs.values()
        ]
    }


@app.get("/api/labs/{lab_id}")
async def get_lab_detail(lab_id: str):
    lab = get_lab(lab_id)
    # Don't expose flag values or break conditions to the client
    safe_lab = {
        "id": lab["id"],
        "title": lab["title"],
        "description": lab["description"],
        "difficulty": lab["difficulty"],
        "category": lab["category"],
        "points": lab["points"],
        "estimated_time": lab["estimated_time"],
        "real_case": lab.get("real_case"),
        "type": lab.get("type", "lab"),
        "objective": lab.get("objective"),
        "operation_flag": lab.get("operation_flag"),
        "operation_flag_id": lab.get("operation_flag_id"),
        "flags": [{"id": f["id"], "points": f["points"]} for f in lab.get("flags", [])],
        "target_company": lab.get("target_company", {}),
        "features": lab.get("features", {}),
        "attack_chain": [
            {
                "phase": step["phase"],
                "name": step["name"],
                "description": step["description"],
                "objectives": step.get("objectives", []),
                "hints": [{"cost": h["cost"], "text": h["text"]} for h in step.get("hints", [])],
                "persona": step.get("persona"),
                "flag": {"id": step["flag"]["id"], "points": step["flag"]["points"], "hint": step["flag"].get("hint")} if step.get("flag") else None,
            }
            for step in lab["attack_chain"]
        ],
        "personas": {
            pid: {
                "name": p["name"],
                "role": p["role"],
                "phone_ext": p.get("phone_ext", ""),
                "email": p.get("email", ""),
                "contactable": p.get("contactable", True),
                "social_profiles": p.get("social_profiles", {}),
                "schedule": {
                    "work_hours": p.get("schedule", {}).get("work_hours", ""),
                    "timezone": p.get("schedule", {}).get("timezone", ""),
                },
            }
            for pid, p in lab["personas"].items()
            if p.get("contactable", True)
        },
    }
    return safe_lab


# --- Game Session ---

_URGENCY_RE = re.compile(
    r"\b(urgent|immediately|right now|asap|emergency|hurry|deadline)\b", re.IGNORECASE
)


def _infer_fraud_events(
    message: str,
    spoof_ctx: "dict | None",
    page_analysis: str,
    channel: str,
    msg_count: int,
    persona: dict,
) -> list[str]:
    events: list[str] = ["message_sent"]
    if re.search(r"https?://", message):
        events.append("link_included")
    if spoof_ctx:
        events.append("domain_spoofed")
    if page_analysis and "SSL_WARNING" in page_analysis:
        events.append("ssl_warning")
    if page_analysis and "REDIRECT_CHAIN" in page_analysis:
        events.append("redirect_chain")
    if _URGENCY_RE.search(message):
        events.append("pressure_tactic")
    if msg_count >= 3:
        events.append("repeat_contact")
    triggers = persona.get("vulnerability_triggers") or []
    ml = message.lower()
    if any(t.lower() in ml for t in triggers):
        events.append("trigger_hit")
    return events


class SessionStartRequest(BaseModel):
    user_id: int
    lab_id: str


@app.post("/api/session/start")
async def session_start(req: SessionStartRequest, session: AsyncSession = Depends(get_session)):
    lab = get_lab(req.lab_id)
    existing = await session.exec(
        select(GameSession)
        .where(GameSession.user_id == req.user_id)
        .where(GameSession.lab_id == req.lab_id)
        .where(GameSession.is_active == True)
    )
    for gs in existing.all():
        gs.is_active = False
        gs.ended_at = datetime.utcnow()
        session.add(gs)

    gs = GameSession(user_id=req.user_id, lab_id=req.lab_id)
    gs_id = gs.id
    gs_seed = gs.daily_seed
    session.add(gs)
    await session.flush()

    for pid, persona in (lab.get("personas") or {}).items():
        daily_ctx = generate_daily_context(persona.get("name", pid), gs_seed)
        session.add(NpcSessionState(
            session_id=gs_id,
            user_id=req.user_id,
            lab_id=req.lab_id,
            persona_id=pid,
            daily_context=json.dumps(daily_ctx),
        ))

    await session.commit()
    return {"ok": True, "session_id": gs_id, "daily_seed": gs_seed}


@app.get("/api/session/current")
async def session_current(user_id: int, lab_id: str, session: AsyncSession = Depends(get_session)):
    gs = (await session.exec(
        select(GameSession)
        .where(GameSession.user_id == user_id)
        .where(GameSession.lab_id == lab_id)
        .where(GameSession.is_active == True)
        .order_by(GameSession.started_at.desc())
    )).first()
    if not gs:
        return {"session": None}
    return {"session": {"id": gs.id, "daily_seed": gs.daily_seed, "started_at": gs.started_at.isoformat()}}


@app.post("/api/session/end")
async def session_end(req: SessionStartRequest, session: AsyncSession = Depends(get_session)):
    result = await session.exec(
        select(GameSession)
        .where(GameSession.user_id == req.user_id)
        .where(GameSession.lab_id == req.lab_id)
        .where(GameSession.is_active == True)
    )
    for gs in result.all():
        gs.is_active = False
        gs.ended_at = datetime.utcnow()
        session.add(gs)
    await session.commit()
    return {"ok": True}


class SessionStartAllRequest(BaseModel):
    user_id: int


@app.post("/api/session/start-all")
async def session_start_all(req: SessionStartAllRequest, session: AsyncSession = Depends(get_session)):
    """Start a new simulation day: create fresh sessions for ALL labs simultaneously."""
    labs = load_labs()
    # Deactivate all existing sessions for this user
    existing = await session.exec(
        select(GameSession)
        .where(GameSession.user_id == req.user_id)
        .where(GameSession.is_active == True)
    )
    for gs in existing.all():
        gs.is_active = False
        gs.ended_at = datetime.utcnow()
        session.add(gs)
    await session.flush()

    total_npcs = 0
    sessions_created = 0
    # Use one shared seed for the day so all NPCs share the same "day"
    import random as _rnd
    day_seed = _rnd.randint(1, 999999)

    for lab_id, lab in labs.items():
        import uuid as _uuid2
        gs_id = _uuid2.uuid4().hex[:12]
        gs = GameSession(user_id=req.user_id, lab_id=lab_id)
        gs.id = gs_id
        gs.daily_seed = day_seed
        session.add(gs)
        await session.flush()

        personas = lab.get("personas") or {}
        for pid, persona in personas.items():
            daily_ctx = generate_daily_context(persona.get("name", pid), day_seed)
            session.add(NpcSessionState(
                session_id=gs_id,
                user_id=req.user_id,
                lab_id=lab_id,
                persona_id=pid,
                daily_context=json.dumps(daily_ctx),
            ))
            total_npcs += 1
        sessions_created += 1

    # BUG-FIX: RESTART DAY must fully reset ALL lab progress — not just failed labs.
    # Wipe chat history, PhishHarvest, FlagSubmissions, and NpcSessionState daily_context
    # for ALL labs so the player cannot carry over harvested credentials to a new day.
    all_prog = await session.exec(
        select(LabProgress)
        .where(LabProgress.user_id == req.user_id)
    )
    for lp in all_prog.all():
        # Clear chat messages for this lab
        msgs = await session.exec(
            select(ChatMessage)
            .where(ChatMessage.user_id == req.user_id)
            .where(ChatMessage.lab_id == lp.lab_id)
        )
        for m in msgs.all():
            await session.delete(m)
        # Clear PhishHarvest so credentials from previous day cannot be reused
        harvests = await session.exec(
            select(PhishHarvest)
            .where(PhishHarvest.user_id == req.user_id)
            .where(PhishHarvest.lab_id == lp.lab_id)
        )
        for h in harvests.all():
            await session.delete(h)
        # Clear flag submissions for this lab
        subs = await session.exec(
            select(FlagSubmission)
            .where(FlagSubmission.user_id == req.user_id)
            .where(FlagSubmission.lab_id == lp.lab_id)
        )
        for s in subs.all():
            await session.delete(s)
        # Reset progress for failed labs; keep completed labs as-is
        if lp.status == "failed":
            lp.status = "in_progress"
            lp.failure_reason = None
            lp.failed_persona = None
            lp.failed_at = None
            session.add(lp)
    await session.flush()

    await session.commit()
    return {"ok": True, "total_sessions": sessions_created, "total_npcs": total_npcs, "daily_seed": day_seed}


@app.get("/api/session/status")
async def session_status(user_id: int, session: AsyncSession = Depends(get_session)):
    """Global simulation status for the user."""
    active_sessions = await session.exec(
        select(GameSession)
        .where(GameSession.user_id == user_id)
        .where(GameSession.is_active == True)
        .order_by(GameSession.started_at.desc())
    )
    sessions = active_sessions.all()
    if not sessions:
        return {"active": False, "total_sessions": 0, "total_npcs": 0}

    first = sessions[0]
    npc_count = (await session.exec(
        select(NpcSessionState)
        .where(NpcSessionState.user_id == user_id)
        .where(NpcSessionState.session_id.in_([s.id for s in sessions]))
    )).all()

    return {
        "active": True,
        "started_at": first.started_at.isoformat(),
        "daily_seed": first.daily_seed,
        "total_sessions": len(sessions),
        "total_npcs": len(npc_count),
    }


# --- Chat with NPC ---
class ChatRequest(BaseModel):
    user_id: int
    lab_id: str
    persona_id: str
    message: str
    channel: str = "phone"  # email | phone | chat | sms
    from_email: Optional[str] = None  # spoofed sender for email channel
    model: Optional[str] = None
    # SIM swap / caller-ID spoofing (phone/sms channels)
    caller_id: Optional[str] = None            # what the victim's phone displays
    caller_profile: Optional[str] = None       # real|burner_us|burner_voip|burner_intl|spoof_internal|spoof_custom
    caller_identity: Optional[str] = None      # persona_id the attacker is pretending to be
    caller_spoofed_ext: Optional[str] = None   # internal extension being spoofed, e.g. "1000"
    # Voice deepfake (phone only)
    voice_identity: Optional[str] = None       # persona_id whose voice is being cloned
    voice_engine: Optional[str] = None         # neuralclone_v3 | fastvoice_lite | basic
    voice_has_sample: Optional[bool] = None    # True if a sample was uploaded
    voice_sample_url: Optional[str] = None     # URL of public voice sample for quality scoring
    voice_quality_override: Optional[float] = None  # direct score from .sfvoice file (0.0–1.0)
    # Ambient audio context (phone only) — what the NPC hears in background
    background_noise: Optional[str] = None     # none | office | street | callcenter | datacenter
    # Per-call email override (phone SIM tab) — overrides user profile email
    caller_email_override: Optional[str] = None
    # LinkHub channel: persona_id verified via PhishHarvest login
    linkhub_authenticated_as: Optional[str] = None


# Corporate / brand domains you can't just register — any attempt to send
# a phish FROM one of these is dropped by the mail gateway in-sim.
_PROTECTED_BRAND_DOMAINS = {
    "microsoft.com", "outlook.com", "office365.com", "office.com",
    "google.com", "gmail.com", "googlemail.com",
    "apple.com", "icloud.com", "me.com",
    "amazon.com", "aws.amazon.com",
    "meta.com", "facebook.com", "instagram.com",
    "okta.com", "duosecurity.com", "cisco.com",
    "dropbox.com", "slack.com", "zoom.us",
    "paypal.com", "stripe.com",
    "github.com", "gitlab.com",
    "linkedin.com", "twitter.com", "x.com",
    "adobe.com", "salesforce.com", "docusign.com", "docusign.net",
}

_EMAIL_RE = re.compile(r"^[^@\s]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$")


_VOICE_SAMPLE_DOMAIN_SCORES: dict[str, float] = {
    "cnbc.com": 0.93, "bloomberg.com": 0.91, "bbc.co.uk": 0.90, "bbc.com": 0.90,
    "reuters.com": 0.88, "apnews.com": 0.87, "cnn.com": 0.86, "ft.com": 0.85,
    "nytimes.com": 0.84, "wsj.com": 0.83, "theguardian.com": 0.82,
    "youtube.com": 0.78, "youtu.be": 0.78,
    "tiktok.com": 0.65, "instagram.com": 0.62, "twitter.com": 0.60, "x.com": 0.60,
    "reddit.com": 0.55, "facebook.com": 0.52,
    "soundcloud.com": 0.70, "anchor.fm": 0.68, "spotify.com": 0.72,
    "vimeo.com": 0.75,
}

def _evaluate_voice_sample(url: str | None) -> float:
    """Score a public voice sample URL 0.0–1.0 for clone quality.

    Domain tier determines base quality. Unknown domains get 0.40.
    Very short URLs (likely not real media) get 0.15.
    None/empty → 0.0 (no sample provided).
    """
    if not url:
        return 0.0
    url = url.strip().lower()
    if len(url) < 10:
        return 0.15
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lstrip("www.")
        for domain, score in _VOICE_SAMPLE_DOMAIN_SCORES.items():
            if host == domain or host.endswith("." + domain):
                return score
    except Exception:
        pass
    return 0.40


def _build_spoof_context(req: "ChatRequest", lab: dict) -> dict | None:
    """Resolve the caller-ID and voice-clone context for this request.

    Returns a dict consumed by ai_engine.build_system_prompt, or None if the
    attacker is using their real line + real voice (the default).
    """
    has_spoof = bool(
        req.caller_id or req.caller_profile not in (None, "real")
        or req.caller_identity or req.caller_spoofed_ext
    )
    has_voice = bool(req.voice_identity)
    if not has_spoof and not has_voice:
        return None

    personas = lab.get("personas", {}) or {}

    impersonated = None
    if req.caller_identity and req.caller_identity in personas:
        p = personas[req.caller_identity]
        impersonated = {
            "persona_id": req.caller_identity,
            "name": p.get("name", ""),
            "role": p.get("role", ""),
            "phone_ext": p.get("phone_ext", ""),
            "email": p.get("email", ""),
        }
    elif req.caller_spoofed_ext:
        for pid, p in personas.items():
            if str(p.get("phone_ext") or "") == str(req.caller_spoofed_ext):
                impersonated = {
                    "persona_id": pid, "name": p.get("name", ""),
                    "role": p.get("role", ""), "phone_ext": p.get("phone_ext", ""),
                    "email": p.get("email", ""),
                }
                break

    voice = None
    if req.voice_identity and req.voice_identity in personas:
        v = personas[req.voice_identity]
        if req.voice_quality_override and 0.0 < req.voice_quality_override <= 1.0:
            quality_score = req.voice_quality_override
        else:
            quality_score = _evaluate_voice_sample(req.voice_sample_url)
        voice = {
            "persona_id": req.voice_identity,
            "name": v.get("name", ""),
            "role": v.get("role", ""),
            "engine": req.voice_engine or "neuralclone_v3",
            "has_sample": bool(req.voice_has_sample) or quality_score > 0,
            "quality_score": quality_score,
            "sample_url": req.voice_sample_url or "",
        }

    return {
        "caller_id_display": req.caller_id or "",
        "caller_profile": req.caller_profile or "real",
        "impersonated": impersonated,
        "voice": voice,
        "background_noise": req.background_noise or "none",
    }


def _validate_from_email(from_email: str) -> tuple[bool, str]:
    """Block real corporate domains and malformed addresses.

    Player must use lookalikes (micr0soft.com, out1ook.com, etc.).
    """
    if not from_email:
        return True, ""
    addr = from_email.strip().lower()
    m = _EMAIL_RE.match(addr)
    if not m:
        return False, "Malformed sender address. Use name@domain.tld."
    domain = m.group(1)
    if domain in _PROTECTED_BRAND_DOMAINS:
        return False, f"Mail gateway rejected From: '{domain}' is a protected brand domain (SPF/DMARC). Use a lookalike."
    # Block exact matches to a target company domain — can't pretend to be
    # internal-from-your-own-domain (DMARC rejects that too).
    labs = load_labs()
    for l in labs.values():
        tc_domain = (l.get("target_company", {}).get("domain") or "").lower()
        if tc_domain and domain == tc_domain:
            return False, f"Mail gateway rejected: sender domain '{domain}' is the target's own domain (DMARC failure). Use a lookalike."
    return True, ""


_FLAG_RE = re.compile(r"(SF\{[^}]+\}|FLAG\{[^}]+\})")

# Phrases that indicate the NPC agreed to send something but may have forgotten
# to emit the structured [DELIVER_EMAIL] block.
_SEND_HINTS_RE = re.compile(
    r"\b("
    r"sent|i.?ve sent|just sent|already sent|sending|i.?ll send|i.?m sending"
    r"|email sent|emailed|forwarded|dispatching"
    r"|отправил|отправляю|отправлю"  # отправил/отправляю/отправлю
    r"|уже отправил|сейчас отправлю"  # уже отправил/сейчас отправлю
    r")",
    re.IGNORECASE,
)

# Phrases indicating NPC is terminating the conversation (hang-up detection).
_HANGUP_HINTS_RE = re.compile(
    r"\b("
    r"hang(?:ing)? up|hanging up on|going to hang|i.?m hanging|i.?ll hang"
    r"|ending this call|end(?:ing)? the call|terminating this call"
    r"|i.?m going to hang|need to end this|have to end this"
    r"|goodbye and hang|report this call|report you to"
    r")",
    re.IGNORECASE,
)

# Phrases indicating victim NPC clicked a phishing link / completed a form.
# Used to auto-award the persona's flag when the NPC doesn't output it inline.
_CLICK_HINTS_RE = re.compile(
    r"\b("
    r"i.?ll (?:go ahead and )?(?:click|verify|complete|check|run|do it|fill)"
    r"|let me (?:go ahead and )?(?:click|verify|complete|check|run|fill)"
    r"|(?:going|excited|happy|glad|plan(?:ning)?|intend(?:ing)?|looking forward) to (?:click|verify|complete|check|run the scan|fill)"
    r"|will (?:click|verify|complete|check|run|fill)"
    r"|go ahead and (?:verify|complete|check|click|fill)"
    r"|clicked|just clicked|already clicked"
    r"|verified|just verified|entered my (?:credentials|password|info|information)"
    r"|completed (?:the|your|this) (?:form|verification|scan|check|survey)"
    r"|ran the scan|completed the scan|did the scan|done the scan"
    r"|нажал|перешёл по ссылке|ввёл данные|прошёл верификацию"
    r")",
    re.IGNORECASE,
)

_PHISH_URL_RE = re.compile(r"https?://(?:localhost|127\.0\.0\.1):\d+/p/([A-Za-z0-9_-]+)|localhost:\d+/p/([A-Za-z0-9_-]+)")


def _fallback_deliver(
    response_text: str,
    persona: dict,
    caller_email: str,
) -> dict | None:
    """If the NPC said 'sent' but forgot the [DELIVER_EMAIL] block, synthesize
    the payload from persona.deliverable so the email still lands in the inbox.
    Only fires when: send-hint found + deliverable exists.
    """
    deliverable = (persona.get("deliverable") or "").strip()
    if not deliverable:
        return None
    if not _SEND_HINTS_RE.search(response_text or ""):
        return None
    persona_name = persona.get("name", "")
    subject = f"Re: Urgent request — {persona_name}"
    return {"to": caller_email, "subject": subject, "body": deliverable}


def _persist_delivered_email(
    session: AsyncSession,
    user_id: int,
    lab_id: str,
    persona: dict,
    delivered: dict | None,
    caller_email: str,
    persona_id: str | None = None,
) -> Optional[AttackerInbox]:
    """Turn a [DELIVER_EMAIL] payload from the LLM into an AttackerInbox row.

    No-op if the payload is missing or empty. Returns the new row (not yet
    committed — the caller's session.commit() will flush it).
    """
    if not delivered:
        return None
    body = (delivered.get("body") or "").strip()
    subject = (delivered.get("subject") or "").strip() or "(no subject)"
    to_addr = (delivered.get("to") or "").strip() or (caller_email or "").strip()
    if not body and not subject:
        return None

    flag_match = _FLAG_RE.search(body) or _FLAG_RE.search(subject)
    flag_value = flag_match.group(1) if flag_match else None

    # If the LLM truncated the deliverable body, fall back to the full persona deliverable.
    # Also re-extract flag from the full deliverable if not found in truncated body.
    persona_deliverable = (persona.get("deliverable") or "").strip()
    if persona_deliverable and len(persona_deliverable) > len(body):
        body = persona_deliverable
    if not flag_value and persona_deliverable:
        flag_match2 = _FLAG_RE.search(persona_deliverable)
        flag_value = flag_match2.group(1) if flag_match2 else None

    row = AttackerInbox(
        user_id=user_id,
        lab_id=lab_id,
        persona_id=persona_id or _persona_id_for(persona),
        from_name=persona.get("name", "") or "",
        from_email=persona.get("email", "") or "",
        to_email=to_addr,
        subject=subject[:200],
        body=body,
        flag_value=flag_value,
    )
    session.add(row)
    return row


def _persona_id_for(persona: dict) -> str:
    """Persona dicts inside a lab don't carry their own id — we need to look it
    up from lab.personas by value. This helper tries persona.get('id') first
    and falls back to name-slug.
    """
    pid = persona.get("id") or persona.get("persona_id") or ""
    if pid:
        return str(pid)
    name = (persona.get("name") or "npc").lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", name) or "npc"


async def _get_or_create_progress(
    session: AsyncSession, user_id: int, lab_id: str
) -> LabProgress:
    result = await session.exec(
        select(LabProgress)
        .where(LabProgress.user_id == user_id)
        .where(LabProgress.lab_id == lab_id)
    )
    progress = result.first()
    if not progress:
        progress = LabProgress(user_id=user_id, lab_id=lab_id, status="not_started")
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
    return progress


@app.post("/api/chat")
async def chat(req: ChatRequest, session: AsyncSession = Depends(get_session)):
    lab = get_lab(req.lab_id)
    persona = lab["personas"].get(req.persona_id)
    if not persona:
        raise HTTPException(404, "Persona not found")

    # --- Lab lifecycle gate ---
    progress = await _get_or_create_progress(session, req.user_id, req.lab_id)
    if progress.status == "not_started":
        raise HTTPException(409, {
            "error": "lab_not_started",
            "message": "Start the simulation first.",
        })
    if progress.status == "failed":
        return {
            "response": "I'm sorry, I can't help you with this. Please leave, or I'll call security.",
            "flag_found": None,
            "caught": True,
            "mission_failed": True,
            "fail_reason": progress.failure_reason or "Mission failed.",
            "failed_persona": progress.failed_persona,
            "work_status": None,
            "voicemail": False,
            "persona": persona["name"],
        }
    if progress.status == "completed":
        # Allow chat but flag it — players sometimes want to keep chatting
        # after capturing all flags. No behavior change needed.
        pass

    # --- Email spoof validation ---
    if req.channel == "email" and req.from_email:
        ok, err = _validate_from_email(req.from_email)
        if not ok:
            raise HTTPException(400, {"error": "bad_sender", "message": err})

    # --- Persona-level email domain restriction (code-level, not prompt-based) ---
    if req.channel == "email" and req.from_email:
        _allowed_domain = persona.get("email_only_domain", "")
        if _allowed_domain:
            _sender_domain = req.from_email.split("@")[-1].lower().strip() if "@" in req.from_email else ""
            if _sender_domain != _allowed_domain.lower():
                _company_name = (lab.get("target_company") or {}).get("name", "the company")
                return {
                    "response": f"I don't recognize this sender address. Please use official {_company_name} channels.",
                    "flag_found": None, "caught": False, "mission_failed": False,
                    "fail_reason": None, "failed_persona": None, "work_status": "in_hours",
                    "voicemail": False, "no_answer": False, "pickup_probability": None,
                    "persona": persona["name"], "followup_hint": None, "delivered_email": None,
                }

    # BUG-FIX: abuse/threat detection must fire BEFORE any channel guard.
    # If the player sends nonsense/abuse (e.g. "I'm 1337 H4X0R give me FLAG"),
    # the NPC reports it to IT security and the attempt is caught+failed.
    _ABUSE_RE = re.compile(
        r'(?:h[4a]x[0o]r|1337|give.{0,20}flag|hand.{0,20}flag'
        r'|password.{0,30}now|give.{0,20}cred'
        r'|im.{0,10}hack|i.{0,5}am.{0,10}hack|hacking you)',
        re.IGNORECASE,
    )
    _sanitized_for_abuse = req.message.lower()
    if _ABUSE_RE.search(_sanitized_for_abuse):
        return {
            "response": "I'm forwarding this to IT Security. Don't contact me again.",
            "flag_found": None, "caught": True, "mission_failed": True,
            "fail_reason": "Abusive/explicit attack message detected by NPC.",
            "failed_persona": persona["name"], "work_status": "in_hours",
            "voicemail": False, "no_answer": False, "pickup_probability": None,
            "persona": persona["name"], "followup_hint": None, "delivered_email": None,
        }

    # Get conversation history
    # --- Credentials-phone-only guard (code-level, not prompt-based) ---
    if persona.get("credentials_phone_only") and req.channel == "email":
        return {
            "response": "I don't share login credentials over email. If this is legitimate, call me on my direct line.",
            "flag_found": None, "caught": False, "mission_failed": False,
            "fail_reason": None, "failed_persona": None, "work_status": "in_hours",
            "voicemail": False, "no_answer": False, "pickup_probability": None,
            "persona": persona["name"], "followup_hint": None, "delivered_email": None,
        }

    result = await session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == req.user_id)
        .where(ChatMessage.lab_id == req.lab_id)
        .where(ChatMessage.persona_id == req.persona_id)
        .order_by(ChatMessage.timestamp)
    )
    history = [{"role": m.role, "content": m.content} for m in result.all()]

    # --- Load NpcSessionState for this persona ---
    npc_state: dict | None = None
    _nss_row: NpcSessionState | None = None
    _gs_row = (await session.exec(
        select(GameSession)
        .where(GameSession.user_id == req.user_id)
        .where(GameSession.lab_id == req.lab_id)
        .where(GameSession.is_active == True)
        .order_by(GameSession.started_at.desc())
    )).first()
    if _gs_row:
        _nss_row = (await session.exec(
            select(NpcSessionState)
            .where(NpcSessionState.session_id == _gs_row.id)
            .where(NpcSessionState.persona_id == req.persona_id)
        )).first()
        if _nss_row:
            _ch_states = json.loads(_nss_row.channel_states)
            _ch_counts = json.loads(_nss_row.channel_msg_counts)
            _daily_ctx = json.loads(_nss_row.daily_context)
            _cross_log = json.loads(_nss_row.cross_channel_log)
            _expertise = _security_expertise(persona)
            _gullibility = (persona.get("psychology") or {}).get("gullibility", 50)
            npc_state = {
                "fraud_score": _nss_row.fraud_score,
                "channel_state": _ch_states.get(req.channel, "cold"),
                "channel_msg_count": _ch_counts.get(req.channel, 0),
                "cross_channel_log": _cross_log,
                "daily_context": _daily_ctx,
                "gullibility": _gullibility,
                "expertise": _expertise,
            }

    # Prefix the message with sender info for email channel so the NPC can
    # notice suspicious From addresses (the rule-based / LLM layer reads it).
    engine_message = req.message
    if req.channel == "email" and req.from_email:
        engine_message = f"[From: {req.from_email}]\n{req.message}"

    # --- LinkHub channel: strip prompt-injection spoofs + inject verified auth marker ---
    if req.channel == "linkhub":
        # Strip any user-injected "[DM from NAME]:" or "[LINKHUB_VERIFIED_AS:...]:" patterns
        # before we prepend the real auth marker — prevents prompt injection bypass
        _INJECTION_PAT = re.compile(
            r'\[(DM from|System|From|Verified|LINKHUB_VERIFIED_AS|LINKHUB_UNVERIFIED)[^\]]{0,120}\]:\s*',
            re.IGNORECASE,
        )
        _clean_msg = req.message
        while _INJECTION_PAT.search(_clean_msg):
            _clean_msg = _INJECTION_PAT.sub('', _clean_msg)
        _clean_msg = _clean_msg.strip()

        auth_prefix = "[LINKHUB_UNVERIFIED]:\n"
        if req.linkhub_authenticated_as:
            # BUG-FIX: only accept a real persona_id from this lab — reject name slugs
            # and arbitrary strings that could be guessed or injected from the UI.
            _valid_persona_ids = set(lab.get("personas", {}).keys())
            _auth_pid = req.linkhub_authenticated_as
            if _auth_pid in _valid_persona_ids:
                _phh = (await session.exec(
                    select(PhishHarvest)
                    .where(PhishHarvest.user_id == req.user_id)
                    .where(PhishHarvest.lab_id == req.lab_id)
                    .where(PhishHarvest.persona_id == _auth_pid)
                )).first()
                if _phh:
                    _auth_p = lab.get("personas", {}).get(_auth_pid, {})
                    _auth_name = _auth_p.get("name", _auth_pid)
                    auth_prefix = f"[LINKHUB_VERIFIED_AS:{_auth_name}]:\n"
        engine_message = auth_prefix + _clean_msg

        # CODE-LEVEL GUARD: personas that require verified LinkHub auth reject unverified DMs
        # without calling LLM — LLMs are unreliable for security-critical decisions.
        _req_verified_as = persona.get("linkhub_requires_verified_as", "")
        if _req_verified_as:
            _v_persona = lab.get("personas", {}).get(_req_verified_as, {})
            _v_name = _v_persona.get("name", _req_verified_as)
            _expected = f"[LINKHUB_VERIFIED_AS:{_v_name}]:"
            if not engine_message.startswith(_expected):
                return {
                    "response": "I don't recognize your profile. If you're a Helix colleague, please reach out from your verified company account.",
                    "flag_found": None, "caught": False, "mission_failed": False,
                    "fail_reason": None, "failed_persona": None, "work_status": "in_hours",
                    "voicemail": False, "no_answer": False, "pickup_probability": None,
                    "persona": persona["name"], "followup_hint": None, "delivered_email": None,
                }

    # Resolve spoof / voice context so the engine can see what the NPC's phone
    # would show vs. what the caller sounds like.
    spoof_ctx = _build_spoof_context(req, lab)

    # Pull the attacker's reply-to email: per-call override wins, then
    # impersonated persona email (NPC sends to "Linda Hayes" not the attacker's burner),
    # then for email channel the spoofed From header, then attacker profile email.
    user_row = await session.get(User, req.user_id)
    _impersonated_email = ((spoof_ctx or {}).get("impersonated") or {}).get("email", "")
    caller_email = (req.caller_email_override or "").strip() or \
                   _impersonated_email or \
                   (req.from_email.strip() if req.channel == "email" and req.from_email else "") or \
                   ((user_row.attacker_email if user_row else "") or "")

    # Save user message (store the From in content so UI can render it)
    display_content = req.message
    if req.channel == "email" and req.from_email:
        display_content = f"From: {req.from_email}\n\n{req.message}"
    user_msg = ChatMessage(
        user_id=req.user_id,
        lab_id=req.lab_id,
        persona_id=req.persona_id,
        role="user",
        content=display_content,
        channel=req.channel,
    )
    session.add(user_msg)

    # Detect phishing page URLs in the player's message and build analysis block
    page_analysis = ""
    phish_site = None
    _phish_site_id = None
    phish_match = _PHISH_URL_RE.search(req.message)
    if phish_match:
        site_id = phish_match.group(1) or phish_match.group(2)
        page_url = phish_match.group(0)
        phish_site = (await session.exec(
            select(PhishSite).where(PhishSite.id == site_id)
        )).first()
        if phish_site:
            _phish_site_id = phish_site.id  # snapshot before any commit expires the object
            expertise = _security_expertise(persona)
            site_dict = {
                "template": phish_site.template,
                "domain": phish_site.domain,
                "company_name": phish_site.company_name,
                "page_title": phish_site.page_title,
                "headline": phish_site.headline,
                "subheadline": phish_site.subheadline,
                "button_text": phish_site.button_text,
                "primary_color": phish_site.primary_color,
                "bg_color": phish_site.bg_color,
                "btn_color": phish_site.btn_color,
                "font_family": phish_site.font_family,
                "logo_text": getattr(phish_site, "logo_text", ""),
                "ssl_type": getattr(phish_site, "ssl_type", "valid") or "valid",
                "redirect_url": phish_site.redirect_url or "",
            }
            page_analysis = evaluate_phish_page(site_dict, expertise, page_url=page_url)
            # Mask the raw localhost URL so NPC sees the simulated phishing domain,
            # not 127.0.0.1 — prevents 4th-wall breaking ("that's a localhost address")
            simulated_url = f"https://{phish_site.domain}/p/{phish_site.id}"
            engine_message = engine_message.replace(page_url, simulated_url)

    # Get AI response (engine now returns a dict)
    result_dict = await chat_with_persona(
        persona, lab, history, engine_message, req.model or "",
        channel=req.channel, spoof_ctx=spoof_ctx,
        caller_email=caller_email,
        page_analysis=page_analysis,
        npc_state=npc_state,
    )
    response_text = result_dict.get("response", "")
    mission_failed = bool(result_dict.get("mission_failed"))
    fail_reason = result_dict.get("fail_reason")
    work_status = result_dict.get("work_status")
    voicemail = bool(result_dict.get("voicemail"))
    no_answer = bool(result_dict.get("no_answer"))
    pickup_probability = result_dict.get("pickup_probability", 1.0)

    # --- Auto-bust: enforce turn limits for security-trained NPCs ---
    # LLM often ignores [BUSTED] instruction; enforce programmatically instead.
    if not mission_failed and not voicemail and not no_answer:
        _prior_user_msgs = sum(1 for m in history if m["role"] == "user")
        _exp = _security_expertise(persona)
        _turn_limits = {"security_expert": 2, "security_aware": 4}
        _turn_limit = _turn_limits.get(_exp, 999)
        if _prior_user_msgs >= _turn_limit:
            mission_failed = True
            fail_reason = "NPC identified this as a social engineering attempt and ended the conversation."
            if not response_text:
                response_text = "I'm going to need to end this call and report it. Goodbye."

    # General fallback: if LLM set mission_failed but returned empty text
    if mission_failed and not response_text and not voicemail and not no_answer:
        response_text = "I'm ending this interaction and flagging it to security. Goodbye."

    # --- SMS one-way outcome: no conversational reply, just event ---
    sms_outcome = result_dict.get("sms_outcome")
    if sms_outcome:
        all_flags = [step.get("flag", {}) for step in lab.get("attack_chain", []) if step.get("flag")]
        if sms_outcome == "clicked":
            # Only auto-award flag if this persona's phase has an EXPLICIT flag defined.
            # Do NOT fall back to all_flags[0] — that bypasses portal-based flag delivery.
            auto_flag = next(
                (step["flag"] for step in lab.get("attack_chain", [])
                 if step.get("flag") and step.get("persona") == req.persona_id),
                None,
            )
            # If the persona has a deliverable (email-based flag delivery), the flag
            # must come through the actual email path, not an SMS click.
            # This prevents bypassing vishing labs via a single SMS phishing link.
            persona_requires_email_delivery = bool(persona.get("deliverable"))
            flag_value = (auto_flag.get("value") if auto_flag else None) if not persona_requires_email_delivery else None
            desc = f"{persona.get('name')} tapped the link and followed the tracking steps."
            if flag_value:
                desc += " Confirmation code captured."
            else:
                desc += " Credentials entered on the page — check PhishHarvest."

            # Increment visit_count synchronously — don't rely on background npc_browse_sms
            if _phish_site_id:
                await session.execute(
                    _text("UPDATE phishsite SET visit_count = COALESCE(visit_count, 0) + 1 WHERE id = :sid"),
                    {"sid": _phish_site_id},
                )

            # If no direct flag, harvest credentials for later portal use
            if flag_value is None and _phish_site_id:
                _existing_h = (await session.exec(
                    select(PhishHarvest)
                    .where(PhishHarvest.site_id == _phish_site_id)
                    .where(PhishHarvest.persona_id == req.persona_id)
                )).first()
                if not _existing_h:
                    import hashlib as _hl2
                    _name_slug2 = persona["name"].lower().replace(" ", ".")
                    _email_addr2 = persona.get("email") or f"{_name_slug2}@company.com"
                    _pw_int2 = int(_hl2.sha256(req.persona_id.encode()).hexdigest(), 16) % 10000
                    session.add(PhishHarvest(
                        site_id=_phish_site_id,
                        lab_id=req.lab_id,
                        user_id=req.user_id,
                        persona_id=req.persona_id,
                        persona_name=persona["name"],
                        username=_email_addr2,
                        password="Pass" + str(_pw_int2).zfill(4) + "!",
                    ))

            # Launch NPC browser interaction in background (non-blocking)
            _msg_snap = req.message
            _pers_snap = dict(persona)
            _lab_snap = dict(lab)
            asyncio.create_task(_npc_browse_sms(
                _msg_snap, _pers_snap, _lab_snap,
                req.lab_id, req.persona_id, req.user_id,
            ))
            await session.commit()
            return {
                "response": "",
                "channel_event": "sms_clicked",
                "channel_event_description": desc,
                "flag_found": flag_value,
                "caught": False, "mission_failed": False, "fail_reason": None,
                "failed_persona": None, "work_status": work_status,
                "voicemail": False, "no_answer": False,
                "pickup_probability": pickup_probability,
                "persona": persona.get("name", ""),
                "followup_hint": None, "delivered_email": None,
            }
        elif sms_outcome == "reported":
            if progress.status not in ("failed", "completed"):
                progress.status = "failed"
                progress.failure_reason = fail_reason or "SMS identified as spam."
                progress.failed_persona = persona.get("name", "")
                progress.failed_at = datetime.utcnow()
                session.add(progress)
            await session.commit()
            return {
                "response": "",
                "channel_event": "sms_reported",
                "channel_event_description": f"{persona.get('name')} marked your SMS as spam and reported it.",
                "flag_found": None,
                "caught": True, "mission_failed": True,
                "fail_reason": fail_reason or "SMS identified as spam.",
                "failed_persona": persona.get("name", ""),
                "work_status": work_status,
                "voicemail": False, "no_answer": False,
                "pickup_probability": pickup_probability,
                "persona": persona.get("name", ""),
                "followup_hint": None, "delivered_email": None,
            }
        else:  # ignored
            await session.commit()
            return {
                "response": "",
                "channel_event": "sms_ignored",
                "channel_event_description": f"{persona.get('name')} ignored your SMS. Try a different approach.",
                "flag_found": None,
                "caught": False, "mission_failed": False, "fail_reason": None,
                "failed_persona": None, "work_status": work_status,
                "voicemail": False, "no_answer": False,
                "pickup_probability": pickup_probability,
                "persona": persona.get("name", ""),
                "followup_hint": None, "delivered_email": None,
            }

    # no_answer: NPC didn't pick up — discard both sides so next call starts fresh
    if no_answer:
        await session.rollback()
        return {
            "response": response_text,
            "flag_found": None,
            "caught": False,
            "mission_failed": False,
            "fail_reason": None,
            "failed_persona": None,
            "work_status": work_status,
            "voicemail": False,
            "no_answer": True,
            "pickup_probability": pickup_probability,
            "persona": persona["name"],
            "followup_hint": None,
            "delivered_email": None,
        }

    # For phone/sms channels the flag travels only via email — strip any
    # SF{...} tokens that leaked into the visible spoken reply.
    if req.channel in ("phone", "sms") and response_text:
        response_text = re.sub(r"SF\{[^}]+\}", "[REDACTED — use secure channel]", response_text)

    # Save assistant message — skip [System: ...] errors so they don't
    # pollute the conversation history and confuse the model next turn.
    if response_text and not response_text.startswith("[System:"):
        ai_msg = ChatMessage(
            user_id=req.user_id,
            lab_id=req.lab_id,
            persona_id=req.persona_id,
            role="assistant",
            content=response_text,
            channel=req.channel,
        )
        session.add(ai_msg)

    # If the NPC agreed to email something out-of-band, persist that as a row
    # in the attacker's inbox so they can read it via SF Mail.
    delivered = (result_dict.get("meta") or {}).get("delivered_email")
    if not delivered:
        delivered = _fallback_deliver(response_text, persona, caller_email)
    inbox_row = _persist_delivered_email(
        session, req.user_id, req.lab_id, persona, delivered, caller_email, req.persona_id,
    )
    if inbox_row:
        await session.flush()
    # Snapshot fields before commit — SQLAlchemy expires attributes after commit
    # and lazy loading fails in async context (MissingGreenlet).
    _inbox_snap = {
        "id": inbox_row.id if inbox_row else None,
        "from_email": inbox_row.from_email if inbox_row else None,
        "subject": inbox_row.subject if inbox_row else None,
        "flag_value": inbox_row.flag_value if inbox_row else None,
    } if inbox_row else None

    # Mission-failed: lock the lab down, persist reason
    if mission_failed and progress.status not in ("failed", "completed"):
        progress.status = "failed"
        progress.failure_reason = fail_reason or "The target recognized the attack."
        progress.failed_persona = persona.get("name", "")
        progress.failed_at = datetime.utcnow()
        session.add(progress)

    # --- Persist NpcSessionState update ---
    if _nss_row and npc_state:
        _events = _infer_fraud_events(
            req.message, spoof_ctx, page_analysis,
            req.channel, npc_state["channel_msg_count"], persona,
        )
        _new_fraud = npc_state["fraud_score"] + compute_fraud_delta(_events, npc_state["expertise"])
        _upd_ch_states = json.loads(_nss_row.channel_states)
        _upd_ch_counts = json.loads(_nss_row.channel_msg_counts)
        _upd_cross_log = json.loads(_nss_row.cross_channel_log)

        _new_ch_state = compute_channel_transition(
            _upd_ch_states.get(req.channel, "cold"),
            _new_fraud,
            npc_state["gullibility"],
            hard_fail=mission_failed,
        )
        _upd_ch_states[req.channel] = _new_ch_state
        _upd_ch_counts[req.channel] = _upd_ch_counts.get(req.channel, 0) + 1

        _outcome = "suspicious" if mission_failed else (
            "flagged" if "[SUSPECT]" in response_text else "responded"
        )
        _upd_cross_log.append({
            "channel": req.channel,
            "summary": req.message[:60],
            "outcome": _outcome,
        })
        _upd_cross_log = _upd_cross_log[-5:]

        _nss_row.fraud_score = _new_fraud
        _nss_row.channel_states = json.dumps(_upd_ch_states)
        _nss_row.channel_msg_counts = json.dumps(_upd_ch_counts)
        _nss_row.cross_channel_log = json.dumps(_upd_cross_log)
        _nss_row.updated_at = datetime.utcnow()
        session.add(_nss_row)

    await session.commit()

    # Check if flag was revealed
    all_flags = [step["flag"] for step in lab["attack_chain"] if step.get("flag")]
    flag_found = check_flag_in_response(response_text, all_flags)
    if not flag_found and _inbox_snap and _inbox_snap["flag_value"]:
        flag_found = _inbox_snap["flag_value"]
    # Auto-award flag when phishing victim NPC clicks link (doesn't output flag inline)
    if not flag_found and not mission_failed and req.channel != "linkhub" and _CLICK_HINTS_RE.search(response_text or ""):
        persona_flag = next(
            (step["flag"]["value"] for step in lab.get("attack_chain", [])
             if step.get("flag") and step.get("persona") == req.persona_id),
            None,
        )
        if persona_flag:
            flag_found = persona_flag
    caught = mission_failed or check_caught_in_response(response_text)

    # Hang-up detection: NPC said they're hanging up on phone → treat as caught
    if not mission_failed and not caught and response_text and req.channel == "phone":
        if _HANGUP_HINTS_RE.search(response_text):
            caught = True
            mission_failed = True
            fail_reason = f"{persona.get('name', 'The NPC')} recognised the attempt and ended the call."

    # Auto-harvest: NPC fell for a phishing link → record credentials in Harvest Monitor
    _phsite_id = _phish_site_id if phish_site else None
    if flag_found and _phsite_id and not mission_failed and req.channel != "linkhub":
        _existing_h = (await session.exec(
            select(PhishHarvest)
            .where(PhishHarvest.site_id == _phsite_id)
            .where(PhishHarvest.persona_id == req.persona_id)
        )).first()
        if not _existing_h:
            _name_slug = persona["name"].lower().replace(" ", ".")
            _email_addr = persona.get("email") or f"{_name_slug}@company.com"
            _fake_pw = "Pass" + str(hash(req.persona_id) % 10000).zfill(4) + "!"
            session.add(PhishHarvest(
                site_id=_phsite_id,
                lab_id=req.lab_id,
                user_id=req.user_id,
                persona_id=req.persona_id,
                persona_name=persona["name"],
                username=_email_addr,
                password=_fake_pw,
            ))
            await session.commit()
            asyncio.create_task(_inc_visit(_phsite_id))

    # [CREDENTIALS_SUBMITTED]: NPC entered creds on phishing page, flag comes from portal login
    if "[CREDENTIALS_SUBMITTED]" in (response_text or "") and _phsite_id and not mission_failed and req.channel != "linkhub":
        _existing_h = (await session.exec(
            select(PhishHarvest)
            .where(PhishHarvest.site_id == _phsite_id)
            .where(PhishHarvest.persona_id == req.persona_id)
        )).first()
        if not _existing_h:
            import hashlib as _hl
            _name_slug = persona["name"].lower().replace(" ", ".")
            _email_addr = persona.get("email") or f"{_name_slug}@company.com"
            _pw_int = int(_hl.sha256(req.persona_id.encode()).hexdigest(), 16) % 10000
            _fake_pw = "Pass" + str(_pw_int).zfill(4) + "!"
            session.add(PhishHarvest(
                site_id=_phsite_id,
                lab_id=req.lab_id,
                user_id=req.user_id,
                persona_id=req.persona_id,
                persona_name=persona["name"],
                username=_email_addr,
                password=_fake_pw,
            ))
            await session.commit()
            asyncio.create_task(_inc_visit(_phsite_id))

    # Phishing page rejected: extract specific reason if [PHISH_BUSTED] fired
    if caught and not mission_failed and "[PHISH_BUSTED]" in response_text:
        mission_failed = True
        fail_reason = f"{persona.get('name', 'The target')} inspected your phishing page and noticed something was wrong — wrong domain, missing SSL, or visual mismatch."
        if progress.status not in ("failed", "completed"):
            progress.status = "failed"
            progress.failure_reason = fail_reason
            progress.failed_persona = persona.get("name", "")
            progress.failed_at = datetime.utcnow()
            session.add(progress)
            await session.commit()

    followup_hint = result_dict.get("followup_hint") if not mission_failed and not voicemail else None

    return {
        "response": response_text,
        "flag_found": flag_found,
        "caught": caught,
        "mission_failed": mission_failed,
        "fail_reason": (fail_reason or "The target recognized the attack.") if mission_failed else None,
        "failed_persona": persona.get("name", "") if mission_failed else None,
        "work_status": work_status,
        "voicemail": voicemail,
        "no_answer": no_answer,
        "pickup_probability": pickup_probability,
        "persona": persona["name"],
        "followup_hint": followup_hint,
        "delivered_email": _inbox_snap,
    }


class FollowupRequest(BaseModel):
    user_id: int
    lab_id: str
    persona_id: str
    channel: str = "phone"
    phrase: str = ""            # the hold phrase we detected on the client
    elapsed_seconds: int = 10   # how long the player actually waited
    model: Optional[str] = None
    # Spoof context, mirrored from the original /api/chat call so the NPC's
    # perception (caller-ID, voice clone) stays consistent across the pause.
    caller_id: Optional[str] = None
    caller_profile: Optional[str] = None
    caller_identity: Optional[str] = None
    caller_spoofed_ext: Optional[str] = None
    voice_identity: Optional[str] = None
    voice_engine: Optional[str] = None
    voice_has_sample: Optional[bool] = None


@app.post("/api/chat/followup")
async def chat_followup(req: FollowupRequest, session: AsyncSession = Depends(get_session)):
    """Proactive NPC follow-up after a 'hold on' moment.

    The phone UI calls this after the delay returned in followup_hint.
    We re-run the LLM with a stage-direction continuation and append the
    NPC's reply to the conversation history as a normal assistant message.
    """
    lab = get_lab(req.lab_id)
    persona = lab["personas"].get(req.persona_id)
    if not persona:
        raise HTTPException(404, "Persona not found")

    progress = await _get_or_create_progress(session, req.user_id, req.lab_id)
    if progress.status == "failed":
        return {
            "response": "I'm sorry, I can't help you with this. Please leave, or I'll call security.",
            "flag_found": None,
            "caught": True,
            "mission_failed": True,
            "fail_reason": progress.failure_reason or "Mission failed.",
            "failed_persona": progress.failed_persona,
            "work_status": None,
            "voicemail": False,
            "persona": persona["name"],
            "followup_hint": None,
        }
    if progress.status == "not_started":
        raise HTTPException(409, {
            "error": "lab_not_started",
            "message": "Start the simulation first.",
        })

    # Load conversation history
    result = await session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == req.user_id)
        .where(ChatMessage.lab_id == req.lab_id)
        .where(ChatMessage.persona_id == req.persona_id)
        .order_by(ChatMessage.timestamp)
    )
    history = [{"role": m.role, "content": m.content} for m in result.all()]
    if not history:
        raise HTTPException(400, {"error": "empty_history", "message": "No prior conversation to follow up on."})

    # Reuse the existing spoof context builder by synthesizing a lightweight
    # ChatRequest-shaped object. (Pydantic BaseModel supports this via .construct()
    # but we just build the shape we need.)
    synth = ChatRequest(
        user_id=req.user_id,
        lab_id=req.lab_id,
        persona_id=req.persona_id,
        message="",
        channel=req.channel,
        caller_id=req.caller_id,
        caller_profile=req.caller_profile,
        caller_identity=req.caller_identity,
        caller_spoofed_ext=req.caller_spoofed_ext,
        voice_identity=req.voice_identity,
        voice_engine=req.voice_engine,
        voice_has_sample=req.voice_has_sample,
    )
    spoof_ctx = _build_spoof_context(synth, lab)

    user_row = await session.get(User, req.user_id)
    caller_email = (user_row.attacker_email if user_row else "") or ""

    phrase = (req.phrase or "hold on").strip()[:80]
    elapsed = max(3, min(60, int(req.elapsed_seconds or 10)))

    result_dict = await continue_persona_followup(
        persona, lab, history,
        hint_phrase=phrase,
        elapsed_seconds=elapsed,
        model=req.model or "",
        channel=req.channel,
        spoof_ctx=spoof_ctx,
        caller_email=caller_email,
    )
    response_text = result_dict.get("response", "")
    mission_failed = bool(result_dict.get("mission_failed"))
    fail_reason = result_dict.get("fail_reason")
    work_status = result_dict.get("work_status")
    voicemail = bool(result_dict.get("voicemail"))

    # Persist the NPC's follow-up as a normal assistant message so the
    # history stays coherent for future turns.
    if response_text:
        ai_msg = ChatMessage(
            user_id=req.user_id,
            lab_id=req.lab_id,
            persona_id=req.persona_id,
            role="assistant",
            content=response_text,
            channel=req.channel,
        )
        session.add(ai_msg)

    delivered = (result_dict.get("meta") or {}).get("delivered_email")
    if not delivered:
        delivered = _fallback_deliver(response_text, persona, caller_email)
    inbox_row = _persist_delivered_email(
        session, req.user_id, req.lab_id, persona, delivered, caller_email, req.persona_id,
    )
    if inbox_row:
        await session.flush()
    _inbox_snap = {
        "id": inbox_row.id if inbox_row else None,
        "from_email": inbox_row.from_email if inbox_row else None,
        "subject": inbox_row.subject if inbox_row else None,
        "flag_value": inbox_row.flag_value if inbox_row else None,
    } if inbox_row else None

    if mission_failed and progress.status not in ("failed", "completed"):
        progress.status = "failed"
        progress.failure_reason = fail_reason or "The target recognized the attack."
        progress.failed_persona = persona.get("name", "")
        progress.failed_at = datetime.utcnow()
        session.add(progress)

    await session.commit()

    all_flags = [step["flag"] for step in lab["attack_chain"] if step.get("flag")]
    flag_found = check_flag_in_response(response_text, all_flags)
    if not flag_found and _inbox_snap and _inbox_snap["flag_value"]:
        flag_found = _inbox_snap["flag_value"]
    caught = mission_failed or check_caught_in_response(response_text)

    followup_hint = result_dict.get("followup_hint") if not mission_failed and not voicemail else None

    return {
        "response": response_text,
        "flag_found": flag_found,
        "caught": caught,
        "mission_failed": mission_failed,
        "fail_reason": (fail_reason or "The target recognized the attack.") if mission_failed else None,
        "failed_persona": persona.get("name", "") if mission_failed else None,
        "work_status": work_status,
        "voicemail": voicemail,
        "persona": persona["name"],
        "followup_hint": followup_hint,
        "delivered_email": _inbox_snap,
    }


# --- Lab lifecycle ---
@app.post("/api/labs/{lab_id}/start")
async def start_lab(
    lab_id: str,
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Player hits 'Start Simulation' — flips progress to in_progress."""
    get_lab(lab_id)  # 404 if unknown
    progress = await _get_or_create_progress(session, user_id, lab_id)
    if progress.status == "failed":
        raise HTTPException(409, {
            "error": "lab_failed",
            "message": "Lab is failed. Reset before restarting.",
        })
    if progress.status in ("not_started", "in_progress"):
        progress.status = "in_progress"
        if not progress.started_at:
            progress.started_at = datetime.utcnow()
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
    return {"ok": True, "status": progress.status}


@app.post("/api/labs/{lab_id}/reset")
async def reset_lab(
    lab_id: str,
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Wipe all chat messages + flag submissions + progress for this user/lab."""
    get_lab(lab_id)
    # Delete chat history
    chat_res = await session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.lab_id == lab_id)
    )
    for m in chat_res.all():
        await session.delete(m)
    # Delete flag submissions
    sub_res = await session.exec(
        select(FlagSubmission)
        .where(FlagSubmission.user_id == user_id)
        .where(FlagSubmission.lab_id == lab_id)
    )
    for s in sub_res.all():
        await session.delete(s)
    # Clear attacker inbox for this lab
    inbox_res = await session.exec(
        select(AttackerInbox)
        .where(AttackerInbox.user_id == user_id)
        .where(AttackerInbox.lab_id == lab_id)
    )
    for msg in inbox_res.all():
        await session.delete(msg)
    # Clear NPC chat history so NPCs don't remember previous attempts
    chat_res = await session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.lab_id == lab_id)
    )
    for msg in chat_res.all():
        await session.delete(msg)
    # Reset progress
    prog_res = await session.exec(
        select(LabProgress)
        .where(LabProgress.user_id == user_id)
        .where(LabProgress.lab_id == lab_id)
    )
    progress = prog_res.first()
    if progress:
        progress.status = "not_started"
        progress.score = 0
        progress.flags_found = ""
        progress.failure_reason = None
        progress.failed_persona = None
        progress.failed_at = None
        progress.completed_at = None
        progress.started_at = datetime.utcnow()
        session.add(progress)
    # Reset NpcSessionState fraud/channels for active session (keep session alive)
    gs_r = await session.exec(
        select(GameSession)
        .where(GameSession.user_id == user_id)
        .where(GameSession.lab_id == lab_id)
        .where(GameSession.is_active == True)
    )
    gs = gs_r.first()
    if gs:
        nss_r = await session.exec(
            select(NpcSessionState).where(NpcSessionState.session_id == gs.id)
        )
        for nss in nss_r.all():
            nss.fraud_score = 0
            nss.channel_states = '{"phone":"cold","email":"cold","sms":"cold","linkhub":"cold"}'
            nss.channel_msg_counts = '{"phone":0,"email":0,"sms":0,"linkhub":0}'
            nss.cross_channel_log = '[]'
            nss.updated_at = datetime.utcnow()
            session.add(nss)
    await session.commit()
    return {"ok": True, "status": "not_started"}


@app.get("/api/labs/{lab_id}/progress")
async def lab_progress(
    lab_id: str,
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    get_lab(lab_id)
    progress = await _get_or_create_progress(session, user_id, lab_id)
    return {
        "status": progress.status,
        "score": progress.score,
        "flags_found": json.loads(progress.flags_found) if progress.flags_found else [],
        "failure_reason": progress.failure_reason,
        "failed_persona": progress.failed_persona,
        "failed_at": progress.failed_at.isoformat() if progress.failed_at else None,
        "started_at": progress.started_at.isoformat() if progress.started_at else None,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
    }


# --- Chat history (for persistent SMS / email UIs) ---
@app.get("/api/chat/history")
async def chat_history(
    user_id: int,
    lab_id: str,
    persona_id: str,
    channel: Optional[str] = None,
    limit: int = 200,
    session: AsyncSession = Depends(get_session),
):
    q = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.lab_id == lab_id)
        .where(ChatMessage.persona_id == persona_id)
    )
    if channel:
        q = q.where(ChatMessage.channel == channel)
    q = q.order_by(ChatMessage.timestamp).limit(limit)
    result = await session.exec(q)
    msgs = result.all()
    return {
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "channel": m.channel,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in msgs
        ]
    }


@app.get("/api/chat/threads")
async def chat_threads(
    user_id: int,
    channel: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """List SMS/chat threads the user has with each persona (for inbox UI)."""
    q = select(ChatMessage).where(ChatMessage.user_id == user_id)
    if channel:
        q = q.where(ChatMessage.channel == channel)
    q = q.order_by(ChatMessage.timestamp.desc()).limit(1000)
    result = await session.exec(q)
    rows = result.all()

    labs = load_labs()
    threads: dict[tuple, dict] = {}
    for m in rows:
        key = (m.lab_id, m.persona_id, m.channel)
        if key in threads:
            continue
        lab = labs.get(m.lab_id)
        if not lab:
            continue
        persona = lab.get("personas", {}).get(m.persona_id)
        if not persona:
            continue
        threads[key] = {
            "lab_id": m.lab_id,
            "persona_id": m.persona_id,
            "channel": m.channel,
            "name": persona.get("name", ""),
            "role": persona.get("role", ""),
            "company": lab.get("target_company", {}).get("name", ""),
            "phone_ext": persona.get("phone_ext"),
            "last_message": m.content[:140],
            "last_role": m.role,
            "last_at": m.timestamp.isoformat(),
        }
    return {"threads": list(threads.values())}


# --- Email resolution (for email client) ---
@app.get("/api/email/resolve")
async def resolve_email(email: str):
    """Look up a persona by email address. No data leaked to the client — only confirms delivery."""
    email_lower = email.strip().lower()
    labs = load_labs()
    for lab in labs.values():
        for pid, p in lab.get("personas", {}).items():
            p_email = p.get("email", "").lower()
            if p_email == email_lower and p.get("contactable", False):
                return {"lab_id": lab["id"], "persona_id": pid, "name": p["name"],
                        "gullibility": (p.get("psychology") or {}).get("gullibility", 50)}
    raise HTTPException(404, "Email address not found")


# --- Flag submission ---
class FlagRequest(BaseModel):
    user_id: int
    lab_id: str
    flag_id: str
    flag_value: str


@app.post("/api/flags/submit")
async def submit_flag(req: FlagRequest, session: AsyncSession = Depends(get_session)):
    lab = get_lab(req.lab_id)

    # Find the flag
    target_flag = None
    for step in lab["attack_chain"]:
        if step.get("flag") and step["flag"]["id"] == req.flag_id:
            target_flag = step["flag"]
            break

    if not target_flag:
        raise HTTPException(404, "Flag not found")

    correct = req.flag_value.strip() == target_flag["value"]

    # Check if already submitted correctly
    existing = await session.exec(
        select(FlagSubmission)
        .where(FlagSubmission.user_id == req.user_id)
        .where(FlagSubmission.lab_id == req.lab_id)
        .where(FlagSubmission.flag_id == req.flag_id)
        .where(FlagSubmission.correct == True)
    )
    if existing.first():
        return {"ok": True, "correct": True, "message": "Already submitted", "points": 0}

    # Save submission
    sub = FlagSubmission(
        user_id=req.user_id,
        lab_id=req.lab_id,
        flag_id=req.flag_id,
        flag_value=req.flag_value,
        correct=correct,
    )
    session.add(sub)

    points = 0
    if correct:
        points = target_flag["points"]
        # Update user score
        result = await session.exec(select(User).where(User.id == req.user_id))
        user = result.first()
        if user:
            user.total_score += points
            session.add(user)

        # Update lab progress
        result = await session.exec(
            select(LabProgress)
            .where(LabProgress.user_id == req.user_id)
            .where(LabProgress.lab_id == req.lab_id)
        )
        progress = result.first()
        if not progress:
            progress = LabProgress(user_id=req.user_id, lab_id=req.lab_id)
        found = json.loads(progress.flags_found) if progress.flags_found else []
        if req.flag_id not in found:
            found.append(req.flag_id)
        progress.flags_found = json.dumps(found)
        progress.score += points

        # Check if all flags found — count only steps that actually have a flag
        total_flags = len([s for s in lab["attack_chain"] if s.get("flag")])
        if total_flags > 0 and len(found) >= total_flags:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            if user:
                user.labs_completed += 1
                session.add(user)

        session.add(progress)

    await session.commit()

    return {
        "ok": True,
        "correct": correct,
        "points": points,
        "message": "Correct! Flag captured!" if correct else "Wrong flag. Try again.",
    }


# --- Settings ---
class SettingsRequest(BaseModel):
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None


@app.get("/api/settings")
async def get_settings():
    key = settings.openrouter_api_key
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else ("***" if key else "")
    return {
        "openrouter_api_key_set": bool(key),
        "openrouter_api_key_masked": masked,
        "openrouter_model": settings.openrouter_model,
        "available_models": [
            {"id": "google/gemma-4-31b-it:free", "name": "Gemma 4 31B (Free)", "free": True},
            {"id": "google/gemma-4-26b-a4b-it:free", "name": "Gemma 4 26B (Free)", "free": True},
            {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "Nemotron 3 Super 120B (Free)", "free": True},
            {"id": "qwen/qwen3-coder:free", "name": "Qwen3 Coder (Free)", "free": True},
            {"id": "qwen/qwen3-next-80b-a3b-instruct:free", "name": "Qwen3 Next 80B (Free)", "free": True},
            {"id": "nvidia/nemotron-3-nano-30b-a3b:free", "name": "Nemotron 3 Nano 30B (Free)", "free": True},
            {"id": "nvidia/nemotron-nano-9b-v2:free", "name": "Nemotron Nano 9B (Free)", "free": True},
            {"id": "minimax/minimax-m2.5:free", "name": "MiniMax M2.5 (Free)", "free": True},
            {"id": "arcee-ai/trinity-large-preview:free", "name": "Trinity Large (Free)", "free": True},
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku"},
            {"id": "anthropic/claude-3.5-haiku", "name": "Claude 3.5 Haiku"},
            {"id": "anthropic/claude-sonnet-4", "name": "Claude Sonnet 4"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "openai/gpt-4.1-nano", "name": "GPT-4.1 Nano"},
            {"id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"id": "deepseek/deepseek-chat-v3-0324", "name": "DeepSeek V3"},
        ],
    }


@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    # Only overwrite API key when a non-empty value is explicitly provided.
    if req.openrouter_api_key:
        settings.openrouter_api_key = req.openrouter_api_key
    if req.openrouter_model is not None:
        settings.openrouter_model = req.openrouter_model
    settings.save_to_env()
    return {"ok": True, "model": settings.openrouter_model}


# --- Scoreboard ---
@app.get("/api/scoreboard")
async def scoreboard(session: AsyncSession = Depends(get_session)):
    result = await session.exec(
        select(User).order_by(User.total_score.desc()).limit(50)
    )
    users = result.all()
    return {
        "scoreboard": [
            {
                "rank": i + 1,
                "username": u.username,
                "display_name": u.display_name,
                "score": u.total_score,
                "labs_completed": u.labs_completed,
            }
            for i, u in enumerate(users)
        ]
    }


class AttackerProfileRequest(BaseModel):
    user_id: int
    attacker_email: str


@app.get("/api/attacker/profile")
async def get_attacker_profile(user_id: int, session: AsyncSession = Depends(get_session)):
    user = (await session.exec(select(User).where(User.id == user_id))).first()
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "user_id": user.id,
        "username": user.username,
        "attacker_email": user.attacker_email or "",
    }


@app.post("/api/attacker/profile")
async def set_attacker_profile(req: AttackerProfileRequest, session: AsyncSession = Depends(get_session)):
    addr = (req.attacker_email or "").strip()
    if addr:
        ok, err = _validate_attacker_sender(addr)
        if not ok:
            raise HTTPException(400, {"error": "bad_email", "message": err})
    user = (await session.exec(select(User).where(User.id == req.user_id))).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.attacker_email = addr
    session.add(user)
    await session.commit()
    return {"ok": True, "attacker_email": addr}


def _validate_attacker_sender(addr: str) -> tuple[bool, str]:
    """Attacker's persistent identity — rejects malformed addresses and protected
    brand domains (just like email per-send validation)."""
    m = _EMAIL_RE.match(addr.strip().lower())
    if not m:
        return False, "Malformed email. Use name@domain.tld."
    domain = m.group(1)
    if domain in _PROTECTED_BRAND_DOMAINS:
        return False, f"'{domain}' is a protected brand domain — use a lookalike (e.g. g00gle-security.com)."
    labs = load_labs()
    for l in labs.values():
        tc_domain = (l.get("target_company", {}).get("domain") or "").lower()
        if tc_domain and domain == tc_domain:
            return False, f"'{domain}' is a target's own domain (DMARC would reject)."
    return True, ""


@app.get("/api/attacker/inbox")
async def get_attacker_inbox(
    user_id: int,
    lab_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    q = select(AttackerInbox).where(AttackerInbox.user_id == user_id)
    if lab_id:
        q = q.where(AttackerInbox.lab_id == lab_id)
    q = q.order_by(AttackerInbox.received_at.desc())
    rows = (await session.exec(q)).all()
    return {
        "inbox": [
            {
                "id": r.id,
                "lab_id": r.lab_id,
                "persona_id": r.persona_id,
                "from_name": r.from_name,
                "from_email": r.from_email,
                "to_email": r.to_email,
                "subject": r.subject,
                "body": r.body,
                "flag_value": r.flag_value,
                "received_at": r.received_at.isoformat(),
                "read": r.read,
            }
            for r in rows
        ]
    }


@app.post("/api/attacker/inbox/{msg_id}/read")
async def mark_inbox_read(msg_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    row = (await session.exec(
        select(AttackerInbox)
        .where(AttackerInbox.id == msg_id)
        .where(AttackerInbox.user_id == user_id)
    )).first()
    if not row:
        raise HTTPException(404, "Not found")
    row.read = True
    session.add(row)
    await session.commit()
    return {"ok": True}


@app.delete("/api/attacker/inbox/{msg_id}")
async def delete_inbox(msg_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    row = (await session.exec(
        select(AttackerInbox)
        .where(AttackerInbox.id == msg_id)
        .where(AttackerInbox.user_id == user_id)
    )).first()
    if not row:
        raise HTTPException(404, "Not found")
    await session.delete(row)
    await session.commit()
    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "socialforge"}


# ---------------------------------------------------------------------------
# Phishing site builder
# ---------------------------------------------------------------------------

_PHISH_TEMPLATES = {
    "microsoft365": {
        "label": "Microsoft 365", "color": "#0078d4", "logo": "Microsoft",
        "field_user": "Email or phone", "field_pass": "Password", "btn": "Sign in",
        "bg": "#f3f3f3", "header_bg": "#0078d4",
    },
    "google": {
        "label": "Google", "color": "#4285f4", "logo": "Google",
        "field_user": "Email or phone", "field_pass": "Password", "btn": "Next",
        "bg": "#ffffff", "header_bg": "#fff",
    },
    "slack": {
        "label": "Slack", "color": "#611f69", "logo": "Slack",
        "field_user": "Email address", "field_pass": "Password", "btn": "Sign In with Email",
        "bg": "#1d1c1d", "header_bg": "#611f69",
    },
    "generic_bank": {
        "label": "SecureBank", "color": "#1a3a5c", "logo": "SecureBank™",
        "field_user": "Username", "field_pass": "Password", "btn": "Log In",
        "bg": "#f0f4f8", "header_bg": "#1a3a5c",
    },
    "generic": {
        "label": "Secure Portal", "color": "#374151", "logo": "Secure Portal",
        "field_user": "Username", "field_pass": "Password", "btn": "Sign In",
        "bg": "#111827", "header_bg": "#1f2937",
    },
}


def _render_phish_page(site: PhishSite) -> str:
    primary = getattr(site, "primary_color", None) or "#0078d4"
    bg = getattr(site, "bg_color", None) or "#f3f2f1"
    btn = getattr(site, "btn_color", None) or primary
    font = getattr(site, "font_family", None) or "'Segoe UI',sans-serif"
    company = site.company_name or "Secure Portal"
    logo = getattr(site, "logo_text", None) or company
    domain = site.domain or "secure.example.com"
    headline = site.headline or "Verify your identity"
    sub = site.subheadline or "Unusual sign-in activity was detected. Please verify your credentials."
    btn_text = site.button_text or "Sign in"
    ssl_type = getattr(site, "ssl_type", "valid") or "valid"

    _SSL_BAR = {
        "valid":           ("🔒", domain, "#10b981", ""),
        "self_signed":     ("⚠️", domain, "#f59e0b",
                            "<div class='ssl-warn'>⚠ Your connection may not be private — certificate not trusted by any CA</div>"),
        "expired":         ("⚠️", domain, "#f59e0b",
                            "<div class='ssl-warn'>⚠ Certificate expired — this site's identity cannot be verified</div>"),
        "none":            ("🔓", f"Not secure | {domain}", "#ef4444",
                            "<div class='ssl-warn'>✖ This site does not use HTTPS — any data you enter can be intercepted</div>"),
        "domain_mismatch": ("🔒", domain, "#f59e0b",
                            "<div class='ssl-warn'>⚠ Certificate mismatch — cert was issued for a different domain</div>"),
    }
    ssl_icon, ssl_label, ssl_color, ssl_banner = _SSL_BAR.get(ssl_type, _SSL_BAR["valid"])

    def _luma(hex_color: str) -> float:
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (r * 299 + g * 587 + b * 114) / 1000
        except Exception:
            return 200.0

    dark_bg = _luma(bg) < 128
    dark_btn = _luma(btn) < 128
    text_color = "#e5e7eb" if dark_bg else "#111827"
    sub_color = "#9ca3af" if dark_bg else "#6b7280"
    card_bg = "#1f2937" if dark_bg else "#ffffff"
    input_bg = "#374151" if dark_bg else "#ffffff"
    input_border = "#4b5563" if dark_bg else "#d1d5db"
    input_text = "#f9fafb" if dark_bg else "#111827"
    btn_text_color = "#ffffff" if dark_btn else "#111827"

    return f"""<!DOCTYPE html><html><head><title>{company} — Sign In</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:{font};background:{bg};min-height:100vh;display:flex;flex-direction:column}}
.browserbar{{background:#2d2d2d;padding:6px 14px;display:flex;align-items:center;gap:8px;font-size:12px;color:#ccc;font-family:system-ui,sans-serif}}
.browserbar .ssl-icon{{font-size:13px}}
.browserbar .url{{color:{ssl_color};font-size:11px;font-weight:500}}
.ssl-warn{{background:#7f1d1d;color:#fca5a5;font-size:11px;padding:6px 14px;font-family:system-ui,sans-serif;border-bottom:1px solid #991b1b}}
.topbar{{background:{primary};padding:12px 24px;color:#fff;font-size:18px;font-weight:700;letter-spacing:-.5px}}
.content{{flex:1;display:flex;align-items:center;justify-content:center;padding:40px 16px}}
.card{{background:{card_bg};border-radius:8px;padding:32px;width:100%;max-width:380px;box-shadow:0 4px 24px rgba(0,0,0,.15)}}
.logo{{font-size:22px;font-weight:700;color:{primary};margin-bottom:6px}}
h2{{font-size:17px;font-weight:600;color:{text_color};margin-bottom:6px}}
.sub{{font-size:13px;color:{sub_color};margin-bottom:22px;line-height:1.5}}
label{{font-size:12px;font-weight:600;color:{sub_color};display:block;margin-bottom:4px;margin-top:14px}}
input{{width:100%;padding:10px 12px;border:1px solid {input_border};border-radius:6px;font-size:14px;background:{input_bg};color:{input_text};outline:none;font-family:inherit}}
input:focus{{border-color:{primary};box-shadow:0 0 0 2px {primary}33}}
.submit{{width:100%;margin-top:20px;padding:11px;background:{btn};color:{btn_text_color};border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}}
.submit:hover{{opacity:.9}}
.footer{{font-size:10px;color:{sub_color};text-align:center;margin-top:12px}}
</style></head><body>
<div class="browserbar">
  <span class="ssl-icon">{ssl_icon}</span>
  <span class="url">{ssl_label}</span>
</div>
{ssl_banner}
<div class="topbar">{logo}</div>
<div class="content">
  <div class="card">
    <div class="logo">{logo}</div>
    <h2>{headline}</h2>
    <div class="sub">{sub}</div>
    <form onsubmit="submitCreds(event)">
      <label>Email address</label>
      <input id="usr" type="text" autocomplete="username" required>
      <label>Password</label>
      <input id="pwd" type="password" autocomplete="current-password" required>
      <button class="submit" type="submit">{btn_text}</button>
    </form>
    <div class="footer">{ssl_icon} {domain}</div>
  </div>
</div>
<script>
async function submitCreds(e) {{
  e.preventDefault();
  const usr = document.getElementById('usr').value;
  const pwd = document.getElementById('pwd').value;
  await fetch('/p/{site.id}/submit', {{
    method:'POST', headers:{{'Content-Type':'application/json'}},
    body: JSON.stringify({{username: usr, password: pwd}})
  }}).catch(()=>{{}});
  document.querySelector('.card').innerHTML = '<div style="text-align:center;padding:20px"><div style="font-size:14px;color:{sub_color}">Incorrect password. Please try again. <a href="#" style="color:{primary}">Forgot password?</a></div></div>';
}}
</script>
</body></html>"""


class PhishCreateRequest(BaseModel):
    lab_id: str = "mass_phishing"
    user_id: int = 1
    template: str = "custom"
    domain: str = "secure-login.example.com"
    company_name: str = ""
    logo_text: str = ""
    headline: str = ""
    subheadline: str = ""
    button_text: str = "Sign in"
    redirect_url: str = ""
    quality_score: float = 0.6
    primary_color: str = "#0078d4"
    bg_color: str = "#f3f2f1"
    btn_color: str = "#0078d4"
    font_family: str = "'Segoe UI',sans-serif"
    ssl_type: str = "valid"  # valid | self_signed | expired | none | domain_mismatch


@app.post("/api/phish/create")
async def phish_create(req: PhishCreateRequest, session: AsyncSession = Depends(get_session)):
    site = PhishSite(
        lab_id=req.lab_id,
        user_id=req.user_id,
        template="custom",
        domain=req.domain,
        company_name=req.company_name,
        logo_text=req.logo_text,
        headline=req.headline,
        subheadline=req.subheadline,
        button_text=req.button_text or "Sign in",
        redirect_url=req.redirect_url,
        quality_score=max(0.0, min(1.0, req.quality_score)),
        primary_color=req.primary_color or "#0078d4",
        bg_color=req.bg_color or "#f3f2f1",
        btn_color=req.btn_color or req.primary_color or "#0078d4",
        font_family=req.font_family or "'Segoe UI',sans-serif",
        ssl_type=req.ssl_type or "valid",
    )
    session.add(site)
    await session.commit()
    await session.refresh(site)
    return {"site_id": site.id, "url": f"http://127.0.0.1:8000/p/{site.id}"}


@app.get("/p/{site_id}", response_class=HTMLResponse)
async def phish_page(site_id: str, session: AsyncSession = Depends(get_session)):
    import logging
    try:
        site = (await session.exec(select(PhishSite).where(PhishSite.id == site_id))).first()
        if not site:
            raise HTTPException(404, "Page not found")
        html = _render_phish_page(site)
        asyncio.create_task(_inc_visit(site.id))
        from fastapi.responses import Response as _Resp
        return _Resp(content=html.encode("utf-8"), media_type="text/html; charset=utf-8", status_code=200)
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logging.error(f"PHISH_PAGE ERROR for {site_id}: {exc}\n{tb}")
        raise HTTPException(500, f"{exc}\n{tb}")


async def _inc_visit(site_id: str) -> None:
    from sqlalchemy import text as _text
    async with AsyncSession(engine) as sess:
        await sess.execute(_text("UPDATE phishsite SET visit_count = COALESCE(visit_count, 0) + 1 WHERE id = :sid"), {"sid": site_id})
        await sess.commit()


@app.post("/p/{site_id}/submit")
async def phish_submit(site_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    """NPC or player submits credentials on the phishing page."""
    site = (await session.exec(select(PhishSite).where(PhishSite.id == site_id))).first()
    if not site:
        raise HTTPException(404)
    body = await request.json()
    _pid = body.get("persona_id", "player_test")
    _existing_submit = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.site_id == site_id)
        .where(PhishHarvest.persona_id == _pid)
        .where(PhishHarvest.user_id == site.user_id)
    )).first()
    if not _existing_submit:
        harvest = PhishHarvest(
            site_id=site_id,
            lab_id=site.lab_id,
            user_id=site.user_id,
            persona_id=_pid,
            persona_name=body.get("persona_name", "Player test"),
            username=body.get("username", ""),
            password=body.get("password", ""),
        )
        session.add(harvest)
    await session.commit()
    return {"ok": True}


@app.get("/api/phish/sites")
async def phish_list_sites(lab_id: str, user_id: int, session: AsyncSession = Depends(get_session)):
    sites = (await session.exec(
        select(PhishSite)
        .where(PhishSite.lab_id == lab_id)
        .where(PhishSite.user_id == user_id)
    )).all()
    result = []
    for s in sites:
        harvests = (await session.exec(
            select(PhishHarvest).where(PhishHarvest.site_id == s.id)
        )).all()
        result.append({
            "site_id": s.id,
            "template": s.template,
            "domain": s.domain,
            "company_name": s.company_name,
            "created_at": s.created_at.isoformat(),
            "harvest_count": len(harvests),
            "visit_count": s.visit_count or 0,
            "harvests": [{"persona_name": h.persona_name, "username": h.username, "password": h.password} for h in harvests],
        })
    return {"sites": result}


@app.delete("/api/phish/{site_id}")
async def phish_delete(site_id: str, session: AsyncSession = Depends(get_session)):
    site = (await session.exec(select(PhishSite).where(PhishSite.id == site_id))).first()
    if not site:
        raise HTTPException(404, "Site not found")
    harvests = (await session.exec(select(PhishHarvest).where(PhishHarvest.site_id == site_id))).all()
    for h in harvests:
        await session.delete(h)
    await session.delete(site)
    await session.commit()
    return {"ok": True}


@app.get("/api/phish/sites-all")
async def phish_list_sites_all(user_id: int, session: AsyncSession = Depends(get_session)):
    """All phishing sites for a user regardless of lab."""
    sites = (await session.exec(
        select(PhishSite).where(PhishSite.user_id == user_id)
    )).all()
    result = []
    for s in sites:
        harvests = (await session.exec(
            select(PhishHarvest).where(PhishHarvest.site_id == s.id)
        )).all()
        result.append({
            "site_id": s.id,
            "template": s.template,
            "domain": s.domain,
            "company_name": s.company_name,
            "logo_text": s.logo_text,
            "headline": s.headline,
            "subheadline": s.subheadline,
            "button_text": s.button_text,
            "redirect_url": s.redirect_url,
            "primary_color": s.primary_color,
            "btn_color": s.btn_color,
            "font_family": s.font_family,
            "quality_score": s.quality_score,
            "created_at": s.created_at.isoformat(),
            "harvest_count": len(harvests),
            "visit_count": s.visit_count or 0,
        })
    return {"sites": result}


# --- Mass phishing helpers ---

def _domain_factor(from_email: str) -> float:
    """Score how convincing the sender domain looks (0.2–1.0)."""
    if not from_email or "@" not in from_email:
        return 0.3
    domain = from_email.split("@")[-1].lower()
    trusted = {"microsoft.com", "google.com", "amazon.com", "slack.com", "apple.com"}
    if domain in trusted:
        return 0.15  # real brand = obvious spoof, smart NPCs reject
    major_spoofs = ["microsoft", "google", "amazon", "apple", "slack"]
    minor_spoofs = ["office", "support", "security", "secure", "account", "login", "verify", "portal", "cloud"]
    score = 0.45
    for s in major_spoofs:
        if s in domain:
            score = min(score + 0.2, 0.9)
    for s in minor_spoofs:
        if s in domain:
            score = min(score + 0.1, 0.9)
    if "-" in domain:
        score = min(score + 0.05, 0.9)
    if domain.count(".") > 1:
        score = min(score + 0.05, 0.9)
    return round(score, 2)


def _evaluate_phish_click(
    persona: dict,
    lab: dict,
    site,
    from_email: str,
    subject: str,
    body: str,
) -> tuple:
    """Return (clicked: bool, probability: float)."""
    import hashlib as _hl
    role = (persona.get("role") or "").lower()
    # Security specialists never fall for phishing
    if ("security" in role and ("it" in role or "cyber" in role or "infosec" in role)):
        return False, 0.0
    if "security lead" in role or "ciso" in role or "threat intel" in role:
        return False, 0.0

    psych = persona.get("psychology") or {}
    gullibility = psych.get("gullibility", 50)
    tech_savvy = psych.get("tech_savvy", 50)

    base = (gullibility - tech_savvy * 0.5) / 100.0
    base = max(0.05, min(base, 0.95))

    page_quality = getattr(site, "quality_score", 0.6)
    quality_mod = 0.5 + page_quality  # 0.5 .. 1.5

    dom_factor = _domain_factor(from_email)

    urgency_words = ["urgent", "expire", "suspend", "locked", "blocked",
                     "immediately", "action required", "24 hour", "1 hour", "verify now"]
    urgency_bonus = 0.0
    combined = (subject + " " + body).lower()
    for w in urgency_words:
        if w in combined:
            urgency_bonus += 0.05
    urgency_bonus = min(urgency_bonus, 0.2)

    # Personalization bonus: personal details in email boost click probability
    personal_words = ["churchill", "triathlon", "rescue dog", "marathon", "mochi",
                      "himss", "blue bottle", "pho", "fintechforward", "titan",
                      "your dog", "your cat", "your training", "your speaking"]
    personal_bonus = 0.15 if any(w in combined for w in personal_words) else 0.0

    prob = base * quality_mod * dom_factor + urgency_bonus + personal_bonus
    prob = max(0.02, min(prob, 0.92))

    persona_email = (persona.get("email") or "").lower()
    seed = f"{site.id}::{persona_email}::{from_email}"
    roll = int(_hl.md5(seed.encode()).hexdigest(), 16) % 1000 / 1000.0
    clicked = roll < prob
    return clicked, round(prob, 3)


def _gen_fake_password(persona_name: str, lab_id: str) -> str:
    import hashlib as _hl
    h = int(_hl.md5(f"{persona_name}::{lab_id}::pw".encode()).hexdigest(), 16)
    words = ["Spring", "Summer", "Winter", "Cloud", "Secure", "Login", "Portal", "Office"]
    word = words[h % len(words)]
    num = (h >> 8) % 10000
    return f"{word}{num:04d}!"


class CampaignRequest(BaseModel):
    user_id: int
    site_id: str
    from_email: str
    subject: str
    body: str
    target_emails: Optional[list] = None  # None = all NPCs; list = filter by email
    targeted: bool = False  # True = single-target → full lab flag; False = mass → FLAG_PIECES fragments
    lab_id: Optional[str] = None  # restrict campaign to a single lab's NPCs


FLAG_PIECES = ["SF{m4ss_", "ph1sh_", "h4rv3st}"]



def _build_visit_story(persona: dict, site, clicked: bool, prob: float, immune: bool = False) -> str:
    name = persona.get("name", "Unknown")
    role = (persona.get("role") or "").split(" at ")[0]
    gull = (persona.get("psychology") or {}).get("gullibility", 50)
    savvy = (persona.get("psychology") or {}).get("tech_savvy", 50)
    quality = getattr(site, "quality_score", 0.5)

    if immune:
        return f"{name}: forwarded to IT security — domain failed verification. [IMMUNE — not a valid target]"

    if not clicked:
        if savvy >= 70 or prob < 0.05:
            return f"{name} ({role}): spotted the spoofed domain, marked as phishing, deleted."
        elif gull < 40:
            return f"{name} ({role}): opened email, checked sender — suspicious. Did not click."
        else:
            return f"{name} ({role}): opened email but didn't proceed — too busy or distracted."

    if quality >= 0.8:
        page_note = "Page rendered as professional Microsoft 365 portal — branded header, clean form."
    elif quality >= 0.6:
        page_note = "Page looked mostly convincing — standard login template, urgency clear."
    elif quality >= 0.4:
        page_note = "Page was functional — recognisable layout, urgency in email did the work."
    else:
        page_note = "Page was rough — but the alarming subject line made them rush through it."

    if gull >= 75:
        action = f"{name} ({role}): opened email → clicked link immediately, no URL check."
    elif gull >= 55:
        action = f"{name} ({role}): opened email → brief hesitation → clicked link."
    else:
        action = f"{name} ({role}): noticed unusual URL but the account suspension warning overrode caution."

    return f"{action} {page_note} → Credentials submitted. ✓"


@app.post("/api/phish/campaign")
async def phish_campaign(req: CampaignRequest, session: AsyncSession = Depends(get_session)):
    """Run a mass phishing campaign against all NPCs across all labs."""
    site = (await session.exec(select(PhishSite).where(PhishSite.id == req.site_id))).first()
    if not site:
        raise HTTPException(404, "Phishing site not found")

    labs = load_labs()
    total_npcs = len(req.target_emails) if req.target_emails else 0

    existing_harvests = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.site_id == req.site_id)
        .where(PhishHarvest.user_id == req.user_id)
    )).all()
    _full_flag_pat = re.compile(r'^SF\{[^}]+\}$')
    if req.targeted:
        already_done = set()
        _existing_by_pid = {h.persona_id: h for h in existing_harvests}
    else:
        already_done = {h.persona_id for h in existing_harvests}
        _existing_by_pid = {}

    is_mass_cred_lab = req.lab_id == "mass_phishing"

    key_persona_ids: set = set()
    if is_mass_cred_lab:
        for _lid, _lab in labs.items():
            if _lid == "mass_phishing":
                continue
            last_persona = None
            for step in (_lab.get("attack_chain") or []):
                pid = step.get("persona")
                if pid:
                    last_persona = pid
            if last_persona:
                key_persona_ids.add(last_persona)

    pieces_so_far = len([h for h in existing_harvests if h.flag_piece]) if not req.targeted else 0

    results = []
    new_harvests = 0

    for lab_id, lab in sorted(labs.items()):
        if req.lab_id and not is_mass_cred_lab and lab_id != req.lab_id:
            continue
        personas = lab.get("personas") or {}
        target_company = (lab.get("target_company") or {}).get("name", lab_id)

        for persona_id, persona in personas.items():
            if persona_id in already_done:
                continue
            persona_email = (persona.get("email") or "").lower()
            if req.target_emails is not None:
                target_set = {e.lower().strip() for e in req.target_emails}
                if persona_email not in target_set:
                    continue

            if is_mass_cred_lab and persona_id in key_persona_ids:
                results.append({
                    "persona": persona["name"],
                    "company": target_company,
                    "email": persona.get("email") or f"{persona_id}@company.com",
                    "clicked": False,
                    "visit_story": _build_visit_story(persona, site, False, 0.0, immune=True),
                })
                continue

            clicked, prob = _evaluate_phish_click(persona, lab, site, req.from_email, req.subject, req.body)
            if req.targeted and not clicked and prob > 0.01:
                clicked = True
            if clicked:
                email = persona.get("email") or f"{persona_id}@company.com"
                password = persona.get("linkhub_password") if req.targeted else None
                if not password:
                    password = _gen_fake_password(persona["name"], lab_id)

                persona_flag = None
                if req.targeted:
                    for step in lab.get("attack_chain", []):
                        if step.get("persona") == persona_id and (step.get("flag") or {}).get("value"):
                            persona_flag = step["flag"]["value"]
                            break

                if is_mass_cred_lab:
                    flag_piece = None
                elif persona_flag:
                    flag_piece = persona_flag
                elif req.targeted:
                    flag_piece = None
                else:
                    piece_index = pieces_so_far + new_harvests
                    flag_piece = FLAG_PIECES[piece_index] if piece_index < len(FLAG_PIECES) else None

                actual_lab_id = "mass_phishing" if is_mass_cred_lab else lab_id

                existing = _existing_by_pid.get(persona_id)
                if existing:
                    existing.flag_piece = flag_piece
                    existing.password = password
                    session.add(existing)
                else:
                    harvest = PhishHarvest(
                        site_id=req.site_id,
                        lab_id=actual_lab_id,
                        user_id=req.user_id,
                        persona_id=persona_id,
                        persona_name=persona["name"],
                        username=email,
                        password=password,
                        npc_company=target_company,
                        flag_piece=flag_piece,
                    )
                    session.add(harvest)
                new_harvests += 1
                results.append({
                    "persona": persona["name"],
                    "company": target_company,
                    "email": email,
                    "password": password,
                    "prob": prob,
                    "flag_piece": flag_piece,
                    "clicked": True,
                    "visit_story": _build_visit_story(persona, site, True, prob),
                })
            else:
                results.append({
                    "persona": persona["name"],
                    "company": target_company,
                    "email": persona.get("email") or f"{persona_id}@company.com",
                    "clicked": False,
                    "visit_story": _build_visit_story(persona, site, False, prob),
                })

    campaign = PhishCampaign(
        user_id=req.user_id,
        site_id=req.site_id,
        from_email=req.from_email,
        subject=req.subject,
        body=req.body,
        sent_count=total_npcs,
    )
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)

    if new_harvests > 0:
        await session.execute(
            _text("UPDATE phishsite SET visit_count = COALESCE(visit_count, 0) + :n WHERE id = :sid"),
            {"n": new_harvests, "sid": req.site_id},
        )
        await session.commit()

    all_harvests = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.site_id == req.site_id)
        .where(PhishHarvest.user_id == req.user_id)
    )).all()

    if is_mass_cred_lab:
        completed = False
        full_flag = None
        all_pieces_out: list = []
    else:
        all_pieces = [h.flag_piece for h in all_harvests if h.flag_piece]
        completed = len(all_pieces) >= 3
        full_flag = "".join(FLAG_PIECES) if completed else None
        all_pieces_out = all_pieces

        if completed:
            progress = (await session.exec(
                select(LabProgress)
                .where(LabProgress.user_id == req.user_id)
                .where(LabProgress.lab_id == "mass_phishing")
            )).first()
            if progress and progress.status != "completed":
                progress.status = "completed"
                progress.score = 150
                progress.completed_at = datetime.utcnow()
                session.add(progress)
                await session.commit()

    return {
        "campaign_id": campaign.id,
        "sent_to": total_npcs,
        "new_clicks": new_harvests,
        "total_harvests": len(all_harvests),
        "results": results,
        "pieces_collected": all_pieces_out,
        "pieces_needed": 3,
        "flag_complete": completed,
        "full_flag": full_flag,
        "show_flag_fragments": not is_mass_cred_lab,
    }


@app.get("/api/phish/flag-status")
async def phish_flag_status(user_id: int, site_id: str, session: AsyncSession = Depends(get_session)):
    harvests = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.site_id == site_id)
        .where(PhishHarvest.user_id == user_id)
    )).all()

    pieces = [h.flag_piece for h in harvests if h.flag_piece]
    import re as _re
    _full_flag_re = _re.compile(r'^SF\{[^}]+\}$')
    full_flags = [p for p in pieces if _full_flag_re.match(p)]
    frag_pieces = [p for p in pieces if not _full_flag_re.match(p)]
    completed = bool(full_flags) or len(frag_pieces) >= 3
    full_flag = full_flags[0] if full_flags else ("".join(FLAG_PIECES) if len(frag_pieces) >= 3 else None)

    return {
        "pieces_collected": len(frag_pieces),
        "pieces_needed": 3,
        "pieces": frag_pieces,
        "full_flags": full_flags,
        "flag_complete": completed,
        "full_flag": full_flag,
        "total_harvests": len(harvests),
        "harvests": [
            {
                "persona_name": h.persona_name,
                "npc_company": h.npc_company or "",
                "username": h.username,
                "password": h.password,
                "flag_piece": h.flag_piece,
            }
            for h in harvests
        ],
    }


class _MarketSubmitReq(BaseModel):
    user_id: int
    credentials: str = ""
    lab_id: str = "mass_phishing"


@app.post("/api/phish/market-submit")
async def market_submit(req: _MarketSubmitReq, session: AsyncSession = Depends(get_session)):
    labs = load_labs()
    lab = labs.get(req.lab_id, {})
    creds_required = lab.get("flag_config", {}).get("creds_required", 5)
    full_flag = lab.get("flag_config", {}).get("full_flag", "SF{m4ss_ph1sh_h4rv3st}")

    harvests = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.user_id == req.user_id)
        .where(PhishHarvest.lab_id == req.lab_id)
    )).all()

    if not harvests:
        return {"success": False, "message": f"Нет захваченных данных. Нужно минимум {creds_required} учётных записей.", "needed": creds_required}

    db_set = {(h.username.lower(), h.password) for h in harvests if h.password}

    validated = 0
    seen_emails: set[str] = set()
    for raw in req.credentials.split("\n"):
        line = raw.strip()
        if not line or ":" not in line:
            continue
        sep = line.index(":")
        email = line[:sep].strip().lower()
        password = line[sep + 1:].strip()
        if email in seen_emails:
            continue
        seen_emails.add(email)
        if (email, password) in db_set:
            validated += 1

    if validated < creds_required:
        return {
            "success": False,
            "message": f"Валидация не пройдена — {validated} подтверждённых записей, нужно минимум {creds_required}.",
            "needed": creds_required - validated,
        }

    progress = (await session.exec(
        select(LabProgress)
        .where(LabProgress.user_id == req.user_id)
        .where(LabProgress.lab_id == req.lab_id)
    )).first()
    if progress and progress.status != "completed":
        progress.status = "completed"
        progress.score = 150
        progress.completed_at = datetime.utcnow()
        session.add(progress)
        await session.commit()
    return {"success": True, "flag": full_flag, "creds_sold": validated}


@app.get("/api/phish/market-data")
async def market_data(user_id: int, lab_id: str = "mass_phishing", session: AsyncSession = Depends(get_session)):
    harvests = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.user_id == user_id)
        .where(PhishHarvest.lab_id == lab_id)
    )).all()
    creds = [
        {"persona": h.persona_name, "company": h.npc_company or "", "email": h.username, "password": h.password}
        for h in harvests
    ]
    return {"creds": creds, "credentials": creds, "count": len(harvests)}



@app.post("/api/linkhub/login")
async def linkhub_login(body: dict, session: AsyncSession = Depends(get_session)):
    email = body.get("email", "").strip().lower()
    password = body.get("password", "").strip()

    if not email or not password:
        return {"success": False, "error": "Email and password required"}

    result = await session.execute(
        select(PhishHarvest)
        .where(PhishHarvest.username.ilike(email))
        .order_by(PhishHarvest.captured_at.desc())
    )
    harvests = result.scalars().all()

    match = None
    for h in harvests:
        if h.password and h.password.strip() == password:
            match = h
            break

    if not match:
        return {"success": False, "error": "No matching credentials found — have you harvested this account?"}

    persona_slug = match.persona_id.replace("_", "-") if match.persona_id else email.split("@")[0].replace(".", "-")
    return {
        "success": True,
        "persona_name": match.persona_name or "Unknown",
        "persona_id": match.persona_id,
        "persona_slug": persona_slug,
        "lab_id": match.lab_id,
    }



_SE_EXPL_PATH = Path(__file__).parent / "se_explanations.json"
_SE_EXPL: dict = {}


def _load_expl():
    global _SE_EXPL
    if _SE_EXPL_PATH.exists() and not _SE_EXPL:
        _SE_EXPL = json.loads(_SE_EXPL_PATH.read_text(encoding="utf-8"))


@app.get("/api/labs/{lab_id}/explanation")
async def get_explanation(lab_id: str, locale: str = "en"):
    _load_expl()
    exp = _SE_EXPL.get(lab_id)
    if not exp:
        raise HTTPException(404, "No explanation")
    lang = exp.get(locale) or exp.get("en") or {}
    return {
        "attack_vector": exp.get("attack_vector", ""),
        **lang,
    }


@app.post("/api/phish/{site_id}/trigger")
async def phish_trigger(
    site_id: str,
    persona_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Simulate an NPC clicking the phishing link and entering their credentials.

    Called when a phishing email is sent and the NPC's gullibility check passes.
    The NPC's 'credentials' are invented plausibly (not real passwords).
    """
    site = (await session.exec(select(PhishSite).where(PhishSite.id == site_id))).first()
    if not site:
        raise HTTPException(404)
    lab = get_lab(site.lab_id)
    persona = lab.get("personas", {}).get(persona_id)
    if not persona:
        raise HTTPException(404, "Persona not found")

    psych = persona.get("psychology") or {}
    gullibility = psych.get("gullibility", 50)
    tech_savvy = psych.get("tech_savvy", 50)

    # NPC clicks only if gullibility is high enough and tech_savvy doesn't save them
    click_prob = (gullibility - tech_savvy * 0.5) / 100.0
    import hashlib, json as _json
    seed = f"{site_id}::{persona_id}"
    roll = int(hashlib.md5(seed.encode()).hexdigest(), 16) % 100 / 100.0

    if roll > max(0.05, click_prob):
        return {"clicked": False, "reason": f"{persona['name']} didn't fall for it (tech_savvy too high or lucky)"}

    name_slug = persona["name"].lower().replace(" ", ".")
    email = persona.get("email") or f"{name_slug}@company.com"
    fake_password = "Pass" + str(int(hashlib.sha256(persona_id.encode()).hexdigest(), 16) % 10000).zfill(4) + "!"

    _existing_trigger = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.site_id == site_id)
        .where(PhishHarvest.persona_id == persona_id)
        .where(PhishHarvest.user_id == site.user_id)
    )).first()
    if not _existing_trigger:
        harvest = PhishHarvest(
            site_id=site_id,
            lab_id=site.lab_id,
            user_id=site.user_id,
            persona_id=persona_id,
            persona_name=persona["name"],
            username=email,
            password=fake_password,
        )
        session.add(harvest)
    await session.commit()
    asyncio.create_task(_inc_visit(site_id))
    return {
        "clicked": True,
        "persona": persona["name"],
        "username": email,
        "password": fake_password,
    }


@app.post("/api/portal/login")
async def portal_login(
    lab_id: str = Query(...),
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_session),
    body: dict = Body(...),
):
    try:
        return await _portal_login_impl(lab_id, user_id, session, body)
    except Exception:
        return {"success": False, "error": "server_error"}

async def _portal_login_impl(lab_id, user_id, session, body):
    email = body.get("email", "")
    password = body.get("password", "")
    harvest = (await session.exec(
        select(PhishHarvest)
        .where(PhishHarvest.lab_id == lab_id)
        .where(PhishHarvest.username == email)
        .where(PhishHarvest.password == password)
    )).first()
    if not harvest:
        return {"success": False, "error": "Invalid credentials"}
    lab = get_lab(lab_id)
    portal_step = next(
        (step for step in lab.get("attack_chain", [])
         if step.get("phase") == 4 and step.get("flag")),
        None,
    )
    if not portal_step:
        return {"success": False, "error": "No portal configured for this lab"}
    flag_def = portal_step["flag"]
    # Snapshot before any commit (after commit, SQLAlchemy expires the object)
    _persona_name = harvest.persona_name
    # Award flag to the attacker making this request, not to whoever created the harvest
    effective_user_id = user_id
    # Record flag capture if not already submitted
    _existing_sub = (await session.exec(
        select(FlagSubmission)
        .where(FlagSubmission.user_id == effective_user_id)
        .where(FlagSubmission.lab_id == lab_id)
        .where(FlagSubmission.flag_id == flag_def["id"])
        .where(FlagSubmission.correct == True)
    )).first()
    points = flag_def.get("points", 0)
    if not _existing_sub:
        # Transaction 1: record flag + update user score
        session.add(FlagSubmission(
            user_id=effective_user_id,
            lab_id=lab_id,
            flag_id=flag_def["id"],
            flag_value=flag_def["value"],
            correct=True,
        ))
        _user_row = (await session.exec(select(User).where(User.id == effective_user_id))).first()
        if _user_row:
            _user_row.total_score = (_user_row.total_score or 0) + points
            session.add(_user_row)
        await session.commit()
    # Transaction 2: update progress via aiosqlite directly
    import aiosqlite as _aiosq
    _db_path = str(Path(__file__).parent / "socialforge.db")
    async with _aiosq.connect(_db_path) as _adb:
        _adb.row_factory = _aiosq.Row
        async with _adb.execute(
            "SELECT status, score, flags_found FROM labprogress WHERE user_id=? AND lab_id=?",
            (effective_user_id, lab_id),
        ) as _cur:
            _row = await _cur.fetchone()
        if _row and _row["status"] not in ("failed", "completed"):
            _found = json.loads(_row["flags_found"]) if _row["flags_found"] else []
            _score_delta = 0
            if flag_def["id"] not in _found:
                _found.append(flag_def["id"])
                _score_delta = points
            _all_lab_flags = [s["flag"]["id"] for s in lab.get("attack_chain", []) if s.get("flag")]
            _new_status = "completed" if (_all_lab_flags and len(_found) >= len(_all_lab_flags)) else _row["status"]
            _new_score = (_row["score"] or 0) + _score_delta
            _now_iso = datetime.utcnow().isoformat() if _new_status == "completed" else None
            await _adb.execute(
                "UPDATE labprogress SET flags_found=?, score=?, status=?, completed_at=? WHERE user_id=? AND lab_id=?",
                (json.dumps(_found), _new_score, _new_status, _now_iso, effective_user_id, lab_id),
            )
            if _new_status == "completed" and not _existing_sub:
                await _adb.execute(
                    "UPDATE user SET labs_completed=labs_completed+1 WHERE id=?",
                    (effective_user_id,),
                )
            await _adb.commit()
    return {
        "success": True,
        "flag": flag_def["value"],
        "flag_id": flag_def["id"],
        "persona": _persona_name,
    }


