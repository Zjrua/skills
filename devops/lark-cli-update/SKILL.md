---
name: lark-cli-update
description: Update lark-cli to the latest version on Linux and macOS, including binary download and skills sync.
version: 1.1.0
author: Hermes Agent
---

# Update lark-cli

lark-cli's `npm install` post-install script (`scripts/install.js`) tries to download the binary from GitHub, which can hang on servers with slow/restricted network access. This skill handles the manual binary download + skills sync.

## Platform Detection

| Platform | npm root | Binary arch |
|----------|----------|-------------|
| Linux amd64 | `/usr/lib/node_modules/` | `linux-amd64` |
| Linux arm64 | `/usr/lib/node_modules/` | `linux-arm64` |
| macOS Intel | `/usr/local/lib/node_modules/` | `darwin-amd64` |
| macOS Apple Silicon | `/usr/local/lib/node_modules/` | `darwin-arm64` |

Use `npm root -g` to confirm the actual path if unsure.

> **macOS note**: `npm install -g` may require `sudo` if Node was installed via `.pkg` or Homebrew. Recommend configuring `npm config set prefix '~/.npm-global'` to avoid sudo, or using nvm.

## Steps

### 1. Update npm package (skip post-install)

```bash
npm install -g @larksuite/cli@latest --ignore-scripts
# macOS may need: sudo npm install -g @larksuite/cli@latest --ignore-scripts
```

### 2. Determine version and platform

```bash
NPM_ROOT=$(npm root -g)
VERSION=$(node -e "console.log(require('${NPM_ROOT}/@larksuite/cli/package.json').version.replace(/-.*$/,''))")
```

### 3. Download the binary

```bash
cd /tmp

# Determine platform string
# Linux amd64: linux-amd64, Linux arm64: linux-arm64
# macOS Intel: darwin-amd64, macOS Apple Silicon: darwin-arm64
PLATFORM="linux-amd64"  # adjust for your platform

# Direct download
curl -L -o lark-cli.tar.gz "https://github.com/larksuite/cli/releases/download/v${VERSION}/lark-cli-${VERSION}-${PLATFORM}.tar.gz"

# If GitHub is slow (common in China), use mirror:
# curl -L -o lark-cli.tar.gz "https://ghfast.top/https://github.com/larksuite/cli/releases/download/v${VERSION}/lark-cli-${VERSION}-${PLATFORM}.tar.gz"

tar xzf lark-cli.tar.gz
```

### 4. Install the binary

The `bin/` directory may not exist (`--ignore-scripts` skips creating it), so create it manually:

```bash
mkdir -p ${NPM_ROOT}/@larksuite/cli/bin
cp /tmp/lark-cli ${NPM_ROOT}/@larksuite/cli/bin/lark-cli
chmod +x ${NPM_ROOT}/@larksuite/cli/bin/lark-cli
```

### 5. Verify

```bash
lark-cli --version
lark-cli auth status
```

### 6. Update Skills (required)

CLI skills must be re-installed after updating:

```bash
npx -y skills add https://open.feishu.cn --skill -y
```

This installs/updates 25 lark-* skills and symlinks them to all detected agents (Claude Code, OpenClaw, Hermes Agent, etc.).

## Notes

- The npm mirror (npmmirror.com) does NOT host the binary — only GitHub releases work
- The `install.js` script also checks checksums; for production security, verify the checksum matches the release notes
- If lark-cli was previously installed via a different prefix, check `which lark-cli` to confirm the binary location
