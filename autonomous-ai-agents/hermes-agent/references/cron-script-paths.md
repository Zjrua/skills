# Cron Script Path Resolution

## How Paths Are Resolved (`cron/scheduler.py` ~L684-705)

```python
scripts_dir = _get_hermes_home() / "scripts"          # ~/.hermes/scripts
scripts_dir_resolved = scripts_dir.resolve()

raw = Path(script_path).expanduser()
if raw.is_absolute():
    path = raw.resolve()
else:
    path = (scripts_dir / raw).resolve()              # joins with ~/.hermes/scripts/

# Security: path MUST be inside scripts_dir
path.relative_to(scripts_dir_resolved)  # raises ValueError if outside

# Then checks: exists? is_file?
```

**Key:** The `workdir` field is NOT used for script path resolution. It only sets the CWD for the script's execution.

## Error Messages

| Error | Cause |
|-------|-------|
| `Script not found: /root/.hermes/scripts/scripts/run_foo.py` | Script configured as `scripts/run_foo.py` but not copied to `~/.hermes/scripts/` |
| `Blocked: script path resolves outside the scripts directory` | Symlink points outside `~/.hermes/scripts/`, or absolute path used |

## Fix Procedure

When project scripts at `/path/to/project/scripts/` need to run as cron jobs:

1. **Copy** (don't symlink) scripts to `~/.hermes/scripts/scripts/`:
   ```bash
   mkdir -p ~/.hermes/scripts/scripts
   cp /path/to/project/scripts/run_*.py ~/.hermes/scripts/scripts/
   cp /path/to/project/scripts/push_*.py ~/.hermes/scripts/scripts/  # dependencies
   ```

2. **Fix path references** in copied scripts:
   - `os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")` → `os.chdir("/path/to/project")`
   - `BASE_DIR = os.path.dirname(SCRIPT_DIR)` → `BASE_DIR = "/path/to/project"`

3. **Verify** by running the script from `~/.hermes/scripts/`:
   ```bash
   cd ~/.hermes/scripts && python3 scripts/run_foo.py
   ```

4. **Trigger cron job** to confirm end-to-end delivery.

## Pitfalls

- **Symlinks are security-blocked** — the resolver follows symlinks and rejects if the target is outside `~/.hermes/scripts/`
- **Subprocess calls** in the copied script will use the project's original `scripts/` dir (via `os.chdir`), which is fine — the cron runner only needs to find the entry-point script
- **State files** (JSON, PROGRESS.md, etc.) referenced by the scripts should use absolute paths to the project directory
