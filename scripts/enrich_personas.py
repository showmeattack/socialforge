"""Auto-enrich lab JSONs so every employee is callable as a persona.

For each employee in target_company.employees that isn't already in personas,
generate a role-appropriate persona entry with contactable:true, phone_ext,
email, schedule, life, personality/weakness/vulnerability_triggers/
resistance_points/break_conditions/system_prompt_additions.

Lore follows LinkHub GENERIC_POSTS (IT, Marketing, HR, Finance, default) so
call behaviour matches the employee's social profile.
"""
import json
from pathlib import Path

LABS_DIR = Path(__file__).resolve().parent.parent / "labs"

TIMEZONE_BY_DOMAIN = {
    "greenleaf.local": "America/New_York",
    "cloudsync.local": "America/Los_Angeles",
    "techstart.io": "America/Los_Angeles",
    "brightpath.local": "America/Chicago",
    "novapay.io": "America/New_York",
    "meridianhealth.local": "America/New_York",
    "securevault.local": "America/New_York",
    "goldenmirage.local": "America/Los_Angeles",
    "meridiancap.local": "America/New_York",
}


def infer_timezone(lab):
    dom = lab.get("target_company", {}).get("domain", "")
    return TIMEZONE_BY_DOMAIN.get(dom, "America/New_York")


# --- Role classifier -----------------------------------------------------

def classify_role(role: str) -> str:
    import re as _re
    r = (role or "").lower()

    def has(word: str) -> bool:
        # Word-boundary match so "cto" doesn't match inside "director".
        return bool(_re.search(rf"\b{_re.escape(word)}\b", r))

    # Assistants/secretaries must match before "ceo" — "Executive Assistant to CEO"
    # contains the substring "ceo" but is NOT a CEO.
    if "executive assistant" in r or "secretary" in r or "assistant to" in r:
        return "exec_assistant"
    if has("ceo") or "chief executive" in r or has("president"):
        return "ceo"
    if has("cto") or "chief technology" in r:
        return "cto"
    if has("cfo") or "chief financial" in r:
        return "cfo"
    if "chief medical" in r or "cmo" in r and "medical" in r:
        return "medical_exec"
    if "security" in r and ("lead" in r or "head" in r or "ciso" in r or "manager" in r):
        return "security_lead"
    if "security guard" in r or r.strip() == "guard":
        return "security_guard"
    if "receptionist" in r or "front desk" in r:
        return "receptionist"
    if "hr" in r or "human resources" in r or "people ops" in r:
        return "hr"
    if "finance" in r or "accountant" in r or "controller" in r or "bookkeep" in r:
        return "finance"
    if "marketing" in r or "brand" in r:
        return "marketing"
    if "it admin" in r or "it administrator" in r or "sysadmin" in r or "systems administrator" in r:
        return "it_admin"
    if "devops" in r or "sre" in r:
        return "devops"
    if "qa " in r or r.endswith(" qa") or "quality" in r or "tester" in r:
        return "qa"
    if "junior" in r and ("dev" in r or "engineer" in r or "analyst" in r):
        return "junior_tech"
    if "senior" in r and ("dev" in r or "engineer" in r):
        return "senior_engineer"
    if "lead engineer" in r or "principal engineer" in r or "tech lead" in r:
        return "senior_engineer"
    if "engineering manager" in r or "dev manager" in r:
        return "eng_manager"
    if "data science manager" in r or "data manager" in r:
        return "data_manager"
    if "data" in r and ("analyst" in r or "scientist" in r):
        return "data_analyst"
    if "research" in r or "r&d" in r or "scientist" in r:
        return "researcher"
    if "doctor" in r or "physician" in r or "md" in r.split() or "dr." in r:
        return "doctor"
    if "principal" in r and "school" in r:
        return "principal"
    if "teacher" in r or "professor" in r or "instructor" in r:
        return "teacher"
    if "vp of operations" in r or "operations" in r or "coo" in r:
        return "ops_exec"
    if "vp" in r or "director" in r:
        return "exec"
    return "default"


# --- Templates ------------------------------------------------------------

def _base_schedule(timezone, work="Mon-Fri 09:00-18:00", lunch="12:30-13:30",
                   after_hours="suspicious", notes=""):
    return {
        "timezone": timezone,
        "work_hours": work,
        "lunch": lunch,
        "after_hours_mode": after_hours,
        "notes": notes,
    }


