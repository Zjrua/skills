---
name: hermes-dashboard
description: Manage and extend the Hermes Dashboard — a FastAPI ops monitoring console at port 80. Add service modules, fix auth issues, manage systemd service.
tags: [fastapi, dashboard, monitoring, systemd, ops]
triggers:
  - dashboard module
  - 器材管理 dashboard
  - hermes-dashboard service
  - add card to dashboard
  - port 80 dashboard
---

# Hermes Dashboard

FastAPI ops monitoring console serving at `http://115.190.6.244` (port 80).
Project: `/root/projects/hermes-dashboard/`
Systemd: `hermes-dashboard.service` (uses `/root/.hermes/hermes-agent/venv/bin/python3`)
Style: Linear.app dark theme — minimal, purple accent

## Architecture

```
main.py                    # FastAPI app, router registration, sub-page routes, login/logout endpoints
auth.py                    # Dual auth: signed cookie session + API key middleware
security.py                # Rate limiter, CORS, log filter
routers/
  hermes_agent.py          # /api/hermes/* (status, health, sessions, system, kanban, cron)
  omlx.py                  # /api/omlx/* (health, models, latency, status)
  zerotier.py              # /api/zerotier/* (status, peers, networks)
  providers.py             # /api/providers/* (status)
  equipment.py             # /api/equipment/* (status, recent) — proxy to localhost:3000
static/
  login.html               # Login page (session auth entry point)
  index.html               # Main dashboard (cards in grid rows)
  hermes.html, omlx.html, network.html, providers.html, equipment.html
  css/dashboard.css, css/subpage.css
  js/dashboard.js, js/subpage.js
.env                       # DASHBOARD_USER, DASHBOARD_PASS, DASHBOARD_SESSION_SECRET, DASHBOARD_API_KEY
```

## Adding a New Service Module (5 steps)

### Step 1: Create proxy router

Create `routers/<module>.py`. For internal services (localhost), proxy with auth:

```python
import os, httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/<module>", tags=["<module>"])
BACKEND_URL = os.getenv("<MODULE>_BACKEND_URL", "http://localhost:PORT")

# Token cache pattern (for services needing auth)
_token_cache = {"token": None, "expires": 0}
async def _get_token() -> str:
    import time
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires"]:
        return _token_cache["token"]
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(f"{BACKEND_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"})
        token = resp.json().get("data", {}).get("token")
        _token_cache["token"] = token
        _token_cache["expires"] = now + 3600
        return token

@router.get("/status")
async def module_status():
    try:
        token = await _get_token()
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(f"{BACKEND_URL}/api/stats/dashboard",
                headers={"Authorization": f"Bearer {token}"})
            data = resp.json().get("data", {})
        return {"status": "online", **extracted_metrics}
    except httpx.ConnectError:
        return {"status": "offline", "error": "Backend unreachable"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### Step 2: Register router in main.py

Add to the `for module_name, label, endpoint` loop:
```python
("equipment", "器材管理系统", "/api/equipment"),
```

### Step 3: Add sub-page route in main.py

```python
@app.get("/equipment")
async def page_equipment():
    return FileResponse(STATIC_DIR / "equipment.html")
```

### Step 4: Add card to index.html

Add to `grid-row-1` (update `grid-template-columns: repeat(4, 1fr)` if needed):
```html
<div class="card clickable" id="card-equipment" tabindex="0" onclick="window.location='/equipment'">
  <div class="card-header">
    <div style="display:flex;align-items:center;gap:10px">
      <div class="health-dot health-unknown" id="equipment-health-dot"></div>
      <span class="card-label">器材管理</span>
    </div>
  </div>
  <div id="equipment-body">...</div>
