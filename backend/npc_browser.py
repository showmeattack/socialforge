"""NPC browser agent — Playwright MCP server via stdio JSON-RPC.

Uses @playwright/mcp tooling via stdio JSON-RPC, NOT the Python
playwright API directly. Communicates with an MCP server subprocess.
"""
import asyncio
import json
import re
import hashlib

_URL_RE = re.compile(r"https?://[^\s\"'<>\)\]]+", re.IGNORECASE)
_SHORTENERS = re.compile(
    r"\b(bit\.ly|t\.co|ow\.ly|tinyurl\.com|goo\.gl|rb\.gy|is\.gd|buff\.ly|tiny\.cc)\b",
    re.IGNORECASE,
)
_SUSPICIOUS_DOMAIN = re.compile(
    r"(login|secure|verify|account|update|portal|signin|helpdesk|microsoft|google|"
    r"paypal|amazon|apple|office365)\W",
    re.IGNORECASE,
)
# Parse snapshot refs for form fields
_FIELD_REF = re.compile(
    r'\[ref=([^\]]+)\].*?(?:email|username|user|login|password|pass)',
    re.IGNORECASE,
)
_PASS_REF = re.compile(
    r'password.*?\[ref=([^\]]+)\]|\[ref=([^\]]+)\].*?password',
    re.IGNORECASE,
)
_SUBMIT_REF = re.compile(
    r'button.*?\[ref=([^\]]+)\]|\[ref=([^\]]+)\].*?(?:sign in|login|submit|continue)',
    re.IGNORECASE,
)


def _extract_url(text: str) -> str | None:
    m = _URL_RE.search(text)
    return m.group(0).rstrip(".,;:!?") if m else None


def _npc_credentials(persona: dict, lab: dict) -> tuple[str, str]:
    name = persona.get("name", "user")
    email = (
        persona.get("email") or
        persona.get("work_email") or
        (persona.get("social_profiles") or {}).get("work_email") or ""
    )
    if not email:
        domain = (lab.get("target_company") or {}).get("domain", "company.com")
        parts = name.lower().split()
        email = (f"{parts[0]}.{parts[-1]}@{domain}" if len(parts) > 1
                 else f"{parts[0]}@{domain}")
    company = (lab.get("target_company") or {}).get("name", "Corp")
    h = hashlib.md5(f"{name}{company}".encode()).hexdigest()[:4]
    password = f"{company.split()[0]}{2024 + int(h[0], 16) % 2}#{h[1:3].upper()}"
    return email, password


def _will_submit(gullibility: int, expertise: str, suspicious: bool, ssl_ok: bool) -> bool:
    if expertise == "security_expert":
        return False
    if expertise == "security_aware" and (suspicious or not ssl_ok):
        return False
    return gullibility >= 70 or (gullibility >= 55 and not suspicious and ssl_ok)


class _MCPClient:
    """Minimal Playwright MCP stdio client using Content-Length framing."""

    def __init__(self):
        self._proc: asyncio.subprocess.Process | None = None
        self._call_id = 0

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            "npx", "@playwright/mcp@latest", "--headless", "--no-sandbox",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        # MCP initialize handshake
        init_resp = await self._raw_call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "npc_browser", "version": "1.0"},
        })
        _ = init_resp  # noqa: response consumed
        # Send initialized notification (no response expected)
        notif = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }).encode()
        await self._write_frame(notif)

    async def _write_frame(self, content: bytes) -> None:
        header = f"Content-Length: {len(content)}\r\n\r\n".encode()
        self._proc.stdin.write(header + content)
        await self._proc.stdin.drain()

    async def _read_frame(self, timeout: float = 20.0) -> dict:
        header = await asyncio.wait_for(
            self._proc.stdout.readuntil(b"\r\n\r\n"), timeout=timeout
        )
        m = re.search(rb"Content-Length: (\d+)", header)
        if not m:
            return {}
        length = int(m.group(1))
        body = await asyncio.wait_for(
            self._proc.stdout.readexactly(length), timeout=timeout
        )
        return json.loads(body)

    async def _raw_call(self, method: str, params: dict) -> dict:
        self._call_id += 1
        msg = json.dumps({
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": method,
            "params": params,
        }).encode()
        await self._write_frame(msg)
        # Skip notifications until we get our response
        for _ in range(10):
            resp = await self._read_frame()
            if resp.get("id") == self._call_id:
                return resp
        return {}

    async def call(self, tool: str, args: dict) -> str:
        """Call a Playwright MCP tool, return text content."""
        resp = await self._raw_call("tools/call", {"name": tool, "arguments": args})
        result = resp.get("result") or {}
        content = result.get("content") or []
        return content[0].get("text", "") if content else ""

    async def close(self) -> None:
        if self._proc:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except Exception:
                pass