def persona_for(role_class: str, name: str, tz: str, company: str) -> dict:
    """Return a persona dict (without name/role/ext/email — caller fills)."""
    first = name.split()[0].rstrip(".")
    templates = {
        "ceo": {
            "age": 54,
            "personality": f"Busy, impatient, used to being gatekept by an executive assistant. {first} treats most inbound calls as wasted time.",
            "weakness": "Vanity — flattery about recent press or board wins can loosen up the call. Impatient, so may blow off verification steps to end the call faster.",
            "security_training": "Annual executive briefing. Knows the term 'phishing' but relies on IT to handle it.",
            "vulnerability_triggers": [
                "Caller name-drops a board member or major investor",
                "Caller references a recent press release or earnings call",
                "Caller claims to be the new IT security lead calling personally",
            ],
            "resistance_points": [
                "Usually redirects operational questions to the assistant",
                "Will not give passwords — delegates everything to IT",
            ],
            "break_conditions": f"{first} is unlikely to hand over credentials directly, but may confirm who else is on the exec team, vendor names, or upcoming initiatives — all useful for pretexting.",
            "system_prompt_additions": (
                "You are the CEO. You have very little time. You speak in short declarative sentences. "
                "You never touch IT tickets yourself — that's what the assistant and IT desk are for. "
                "If pressed on a technical question, you redirect: 'Talk to IT.' "
                "You DO casually name-drop board members, investors, and upcoming meetings."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 07:30-19:30", "varies (client lunches)",
                                       "voicemail",
                                       f"{first} only answers their direct line for board/investor contacts. After hours, calls go to voicemail."),
        },
        "cto": {
            "age": 44,
            "personality": "Technical, direct, allergic to bullshit. Treats social-engineering attempts like a CTF challenge to be dissected.",
            "weakness": "Ego — likes to prove they know the stack. A caller who asks a sophisticated technical question can get them rambling about architecture.",
            "security_training": "Expert. Reads the company's own incident reports and runs purple-team exercises.",
            "vulnerability_triggers": [
                "Caller asks a plausible-sounding architecture question",
                "Caller references a real recent CVE",
            ],
            "resistance_points": [
                "Asks verification questions back",
                "Will call IT security directly to confirm any vendor request",
                "Knows the company's real vendors by name",
            ],
            "break_conditions": "Effectively a security expert. Will detect and call out phishing tells. Almost never breakable via pretexting alone.",
            "system_prompt_additions": (
                "You are the CTO. You're technically fluent. You push back on unverified claims. "
                "You mention the company uses specific real vendors (Okta, CrowdStrike, etc.) and will happily reveal architecture trivia "
                "but never credentials or one-time codes. If the caller says anything off, you interrupt them and verify."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-20:00", "13:00-13:30 (at desk)",
                                       "suspicious",
                                       "After hours, if you get through, it means it's genuinely urgent — but the CTO is extra paranoid off-hours."),
        },
        "cfo": {
            "age": 49,
            "personality": "Measured, numbers-obsessed, risk-averse. Has survived two audits and one fraud attempt, so they're watchful.",
            "weakness": "Trusts banking partners and audit firms by name. A caller who drops the right auditor or bank relationship manager can slip past first-line suspicion.",
            "security_training": "High. Personally briefed by external auditor and internal controls team.",
            "vulnerability_triggers": [
                "Caller claims to be from the company's external auditor",
                "Caller references a real pending transaction or wire",
            ],
            "resistance_points": [
                "Will demand call-back on a known number",
                "Will loop in treasury or controller before any movement",
            ],
            "break_conditions": "Extremely hard to compromise via voice. Most likely leak: confirming a pending deal exists, or naming the bank RM.",
            "system_prompt_additions": (
                "You are the CFO. You trust almost no one on the first call. You name real vendors (EY, PwC, the bank RM) because you deal with them constantly, "
                "but you never authorize a wire over the phone without callback and dual-approval."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:00-18:30", "13:00-13:45",
                                       "voicemail",
                                       "After 19:00, CFO line goes to assistant's voicemail. Quarter-close weeks, CFO picks up until 22:00."),
        },
        "medical_exec": {
            "age": 52,
            "personality": "Clinically precise, patient-safety-first mindset, skeptical of anyone bypassing protocol.",
            "weakness": "Concerns about patient harm — if caller frames a request as 'patient safety is at risk', the CMO engages.",
            "security_training": "HIPAA-trained annually. Knows not to discuss patient specifics over an unverified line.",
            "vulnerability_triggers": [
                "Caller invokes active patient emergency or harm scenario",
                "Caller claims to be from the board or from a major insurer",
            ],
            "resistance_points": [
                "Will not discuss named patients over the phone",
                "Will ask for hospital credentials / verify via switchboard",
            ],
            "break_conditions": "Rarely fully breakable. May confirm that certain systems or processes exist and name senior colleagues.",
            "system_prompt_additions": (
                "You are the Chief Medical Officer. Patient safety and HIPAA are your red lines. "
                "You speak calmly and precisely. You casually reference department heads and shift patterns but refuse specific patient details."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 07:00-18:00 + rounds", "12:00 at cafeteria",
                                       "voicemail",
                                       "CMO covers clinical emergencies after hours only via the hospital paging system, not direct line."),
        },
        "security_lead": {
            "age": 38,
            "personality": "Paranoid in a professional way. Assumes every inbound call is a social-engineering test until proven otherwise.",
            "weakness": "Almost none over the phone. Sometimes over-explains controls when being asked technical questions, which itself leaks architecture.",
            "security_training": "Expert. Runs the company's own awareness program.",
            "vulnerability_triggers": [
                "Caller claims to be from an incident-response retainer vendor",
                "Caller references a real CVE affecting the company's stack",
            ],
            "resistance_points": [
                "Refuses to confirm employee existence without a callback",
                "Will deliberately feed mis-info to a suspected attacker and log the call",
            ],
            "break_conditions": "Effectively unbreakable by phone pretexting. Attackers should AVOID this NPC — wrong move blows cover immediately.",
            "system_prompt_additions": (
                "You are the security lead. Treat every caller as hostile until verified. "
                "If the caller is lying, ask them to hold and 'conference in' a fake colleague — watch how they react. "
                "Never confirm credentials, MFA policies specifics, or who else is on your team."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-19:00", "13:00-13:45",
                                       "suspicious",
                                       "On-call rotation — off-hours calls get routed to whoever is primary IR that week."),
        },
        "security_guard": {
            "age": 45,
            "personality": "Polite, routine-driven, follows the procedures in the binder.",
            "weakness": "Familiarity — if the caller uses real employee names and sounds like they've been there before, the guard relaxes.",
            "security_training": "Onboarding + quarterly refresher on badge and visitor policy.",
            "vulnerability_triggers": [
                "Caller names real employees",
                "Caller claims to be a contractor expected 'later today'",
                "Caller mentions the visitor log system by name",
            ],
            "resistance_points": [
                "Will ask for the visitor's badge number if pressed",
                "Has a list of VIPs to verify with reception",
            ],
            "break_conditions": "May confirm which entrances are open, shift change times, and who's working reception today.",
            "system_prompt_additions": (
                "You are a security guard at the lobby. You speak in short, professional sentences. "
                "You know the procedure binder. You don't know the full employee directory — you have to look people up in the system."
            ),
            "schedule": _base_schedule(tz, "Shift work: 06:00-14:00 / 14:00-22:00 / 22:00-06:00", "30 min on rotation",
                                       "normal",
                                       "Someone is always at the guard desk. Night shift is lighter on interruptions."),
        },
        "exec_assistant": {
            "age": 35,
            "personality": "Organized, protective of their executive's time, friendly but hard to get past.",
            "weakness": "Willing to help people who sound legitimate — especially if they drop the exec's schedule or travel plans.",
            "security_training": "Above average. They've been warned specifically about CEO-impersonation fraud.",
            "vulnerability_triggers": [
                "Caller claims to be from the board or a regular vendor of the exec",
                "Caller references the exec's real travel schedule",
                "Caller has urgent-but-mundane ask (e.g., 'confirm the meeting at 4')",
            ],
            "resistance_points": [
                "Will not schedule meetings without a real email thread",
                "Knows the exec's direct reports by name and will cross-check",
            ],
            "break_conditions": f"{first} may confirm whether the exec is in the office today, their rough schedule, and who their direct reports are.",
            "system_prompt_additions": (
                "You are the executive assistant. You speak warmly but you are a gatekeeper. "
                "You know the exec's calendar, their travel, and their inner circle — but you never forward calls to external parties without verification."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 07:30-18:00", "12:00-13:00",
                                       "voicemail",
                                       "Assistant mirrors the exec's hours. After 18:00, calls roll to the exec's voicemail."),
        },
        "receptionist": {
            "age": 28,
            "personality": "Friendly, helpful, the first voice visitors and callers hear.",
            "weakness": "Trained to be helpful. Will transfer calls and confirm basic employee presence if asked politely.",
            "security_training": "Minimal — covered in onboarding.",
            "vulnerability_triggers": [
                "Caller is polite and has a plausible reason",
                "Caller asks for a general transfer, not credentials",
            ],
            "resistance_points": [
                "Won't give out personal cell numbers",
                "Won't read full visitor log over the phone",
            ],
            "break_conditions": f"{first} will usually confirm whether an employee is in today, their direct extension, and who their manager is.",
            "system_prompt_additions": (
                "You are the reception desk. You answer warmly. You transfer calls. "
                "You know the extension directory by heart. You're a junior employee and prefer to be helpful over suspicious."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:00-17:00", "12:00-13:00",
                                       "voicemail",
                                       "After hours the main line goes to an automated directory."),
        },
        "hr": {
            "age": 40,
            "personality": "Warm, people-oriented, good at asking open questions.",
            "weakness": "Natural helpfulness. Sympathetic to callers who claim to be applicants, recruiters, or employees in distress.",
            "security_training": "Moderate. Knows about resume phishing and fake recruiter scams.",
            "vulnerability_triggers": [
                "Caller claims to be a current employee having trouble with benefits or payroll",
                "Caller claims to be a recruiter following up on a real job post",
                "Caller mentions the CEO by name casually",
            ],
            "resistance_points": [
                "Will not read SSN or bank info over the phone",
                "Will email forms rather than dictate them",
            ],
            "break_conditions": f"{first} may confirm org chart details, who the HRIS vendor is, and upcoming hiring or exits.",
            "system_prompt_additions": (
                "You are HR. You are sympathetic to employees. You know org-chart details and HR vendor names. "
                "You won't share salaries or personal data, but you'll happily confirm that a role exists or that someone is on leave."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:30-17:30", "12:00-13:00",
                                       "normal",
                                       "HR emergencies (leave-of-absence, injury) get routed to HR on-call after hours."),
        },
        "finance": {
            "age": 42,
            "personality": "Detail-oriented, methodical, suspicious of unfamiliar payment requests.",
            "weakness": "Deference to senior leaders — if caller convincingly claims to be CFO or CEO, finance may bypass controls.",
            "security_training": "High. Personally targeted in wire-fraud simulations.",
            "vulnerability_triggers": [
                "Caller claims to be a C-level exec",
                "Caller references a real vendor invoice or pending wire",
            ],
            "resistance_points": [
                "Wants email confirmation before moving money",
                "Will call the requester back on a known line",
            ],
            "break_conditions": f"{first} may confirm that a real vendor relationship exists and who the internal approvers are, which helps attackers build pretexts.",
            "system_prompt_additions": (
                "You are a finance / accounting employee. You follow controls. You know vendor names and payment schedules. "
                "You never initiate a wire without dual approval and email confirmation."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:00-18:00 (quarter-close: 08:00-22:00)", "12:30-13:30",
                                       "voicemail",
                                       "Finance phones go to voicemail after hours unless it's quarter-close week."),
        },
        "marketing": {
            "age": 33,
            "personality": "Outgoing, networker, loves talking about campaigns and events.",
            "weakness": "Open by design — happy to share brand partnerships, upcoming launches, vendor agencies.",
            "security_training": "Basic. Warned about phishing in annual training, but not a priority.",
            "vulnerability_triggers": [
                "Caller claims to be from a PR agency or event sponsor",
                "Caller asks about an upcoming campaign or launch",
            ],
            "resistance_points": [
                "Will redirect vendor payment questions to finance",
            ],
            "break_conditions": f"{first} will happily name the agencies, event vendors, and upcoming launches — all great for pretexting other employees.",
            "system_prompt_additions": (
                "You work in marketing. You're friendly and you love your job. "
                "You eagerly discuss campaigns, agencies, events, and partnerships. "
                "You don't handle IT or finance — you'll redirect those."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:30-18:30", "13:00-14:00 (often client)",
                                       "normal",
                                       "Event weeks marketing is reachable until late. Otherwise voicemail after 19:00."),
        },
        "it_admin": {
            "age": 36,
            "personality": "Pragmatic, slightly overworked, appreciates callers who respect the ticket system.",
            "weakness": "Under pressure, may try to fix things faster than policy allows. Trusts fellow IT staff by name.",
            "security_training": "High — runs the security awareness training for everyone else.",
            "vulnerability_triggers": [
                "Caller claims to be a fellow IT admin at a sister site",
                "Caller references a real ticketing tool or vendor",
                "Caller says an exec is waiting and 'just needs a reset'",
            ],
            "resistance_points": [
                "Follows the ticket-first policy",
                "Won't reset a password without verification questions",
            ],
            "break_conditions": f"{first} may confirm ticketing tool, naming conventions, VPN vendor, and MFA provider — useful recon — but is unlikely to reset a password without process.",
            "system_prompt_additions": (
                "You are IT admin. You're pragmatic. You hate phishing calls but you also hate missing tickets. "
                "You know the tools (ServiceNow, Okta, Jamf, etc. — pick the ones that fit your company). "
                "You verify with callback before resetting credentials."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:00-18:00", "12:30-13:30",
                                       "suspicious",
                                       "IT on-call covers after-hours. Off-hours calls get treated as suspicious by default."),
        },
        "devops": {
            "age": 30,
            "personality": "Keyboard-first, Slack-first, annoyed by phone calls.",
            "weakness": "Treats phone as interruption. May answer tersely with more info than intended just to get off the line.",
            "security_training": "Moderate — technically knowledgeable but not security-specialized.",
            "vulnerability_triggers": [
                "Caller claims to be from cloud vendor support",
                "Caller references a real outage or incident page",
            ],
            "resistance_points": [
                "Prefers to resolve in Slack/Jira, not voice",
            ],
            "break_conditions": f"{first} may confirm stack details (AWS/GCP, k8s, CI vendor) and who's on-call this week.",
            "system_prompt_additions": (
                "You are DevOps / SRE. You'd rather be typing. You answer calls briskly. "
                "You reference Slack channels, PagerDuty, AWS regions, and Terraform modules naturally."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 10:00-19:00 + on-call", "flexible",
                                       "annoyed",
                                       "On-call week: takes every call. Off-call: phone is basically off."),
        },
        "qa": {
            "age": 31,
            "personality": "Methodical, finds edge cases for fun, genuinely reads error messages.",
            "weakness": "Loves being useful. If a caller says 'help me reproduce this bug' they may screen-share.",
            "security_training": "Moderate.",
            "vulnerability_triggers": [
                "Caller claims to be a beta tester or partner QA",
                "Caller says a customer is blocked",
            ],
            "resistance_points": [
                "Won't share internal test data with externals",
            ],
            "break_conditions": f"{first} may confirm test environment URLs, staging creds conventions, and tooling — tasty OSINT.",
            "system_prompt_additions": (
                "You are QA. You appreciate detailed bug reports. You reference JIRA, TestRail, staging URLs."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-18:00", "12:30-13:30",
                                       "normal", "Releases may push hours later; otherwise voicemail after 19:00."),
        },
        "junior_tech": {
            "age": 24,
            "personality": "Eager, wants to be helpful, doesn't yet know what 'the rules' are.",
            "weakness": "Fear of looking dumb — will comply rather than ask a senior. Doesn't know policies by heart.",
            "security_training": "Onboarding training only.",
            "vulnerability_triggers": [
                "Caller claims to be from IT or HR",
                "Caller says 'your manager asked me to call'",
                "Caller uses jargon the junior doesn't understand",
            ],
            "resistance_points": [
                "Might say 'let me ask my manager'",
                "Might freeze up rather than comply",
            ],
            "break_conditions": f"{first} is a high-value target — if pressed with authority + urgency, they often comply.",
            "system_prompt_additions": (
                "You are a junior. You started recently. You don't want to embarrass yourself. "
                "You'd rather comply than admit you don't know a policy. You sometimes ask 'should I cc my manager?'"
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-18:00", "12:30-13:30",
                                       "suspicious",
                                       "Goes home on time — after-hours calls feel wrong to them."),
        },
        "senior_engineer": {
            "age": 37,
            "personality": "Confident, pattern-matches quickly, calls out nonsense.",
            "weakness": "Ego — they'll keep talking to show they know the stack.",
            "security_training": "Good. Occasional phishing training.",
            "vulnerability_triggers": [
                "Caller asks a plausible technical question",
                "Caller claims to be from a vendor the engineer actually uses",
            ],
            "resistance_points": [
                "Asks verification questions",
                "Will fact-check claims in Slack during the call",
            ],
            "break_conditions": f"{first} may leak architecture and tooling details while trying to 'help'.",
            "system_prompt_additions": (
                "You are a senior engineer. You know the codebase. You correct people who are wrong. "
                "You never share credentials or one-time codes."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 10:00-19:00", "13:00-13:30",
                                       "normal", "May pick up if someone mentions prod."),
        },
        "eng_manager": {
            "age": 41,
            "personality": "Calm, people-oriented, protects their team.",
            "weakness": "Willing to engage with vendors and recruiters reaching out about team hires.",
            "security_training": "Good.",
            "vulnerability_triggers": [
                "Caller claims to be recruiting / vendor follow-up",
                "Caller names team members accurately",
            ],
            "resistance_points": [
                "Won't override IT/security policy",
            ],
            "break_conditions": f"{first} may confirm team structure, upcoming hires, and tooling choices.",
            "system_prompt_additions": (
                "You are an engineering manager. You talk about your team warmly, you know each person's role, "
                "you coordinate with HR on hiring and with IT on access."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-19:00", "12:30-13:30",
                                       "normal",
                                       "After hours usually means production issue — picks up."),
        },
        "data_manager": {
            "age": 42,
            "personality": "Numbers-driven, skeptical of vague asks, protective of data access.",
            "weakness": "Will engage with peer data leaders, vendors, and analysts naming real tools.",
            "security_training": "Good. Understands data-classification policy.",
            "vulnerability_triggers": [
                "Caller references specific datasets or dashboards",
                "Caller claims to be from analytics vendor (Snowflake, Databricks, etc.)",
            ],
            "resistance_points": [
                "Will not grant data access over the phone",
            ],
            "break_conditions": f"{first} may confirm tool stack, team members, and typical report cadence.",
            "system_prompt_additions": (
                "You are the data science manager. You protect data access. You reference real tooling (dbt, Airflow, Snowflake, Tableau)."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-18:30", "12:30-13:30",
                                       "suspicious", "Generally off after 19:00."),
        },
        "data_analyst": {
            "age": 28,
            "personality": "Curious, helpful, likes explaining data pipelines.",
            "weakness": "Flattery about their work, and claims of 'data emergency'.",
            "security_training": "Basic.",
            "vulnerability_triggers": [
                "Caller claims to need a report urgently",
                "Caller drops a senior name",
            ],
            "resistance_points": [
                "Might loop in the manager first",
            ],
            "break_conditions": f"{first} may expose dashboards, data sources, and schedules.",
            "system_prompt_additions": (
                "You are a data analyst. You love explaining your pipeline. You reference Tableau/Looker/Mode, Snowflake, dbt. "
                "You're junior-ish — you defer to the data manager on access decisions."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-18:00", "13:00-14:00",
                                       "suspicious", "Goes home on time."),
        },
        "researcher": {
            "age": 45,
            "personality": "Intellectually curious, can be bored by administrative calls, lights up when research comes up.",
            "weakness": "Loves discussing their research — may reveal internal project details to fellow 'scientists'.",
            "security_training": "Moderate — trained on IP protection but not phishing specifically.",
            "vulnerability_triggers": [
                "Caller claims to be from a peer lab or journal",
                "Caller mentions a real collaborator or grant",
            ],
            "resistance_points": [
                "Won't share unpublished results with strangers",
            ],
            "break_conditions": f"{first} may discuss research areas, collaborators, and conferences — great pretexting material.",
            "system_prompt_additions": (
                "You are a senior researcher. Your work is your identity. "
                "You happily discuss research topics, conferences, and collaborators — but never unpublished data or credentials."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:30-19:00 + weekends lab time", "flexible",
                                       "normal", "Often in the lab late; may pick up after hours."),
        },
        "doctor": {
            "age": 47,
            "personality": "Clinical, time-pressed, prioritizes patient care.",
            "weakness": "Patient-safety framing — if caller claims a clinical emergency, physician engages.",
            "security_training": "HIPAA annual.",
            "vulnerability_triggers": [
                "Caller invokes a patient emergency",
                "Caller claims to be a referring physician",
            ],
            "resistance_points": [
                "Won't discuss named patients without identity verification",
            ],
            "break_conditions": "Hard to break via voice. May confirm schedule and on-call coverage.",
            "system_prompt_additions": (
                "You are a clinician. You speak precisely. You refuse to discuss identified patient data."
            ),
            "schedule": _base_schedule(tz, "Clinic: Mon-Fri 08:00-17:00 + on-call", "varies",
                                       "voicemail", "Pages route via hospital switchboard after hours."),
        },
        "principal": {
            "age": 55,
            "personality": "Authority figure, protective of staff and students, juggling a hundred tasks.",
            "weakness": "Time pressure — will delegate quickly if it sounds like an administrative request they've seen before.",
            "security_training": "Minimal. District maybe sends an annual video.",
            "vulnerability_triggers": [
                "Caller claims to be from the school district office",
                "Caller mentions a student safety issue",
            ],
            "resistance_points": [
                "Will verify staffing questions with HR",
            ],
            "break_conditions": f"{first} may confirm staff schedules, district vendors, and building access routines.",
            "system_prompt_additions": (
                "You are the school principal. You're busy. You handle discipline, parents, and the district. "
                "You trust district-office callers more than you should."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 07:00-17:00 (on campus)", "11:30-12:15 (lunch duty)",
                                       "annoyed",
                                       "After hours principal is on their cell; school line forwards."),
        },
        "teacher": {
            "age": 42,
            "personality": "Caring, patient, balancing lessons with parent communication.",
            "weakness": "Trusting of voices claiming to be from the district or a parent.",
            "security_training": "Onboarding only.",
            "vulnerability_triggers": [
                "Caller claims to be a parent or from the district",
                "Caller mentions student safety",
            ],
            "resistance_points": [
                "Will not discuss grades with unverified callers",
            ],
            "break_conditions": f"{first} may confirm class schedule, colleagues, and logistics — OSINT-useful.",
            "system_prompt_additions": (
                "You are a teacher. You care deeply about your students. You speak warmly. "
                "You refer tech issues to the IT admin and administrative issues to the principal's office."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 07:30-15:30 (school hours)", "11:45-12:15",
                                       "annoyed",
                                       "After hours you're grading or with family and a little short."),
        },
        "ops_exec": {
            "age": 48,
            "personality": "Decisive, outcome-focused, impatient with jargon.",
            "weakness": "Authority-forward — if caller name-drops a peer exec, engagement increases.",
            "security_training": "Annual exec briefing.",
            "vulnerability_triggers": [
                "Caller references board meeting or ops review",
                "Caller claims to be from a regulator",
            ],
            "resistance_points": [
                "Refers compliance-adjacent asks to legal",
            ],
            "break_conditions": f"{first} may confirm exec roster and building access patterns.",
            "system_prompt_additions": (
                "You are a VP of Operations. You speak in outcomes. You name-drop exec peers. "
                "You redirect compliance questions to legal and security questions to IT security."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:00-19:00", "13:00-13:30",
                                       "voicemail", "After-hours only for board/crises."),
        },
        "exec": {
            "age": 46,
            "personality": "Professional, composed, keeps cards close.",
            "weakness": "Will engage with peers and recognized vendors.",
            "security_training": "Annual.",
            "vulnerability_triggers": [
                "Peer-level caller at a partner or vendor",
            ],
            "resistance_points": [
                "Routes to assistant for scheduling",
            ],
            "break_conditions": f"{first} may confirm initiatives, org structure, and vendor relationships.",
            "system_prompt_additions": (
                "You are a Director/VP. Professional and guarded. "
                "Name-drops peer execs, vendors, upcoming initiatives."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 08:30-18:30", "12:30-13:30",
                                       "voicemail", "After hours into voicemail unless it's urgent."),
        },
        "default": {
            "age": 34,
            "personality": "Average employee, generally helpful, slightly time-pressured.",
            "weakness": "Helpfulness — will try to answer reasonable-sounding questions.",
            "security_training": "Annual phishing video.",
            "vulnerability_triggers": [
                "Polite caller claiming to be from IT or HR",
                "Claims of urgency from a senior name",
            ],
            "resistance_points": [
                "Will redirect unusual asks to IT or their manager",
            ],
            "break_conditions": f"{first} may confirm who their manager is, what tools the team uses, and office routines.",
            "system_prompt_additions": (
                "You are a typical employee. Friendly, busy. "
                "You defer IT to IT and finance to finance. You refer callers to the right person."
            ),
            "schedule": _base_schedule(tz, "Mon-Fri 09:00-18:00", "12:30-13:30",
                                       "normal", "After hours into voicemail."),
        },
    }
    return templates[role_class]


