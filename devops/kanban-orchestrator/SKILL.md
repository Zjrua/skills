---
name: kanban-orchestrator
description: Decomposition playbook + specialist-roster conventions + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.
version: 2.0.0
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing]
    related_skills: [kanban-worker]
---

# Kanban Orchestrator — Decomposition Playbook

> The **core worker lifecycle** (including the `kanban_create` fan-out pattern and the "decompose, don't execute" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This skill is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **If no specialist fits, ask the user which profile to create.** Do not default to doing it yourself under "close enough."
- **Decompose, route, and summarize — that's the whole job.**

## The standard specialist roster (convention)

Unless the user's setup has customized profiles, assume these exist. Adjust to whatever the user actually has — ask if you're unsure.

| Profile | Does | Typical workspace |
|---|---|---|
| `researcher` | Reads sources, gathers facts, writes findings | `scratch` |
| `analyst` | Synthesizes, ranks, de-dupes. Consumes multiple `researcher` outputs | `scratch` |
| `writer` | Drafts prose in the user's voice | `scratch` or `dir:` into their Obsidian vault |
| `reviewer` | Reads output, leaves findings, gates approval | `scratch` |
| `backend-eng` | Writes server-side code | `worktree` |
| `frontend-eng` | Writes client-side code | `worktree` |
| `pm` | Writes specs, acceptance criteria | `scratch` |
| `designer` | Creates design systems, UI mockups, HTML artifacts | `scratch` |
| `ops` | Server setup, deployments, systemd, security | `dir:` into project root |

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph out loud (in your response to the user). Example for "Analyze whether we should migrate to Postgres":

```
T1  researcher        research: Postgres cost vs current
T2  researcher        research: Postgres performance vs current
T3  analyst           synthesize migration recommendation       parents: T1, T2
T4  writer            draft decision memo                       parents: T3
```

Show this to the user. Let them correct it before you create anything.

### Step 3 — Create tasks and link

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="researcher",
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="researcher",
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="analyst",
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="writer",
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`. No manual coordination needed; the dispatcher and dependency engine handle it.

### Step 4 — Complete your own task

If you were spawned as a task yourself (e.g. `planner` profile was assigned `T0: "investigate Postgres migration"`), mark it done with a summary of what you created:

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 researchers parallel, 1 analyst on their outputs, 1 writer on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "researcher", "parents": []},
            "T2": {"assignee": "researcher", "parents": []},
            "T3": {"assignee": "analyst", "parents": ["T1", "T2"]},
            "T4": {"assignee": "writer", "parents": ["T3"]},
        },
    },
)
```

### Step 5 — Report back to the user

Tell them what you created in plain prose:

> I've queued 4 tasks:
> - **T1** (researcher): cost comparison
> - **T2** (researcher): performance comparison, in parallel with T1
> - **T3** (analyst): synthesizes T1 + T2 into a recommendation
> - **T4** (writer): turns T3 into a CTO memo
>
> The dispatcher will pick up T1 and T2 now. T3 starts when both finish. You'll get a gateway ping when T4 completes. Use the dashboard or `hermes kanban tail <id>` to follow along.

## Setting up a multi-profile kanban team

For the full end-to-end workflow (creating profiles, writing SOUL.md, configuring models/fallbacks, initializing boards), see `references/multi-profile-team-setup.md`.

Key principle: each profile needs its own `SOUL.md` (role definition), `config.yaml` (model + tools), and `.env` (API keys). Clone from default, then customize per role.

## Common patterns

**Fan-out + fan-in (research → synthesize):** N `researcher` tasks with no parents, one `analyst` task with all of them as parents.

**Pipeline with gates:** `pm → backend-eng → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** 50 tasks, all assigned to `translator`, no dependencies between them. Dispatcher serializes — translator processes them in priority order, accumulating experience in their own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Profile Setup

To use Kanban with multiple specialists, each role needs a dedicated Hermes profile with its own SOUL.md (personality), tool restrictions, and config. The full setup procedure is in **`references/profile-setup.md`**.

Ready-to-use SOUL.md templates for the standard roster:

| Template | Profile | Role |
|---|---|---|
| `templates/soul-planner.md` | `planner` | Task decomposition & routing |
| `templates/soul-coder.md` | `coder` | Software development |
| `templates/soul-writer.md` | `writer` | Content creation |
| `templates/soul-researcher.md` | `researcher` | Information gathering |
| `templates/soul-reviewer.md` | `reviewer` | Quality assurance |
| `templates/soul-ops.md` | `ops` | System administration & deployment |
| `templates/soul-designer.md` | `designer` | UI/UX design & design systems |
| `templates/soul-backend-eng.md` | `backend-eng` | API & server-side development |
| `templates/soul-frontend-eng.md` | `frontend-eng` | Client-side & dashboards |

Quick setup (clone default profile, then write SOUL.md from templates):
```bash
for role in planner coder writer researcher reviewer; do
    hermes profile create "$role" --clone --no-alias
    cp templates/soul-$role.md ~/.hermes/profiles/$role/SOUL.md
done
```

Then configure tool restrictions per profile (planner should have terminal/file/web disabled). See `references/profile-setup.md` for the complete table of per-role settings.

## Pitfalls

**Reassignment vs. new task.** If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task — don't re-run the same task with a stern look. The new task is assigned to the original implementer profile.

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

**Dependency deadlock bug (as of v23 config).** The dispatcher's `recompute_ready()` (called `promote_ready_tasks` internally) only scans tasks in `todo` status. If the dispatcher prematurely claims a `todo` task (e.g. on its first tick before parents finish), the worker fails, and the task gets `auto_blocked`, the task is now in `blocked` status — which `promote_ready_tasks` never touches. Result: **permanent deadlock**. The child stays `blocked` even after all parents reach `done`.

**Recommended: manual unblock with root-cause fix.** When a task blocks, it means something actually went wrong (config error, iteration exhaustion, model mismatch). Do NOT set up cron scripts to auto-unblock — that hides the symptom without fixing the cause. Instead:
1. Check the task log: `hermes kanban log <task_id>` to see why the worker failed.
2. Fix the root cause (e.g. increase `max_turns`, fix `delegation.model`, correct API key).
3. `hermes kanban unblock <task_id> "fix applied: <what you changed>"`

**Alternative workaround: create tasks WITH `--parent`** at creation time instead of `kanban create` + `kanban link` separately — this sets initial status to `todo` directly, avoiding the premature-claim window entirely.

Root cause: in `kanban_db.py`, `recompute_ready()` queries `WHERE status = 'todo'` but auto-blocked tasks land in `status = 'blocked'`. A future Hermes release should fix this by also checking blocked tasks with met dependencies.

See `references/kanban-auto-unblock.md` for the full workaround script, setup instructions, and status reference table.

**Don't pre-create the whole graph if the shape depends on intermediate findings.** If T3's structure depends on what T1 and T2 find, let T3 exist as a "synthesize findings" task whose own first step is to read parent handoffs and plan the rest. Orchestrators can spawn orchestrators.

**Tenant inheritance.** If `HERMES_TENANT` is set in your env, pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` call so child tasks stay in the same namespace.

**"Done" tasks may contain stubs, not real implementations.** Workers sometimes mark tasks `done` with placeholder code (e.g. `return {"message": "占位实现 — waiting for task"}`). This happened with dashboard API routers — T3 and T4 were marked `done` but returned stub messages instead of real data. After tasks complete, **verify the actual output**: grep for "占位", "placeholder", "TODO", "waiting for" in produced files. Check that API endpoints the frontend calls actually exist in the router. Trust but verify — `done` status means the worker finished, not necessarily that the code works.

**Worker delegation model mismatch.** When a worker spawns sub-agents via `delegate_task`, the sub-agent inherits the worker's `delegation` config — NOT the worker's primary model. If `delegation.provider` is not set explicitly, it falls back to `auto` which may route to a different provider than expected. Explicitly set `delegation.provider` and `delegation.model` in the worker profile's config.yaml to match its primary model (e.g. if researcher uses `deepseek/deepseek-v4-flash`, set `delegation.provider: deepseek` and `delegation.model: deepseek-v4-flash`).

**Model names must be API-verified.** Never guess or invent model IDs. Before configuring a profile's model or fallback, call the provider's `/v1/models` endpoint and use an exact ID from the response. Names like `deepseek-chat` may not exist or may be deprecated. If unsure, ask the user to verify. See `references/profile-setup.md` → "Pitfalls" for per-provider verification commands.

**Fallback to custom provider needs custom_providers entry.** If a profile falls back to a custom provider (e.g. `zai`), that profile's `config.yaml` must have the provider in `custom_providers`. Cloning from default usually copies this, but if you change the primary provider, verify the fallback entries survive.

## Profile setup for Kanban workers

### Creating profiles

```bash
# Clone from default (copies config, .env, SOUL.md, skills)
hermes profile create planner --clone --no-alias
hermes profile create coder --clone --no-alias
# ... repeat for writer, researcher, reviewer, doubter, etc.
```

Each profile gets its own `~/.hermes/profiles/<name>/` with independent:
- `SOUL.md` — system prompt / personality
- `config.yaml` — model, toolsets, fallback chain, delegation settings
- `.env` — API keys (cloned from default)

### Model configuration — critical rules

1. **Verify model names via API before configuring.** Never guess or assume model names — call the provider's `/v1/models` endpoint to get the exact `id` strings:
   ```bash
   curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $KEY"
   curl -s https://open.bigmodel.cn/api/paas/v4/models -H "Authorization: Bearer $KEY"
   ```
   Wrong model names cause silent routing failures in fallback chains.

2. **Keep fallback chains simple — 2 layers max.** Primary + one cross-cloud fallback. Don't chain through local/self-hosted models unless they're reliably available. Principle: if the fallback might be down, it's not a real fallback.

3. **Set `delegation.model` and `delegation.provider` to match the profile's primary.** When a worker spawns subagents via `delegate_task`, the delegation config determines what model the subagent uses. If delegation inherits a mismatched default (e.g., zai provider but deepseek endpoint), subagents fail with HTTP 400. Fix:
   ```yaml
   delegation:
     provider: deepseek      # match the profile's primary provider
     model: deepseek-v4-flash  # match the profile's primary model
   ```

4. **Research-heavy profiles need higher iteration limits.** Web search tasks burn through iterations fast. Default `max_turns: 50` is often insufficient:
   ```yaml
   agent:
     max_turns: 90          # up from default 50
   delegation:
     max_iterations: 80     # up from default 50
   ```

### Feishu notification subscriptions

Tasks created via the Feishu `/kanban create` slash command auto-subscribe the originating chat to terminal events (completed, blocked, crashed, timed_out, gave_up). Tasks created via CLI `hermes kanban create` do NOT auto-subscribe — use `hermes kanban notify-subscribe` manually, or tell the user to create tasks via `/kanban` in Feishu.

### Task status lifecycle

```
triage → todo → ready → running → done
                      ↓          ↑
                    blocked ←----┘ (failure / needs human)
                      
all → archived
```

| Status | Meaning |
|--------|---------|
| `triage` | Needs a human to flesh out the spec |
| `todo` | Has unmet parent dependencies; dispatcher ignores it |
| `ready` | All parents done (or no parents); dispatcher will claim it |
| `running` | Worker is executing |
| `blocked` | Worker hit an issue; needs human to `/kanban unblock` |
| `done` | Completed successfully |
| `archived` | Archived, inactive |

**When tasks block, tell the user.** Blocked tasks need human attention — don't auto-workaround with cron scripts or silent retries. The block happened for a reason (config error, iteration exhaustion, API failure). Fix the root cause, then unblock. The user explicitly prefers this: "有问题就应该block一下" — block is the correct signal, not something to paper over.

---

## Recovering stuck workers

When a worker profile keeps crashing, hallucinating, or getting blocked by its own mistakes (usually: wrong model, missing skill, broken credential), the kanban dashboard flags the task with a ⚠ badge and opens a **Recovery** section in the drawer. Three primary actions:

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`. The existing claim TTL is ~15 min; this is the fast path out.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile and let the dispatcher pick it up with a fresh worker.
3. **Change profile model** — the dashboard prints a copy-paste hint for `hermes -p <profile> model` since profile config lives on disk; edit it in a terminal, then Reclaim to retry with the new model.

Hallucination warnings appear on tasks where a worker's `kanban_complete(created_cards=[...])` claim included card ids that don't exist or weren't created by the worker's profile (the gate blocks the completion), or where the free-form summary references `t_<hex>` ids that don't resolve (advisory prose scan, non-blocking). Both produce audit events that persist even after recovery actions — the trail stays for debugging.

## Worker protocol violations

If a worker process exits with code 0 but never called `kanban_complete()` or `kanban_block()`, the dispatcher records a `protocol_violation` event and treats the run as crashed. Common causes:
- **Iteration budget exhausted** (`max_iterations` / `max_turns` reached) — the worker is force-stopped before it can call complete.
- **API timeout cascade** — the worker's model provider times out repeatedly, the process gets killed, no cleanup.
- **Delegation routing error** — if the profile's `delegation.model` / `delegation.provider` doesn't match a valid endpoint, subagents fail immediately and the parent may exit without completing.

Prevention:
- Set `delegation.provider` and `delegation.model` explicitly in each profile's config to match that profile's primary model (not the gateway default).
- Increase `agent.max_turns` for research-heavy profiles (60 → 90).
- Increase `delegation.max_iterations` (50 → 80) for web-search-heavy tasks.
- Write results to workspace files *before* calling `kanban_complete` so data survives crashes.

## Profile setup reference

For the full profile creation workflow (model verification, SOUL.md templates, fallback chain design, delegation config, per-profile tuning), see `references/profile-setup-playbook.md`.
