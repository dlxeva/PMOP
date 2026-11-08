---
name: pmop
description: >-
  Run a project's logical master for natural-language intake, priorities,
  cross-task routing, callback verification, owner gates, minimal control
  state, master succession, and the cross-project owner inbox. Use when
  starting, resuming, coordinating, or reviewing a multi-task project. Load
  project-specific safety adapters when available.
---

# PMOP

Operate one logical master for one project. Let the user send every project
request to that master. Route implementation and substantial exploration using
the current host rules and the project execution policy; visible child chats
require the authorization those rules specify. Keep detailed evidence in the
executing task or formal project files.

Load a project-specific adapter when present. Let the adapter add project-specific safety
checks; retain this Skill as the routing and lifecycle protocol.

Read [project-master-contract.md](references/project-master-contract.md) when
activating, migrating, or handing off a master. Read
[orchestration-contract.md](references/orchestration-contract.md) before
creating or editing `ORCHESTRATION.json`. Read
[child-task-handoff.md](references/child-task-handoff.md) before creating or
continuing a child task.

## Host adapter boundary

Read [adapters/README.md](adapters/README.md) before host-specific routing.
The common protocol defines outcomes, evidence, owner gates and succession;
the adapter maps actual host capabilities, identifiers and lifecycle limits.
Do not invent a tool, assume a session survives its parent, or equate a CLI
process, an internal agent and a user-visible chat. Missing capabilities are
explicit stop points, not permission to install or reconfigure a host.

## Keep the control model small

Use two project-local files:

- `PROJECT_MASTER.json`: stable identity, roots, current logical master, state
  backend, and execution policy.
- `ORCHESTRATION.json`: current active outcomes, owner gates, governance health,
  and pointers to legacy sources.

Do not create a global controller, database, background daemon, duplicate
decision ledger, or file per control object. Generate a read-only owner inbox
from project-local files when requested.

## Activate or resume

Follow this order:

1. Preserve the user's request in the task packet or project capture source.
   Keep the original wording available in one canonical source. Put a short
   request or pointer in the child packet when the source is long.
2. Resolve `governance_root`, actual `code_roots`, optional durable state
   backend, current master thread ID, and project-specific adapter.
3. Read `PROJECT_MASTER.json` and `ORCHESTRATION.json` when present. Treat a v1
   manifest or legacy controller as compatibility input; do not rewrite it by
   assumption.
4. Compare the current thread with `master_thread.current.thread_id`. Handle a
   mismatch as a child task or explicit master handoff.
5. Inspect only the live facts needed for the request: thread state, Git
   identity, dirty files, tests, runtime, remote refs, or external status.
6. Report current goal, up to three active outcomes in priority order, true
   owner gates, governance health, and the next safe action.

Mark governance `degraded` when project state is stale, partially unavailable,
or internally inconsistent. Continue reversible local work whose scope and live
facts are clear. Restore and verify governance before release, destructive, or
other high-risk work.

## Keep current work usable

When a project has a canonical business ledger, read current outcomes from that
ledger; orchestration stores routing and references, not another status copy.
An ongoing business outcome need not have an executing child. Do not retain an
obsolete child route as active merely to represent unfinished business. Preserve
its evidence and remaining boundary in the project's historical/reference area;
move only the route, without claiming completion or cancellation. Use the local
adapter's distinction between business priorities and execution routes.

Keep current entries focused on the latest result, next action, dependency and
acceptance boundary. Replace superseded state; preserve sources and still-active
details in the canonical ledger's task-specific detail section. Use the project's
validated writer when available: preview the candidate recovery before writing,
then refresh and read back the affected view. If primary work no longer fits,
reorganize history/details without dropping constraints; retain the candidate
and report an unapplied update until resolved. Check the actual rendered budget,
including links and metadata. Explicit omissions remain necessary for readers;
they do not establish that the recovery view is operationally useful.

After a consequential correction, inspect the directly affected current entry,
current deliverable, and recovery pointer. Confirm the next read preserves the
correction, including completed actions and rejected premises. Saving the source
or passing structural validation alone does not establish propagation. Keep
validation scoped to affected work; do not turn every correction into a full
project audit. Measure reliability through subsequent real tasks and repeated
user corrections, not rule count or claimed token savings.

## Reconcile the next action

Before proposing coordination, check the affected task's latest evidence for what
has already been requested, who has accepted it, what result is awaited, and what
would trigger a follow-up. Turn an existing request into review criteria or an
escalation condition; do not reissue it because the final artifact is unseen.
Keep unassigned work distinct from accepted work awaiting evidence.

Infer whether this turn explores a problem, aligns direction, coordinates
execution, or accepts a result. Match the output to that stage without making
the user complete a form. A user's identified need does not make them its
operational executor. Prepare evidence, alternatives and acceptance criteria;
keep actual ownership and authorization grounded in the project's sources.