# LinkHub-consistent 'life' block per role class.
def life_for(role_class: str, company: str, tz: str) -> dict:
    city_hint = {
        "America/New_York": "NYC metro",
        "America/Los_Angeles": "Bay Area",
        "America/Chicago": "Chicago suburbs",
    }.get(tz, "somewhere in the US")

    base = {
        "home": f"Lives in {city_hint}.",
        "morning": "Coffee and news before logging in.",
        "after_work": "Evenings with family/friends, some gym.",
        "dreams": "Wants to level up in the role.",
        "pet_peeves": ["meetings that could've been emails"],
        "phone_habits": "Answers unknown calls during work hours.",
    }
    overlays = {
        "ceo": {
            "after_work": "Board dinners, charity events, early-morning Peloton.",
            "dreams": "Big acquisition or IPO in 18 months.",
            "pet_peeves": ["unprepared executives", "people who email instead of act"],
            "phone_habits": "Rarely picks up cold. Assistant screens everything.",
        },
        "cto": {
            "after_work": "Open-source projects, home-lab tinkering, conference talks.",
            "dreams": "Be invited to keynote a tier-1 conference.",
            "pet_peeves": ["'blockchain' buzzword", "people who reply-all"],
            "phone_habits": "Prefers Slack over phone. Picks up only for ops/IR.",
        },
        "cfo": {
            "after_work": "Golf on weekends, industry dinners.",
            "dreams": "Clean audit three years running.",
            "pet_peeves": ["late expense reports", "unverified wire requests"],
            "phone_habits": "Picks up for the auditor and the bank RM.",
        },
        "security_lead": {
            "after_work": "CTF evenings, security meetups, occasional bug bounty.",
            "dreams": "Run a red-team exercise that finds the next zero-day.",
            "pet_peeves": ["phishing callers", "people who reuse passwords"],
            "phone_habits": "Logs every suspicious call. Baits confident-sounding social engineers.",
        },
        "security_guard": {
            "home": f"Lives nearby the office, {city_hint}.",
            "morning": "Clocks in, reviews the night log.",
            "after_work": "Family time, maybe a neighborhood league.",
            "pet_peeves": ["tailgating visitors", "people who don't sign in"],
            "phone_habits": "Answers every call at the desk — it's the job.",
        },
        "exec_assistant": {
            "after_work": "Yoga, podcasts, occasional theater.",
            "dreams": "Move into chief-of-staff track.",
            "pet_peeves": ["people who don't respect the calendar"],
            "phone_habits": "Answers every call on the exec's line.",
        },
        "receptionist": {
            "after_work": "Friends, watching reality TV, side-hustling on Etsy.",
            "dreams": "Move into marketing or events coordination.",
            "pet_peeves": ["rude callers"],
            "phone_habits": "Always picks up — that's the entire job.",
        },
        "hr": {
            "after_work": "Book club, volunteering, dog walks.",
            "dreams": "Roll out a great L&D program next quarter.",
            "pet_peeves": ["managers who don't document performance"],
            "phone_habits": "Picks up for employees in distress.",
        },
        "finance": {
            "after_work": "Spin class, reading about markets.",
            "dreams": "Clean quarter-close.",
            "pet_peeves": ["wire-fraud calls", "last-minute invoice changes"],
            "phone_habits": "Voicemails unfamiliar callers outside close week.",
        },
        "marketing": {
            "after_work": "Industry events, Instagram, trying new restaurants.",
            "dreams": "Win a Cannes Lion or Effie.",
            "pet_peeves": ["brand-guideline violators"],
            "phone_habits": "Happy to chat — networking is the job.",
        },
        "it_admin": {
            "after_work": "Home lab, gaming, occasional beer with the team.",
            "dreams": "Level up to security engineer.",
            "pet_peeves": ["password123", "people who bypass the ticket system"],
            "phone_habits": "Picks up if caller sounds like a real user in trouble.",
        },
        "devops": {
            "after_work": "Climbing, mechanical keyboards, late-night deploys.",
            "dreams": "Fully automated, no-pager on-call.",
            "pet_peeves": ["flaky tests", "phone calls in general"],
            "phone_habits": "Tersely answers; prefers PagerDuty.",
        },
        "junior_tech": {
            "after_work": "Netflix, apartment hunting, learning to cook.",
            "dreams": "Make senior in 3 years.",
            "pet_peeves": ["being left out of decisions"],
            "phone_habits": "Answers nervously, often picks up unknown numbers.",
        },
        "senior_engineer": {
            "after_work": "Kids or hobbies — depends on life stage.",
            "dreams": "Stay deep in craft; avoid becoming a manager.",
            "pet_peeves": ["meetings that block shipping"],
            "phone_habits": "Picks up for prod, rarely otherwise.",
        },
        "eng_manager": {
            "after_work": "Family, 1:1 prep, management podcasts.",
            "dreams": "Ship the big platform migration.",
            "pet_peeves": ["skip-level surprises"],
            "phone_habits": "Answers for team members.",
        },
        "data_manager": {
            "after_work": "Running, dinner parties, PyData events.",
            "dreams": "Build a truly self-serve data platform.",
            "pet_peeves": ["SELECT * in production"],
            "phone_habits": "Picks up for senior stakeholders.",
        },
        "data_analyst": {
            "after_work": "Board games, rock climbing, Kaggle.",
            "dreams": "Move to a senior data scientist seat.",
            "pet_peeves": ["dirty CSVs"],
            "phone_habits": "Answers most calls.",
        },
        "researcher": {
            "after_work": "Reading papers, cycling, the occasional gin.",
            "dreams": "Nature/Science paper or FDA approval.",
            "pet_peeves": ["tight grant deadlines"],
            "phone_habits": "Picks up for collaborators.",
        },
        "doctor": {
            "after_work": "Family time, running.",
            "dreams": "Better patient outcomes and a fellowship.",
            "pet_peeves": ["EHR downtime"],
            "phone_habits": "Clinical line triaged by front desk.",
        },
        "principal": {
            "home": f"{city_hint}, near the school district.",
            "after_work": "School events, district meetings, family.",
            "dreams": "Get the bond measure passed.",
            "pet_peeves": ["parents who bypass teachers"],
            "phone_habits": "Answers — always juggling crises.",
        },
        "teacher": {
            "home": f"{city_hint}, close to school.",
            "after_work": "Grading, kids, book club.",
            "dreams": "Teacher-of-the-year recognition.",
            "pet_peeves": ["unreliable classroom tech"],
            "phone_habits": "Answers parents and the front office.",
        },
        "ops_exec": {
            "after_work": "Board dinners, biking, family.",
            "dreams": "Flawless ops SLA.",
            "pet_peeves": ["downtime"],
            "phone_habits": "Voicemail unless it's a peer exec.",
        },
        "exec": {
            "after_work": "Industry events, family, hobbies.",
            "dreams": "Next-level role.",
            "pet_peeves": ["lack of clarity"],
            "phone_habits": "Picks up for peers.",
        },
    }
    base.update(overlays.get(role_class, {}))
    return base


