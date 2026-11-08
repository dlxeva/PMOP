# PMOP host adapter contract

PMOP separates a common project protocol from host-specific execution. These
adapters are instructions, not executable integrations. No host is yet certified
by a complete end-to-end run. A host's policy and the user's authorization always
apply; installing this skill grants no new permissions.

## Required mapping

Before dispatch, record the host name/version, actual visible tools, execution
root, current master identity, child identity type, lifecycle, result retrieval,
cancellation behavior and unsupported operations. Keep the observation local:
it can include private identifiers. Never export a user's host configuration.

The master maps an outcome to exactly one owning route. Record a real child ID
only after successful creation. A delivered packet is not execution evidence;
an idle process is not completion. A result must identify its outcome, status,
changes, evidence, unverified boundary and next action. Validate the actual
artifact separately before acceptance. Children propose control-state changes;
the master remains the single writer with a fresh revision check.

If callback is unavailable, the parent reads the saved result using an available
host interface. If neither is possible, pause rather than claiming success.
Do not automatically retry creation after an ambiguous response: inspect for an
existing child first. On cancellation or parent loss, preserve the last verified
result and mark unfinished work interrupted; do not silently call it completed.

## Certification gate (not yet passed)

Use a new fictional workspace, not a real project. Have a child produce a small
artifact, record the real child ID, retrieve the result, independently verify the
artifact, update the project state, and resume from that state in a fresh context.
Also test a blocked result, duplicate-dispatch prevention and interruption. Save
commands/tool calls, observed IDs and checks privately; publish only a sanitized
summary. A fixture test, CLI help or source reading is not a real host run.

Status: Codex and Hermes have inspected interfaces and manual adapter guidance;
Claude is planned only. Python tests cover local utilities, not host execution.