async def npc_click_link(message: str, persona: dict, lab: dict) -> dict:
    """
    NPC clicks a URL from message via Playwright MCP server.

    Returns:
        url, visited, page_title, form_found, submitted,
        credentials {username, password} | None,
        bounced, bounce_reason, page_analysis, domain_suspicious, ssl_valid
    """
    url = _extract_url(message)
    out: dict = {
        "url": url, "visited": False, "page_title": "",
        "form_found": False, "submitted": False, "credentials": None,
        "bounced": False, "bounce_reason": "", "page_analysis": "",
        "domain_suspicious": False, "ssl_valid": True,
    }
    if not url:
        return out

    psych = persona.get("psychology") or {}
    gullibility = psych.get("gullibility", 50)
    training = (persona.get("security_training") or "").lower()
    role = (persona.get("role") or "").lower()
    if "expert" in training or "cissp" in training or "ceh" in training:
        expertise = "security_expert"
    elif "aware" in training or "phishing" in training or "it " in role or "soc" in role:
        expertise = "security_aware"
    elif psych.get("tech_savvy", 50) <= 30:
        expertise = "novice"
    else:
        expertise = "average"

    ssl_ok = url.startswith("https://")
    domain_m = re.search(r"https?://([^/:]+)", url)
    domain = domain_m.group(1) if domain_m else ""
    domain_suspicious = (
        bool(_SUSPICIOUS_DOMAIN.search(domain + "/")) or
        bool(_SHORTENERS.search(url)) or
        not ssl_ok or
        bool(re.search(r"\d", domain.split(".")[0]))
    )
    out["domain_suspicious"] = domain_suspicious
    out["ssl_valid"] = ssl_ok

    analysis: list[str] = []
    if not ssl_ok:
        analysis.append("SSL_WARNING")
    if domain_suspicious:
        analysis.append(f"SUSPICIOUS_DOMAIN:{domain}")
    if _SHORTENERS.search(url):
        analysis.append("LINK_SHORTENER")

    client = _MCPClient()
    try:
        await client.start()

        # Navigate
        await client.call("browser_navigate", {"url": url})
        out["visited"] = True

        # Snapshot — get accessibility tree to find form refs
        snap_text = await client.call("browser_snapshot", {})

        # Extract page title from snapshot
        title_m = re.search(r'page title[:\s]+"?([^"\n]+)"?', snap_text, re.IGNORECASE)
        if not title_m:
            title_m = re.search(r'heading\s+"([^"]+)"', snap_text, re.IGNORECASE)
        out["page_title"] = (title_m.group(1)[:80] if title_m else "")

        analysis.append(f"PAGE_TITLE:{out['page_title'] or '(unknown)'}")

        has_password = bool(re.search(r"password|passwd", snap_text, re.IGNORECASE))
        has_email = bool(re.search(r"email|username|user name", snap_text, re.IGNORECASE))
        has_form = has_password or has_email
        out["form_found"] = has_form

        if has_form:
            fields = []
            if has_email:
                fields.append("email/username")
            if has_password:
                fields.append("password")
            analysis.append(f"FORM_FIELDS:{','.join(fields)}")

        out["page_analysis"] = " | ".join(analysis) or "PAGE_VISITED"

        if not has_form:
            out["bounced"] = True
            out["bounce_reason"] = "no login form on page"
        elif not _will_submit(gullibility, expertise, domain_suspicious, ssl_ok):
            out["bounced"] = True
            out["bounce_reason"] = "NPC did not trust the page"
        else:
            username, password = _npc_credentials(persona, lab)
            # Find email/username field ref
            email_ref = None
            for pattern in [
                r'(?:textbox|input).*?(?:email|username|user)[^\[]*\[ref=([^\]]+)\]',
                r'\[ref=([^\]]+)\][^\n]*(?:email|username|user)',
            ]:
                m = re.search(pattern, snap_text, re.IGNORECASE)
                if m:
                    email_ref = m.group(1)
                    break
            # Find password field ref
            pass_ref = None
            for pattern in [
                r'(?:textbox|input).*?password[^\[]*\[ref=([^\]]+)\]',
                r'\[ref=([^\]]+)\][^\n]*password',
            ]:
                m = re.search(pattern, snap_text, re.IGNORECASE)
                if m:
                    pass_ref = m.group(1)
                    break
            # Find submit button ref
            submit_ref = None
            for pattern in [
                r'button[^\[]*(?:sign in|log in|login|submit|continue)[^\[]*\[ref=([^\]]+)\]',
                r'\[ref=([^\]]+)\][^\n]*(?:sign in|log in|login|submit)',
            ]:
                m = re.search(pattern, snap_text, re.IGNORECASE)
                if m:
                    submit_ref = m.group(1)
                    break

            # Fill via MCP tools
            try:
                if email_ref:
                    await client.call("browser_type", {
                        "ref": email_ref,
                        "element": "Email or username field",
                        "text": username,
                    })
                if pass_ref:
                    await client.call("browser_type", {
                        "ref": pass_ref,
                        "element": "Password field",
                        "text": password,
                    })
                if submit_ref:
                    await client.call("browser_click", {
                        "ref": submit_ref,
                        "element": "Submit / Sign in button",
                    })
                elif has_form:
                    # Try pressing Enter if no button ref found
                    await client.call("browser_press_key", {"key": "Enter"})

                await asyncio.sleep(2)
                out["submitted"] = True
                out["credentials"] = {"username": username, "password": password}
            except Exception as fill_err:
                out["bounced"] = True
                out["bounce_reason"] = f"fill_error:{type(fill_err).__name__}"

    except FileNotFoundError:
        out["bounce_reason"] = "npx not found — MCP server unavailable"
        out["page_analysis"] = "MCP_UNAVAILABLE"
    except asyncio.TimeoutError:
        out["bounce_reason"] = "MCP server timeout"
        out["page_analysis"] = "MCP_TIMEOUT"
    except Exception as exc:
        out["bounce_reason"] = f"mcp_error:{type(exc).__name__}"
    finally:
        await client.close()

    return out