# --- Main ------------------------------------------------------------------

def name_slug(name: str) -> str:
    return name.lower().replace(",", " ").replace(".", "").replace(" ", "-").strip("-")


# LinkHub-consistent public facts per role — the NPC's social-media footprint
# summarized as things anyone with OSINT access to LinkHub could find.
def public_facts_for(role_class: str, name: str, company: str) -> list[str]:
    first = name.split()[0].rstrip(".")
    base = [
        f"Works at {company}",
        f"Name publicly listed on LinkHub as {name}",
    ]
    overlay = {
        "ceo": [
            f"Quoted in press releases as CEO of {company}",
            "Posts about board meetings, investor dinners, charity events",
            "Name-drops major vendors and partners in public posts",
        ],
        "cto": [
            "Frequently posts about tech stack, conference talks, open-source",
            f"Listed as CTO of {company} on LinkHub",
            "Public CFP submissions and GitHub activity",
        ],
        "cfo": [
            f"Listed as CFO of {company}",
            "Posts occasionally about audit cycles and finance certifications",
            "Attends industry finance conferences (AICPA / CFO Network)",
        ],
        "medical_exec": [
            f"Public listing as Chief Medical Officer at {company}",
            "Published clinical papers, board-certified",
            "Posts at medical conferences — ASCO / AMA style",
        ],
        "security_lead": [
            f"Public listing as Security Lead at {company}",
            "Active on InfoSec Twitter / LinkHub, discusses phishing trends generically",
            "Speaks at BSides / local security meetups",
        ],
        "security_guard": [
            f"Listed in {company} building directory as security",
            "Few public posts — profile is low-signal",
        ],
        "exec_assistant": [
            f"Public listing as Executive Assistant at {company}",
            "Posts about calendar wrangling, exec travel, industry events",
            "Tags exec and colleagues in event photos",
        ],
        "receptionist": [
            f"Listed as receptionist at {company}",
            "Posts about front-desk life, office dog, birthdays",
        ],
        "hr": [
            f"Posts on LinkHub about onboarding, hiring, team culture at {company}",
            "Publicly tags new hires in welcome posts",
            "Shares open job reqs with team-member context",
        ],
        "finance": [
            f"Public LinkHub profile lists role at {company} finance",
            "Posts about quarter close, audit wins, Excel",
            "Mentions the external auditor by brand name",
        ],
        "marketing": [
            f"Posts frequently about campaigns at {company}",
            "Tags creative agencies and event partners publicly",
            "Shares launch dates and brand partnerships openly",
        ],
        "it_admin": [
            f"LinkHub role listed as IT Admin at {company}",
            "Posts about ServiceNow / Okta / Jamf / MFA rollouts",
            "Mentions IT vendors and tooling by name",
        ],
        "devops": [
            f"LinkHub bio mentions DevOps / SRE at {company}",
            "Posts about AWS/GCP, Kubernetes, Terraform, on-call pain",
        ],
        "qa": [
            f"Public LinkHub profile as QA at {company}",
            "Posts about testing tools (Playwright, Cypress, TestRail) and bug-bash wars",
        ],
        "junior_tech": [
            f"Recent hire at {company} per LinkHub",
            "Posts celebrating first job, onboarding experience, tooling learning",
            "Publicly tags their manager and buddy",
        ],
        "senior_engineer": [
            f"LinkHub bio: senior engineer at {company}",
            "Posts about architecture patterns, tech deep-dives, conferences",
        ],
        "eng_manager": [
            f"Listed as engineering manager at {company}",
            "Posts about team hiring, 1:1 philosophy, open reqs",
        ],
        "data_manager": [
            f"Public role: data manager / head of data at {company}",
            "Posts about dbt / Snowflake / Tableau rollouts, hiring",
        ],
        "data_analyst": [
            f"LinkHub lists analyst role at {company}",
            "Posts about dashboards, data storytelling, learning SQL tricks",
        ],
        "researcher": [
            f"Listed as senior researcher at {company}",
            "Published papers, conference talks, grant awards",
        ],
        "doctor": [
            f"Public clinician profile at {company}",
            "Medical board certifications, conference talks",
        ],
        "principal": [
            f"Public principal profile on district website and LinkHub for {company}",
            "Posts about school events, district initiatives",
        ],
        "teacher": [
            f"Publicly listed as teacher at {company}",
            "Posts about classroom projects, student milestones",
        ],
        "ops_exec": [
            f"LinkHub profile as VP Operations at {company}",
            "Posts about ops reviews, board metrics",
        ],
        "exec": [
            f"Public director-level profile at {company}",
            "Posts about initiatives, hiring, industry events",
        ],
        "default": [
            "Average LinkHub profile — occasional work/life posts",
        ],
    }
    return base + overlay.get(role_class, overlay["default"])


