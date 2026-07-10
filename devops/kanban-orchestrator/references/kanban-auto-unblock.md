# Kanban Dependency Auto-Unlock Workaround

## Problem

The Hermes kanban dispatcher has a bug (as of config v23) where `recompute_ready()` only scans `todo` status tasks for dependency promotion. Tasks that were prematurely claimed by the dispatcher and then auto-blocked (e.g. due to worker crash, protocol violation, or iteration exhaustion) remain in `blocked` status forever, even after all their parent tasks complete. This causes **dependency deadlock**.

## Root Cause

In `kanban_db.py`:
```python
# recompute_ready() only checks 'todo':
todo_rows = conn.execute(
    "SELECT id FROM tasks WHERE status = 'todo'"
).fetchall()
# 'blocked' tasks are never scanned
```

The dispatcher's first tick claims ALL ready tasks including those with unmet dependencies (they were set to `ready` because `kanban create` was called without `--parent`, then linked separately). The worker fails, the task goes to `blocked`, and `recompute_ready()` never touches it again.

## Workaround: Auto-Unlock Cron Script

A lightweight Python script that runs every 1-2 minutes via Hermes cron:

```python
#!/usr/bin/env python3
"""
Find blocked tasks whose all parents are done, set them back to 'ready'.
"""
import sqlite3, os
from pathlib import Path

def get_db_path(board="default"):
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    if board == "default":
        return home / "kanban.db"
    return home / "kanban" / "boards" / board / "kanban.db"

def main():
    db_path = get_db_path()
    if not db_path.exists(): return
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    blocked = conn.execute(
        "SELECT id, title FROM tasks WHERE status = 'blocked'"
    ).fetchall()
    for task in blocked:
        parents = conn.execute(
            "SELECT t.status FROM tasks t "
            "JOIN task_links l ON l.parent_id = t.id WHERE l.child_id = ?",
            (task["id"],)
        ).fetchall()
        if parents and all(p["status"] == "done" for p in parents):
            conn.execute(
                "UPDATE tasks SET status='ready', claim_lock=NULL, "
                "current_run_id=NULL, blocked_reason=NULL WHERE id=?",
                (task["id"],)
            )
            conn.execute(
                "INSERT INTO task_events (task_id, event_type, detail) "
                "VALUES (?, 'unblocked', ?)",
                (task["id"], "auto-unblocked: all parents done")
            )
            print(f"Unblocked {task['id']} ({task['title']})")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
```

### Setup as Hermes Cron Job

```bash
# Save script to ~/.hermes/scripts/kanban_auto_unblock.py
# Create cron job (no_agent=true, runs the script directly)
hermes cron create "every 2m" --name "kanban-auto-unblock" \
  --no-agent --script kanban_auto_unblock.py \
  --workdir ~/.hermes/scripts
```

## Alternative: Create Tasks with --parent at Creation Time

Using `--parent` at creation time sets initial status to `todo` directly (skipping the `ready` state), which avoids the premature-claim window entirely:

```bash
# GOOD: parent specified at creation → starts as 'todo'
hermes kanban create "child task" --assignee coder --parent t_abc123

# RISKY: create then link → brief 'ready' window where dispatcher may claim
hermes kanban create "child task" --assignee coder
hermes kanban link t_abc123 t_def456
```

## Status Reference

| Status | Meaning | Who sets it |
|--------|---------|-------------|
| triage | Needs specification | `create --triage` |
| todo | Waiting for parent deps | `link_tasks()` demotes from ready |
| ready | Executable | `create` default, or `promote` from todo |
| running | Worker claimed | dispatcher `claim_task()` |
| blocked | Stuck (failure/human needed) | worker `kanban_block()` or auto_block |
| done | Completed | worker `kanban_complete()` |
| archived | Inactive | manual `archive` |