## Resolve capabilities on demand

Before a tool-dependent route, or whenever capability availability is unclear,
inspect the current task's actual tool surface and run the bundled read-only
inventory:

```bash
python3 scripts/capability_index.py --root ./skills --format markdown
```

The index inventories files only within explicitly selected roots. It does not
read host configuration, probe runtimes, or establish enabled state. Inspect the
current host tool surface separately to establish runtime visibility. Do not paste the full index into child packets; include only
the selected capability, required permission, fallback, and unresolved gate.
The index informs routing and never grants authority.

## Route by outcome

Apply the user's explicit execution-location instruction before the default
route. Phrases such as "就在主编排做", "在这里直接执行", or "不要开子任务"
select `current_thread`. In that case, the master performs the scoped work and
does not create, reuse, or message a child for that execution slice. A plain
"继续" or "你来做" does not by itself change the recorded route.

This location choice overrides the orchestration preference for delegation. It
does not expand scope or bypass owner, external-action, destructive-action,
privacy, runtime-ownership, or evidence gates. If another task already owns the
same files or runtime, inspect the real conflict and stop only when concurrent
execution would be unsafe.

Derive a stable `outcome_key` from the intended result, not from the latest
wording. Reuse the child task that already owns that key. Create a visible child
task only when the user has not selected `current_thread`, no matching active
child exists, and the project policy contains the user's standing authorization
for automatic visible child routing.

Handle these in the master:

- status, priorities, feedback, clarification, and owner decisions;
- acceptance, archive, and control-state maintenance;
- short read-only inspection or explanation with no durable artifact;
- routing corrections and master succession.

By default, use a child task for a distinct durable outcome:

- code, content, data, or document changes;
- substantive research or browser-heavy work;
- independent verification;
- a bounded release operation after authorization.

Classify the route as `current_thread`, `quick_fix`, `isolated_task`,
`blueprint`, `backlog`, `needs_clarification`, `handoff`, or `archive`.
`quick_fix` describes a small child outcome when files change. Put a fourth
concurrent outcome into backlog or replace an active outcome after reprioritizing.
Keep `active_outcomes` at or below the project's configured limit, with a hard
maximum of three.

Before starting an execution slice, tell the user once:

```text
准备：<action>｜风险：<main risk>｜停点：<owner or external gate>
```

Proceed after the notice when the work is reversible and within the recorded
scope. Avoid repeated progress permission checks.

## Dispatch a child task

Give the child one bounded outcome and the smallest useful context. Stable
project rules live in this Skill, the project adapter, and project-local control
files; let the child read those sources when relevant. Send task-specific facts
once and changed facts thereafter.

For a new child, use a **Task Packet** with an explicit, human-readable title.
For an existing child with the same `outcome_key`, use a **Delta Packet** that
contains only the changed request, facts, authority, evidence, or stop point.
Never resend the full handoff merely to continue the same outcome.

Use the project's packet policy when present. Defaults are:

- title: at most 30 characters;
- Task Packet: target 800 characters, hard limit 1400;
- Delta Packet: hard limit 500 characters;
- input file references: at most five.

Name a common root once and list relative paths beneath it. If more detail is
needed, place it in one project-local task brief and send that path. Exceed the
hard limit only for a concrete safety or cross-system dependency; state the
reason in one short line. Do not paste project history, full Skill text,
unchanged safety defaults, detailed callback instructions, or repeated absolute
paths into a child message.

Each Task Packet carries the outcome, bounded deliverable, relevant workspace
and scope, up to five task-specific facts, verification, and the first real
stop point. Preserve a long verbatim user request in the canonical capture
source and send a pointer. See the handoff reference for both packet forms.

Classify every child as `one_shot` or `exploratory` in its Task Packet:

- `one_shot` owns one bounded deliverable and should callback when that
  deliverable is complete or blocked.
- `exploratory` is a durable workspace where the user may continue for many
  turns. An ordinary answer, a completed turn, or an idle thread is not an
  outcome completion and must not callback by default.

For an exploratory child, callback only when it reaches an explicit deliverable
milestone, needs parent or owner intervention, the user asks to close out or
return, or the child determines the entire outcome is complete, cancelled, or
superseded. Label the callback `milestone`, `blocked`, `completed`, `cancelled`,
or `superseded`. A milestone callback transfers evidence without archiving the
child; only a terminal callback can enter acceptance and archive review.

Pass the explicit title during task creation. Create the task before recording
its real thread ID. Record delivery as a route fact, not proof of work. Take one
immediate progress snapshot, then let the child execute.

## Control context growth