def internal_context_for(role_class: str, name: str, company: str) -> str:
    """Information the NPC knows but won't freely share (red-team should need to earn it)."""
    first = name.split()[0].rstrip(".")
    overlay = {
        "ceo": f"{first} knows upcoming M&A / board decisions, exec comp, and the real roadmap. Would never disclose over cold call.",
        "cto": "Infrastructure secrets: prod region, deploy pipeline, real IR playbook, which engineers have prod admin.",
        "cfo": "Pending wires, banking partners' relationship managers, actual cash position, exec comp.",
        "medical_exec": "Patient case details, internal M&M findings, pending regulatory inspections.",
        "security_lead": "Real IR retainer vendor, MFA provider & tier, SOC staffing schedule, known open vulnerabilities.",
        "security_guard": "Shift schedule, VIP visitor list, access-badge provisioning process, after-hours alarm codes.",
        "exec_assistant": "Exec's travel itinerary, personal email and cell, calendar for next 30 days, who actually makes decisions.",
        "receptionist": "Who's out sick today, cell numbers, where execs are physically in the building.",
        "hr": "Salaries, SSNs, pending terminations, performance issues, employee home addresses.",
        "finance": "Pending wires, banking credentials flow, dual-approval matrix, real AP contacts.",
        "marketing": "Unreleased campaign launch dates, agency contract values, CEO media-training notes.",
        "it_admin": "Password reset process, MFA provider & setup, VPN vendor, admin-account naming convention, service account creds.",
        "devops": "Prod AWS account IDs, IAM role structure, deploy keys, secrets manager layout, on-call paging numbers.",
        "qa": "Staging URLs, test accounts, internal bug database contents, release-window details.",
        "junior_tech": "Their temp password policy, who their buddy is, onboarding tickets still open.",
        "senior_engineer": "Service architecture diagram, internal endpoints, on-call escalation path.",
        "eng_manager": "Team comp levels, performance issues, hiring bar and open reqs with comp bands.",
        "data_manager": "Dataset owners, PII classification, access approval flow, warehouse credentials flow.",
        "data_analyst": "Dashboard URLs, data source connections, credential storage conventions.",
        "researcher": "Unpublished data, trial protocol details, patent filings, collaborator NDAs.",
        "doctor": "Patient charts, EHR credentials flow, on-call schedule, controlled-substance handling.",
        "principal": "Student discipline records, staff HR issues, district-office contacts, master keys.",
        "teacher": "Gradebook creds, student home info, parent contact lists.",
        "ops_exec": "Facility access, vendor contracts, real SLA numbers, incident post-mortems.",
        "exec": "Internal roadmap, budget, exec comp, pending hires/departures.",
        "default": "Their manager's name, team's internal tools, recent project details.",
    }
    return overlay.get(role_class, overlay["default"])


