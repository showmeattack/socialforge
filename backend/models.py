"""Database models."""
import uuid as _uuid
import random as _random
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str
    display_name: str = ""
    locale: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_score: int = 0
    labs_completed: int = 0
    # Attacker identity — what NPCs see as the player's "From:" address and
    # where NPCs "deliver" emails when asked to send something to the caller.
    attacker_email: str = ""


class LabProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    status: str = "not_started"  # not_started | in_progress | completed | failed
    score: int = 0
    flags_found: str = ""  # JSON list of flag IDs
    failure_reason: Optional[str] = None
    failed_persona: Optional[str] = None
    failed_at: Optional[datetime] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    persona_id: str  # which NPC
    role: str  # user | assistant
    content: str
    channel: str = "email"  # email | chat | phone | sms
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FlagSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    flag_id: str
    flag_value: str
    correct: bool
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class PhishSite(SQLModel, table=True):
    """A fake login page created by the player."""
    id: str = Field(default_factory=lambda: _uuid.uuid4().hex[:8], primary_key=True)
    lab_id: str = Field(index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    template: str = "microsoft365"
    domain: str = ""
    company_name: str = ""
    logo_text: str = ""
    page_title: str = ""
    # Constructor fields (added via migration)
    headline: str = ""
    subheadline: str = ""
    button_text: str = "Sign in"
    redirect_url: str = ""
    quality_score: float = 0.6
    primary_color: str = "#0078d4"
    bg_color: str = "#f3f2f1"
    btn_color: str = "#0078d4"
    font_family: str = "'Segoe UI',sans-serif"
    ssl_type: str = Field(default="valid")  # valid | self_signed | expired | none | domain_mismatch
    visit_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PhishHarvest(SQLModel, table=True):
    """Credentials captured when an NPC 'visits' a phishing page."""
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: str = Field(index=True)
    lab_id: str
    user_id: int
    persona_id: str
    persona_name: str
    username: str = ""
    password: str = ""
    # Added via migration
    campaign_id: Optional[str] = None
    npc_company: str = ""
    flag_piece: Optional[str] = None
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class PhishCampaign(SQLModel, table=True):
    """A mass phishing campaign run by the player."""
    id: str = Field(default_factory=lambda: _uuid.uuid4().hex[:8], primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    site_id: str = Field(index=True)
    from_email: str = ""
    subject: str = ""
    body: str = ""
    sent_count: int = 0
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class GameSession(SQLModel, table=True):
    """One playthroughs of a lab. All NPC states are scoped to a session."""
    id: str = Field(default_factory=lambda: _uuid.uuid4().hex[:12], primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    is_active: bool = Field(default=True)
    daily_seed: int = Field(default_factory=lambda: _random.randint(1, 999999))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class NpcSessionState(SQLModel, table=True):
    """Per-NPC state within a GameSession: fraud score, FSM states, cross-channel log."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    persona_id: str = Field(index=True)
    fraud_score: int = Field(default=0)
    # JSON: {"phone":"cold","email":"cold","sms":"cold","linkhub":"cold"}
    channel_states: str = Field(default='{"phone":"cold","email":"cold","sms":"cold","linkhub":"cold"}')
    # JSON: {"phone":0,"email":0,"sms":0,"linkhub":0}
    channel_msg_counts: str = Field(default='{"phone":0,"email":0,"sms":0,"linkhub":0}')
    # JSON list — last 5 cross-channel events (compact dicts)
    cross_channel_log: str = Field(default='[]')
    # JSON — mood_delta, workload, events, effective_gullibility_modifier
    daily_context: str = Field(default='{}')
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AttackerInbox(SQLModel, table=True):
    """Emails 'delivered' to the player when an NPC sends something in-fiction.

    When a compromised NPC agrees to email a report / document / credentials
    to the caller's address, ai_engine extracts the payload and the backend
    writes it here. The player reads it through the SF Mail inbox view.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    persona_id: str  # which NPC sent it
    from_name: str = ""         # human display name
    from_email: str = ""        # NPC's email address
    to_email: str = ""          # what the attacker asked for
    subject: str = ""
    body: str = ""
    flag_value: Optional[str] = None   # extracted SF{...} if present
    received_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
