# lark-cli docs +update v2 Migration Notes

**Discovered**: 2026-05-27
**lark-cli version**: 1.0.41 (upgraded from 1.0.40 during session)
**Doc token**: XCehdq7FVoX6rUxLQjkcEasdnub

## Problem

When using `lark-cli docs +update` with `--api-version v2`, the v1 flags silently fail:

```
lark-cli docs +update --doc TOKEN --as bot --mode overwrite --markdown @file.md --api-version v2
# Error: "--command is required"
```

## Root Cause

v2 API completely redesigned the `+update` subcommand. The `--help` without `--api-version v2` shows v1 flags which are **incompatible** with v2 mode.

## Solution

```bash
cd /tmp && lark-cli docs +update \
  --doc {TOKEN} --as bot --api-version v2 \
  --command overwrite \
  --doc-format markdown \
  --content @your_file.md \
  --revision-id -1
```

## Key Changes

| v1 Flag | v2 Replacement |
|---------|---------------|
| `--mode overwrite` | `--command overwrite` |
| `--mode append` | `--command append` |
| `--markdown "text"` / `@file` | `--content @file` |
| N/A | `--doc-format markdown` (required) |
| N/A | `--revision-id -1` (default latest) |

## Also Discovered

- `lark-cli api POST ... batch_update` returns 404 for docx block operations — use `docs +update` instead
- `--page-all` and `-o` are mutually exclusive in `lark-cli api` — use `> file.json` redirect
- `@file` in `--content` requires relative path: `cd /tmp && --content @file.md` (not `/tmp/file.md`)
- Markdown with literal `\n` strings renders as-is in Feishu — must pre-clean with `.replace('\\n', '\n')`