</div>
```

### Step 5: Add JS load function in dashboard.js

Create `loadXxxStatus()` function + add to `refreshAll()` Promise.all array.

## Authentication System

The dashboard uses **dual auth**: signed cookie sessions for browsers + API key for scripts.

| Method | How | Use case |
|--------|-----|----------|
| Session cookie | Browser login at `/login` → `hermes_session` cookie | Human visitors |
| API Key | `X-API-Key` header or `?key=` param | curl, scripts, CLI |

### Auth middleware logic (auth.py)

```
Request arrives
  → Is path in PUBLIC_PATHS or /static/*? → pass through
  → Has valid API Key? → pass through
  → Has valid session cookie? → pass through (auto-renew near expiry)
  → Is HTML request (Accept: text/html)? → 302 redirect to /login
  → Otherwise → 401 JSON
```

### Config (.env)

```
DASHBOARD_USER=admin          # login username
DASHBOARD_PASS=admin123       # login password
DASHBOARD_SESSION_SECRET=...  # hex string for HMAC-SHA256 cookie signing
DASHBOARD_SESSION_TTL=604800  # 7 days
DASHBOARD_API_KEY=...         # legacy API key for scripts
```

### Adding a new public path

If a new route should skip auth (e.g. a webhook endpoint), add it to `PUBLIC_PATHS` in `auth.py`:
```python
PUBLIC_PATHS = {"/login", "/api/auth/login", "/api/health", "/api/docs", "/api/redoc", "/openapi.json"}
```

## Pitfalls

### ⚠️ Auth Middleware: API Routes Must Be Public for Browser JS

The `auth.py` middleware uses **two checks** to allow browser JS access to API endpoints:

1. `PUBLIC_PATHS` set — exact path matches (e.g. `/login`, `/api/health`)
2. `_should_skip()` — prefix match: `path.startswith("/api/")` (except `/api/docs`)

Without (2), browser `fetch('/api/hermes/status')` gets 401 because the request has no API key header — the session cookie is present but the middleware only checked API keys for `/api/*` paths. **FIX**: the `_should_skip()` function must return True for all `/api/` paths (the session cookie check handles actual auth).

Also: sub-page routes (`/hermes`, `/equipment`, etc.) must be in `PUBLIC_PATHS` so the HTML page itself loads — the auth is then handled by the JS fetch calls which check session.

Without these fixes, the dashboard shows "Cannot reach API" for all cards.

### ⚠️ zerotier-cli Output Has Header Lines

`zerotier-cli listpeers` and `listnetworks` output a header line before the data:
```
200 listpeers <ztaddr> <path> <latency> <version> <role>    ← header (skip!)
200 listpeers 4f0722cf8a 61.167.60.34/9993;3864;3864 28 1.14.2 LEAF  ← data
```

The parser MUST skip lines where the ID field starts with `<`:
```python
ztaddr = parts[2]
if ztaddr.startswith("<"):
    continue
```

Without this, the dashboard shows a phantom peer `<ztaddr>` with latency -1.

### ⚠️ psutil.cpu_percent(interval=) Blocks the Event Loop

`psutil.cpu_percent(interval=0.5)` blocks the async handler for 500ms. In a FastAPI endpoint this delays the response. Use `interval=0.1` or `interval=0` (returns last measurement) instead.

### ⚠️ Gateway Health Status Must Be "ok" Not "running"

The JS `loadHermesStatus()` checks `health.gateway.status === 'ok'`. The router must return `"ok"` for a healthy gateway, NOT `"running"`. Using `"running"` makes the JS think the gateway is degraded.

### ⚠️ /dashboard Route (Not Just /)

The main dashboard is accessible at both `/` and `/dashboard`. Sub-pages link back to `/dashboard` (not `/`). When adding new sub-pages, always use `href="/dashboard"` for the back link.

The login page also redirects to `/dashboard` after successful login (not `/`).

### ⚠️ Mobile CSS: Don't Hide All of topnav-meta

The sub-page CSS (`subpage.css`) had `@media (max-width: 768px) { .topnav-meta { display: none; } }` which hid the refresh button and health status on mobile. The fix: only hide the clock text (`.topbar-clock`), keep the refresh button and health dot visible.

For the main dashboard (`dashboard.css`), the inline `grid-template-columns: repeat(4, 1fr)` on `grid-row-1` needs `!important` in the mobile media query to override. Also hide `.topbar-user span` (username text) and `.topbar-title span` ("Hermes Dashboard" text) on mobile, keeping just the icons.

### ⚠️ systemctl restart Hangs

`systemctl restart hermes-dashboard` can hang indefinitely. Use instead:
```bash
systemctl kill hermes-dashboard && sleep 1 && systemctl start hermes-dashboard
```

### ⚠️ API Response Format Varies

Backend APIs may return `data` as a list OR as `{items: [...]}`. Always handle both:
```python
loans = data.get("data", [])
if isinstance(loans, dict):
    loans = loans.get("items", [])
if not isinstance(loans, list):
    loans = []
```

### ⚠️ Systemd PATH Missing /usr/sbin

When routers call external CLI tools (e.g. `zerotier-cli`), the systemd service's `PATH` only includes `/root/.hermes/hermes-agent/venv/bin:/usr/local/bin:/usr/bin:/bin`. Tools in `/usr/sbin` (like `zerotier-cli`) will fail silently with `FileNotFoundError`.

**FIX**: Always use absolute paths for external commands in routers:
```python
subprocess.run(["/usr/sbin/zerotier-cli", "info"], ...)  # ✓
subprocess.run(["zerotier-cli", "info"], ...)              # ✗ fails under systemd
```

Similarly, `hermes` CLI is at `/root/.hermes/hermes-agent/venv/bin/hermes` and IS in the service PATH. But any tool outside those dirs needs the full path.

### ⚠️ Kanban "Done" Tasks May Be Stubs

Tasks marked `done` by kanban workers may contain placeholder/stub implementations (e.g. `return {"message": "占位实现 — 等待 T3 后端任务填充真实逻辑"}`). **Always verify** the actual router code after tasks complete — don't trust the `done` status.

Check each router for:
- Placeholder return messages containing "占位", "placeholder", "TODO", "waiting for"
- Missing real data-fetching logic (no httpx calls, no subprocess calls, no file reads)
- Endpoints that the JS/frontend calls but the router doesn't define (e.g. JS calls `/api/omlx/health` but router only has `/status` and `/models`)

### ⚠️ httpx Dependency

The proxy routers need `httpx`. It's available in the hermes-agent venv used by the service:
```bash
/root/.hermes/hermes-agent/venv/bin/python3 -c "import httpx"
```

### ⚠️ Service Restart Required

Changes to Python files require restarting the service. Static HTML/JS/CSS changes do NOT require restart (served directly).

## Verification

After adding a module:
```bash
systemctl kill hermes-dashboard && sleep 1 && systemctl start hermes-dashboard
sleep 3
curl -s http://127.0.0.1/api/<module>/status | python3 -m json.tool
curl -s http://127.0.0.1/<subpage> | grep -c "<title>"
curl -s http://127.0.0.1/ | grep -c "card-<module>"
```

## Existing Modules

| Module | Backend | API Prefix | Sub-page |
|--------|---------|------------|----------|
| Hermes Agent | hermes gateway :8642 | /api/hermes | /hermes |
| OMLX Server | 192.168.192.2:8000 | /api/omlx | /omlx |
| ZeroTier | zerotier-cli | /api/zerotier | /network |
| Providers | in-process | /api/providers | /providers |
| 器材管理 | localhost:3000 | /api/equipment | /equipment |
| System Resources | via hermes system API | (in hermes card) | — |
| Kanban Board | via hermes kanban API | (in hermes card) | — |
| Cron Tasks | via hermes cron API | (in hermes cron table) | — |
