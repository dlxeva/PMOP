# Hermes adapter (manual, not end-to-end certified)

Observed locally on 2026-11-08: installed Hermes source revision aaa863f7ff,
`tools/delegate_tool.py`. No Hermes source is bundled with PMOP. This is a local
source observation, not a claim about every upstream release.

The inspected model-facing schema exposes `delegate_task` with `tasks` entries
containing `goal`, `context` and optional `output_schema`; control actions are
`spawn`, `list`, `steer` and `stop`, using `subagent_id` and `message` as applicable.
Top-level model-facing delegation is background execution. The legacy background
flag is deprecated and is not part of the advertised schema. Direct Python calls
have different defaults; do not infer behavior from one surface for another.

1. Confirm the tool is actually visible and inspect current concurrency/depth
   limits. Local limits are not protocol defaults and must not be copied to users.
2. Put a bounded outcome and verification criteria in goal/context. Capture the
   returned child ID; use list to reconcile an uncertain dispatch before retrying.
3. Steer only the same owning child. Retrieve the result from the host and check
   the artifact independently; a schema-valid summary is not proof of completion.
4. Treat stop and parent/session termination as interruption boundaries. `/stop`,
   `/new` and parent process loss can terminate the child tree. These children are
   not persistent user-visible sidebar chats and must not be advertised as such.
5. Save verified progress in the project's files before succession. A new parent
   must inspect unfinished work, not assume old in-memory child IDs remain live.

The Hermes CLI version probe attempted an asset-server connection which the
execution policy blocked. No bypass or retry was used. Therefore CLI startup and
an actual delegate/result/accept/resume cycle remain unverified. Do not promote
this adapter to production support until the certification gate is completed.
