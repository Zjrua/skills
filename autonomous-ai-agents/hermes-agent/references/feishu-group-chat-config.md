# Feishu Group Chat Configuration

How Hermes handles group chat access control on Feishu. Source: `gateway/platforms/feishu.py` (`_admit()`, `FeishuAdapterSettings`).

## Config Hierarchy

| Level | Where | Scope |
|-------|-------|-------|
| Global | `.env` env vars | All groups |
| Default group | `config.yaml` → `feishu.default_group_policy` | Groups without per-group rules |
| Per-group | `config.yaml` → `feishu.group_rules.<chat_id>` | Specific group |

## Environment Variables

```bash
# Who can interact in groups (default: "allowlist")
FEISHU_GROUP_POLICY=allowlist          # open | allowlist | blacklist | admin_only | disabled

# Comma-separated open_ids allowed when policy is allowlist
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy

# Require @mention in groups to trigger bot (default: "true")
FEISHU_REQUIRE_MENTION=true

# Whether bots can interact: none | mentions | all (default: "none")
FEISHU_ALLOW_BOTS=none
```

## config.yaml (feishu section)

```yaml
feishu:
  require_mention: true               # Global: need @bot in groups?
  default_group_policy: open          # Default for groups without rules
  group_rules:
    "oc_xxxxx":                       # Per-group by chat_id
      policy: open                    # open | allowlist | blacklist | admin_only | disabled
      require_mention: false           # Override global require_mention for this group
      allowlist: ["ou_aaa", "ou_bbb"]
      blacklist: ["ou_ccc"]
```

Note: `feishu.require_mention` in config.yaml overrides `FEISHU_REQUIRE_MENTION` env var.

## Admission Logic (`_admit()`)

1. **Self-echo check** — reject own messages
2. **Bot check** — if sender is bot and `FEISHU_ALLOW_BOTS` is "none", reject
3. **DM passthrough** — all DMs always go through
4. **Group policy** — check `_allow_group_message()`:
   - `disabled`: reject all
   - `open`: allow all
   - `admin_only`: reject all non-admins
   - `allowlist`: only users in allowlist (or admins)
   - `blacklist`: everyone except blacklisted
5. **Mention check** — if `require_mention` is true, message must contain `@bot` or `@_all`

Admins (from `feishu.admins` in config.yaml) always bypass group policy.

## Common Configurations

### Open group (anyone can @bot)
```bash
# .env
FEISHU_GROUP_POLICY=open
FEISHU_REQUIRE_MENTION=true
```

### Allowlist + per-group override
```yaml
# config.yaml
feishu:
  require_mention: true
  default_group_policy: allowlist
  group_rules:
    "oc_public_group":
      policy: open
      require_mention: true
```

### Disable specific group
```yaml
feishu:
  group_rules:
    "oc_noisy_group":
      policy: disabled
```

## Troubleshooting

- **Bot ignores @mentions in group**: Check `FEISHU_GROUP_POLICY` is not `disabled` and user is in `FEISHU_ALLOWED_USERS` (if allowlist mode).
- **Bot responds to every message**: Set `require_mention: true`.
- **Only want specific group open**: Use `default_group_policy: allowlist` + per-group `policy: open`.
- **`FEISHU_BOT_OPEN_ID` not set**: Mention detection won't work. Gateway logs `self_ids_unknown`.
