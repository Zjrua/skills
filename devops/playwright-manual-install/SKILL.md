---
name: playwright-manual-install
description: Install Playwright chromium when automated download fails (common in China/restricted networks).
---

# Playwright Chromium Manual Install

When `npx playwright install chromium` fails (timeout, mirror issues, GFW, etc.), use this manual approach.

## Symptoms

```
browserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-XXXX/
```

Or download failures from Google/CDN mirrors.

## How It Works

Playwright expects chromium headless shell at a specific path:
```
/root/.cache/ms-playwright/chromium_headless_shell-{VERSION}/chrome-headless-shell-linux64/chrome-headless-shell
```

The version number (e.g. `1217`) maps to a specific Chrome for Testing version (e.g. `147.0.7727.15`).

## Steps

### 1. Find the required version

```bash
# Check which version playwright expects
npx playwright install chromium 2>&1 | grep "Chrome for Testing"
# Or check existing cache
ls /root/.cache/ms-playwright/
```

### 2. Download the zip on a machine with internet access

URL pattern:
```
https://storage.googleapis.com/chrome-for-testing-public/{VERSION}/linux64/chrome-headless-shell-linux64.zip
```

Common versions:
- Playwright chromium v1217 → Chrome 147.0.7727.15

### 3. Upload zip to server, extract and place

```bash
mkdir -p /root/.cache/ms-playwright/chromium_headless_shell-{VERSION}
unzip -o /path/to/chrome-headless-shell-linux64.zip -d /tmp/chrome-extract
mv /tmp/chrome-extract/chrome-headless-shell-linux64 /root/.cache/ms-playwright/chromium_headless_shell-{VERSION}/
chmod +x /root/.cache/ms-playwright/chromium_headless_shell-{VERSION}/chrome-headless-shell-linux64/chrome-headless-shell
```

### 4. Verify

```bash
/root/.cache/ms-playwright/chromium_headless_shell-{VERSION}/chrome-headless-shell-linux64/chrome-headless-shell --version
```

## Mirrors to Try First (China)

```bash
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright npx playwright install chromium
PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright npx playwright install chromium
```

Note: npmmirror mirrors often don't have the latest Chrome for Testing builds. Manual download from Google Storage (`storage.googleapis.com`) is the most reliable approach.
