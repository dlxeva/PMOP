# Child Task Handoff Contract

Child messages carry task-specific context. Stable routing, safety, commit,
external-action, and callback rules are inherited from the orchestration Skill,
the project adapter, and project-local control files.

## New child: Task Packet

Always pass a human-readable title during task creation. Use this compact form:

```text
Title: <human-readable, within project limit>
Outcome: <outcome_key> — <one bounded deliverable>
Parent: <master thread id>
Lifecycle: <one_shot | exploratory>
Workspace: <one common root>; scope: <up to five relative paths or one task brief>
Facts: <only task-specific state, dirty ownership, runtime, or user constraint>
Verify: <command or evidence that proves this outcome>
Stop: <first real owner, external, ambiguity, or scope-expansion gate>
Callback: <one_shot: terminal; exploratory: milestone-or-terminal only>
Return: status / conclusion / changes / evidence / boundary / next
```

Target 800 characters and stop at 1400 unless project policy sets tighter
limits. Preserve long verbatim input in its canonical capture source; put its
path or identifier in `Facts`. State a one-line reason when a concrete safety or
cross-system dependency requires exceeding the hard limit.

## Existing child: Delta Packet

Reuse the child when its `outcome_key` matches. Send only what changed:

```text
Continue: <outcome_key>
Change: <new request or correction>
Facts: <new evidence or changed state only>
Authority: <new authorization, or unchanged>
Stop: <this turn's first real gate>
```

Keep a Delta Packet within 500 characters unless project policy is tighter.
Omit unchanged fields. Do not repeat the parent ID, roots, full scope, safety
defaults, callback contract, or prior evidence.

## Lifecycle and callback semantics

`one_shot` is the default for a bounded implementation, audit, publication
preparation, or verification task with a clear delivery condition. Send one
callback when the deliverable is complete, or earlier when blocked by a real
parent or owner gate.

`exploratory` is a persistent task for research, product discussion, iterative
testing, or other work where the user is expected to continue in the child.
Do not callback merely because:

- one child turn produced a final answer;
- the thread became idle;
- a partial note or draft was saved;
- the child suggested a possible next question.

An exploratory child sends a callback only for:

- `milestone`: a named deliverable or evidence package is ready for parent
  awareness, while exploration remains open;
- `blocked`: progress requires parent routing or a true owner gate;
- `completed`: the full outcome and its acceptance evidence are ready;
- `cancelled` or `superseded`: the outcome should be retired or replaced;
- an explicit user instruction such as close out, return, hand back, or report
  to the master.

Use cross-thread messaging to deliver the callback when available. A milestone
does not authorize acceptance or archive. The parent verifies every callback
and never treats `idle` as terminal evidence. If messaging fails, retain the
result in the child so the parent's next recovery sweep can read it.

Compact callback shape:

```text
Status: <milestone | blocked | completed | cancelled | superseded>
Outcome: <outcome_key>
Conclusion: <one sentence>
Changes: <files or external actions>
Evidence: <strongest verification>
Boundary: <unverified edge or owner gate>
Next: <continue here | parent action | archive candidate>
```

## Reference budget

- Name a common root once; use relative paths underneath it.
- Cite at most five input files. Use one project-local task brief for a larger
  set.
- Keep full logs, research, and evidence in the child or project files.
- A delivered message proves routing only. The master verifies the callback
  before acceptance.
