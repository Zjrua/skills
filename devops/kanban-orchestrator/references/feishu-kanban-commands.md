# Feishu /kanban Commands Reference

Commands available in Feishu (and other gateway platforms) via `/kanban <subcommand>`.

## Viewing
| Command | Description |
|---|---|
| `/kanban list` or `/kanban ls` | List all tasks with status |
| `/kanban show t_xxx` | Task detail (comments, events, dependencies) |
| `/kanban tail t_xxx` | Live task log |
| `/kanban context t_xxx` | Worker context |

## Create & Edit
| Command | Description |
|---|---|
| `/kanban create "title" --assignee <profile>` | Create task (**auto-subscribes notifications**) |
| `/kanban create "title" --assignee <profile> --parent t_xxx` | Create with dependency |
| `/kanban assign t_xxx <profile>` | Reassign task |
| `/kanban comment t_xxx "text"` | Add comment |
| `/kanban link t_parent t_child` | Add dependency |
| `/kanban unlink t_parent t_child` | Remove dependency |

## Status Control
| Command | Description |
|---|---|
| `/kanban complete t_xxx --result "summary"` | Mark done |
| `/kanban block t_xxx "reason"` | Block (wait for human) |
| `/kanban unblock t_xxx` | Unblock |
| `/kanban archive t_xxx` | Archive |

## Notifications
| Command | Description |
|---|---|
| `/kanban notify-subscribe t_xxx --platform feishu --chat-id <id>` | Subscribe to events |
| `/kanban notify-list` | List subscriptions |
| `/kanban notify-unsubscribe t_xxx` | Unsubscribe |

## Admin
| Command | Description |
|---|---|
| `/kanban dispatch` | Manual dispatcher tick (reclaim + promote + spawn) |
| `/kanban init` | Initialize board DB |
| `/kanban gc` | Garbage collect |

## Key: Gateway vs CLI

- **Gateway `/kanban create`** → auto-subscribes originating chat to terminal events (completed, blocked, crashed, gave_up, timed_out)
- **CLI `hermes kanban create`** → NO auto-subscribe. Use `notify-subscribe` manually.
- Both routes go through the same `kanban_db` layer — reads/writes are consistent.
