# Orchestration State Contract

## Contents

1. Purpose
2. Minimal state
3. Active outcomes
4. Owner gates
5. Six control objects
6. Governance states
7. Update rules

## Purpose

Store only the live facts needed to resume and route project work. Keep task
transcripts, full evidence, Git history, and durable decisions in their native
systems. Store `ORCHESTRATION.json` beside `PROJECT_MASTER.json`.

## Minimal state

```json
{
  "schema_version": 1,
  "project_id": "stable-project-id",
  "revision": 1,
  "updated_at": "2026-01-01T00:00:00Z",
  "governance": {
    "status": "healthy",
    "reason": null,
    "local_safe_work": "allowed",
    "external_high_risk_work": "requires_fresh_verification"
  },
  "active_outcomes": [],
  "owner_gates": [],
  "legacy_sources": []
}
```

Keep `active_outcomes` at or below `policy.max_active_outcomes`, with a hard
maximum of three. Keep backlog and archived work outside this array.

## Active outcomes

```json
{
  "outcome_key": "stable-result-key",
  "title": "Bounded result",
  "priority": 1,
  "route": "isolated_task",
  "status": "running",
  "thread": {
    "thread_id": "real-child-thread-id",
    "host_id": "local",
    "title": "Visible child title"
  },
  "scope": {
    "allowed": ["/absolute/path"],
    "protected": ["/absolute/path"]
  },
  "last_verified": {
    "at": "2026-01-01T00:00:00Z",
    "claim": "What was observed",
    "evidence": ["thread snapshot, diff, test, or external fact"]
  },
  "next_action": "One concrete next action"
}
```

Allowed active statuses: `running`, `verifying`, `waiting_owner`, `blocked`.
Allowed child routes: `quick_fix`, `isolated_task`. Use the task packet for the
full route rationale and acceptance criteria.

Use a stable key for the intended result. A new wording, retry, or follow-up
does not create a new key. Replace or archive an outcome only after transferring
its evidence and remaining boundary.

## Owner gates

```json
{
  "gate_id": "OWNER-001",
  "type": "owner_decision",
  "status": "open",
  "blocking": true,
  "request": "The exact action or decision needed",
  "why_owner_only": "Why AI cannot responsibly complete it",
  "recommendation": "Recommended choice or procedure",
  "risk": "Risk of approving or delaying",
  "estimated_minutes": 5,
  "resume_action": "What the master does after the gate",
  "related_outcome_key": "stable-result-key"
}
```

Use `owner_action` for personal operation, authentication, private input, or a
genuine human test. Use `owner_decision` when the owner may decide from supplied
evidence. Remove resolved gates from the live file after recording the result in
the relevant task or durable backend.

Do not add routine AI work, optional ideas, reminders without a current stop, or
legacy `waiting_for_user` entries that no longer require the owner.

## Six control objects

Represent the minimum control protocol without creating six files:

| Object | Canonical location |
| --- | --- |
| Project Boundary | `PROJECT_MASTER.json` |
| Task Packet | child task prompt or formal task file |
| Route Record | `active_outcomes[]` |
| Task Callback | child task final report |
| Acceptance Record | master response plus strongest project evidence |
| Archive Record | archived task plus durable summary or decision pointer |

## Governance states

- `healthy`: project-local control state and relevant live facts agree.
- `degraded`: state is stale, partial, or inconsistent; clear reversible local
  work may continue.
- `blocked`: identity, ownership, safety, or required evidence is too ambiguous
  for the requested action.

With `degraded`, restore fresh state before push, PR, merge, release, deploy,
publish, destructive work, or other external high-risk action.

## Update rules

1. Keep the canonical project master as the single writer.
2. Let a child write only when its task packet explicitly lists this file and an
   expected base revision.
3. Re-read the live revision immediately before writing; merge unrelated newer
   changes or stop on a conflict.
4. Read live thread and project evidence before changing a status.
5. Increment `revision` and refresh `updated_at` for every state change.
6. Keep priorities unique and ordered from `1`.
7. Keep child thread IDs unique and different from the master ID.
8. Preserve unrelated active outcomes and owner gates.
9. Never copy full transcripts, logs, or large evidence payloads into this file.
10. Validate after editing and treat validation as structural evidence only.