Treat one logical master as a stable project entry, not as an immortal physical
chat session. Project-local control files and compact evidence packets preserve
continuity; full conversation history does not.

When the runtime exposes input and call counts, use these operational defaults:

- at 80,000 input tokens in one model call, finish the bounded step, return an
  evidence packet, and avoid adding more history to the same execution phase;
- after 25 model calls in one execution phase, close the phase with evidence
  and continue in a fresh phase or task;
- at 160,000 input tokens in one model call, do not begin another substantial
  execution slice until state has been compressed or the work has moved;
- thresholds are routing signals, not proof of failure and not model limits.

These defaults do not override the user's explicit request to execute in the
master. In that case, keep the work in the master but still close bounded
phases, externalize large evidence, and recommend an authorized master
succession before starting another heavy slice when the red threshold persists.

When the platform exposes history-fork depth, choose no inherited history or
the shortest supported window for a new child. The Task Packet and its file
references are the child's context. Do not clone the full master history merely
for convenience.

Keep full logs, large tool outputs, generated research, and repeated screenshots
in the executing task or a project file. Return only the conclusion, strongest
evidence, boundary, next action, and paths. Include at most two screenshots in a
callback unless additional images are the evidence being accepted.

For a substantive milestone, recover the changed judgment (or explicitly no
change), artifact/evidence, verification scope, and next mainline action with its
actual owner. Keep ordinary conversation endings out of milestone acceptance.
Use cross-thread callbacks only when the host rules and user authorization permit
them; otherwise the parent reads the saved result. A callback is a claim to verify,
not acceptance. Never infer terminal completion from `idle` alone.

## Coordinate state and evidence

Let the master own live routing, priority, child ownership, acceptance, and the
next gate. Let the project's durable backend own attributed decisions,
evidence, constraints, rejected directions, and resumable project knowledge.
Do not duplicate transient child status into a durable decision ledger.

Keep the canonical master as the single writer of `ORCHESTRATION.json`. Let a
child return a proposed state change in its callback. Permit a control-maintenance
child to write only when its task packet explicitly names `ORCHESTRATION.json`
and the expected base revision. Re-read the revision immediately before every
write; merge unrelated newer changes or stop on a conflict.

Use `confirmed`, `observed`, `inferred`, `assumed`, `unknown`, and `blocked`
consistently. Treat a callback as a claim. Verify the narrowest live evidence
needed before accepting it.

## Apply owner and external gates

Use two owner gate types:

- `owner_action`: the owner must personally operate, authenticate, provide
  private material, or perform a genuine human test.
- `owner_decision`: the owner may approve or reject from the evidence without
  personally rerunning every step; record the recommendation and risk.

Include only items that truly require the owner in `owner_gates`. Keep ordinary
AI work, deferred ideas, and stale reminders out of the owner inbox.

Permit a local commit when all of these are true:

- the project policy allows `auto_when_scope_clear_and_verified`;
- file ownership and diff scope are unambiguous;
- relevant verification passes;
- unrelated dirty changes remain untouched;
- the commit creates no external side effect.

Require explicit scoped authorization for push, PR creation or ready status,
merge, tag or Release, deploy, publish, account actions, spending, permission
changes, private uploads, and destructive operations. One authorization may
cover a named sequence; stay within that sequence and stop at its stated end.

## Accept, archive, and hand off

For every milestone or terminal callback, return:

1. conclusion;
2. changed files or external actions;
3. strongest verified evidence;
4. unverified boundary or owner gate;
5. next action.

Accept an outcome only after verifying its scoped evidence. A milestone updates
evidence and the next action while keeping an exploratory child active. Archive
only after a verified terminal callback, when the result and remaining
boundaries have transferred, no owner response remains in that child, and
unresolved work is parked or routed.

When the master grows too long, first write a compact succession packet with the
current goal, up to three active outcomes, strongest accepted evidence, open
owner gates, project roots, and the next action. Then create an explicitly
authorized successor. Update `master_thread.current`, append the predecessor to
history, verify that the successor reads the same project roots and state, then
mark the predecessor superseded. Preserve one logical entry even when its
physical thread changes; never use a pasted transcript as the succession packet.

## Validate and aggregate

Use the bundled read-only script after editing project control files:

```bash
python3 scripts/orchestration_state.py validate --root /absolute/project/root
python3 scripts/orchestration_state.py owner-inbox \
  --root /absolute/project-a --root /absolute/project-b
```

For a cross-project owner-inbox request, resolve candidate roots from the user's
explicit scope or the host's read-only project list. Include only roots that
already contain both control files. Do not scan the home directory, migrate a
project, or create missing state as a side effect of aggregation. Validate every
included root and report invalid or excluded projects separately.

Treat the generated owner inbox as a view. Project masters remain the writers
and factual authorities for their own projects.
