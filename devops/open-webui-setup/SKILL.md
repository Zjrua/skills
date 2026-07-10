---
name: open-webui-setup
description: Configure Open WebUI as a web frontend for Hermes Agent via its built-in API server.
---

# Open WebUI Integration with Hermes Agent

Connect Open WebUI as a polished web chat frontend for your Hermes Agent instance.

## Reference

- Docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui
- Architecture: Open WebUI sends `/v1/chat/completions` to Hermes API server (port 8642), Hermes responds with SSE streaming.

## Prerequisites

- Docker installed and running
- Hermes Agent gateway running

## Setup Steps

### 1. Enable Hermes API Server

Add to `~/.hermes/.env`:

```
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<your-secret-key>
```

**IMPORTANT:** `API_SERVER_HOST` MUST be `0.0.0.0`, not the default `127.0.0.1`. Docker containers cannot access the host's loopback address. Without this, Open WebUI will get "Connection refused" when trying to reach the API server.

### 2. Restart Hermes Gateway

```bash
hermes gateway stop
hermes gateway start
```

Verify it's listening on all interfaces:

```bash
ss -tlnp | grep 8642
# Should show: 0.0.0.0:8642 (NOT 127.0.0.1:8642)
```

**Pitfall:** `hermes gateway stop` can hang/timeout. If it does:
```bash
kill -9 <pid>  # find PID from `ss -tlnp | grep 8642` or `hermes gateway status`
systemctl --user reset-failed hermes-gateway.service
hermes gateway start
```

**Pitfall:** `hermes gateway restart` only does a reload (USR1 signal), which does NOT pick up new environment variables. You must do a full stop + start.

### 3. Start/Configure Open WebUI

**Docker run:**
```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8642/v1 \
  -e OPENAI_API_KEY=<your-secret-key> \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

**Key points:**
- URL must end with `/v1` (not just `:8642`)
- `--add-host=host.docker.internal:host-gateway` is required for Docker bridge networking
- Port 3000 maps to container port 8080

### 4. Verify

```bash
# From host
curl http://localhost:8642/health
# Should return: {"status":"ok","platform":"hermes-agent"}

# From inside the Open WebUI container
docker exec open-webui python3 -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:8642/health', timeout=5).read().decode())"
```

### 5. Use It

1. Open `http://localhost:3000` in browser
2. Create admin account (first user = admin)
3. Select `hermes-agent` from the model dropdown
4. Start chatting — your agent has full toolset (terminal, files, web, memory, skills)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No models in dropdown | Check URL has `/v1` suffix. Verify with `curl http://localhost:8642/v1/models` |
| Connection test passes but no models | Almost always missing `/v1` suffix — the test only checks connectivity |
| "Invalid API key" | Match `OPENAI_API_KEY` in Open WebUI with `API_SERVER_KEY` in Hermes |
| Response takes long | Normal for complex queries — agent may be running multiple tool calls |
| Container can't reach API | Ensure `API_SERVER_HOST=0.0.0.0` AND gateway was fully restarted |
| Env vars not taking effect | Open WebUI env vars only apply on first launch. Use Admin UI after that, or delete volume and recreate |
| `hermes gateway stop` hangs | Kill process manually, reset-failed, then start |

## Environment Variable Summary

| Variable | Location | Default | Notes |
|----------|----------|---------|-------|
| `API_SERVER_ENABLED` | `~/.hermes/.env` | `false` | Must be `true` |
| `API_SERVER_HOST` | `~/.hermes/.env` | `127.0.0.1` | Must be `0.0.0.0` for Docker |
| `API_SERVER_KEY` | `~/.hermes/.env` | none | Any non-empty string for auth |
| `OPENAI_API_BASE_URL` | Docker env | — | `http://host.docker.internal:8642/v1` |
| `OPENAI_API_KEY` | Docker env | — | Must match `API_SERVER_KEY` |
