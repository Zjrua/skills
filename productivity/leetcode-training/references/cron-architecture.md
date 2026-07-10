# Cron Chain Architecture — LC100 Blitz

## Design Decision: 6 distributed jobs vs 3 batched jobs

Originally had 3 jobs (9:00 push 5, 14:00 review, 20:00 summary). User feedback: "你别都堆在早上呗，分散开" — spread them out.

Redesigned to 6 jobs with new/review/new/review/summary interleaving:
- Morning 2+2 new problems (9:00, 11:00)
- Midday review (13:00)
- Afternoon 1 new problem (15:00)
- Evening review (17:00)
- Night summary (20:00)

## STATE.json mechanism

Problem: each `push_new.py` run independently reads PROGRESS.md `completed` count. Without state, all runs in one day would push the same problems.

Solution: `STATE.json` tracks `{"date": "2026-05-27", "pushed_today": 4}`. Each push increments the counter. On new day (date mismatch), counter resets to 0.

Start offset = `completed + pushed_today`

## Wrapper script pattern

`no_agent: true` cron jobs run the script directly — no way to pass CLI args.

Solution: tiny wrapper scripts that `chdir` to project root and call core script with hardcoded args:

```python
#!/usr/bin/env python3
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
subprocess.run([sys.executable, "scripts/push_new.py", "2", "早题①"])
```

## File sync checklist

After any script change, sync project → hermes:
```bash
cp /root/projects/leetcode-hot100/scripts/run_*.py ~/.hermes/scripts/
cp /root/projects/leetcode-hot100/scripts/push_*.py ~/.hermes/scripts/
```
