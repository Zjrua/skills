# Pitfall: Cron Prompt ↔ Skill Drift

## Problem

The cron job prompt and the skill's "推荐的 cron prompt 结构" section can drift apart over time. When they disagree, the agent gets confused and may:

- Use deprecated API flags (v1 `--mode overwrite` was used for weeks after v1 shutdown)
- Try browser-first when curl is more reliable in cron
- Miss packaged scripts (`parse_all_sources.py`) and hand-write parsing code each run
- Follow dead instructions (e.g., `--new-title` step that errors)

## Root Cause

Cron prompts are updated via `cronjob action=update` — a separate action from skill patches. When you fix a skill, the cron prompt doesn't auto-update. Conversely, when you update a cron prompt, the skill's reference section can become stale.

## Prevention Rules

1. **When updating a cron prompt**: Also update the skill's "推荐的 cron prompt 结构" section to match. They must be identical in substance.
2. **When patching the skill's cron section**: Check if the live cron prompt still matches. Use `cronjob action=list` to find the job, read its `prompt_preview`, and `cronjob action=update` if drifted.
3. **The skill is the source of truth**: If cron prompt and skill conflict, the skill wins. But the goal is to keep them in sync so there's no conflict.

## 2026-07-08 Incident

- Cron prompt still had v1 API instructions (`--mode overwrite`, `--mode append --new-title`)
- Cron prompt said "先 browser_navigate" (browser-first)
- Cron prompt didn't mention `parse_all_sources.py` packaged script
- Skill had v2 instructions but also had browser-first language in multiple places
- Fix: rewrote cron prompt to curl-first/v2-only/script-referencing, patched 4 sections in skill to match

## Verification Checklist

After any cron prompt or skill update, verify:

- [ ] Cron prompt uses only v2 API (`--command overwrite`, no `--mode`/`--markdown`/`--new-title`)
- [ ] Cron prompt says curl-first, not browser-first
- [ ] Cron prompt references `parse_all_sources.py` script
- [ ] Cron prompt lists all 10 parallel curl sources
- [ ] Skill's "推荐的 cron prompt 结构" matches cron prompt
- [ ] Skill's "推荐的 cron 采集流程" bullet says curl-first
- [ ] Skill's "工具选择" note says curl-first
