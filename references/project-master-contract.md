# Project Master Contract

Use this contract when a project has no equivalent stable manifest. Store it as
`PROJECT_MASTER.json` in the formal governance root. Keep code repositories,
separate governance roots, and state backends as separate paths when they differ.

## Version 2 manifest

```json
{
  "schema_version": 2,
  "project_id": "stable-project-id",
  "project_name": "Human-readable project name",
  "governance_root": "/absolute/path/to/formal/project/root",
  "code_roots": [
    "/absolute/path/to/code/repository"
  ],
  "state_backend": {
    "kind": "project-local",
    "orchestration_file": "/absolute/path/to/ORCHESTRATION.json",
    "legacy_sources": []
  },
  "master_thread": {
    "current": {
      "thread_id": "current-thread-id",
      "host_id": "local",
      "title": "Project Name｜项目主编排",
      "status": "active",
      "activated_at": "2026-01-01T00:00:00Z"
    },
    "history": []
  },
  "policy": {
    "max_active_outcomes": 3,
    "visible_child_threads": "manual",
    "routing": "reuse_by_outcome_key",
    "local_commit": "owner_confirmation",
    "external_actions": "owner_confirmation",
    "pre_action_notice": "准备｜风险｜停点",
    "handoff_mode": "task_then_delta",
    "child_lifecycle_default": "infer_from_outcome",
    "callback_policy": "terminal_or_explicit_milestone",
    "task_title_max_chars": 30,
    "task_packet_soft_chars": 800,
    "task_packet_hard_chars": 1400,
    "delta_packet_hard_chars": 500,
    "max_input_file_refs": 5
  },
  "execution_policy": "master routes and accepts; scoped child tasks execute",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

## Identity rules

- Keep `project_id` stable across master-thread succession.
- Point `governance_root` at the project's formal control folder.
- List actual execution repositories or worktrees in `code_roots`; never infer
  repository identity from the governance folder.
- Record the user's standing child-routing and local-commit choices in
  `policy`. Use `manual` or `owner_confirmation` when the user has not granted
  the corresponding standing authority.
- Keep handoff budgets in `policy` so the master, project adapter, and validator
  share one limit. `task_then_delta` sends a complete compact packet only at
  task creation and changed facts on later turns. Older v2 manifests may omit
  these fields and inherit the defaults documented by the Skill.
- `child_lifecycle_default=infer_from_outcome` requires every Task Packet to
  resolve to `one_shot` or `exploratory`. The callback policy prevents an
  exploratory child's ordinary completed turn or idle state from being treated
  as outcome completion; only an explicit milestone or terminal state returns.
- Keep one `master_thread.current`. Append each superseded master to `history`
  with `thread_id`, `host_id`, `status`, and `superseded_at`.
- Keep legacy controller paths in `state_backend.legacy_sources` during a
  compatibility period. Treat them as read-only unless their own adapter owns a
  safety transition.
- Never place this manifest in a cross-project home folder or shared global
  inbox.

## Migration from version 1

Read a v1 manifest as valid compatibility input. Upgrade only during an
authorized control-plane change:

1. Move the flat `master_thread` object into `master_thread.current`.
2. Add an empty `master_thread.history` array.
3. Add the explicit `policy` object from confirmed user choices.
4. Point `state_backend.orchestration_file` to the project-local
   `ORCHESTRATION.json`.
5. Preserve every existing root, thread ID, timestamp, and backend path.
6. Validate before treating v2 as canonical.

Do not migrate durable decisions, task transcripts, or legacy event history into
the manifest.
