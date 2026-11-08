# Codex adapter (manual, not end-to-end certified)

Observed locally on 2026-11-08: codex-cli 0.145.0. `codex exec --help`
exposes noninteractive execution and `resume`. Versions and tool availability
vary; recheck the current host instead of assuming these names are universal.

1. Use an explicitly authorized workspace and the current host's supported task
   interface. A desktop chat, CLI session and internal worker are different
   identities. Do not create a visible chat merely to emulate an internal worker.
2. Dispatch the common Task Packet. Record the returned session/task ID and
   how its result can be read. Do not use `resume --last` in a multi-project
   workflow; it can select unrelated work. Resume the verified explicit ID.
3. Retrieve the result using the host's actual interface. No automatic cross-chat
   callback is assumed. Verify the changed artifact and tests before acceptance.
4. For succession, pass the compact project state and verify that the successor
   reads the same roots. Session continuation alone does not transfer mastery.

PMOP does not launch CLI commands, change sandbox/approval settings, install
plugins, or persist credentials. Never use sandbox-bypass flags as an adapter
fallback. This candidate has not created a Codex task for a synthetic closed loop;
CLI help inspection establishes interface availability only.