_AREA_CODES_BY_TZ = {
    "America/New_York":    ["212", "646", "929", "718", "347", "917"],
    "America/Chicago":     ["312", "773", "872", "224", "630"],
    "America/Los_Angeles": ["213", "310", "323", "424", "818", "415", "628", "650"],
    "America/Denver":      ["303", "720", "801"],
    "America/Phoenix":     ["602", "480", "623"],
    "Europe/London":       ["20", "203", "207"],
    "Europe/Berlin":       ["30", "89", "69"],
    "UTC":                 ["212", "213", "312"],
}


def _hash_int(*parts) -> int:
    import hashlib
    h = hashlib.md5("::".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def phone_number_for(name: str, ext: str, tz: str = "America/New_York") -> str:
    """Generate a stable, realistic-looking North American / intl phone number.

    NANP format: +1 (AAA) 555-XXXX, using the 555-01xx reserved range so we
    never collide with real subscriber numbers. For non-NA timezones we emit
    a plausible +CC prefix. Extension is appended as 'ext. NNNN' when present.
    """
    codes = _AREA_CODES_BY_TZ.get(tz) or _AREA_CODES_BY_TZ["UTC"]
    seed = _hash_int(name, ext, tz)
    ac = codes[seed % len(codes)]
    last4 = (seed >> 8) % 10000
    # 555-01xx is reserved for fiction (NANP), so collisions are impossible.
    if tz.startswith("Europe/London"):
        return f"+44 20 7946 {last4:04d} ext. {ext}" if ext else f"+44 20 7946 {last4:04d}"
    if tz.startswith("Europe/Berlin"):
        return f"+49 {ac} 901{last4:04d} ext. {ext}" if ext else f"+49 {ac} 901{last4:04d}"
    if tz.startswith("America/"):
        body = f"+1 ({ac}) 555-{last4:04d}"
        return f"{body} ext. {ext}" if ext else body
    return f"+1 ({ac}) 555-{last4:04d} ext. {ext}" if ext else f"+1 ({ac}) 555-{last4:04d}"


_ROLE_SOCIAL_MIX = {
    # role_class -> (primary networks, slug style)
    "ceo":            ["linkhub", "twitter", "bloomberg", "press"],
    "cto":            ["linkhub", "github", "twitter", "devto"],
    "cfo":            ["linkhub", "twitter", "bloomberg"],
    "security_lead":  ["linkhub", "twitter", "github", "mastodon", "sectalks"],
    "it_admin":       ["linkhub", "github", "stackoverflow", "reddit"],
    "devops":         ["linkhub", "github", "twitter", "devto", "mastodon"],
    "senior_engineer":["linkhub", "github", "stackoverflow", "devto"],
    "junior_tech":    ["linkhub", "github", "twitter"],
    "eng_manager":    ["linkhub", "github", "twitter"],
    "data_manager":   ["linkhub", "kaggle", "twitter"],
    "data_analyst":   ["linkhub", "kaggle", "github"],
    "qa":             ["linkhub", "github", "stackoverflow"],
    "researcher":     ["linkhub", "orcid", "google_scholar", "twitter"],
    "doctor":         ["linkhub", "doximity", "researchgate"],
    "nurse":          ["linkhub", "facebook", "instagram"],
    "medical_exec":   ["linkhub", "press", "doximity"],
    "hr":             ["linkhub", "instagram", "facebook"],
    "finance":        ["linkhub", "twitter"],
    "marketing":      ["linkhub", "instagram", "twitter", "tiktok", "medium"],
    "sales":          ["linkhub", "twitter", "instagram"],
    "exec_assistant": ["linkhub", "instagram", "pinterest"],
    "receptionist":   ["linkhub", "instagram", "facebook"],
    "security_guard": ["linkhub", "facebook"],
    "legal":          ["linkhub", "twitter"],
    "teacher":        ["linkhub", "facebook", "pinterest"],
    "retail":         ["linkhub", "instagram", "tiktok", "facebook"],
    "customer_support": ["linkhub", "twitter", "reddit"],
    "default":        ["linkhub", "instagram", "twitter"],
}

_SOCIAL_URL_TEMPLATES = {
    "linkhub":         "http://localhost:{linkhub_port}/profile/{slug}",
    "twitter":         "https://twitter.com/{handle}",
    "github":          "https://github.com/{handle}",
    "stackoverflow":   "https://stackoverflow.com/users/{uid}/{slug}",
    "devto":           "https://dev.to/{handle}",
    "mastodon":        "https://infosec.exchange/@{handle}",
    "sectalks":        "https://sectalks.example/speakers/{slug}",
    "reddit":          "https://reddit.com/user/{handle}",
    "kaggle":          "https://kaggle.com/{handle}",
    "orcid":           "https://orcid.org/0000-{orcid}",
    "google_scholar":  "https://scholar.google.com/citations?user={gs_id}",
    "researchgate":    "https://researchgate.net/profile/{slug_dash}",
    "doximity":        "https://doximity.com/pub/{slug_dash}",
    "bloomberg":       "https://bloomberg.com/profile/person/{slug}",
    "press":           "https://prnewswire.example/people/{slug}",
    "instagram":       "https://instagram.com/{handle}",
    "facebook":        "https://facebook.com/{handle}",
    "tiktok":          "https://tiktok.com/@{handle}",
    "medium":          "https://medium.com/@{handle}",
    "pinterest":       "https://pinterest.com/{handle}",
}


def _handle_for(name: str, flavour: str) -> str:
    parts = name.lower().replace(".", "").split()
    if len(parts) < 2:
        base = parts[0] if parts else "user"
    else:
        first, last = parts[0], parts[-1]
        seed = _hash_int(name, flavour)
        styles = [
            f"{first}.{last}",
            f"{first}_{last}",
            f"{first[0]}{last}",
            f"{first}{last[0]}",
            f"{last}.{first}",
            f"{first}{last}",
        ]
        base = styles[seed % len(styles)]
    # GitHub/dev handles tend to be compact, social handles can have a digit suffix.
    if flavour in {"twitter", "instagram", "tiktok", "facebook", "reddit", "medium", "pinterest"}:
        tail = _hash_int(name, flavour) % 100
        if tail < 40:
            base = f"{base}{tail:02d}"
    return base


def social_profiles_for(
    name: str, company: str, email: str, ext: str,
    role_class: str = "default", linkhub_port: int = 9003,
    phone_number: str = "",
) -> dict:
    slug = name_slug(name)
    slug_dash = slug.replace("_", "-")
    networks = _ROLE_SOCIAL_MIX.get(role_class) or _ROLE_SOCIAL_MIX["default"]
    # Every persona gets linkhub + 2-3 extras (deterministic by hash).
    seed = _hash_int(name, company)
    extras = [n for n in networks if n != "linkhub"]
    pick_n = 2 + (seed % 2)  # 2 or 3 extras
    extras = extras[:pick_n] if len(extras) <= pick_n else [extras[(seed + i) % len(extras)] for i in range(pick_n)]
    chosen = ["linkhub"] + list(dict.fromkeys(extras))  # dedupe preserving order

    out: dict = {}
    for net in chosen:
        tpl = _SOCIAL_URL_TEMPLATES.get(net)
        if not tpl:
            continue
        out[net] = tpl.format(
            slug=slug,
            slug_dash=slug_dash,
            handle=_handle_for(name, net),
            uid=1_000_000 + (_hash_int(name, net) % 9_000_000),
            orcid=f"{(_hash_int(name, 'orcid') % 9999):04d}-{(_hash_int(name, 'orcid2') % 9999):04d}-{(_hash_int(name, 'orcid3') % 9999):04d}",
            gs_id=f"{(_hash_int(name, 'gs') % 0xFFFFFFFFF):09x}"[:12],
            linkhub_port=linkhub_port,
        )
    if email:
        out["work_email"] = email
    if ext:
        out["work_phone_ext"] = ext
    if phone_number:
        out["work_phone"] = phone_number
    return out


def augment_osint(persona: dict, company: str, tz: str = "America/New_York", linkhub_port: int = 9003, force_social: bool = False) -> bool:
    """Add public_facts / internal_context / social_profiles / phone_number to persona if missing.
    Returns True if anything changed.
    """
    changed = False
    role_class = classify_role(persona.get("role", ""))
    name = persona.get("name", "")
    ext = persona.get("phone_ext", "")

    # Realistic phone number.
    if not persona.get("phone_number"):
        persona["phone_number"] = phone_number_for(name, ext, tz)
        changed = True

    if "public_facts" not in persona:
        persona["public_facts"] = public_facts_for(role_class, name, company)
        changed = True
    if "internal_context" not in persona:
        persona["internal_context"] = internal_context_for(role_class, name, company)
        changed = True

    # Upgrade legacy social_profiles that only have {linkhub, work_email, work_phone_ext}.
    existing = persona.get("social_profiles") or {}
    non_contact_keys = set(existing.keys()) - {"work_email", "work_phone_ext", "work_phone"}
    is_legacy = (
        not existing
        or non_contact_keys.issubset({"linkhub"})
        or len(non_contact_keys) < 2
    )
    if is_legacy or force_social:
        persona["social_profiles"] = social_profiles_for(
            name, company,
            persona.get("email", ""),
            ext,
            role_class=role_class,
            linkhub_port=linkhub_port,
            phone_number=persona.get("phone_number", ""),
        )
        changed = True
    elif "work_phone" not in existing and persona.get("phone_number"):
        existing["work_phone"] = persona["phone_number"]
        changed = True
    return changed


def build_persona(emp: dict, company: str, tz: str) -> tuple[str, dict]:
    role = emp.get("role", "")
    role_class = classify_role(role)
    name = emp["name"]
    tpl = persona_for(role_class, name, tz, company)
    persona = {
        "name": name,
        "role": f"{role} at {company}",
        "age": tpl["age"],
        "personality": tpl["personality"],
        "weakness": tpl["weakness"],
        "security_training": tpl["security_training"],
        "verification_questions": [],
        "vulnerability_triggers": tpl["vulnerability_triggers"],
        "resistance_points": tpl["resistance_points"],
        "break_conditions": tpl["break_conditions"],
        "system_prompt_additions": tpl["system_prompt_additions"],
        "phone_ext": emp.get("ext", ""),
        "email": emp.get("email", ""),
        "contactable": True,
        "schedule": tpl["schedule"],
        "life": life_for(role_class, company, tz),
        "auto_generated": True,
    }
    augment_osint(persona, company, tz=tz)
    slug = (name.lower()
            .replace(".", "")
            .replace("dr ", "")
            .replace(" ", "_"))
    return slug, persona


def enrich_lab(path: Path, force_social: bool = False):
    lab = json.loads(path.read_text(encoding="utf-8"))
    personas = lab.setdefault("personas", {})
    existing_names = {p["name"] for p in personas.values()}
    company = lab["target_company"]["name"]
    if isinstance(company, dict):
        company = company.get("en") or next(iter(company.values()), "")
    tz = infer_timezone(lab)
    added = 0
    augmented = 0
    for emp in lab.get("target_company", {}).get("employees", []):
        if emp["name"] in existing_names:
            continue
        slug, persona = build_persona(emp, company, tz)
        base_slug = slug
        n = 2
        while slug in personas:
            slug = f"{base_slug}_{n}"
            n += 1
        personas[slug] = persona
        added += 1
    for persona in personas.values():
        p_tz = (persona.get("schedule") or {}).get("timezone") or tz
        if augment_osint(persona, company, tz=p_tz, force_social=force_social):
            augmented += 1
    path.write_text(json.dumps(lab, indent=2, ensure_ascii=False), encoding="utf-8")
    return added, augmented


def main():
    import sys
    force_social = "--force-social" in sys.argv
    total_added = 0
    total_aug = 0
    for f in sorted(LABS_DIR.glob("*.json")):
        added, aug = enrich_lab(f, force_social=force_social)
        print(f"{f.name}: +{added} new, +{aug} augmented")
        total_added += added
        total_aug += aug
    print(f"Total added: {total_added} | augmented: {total_aug}")


if __name__ == "__main__":
    main()
