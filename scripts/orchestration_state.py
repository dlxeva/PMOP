#!/usr/bin/env python3
"""Validate project orchestration state and render a read-only owner inbox."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ACTIVE_STATUSES = ("running", "verifying", "waiting_owner", "blocked",)
CHILD_ROUTES = ("quick_fix", "isolated_task",)
GOVERNANCE_STATUSES = ("healthy", "degraded", "blocked",)
OWNER_GATE_TYPES = ("owner_action", "owner_decision",)


@dataclass
class ValidationResult:
    root: Path
    manifest: dict[str, Any] | None
    orchestration: dict[str, Any] | None
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read JSON {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"top-level JSON must be an object: {path}")
        return None
    return value


def require_string(obj: dict[str, Any], key: str, where: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}.{key} must be a non-empty string")
        return None
    return value


def require_object(obj: dict[str, Any], key: str, where: str, errors: list[str]) -> dict[str, Any] | None:
    value = obj.get(key)
    if not isinstance(value, dict):
        errors.append(f"{where}.{key} must be an object")
        return None
    return value


def require_list(obj: dict[str, Any], key: str, where: str, errors: list[str]) -> list[Any] | None:
    value = obj.get(key)
    if not isinstance(value, list):
        errors.append(f"{where}.{key} must be an array")
        return None
    return value


def validate_timestamp(value: Any, where: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{where} must be a non-empty ISO-8601 timestamp")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timezone required")
    except ValueError:
        errors.append(f"{where} must be a valid ISO-8601 timestamp")


def validate_absolute_paths(values: Any, where: str, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"{where} must be an array")
        return
    for index, value in enumerate(values):
        if not isinstance(value, str) or not Path(value).is_absolute():
            errors.append(f"{where}[{index}] must be an absolute path")


def validate_manifest(
    manifest: dict[str, Any], root: Path, errors: list[str], warnings: list[str]
) -> tuple[str | None, str | None, int]:
    schema_version = manifest.get("schema_version")
    if type(schema_version) is not int or schema_version not in (1, 2):
        errors.append("PROJECT_MASTER.json.schema_version must be 1 or 2")
    if schema_version == 1:
        warnings.append("PROJECT_MASTER.json uses legacy schema_version 1")

    project_id = require_string(manifest, "project_id", "PROJECT_MASTER.json", errors)
    require_string(manifest, "project_name", "PROJECT_MASTER.json", errors)
    governance_root = require_string(manifest, "governance_root", "PROJECT_MASTER.json", errors)
    if governance_root and Path(governance_root).resolve() != root:
        warnings.append(
            "PROJECT_MASTER.json.governance_root differs from the validated root"
        )
    validate_absolute_paths(manifest.get("code_roots"), "PROJECT_MASTER.json.code_roots", errors)
    require_object(manifest, "state_backend", "PROJECT_MASTER.json", errors)
    validate_timestamp(manifest.get("updated_at"), "PROJECT_MASTER.json.updated_at", errors)

    master_thread_id: str | None = None
    master = require_object(manifest, "master_thread", "PROJECT_MASTER.json", errors)
    if master is not None:
        if schema_version == 2:
            current = require_object(master, "current", "PROJECT_MASTER.json.master_thread", errors)
            if current is not None:
                master_thread_id = require_string(
                    current,
                    "thread_id",
                    "PROJECT_MASTER.json.master_thread.current",
                    errors,
                )
                require_string(
                    current,
                    "host_id",
                    "PROJECT_MASTER.json.master_thread.current",
                    errors,
                )
                require_string(
                    current,
                    "title",
                    "PROJECT_MASTER.json.master_thread.current",
                    errors,
                )
                require_string(
                    current,
                    "status",
                    "PROJECT_MASTER.json.master_thread.current",
                    errors,
                )
                validate_timestamp(
                    current.get("activated_at"),
                    "PROJECT_MASTER.json.master_thread.current.activated_at",
                    errors,
                )
            history = require_list(
                master, "history", "PROJECT_MASTER.json.master_thread", errors
            )
            if history is not None:
                history_ids = [
                    item.get("thread_id")
                    for item in history
                    if isinstance(item, dict) and isinstance(item.get("thread_id"), str)
                ]
                if len(history_ids) != len(set(history_ids)):
                    errors.append("PROJECT_MASTER.json.master_thread.history has duplicate thread IDs")
        else:
            master_thread_id = require_string(
                master, "thread_id", "PROJECT_MASTER.json.master_thread", errors
            )

    max_active = 3
    if schema_version == 2:
        policy = require_object(manifest, "policy", "PROJECT_MASTER.json", errors)
        if policy is not None:
            configured = policy.get("max_active_outcomes")
            if not isinstance(configured, int) or isinstance(configured, bool) or not 1 <= configured <= 3:
                errors.append(
                    "PROJECT_MASTER.json.policy.max_active_outcomes must be an integer from 1 to 3"
                )
            else:
                max_active = configured
            if policy.get("visible_child_threads") not in (
                "auto_for_distinct_outcomes",
                "manual",
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.visible_child_threads has an unsupported value"
                )
            if policy.get("routing") != "reuse_by_outcome_key":
                errors.append(
                    "PROJECT_MASTER.json.policy.routing must be reuse_by_outcome_key"
                )
            if policy.get("local_commit") not in (
                "auto_when_scope_clear_and_verified",
                "owner_confirmation",
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.local_commit has an unsupported value"
                )
            if policy.get("external_actions") != "owner_confirmation":
                errors.append(
                    "PROJECT_MASTER.json.policy.external_actions must be owner_confirmation"
                )
            if "handoff_mode" in policy and policy.get("handoff_mode") != "task_then_delta":
                errors.append(
                    "PROJECT_MASTER.json.policy.handoff_mode must be task_then_delta"
                )
            if "child_lifecycle_default" in policy and policy.get("child_lifecycle_default") != "infer_from_outcome":
                errors.append(
                    "PROJECT_MASTER.json.policy.child_lifecycle_default must be infer_from_outcome"
                )
            if "callback_policy" in policy and policy.get("callback_policy") != "terminal_or_explicit_milestone":
                errors.append(
                    "PROJECT_MASTER.json.policy.callback_policy must be terminal_or_explicit_milestone"
                )

            title_max = policy.get("task_title_max_chars")
            if title_max is not None and (
                not isinstance(title_max, int)
                or isinstance(title_max, bool)
                or not 10 <= title_max <= 60
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.task_title_max_chars must be an integer from 10 to 60"
                )

            task_soft = policy.get("task_packet_soft_chars")
            task_hard = policy.get("task_packet_hard_chars")
            delta_hard = policy.get("delta_packet_hard_chars")
            if task_soft is not None and (
                not isinstance(task_soft, int)
                or isinstance(task_soft, bool)
                or task_soft <= 0
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.task_packet_soft_chars must be a positive integer"
                )
            if task_hard is not None and (
                not isinstance(task_hard, int)
                or isinstance(task_hard, bool)
                or task_hard <= 0
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.task_packet_hard_chars must be a positive integer"
                )
            if (
                isinstance(task_soft, int)
                and not isinstance(task_soft, bool)
                and isinstance(task_hard, int)
                and not isinstance(task_hard, bool)
                and task_hard < task_soft
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.task_packet_hard_chars must be at least task_packet_soft_chars"
                )
            if delta_hard is not None and (
                not isinstance(delta_hard, int)
                or isinstance(delta_hard, bool)
                or delta_hard <= 0
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.delta_packet_hard_chars must be a positive integer"
                )
            if (
                isinstance(delta_hard, int)
                and not isinstance(delta_hard, bool)
                and isinstance(task_hard, int)
                and not isinstance(task_hard, bool)
                and delta_hard > task_hard
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.delta_packet_hard_chars must not exceed task_packet_hard_chars"
                )

            max_refs = policy.get("max_input_file_refs")
            if max_refs is not None and (
                not isinstance(max_refs, int)
                or isinstance(max_refs, bool)
                or not 1 <= max_refs <= 10
            ):
                errors.append(
                    "PROJECT_MASTER.json.policy.max_input_file_refs must be an integer from 1 to 10"
                )

    return project_id, master_thread_id, max_active


def validate_orchestration(
    state: dict[str, Any],
    project_id: str | None,
    master_thread_id: str | None,
    max_active: int,
    errors: list[str],
) -> None:
    if type(state.get("schema_version")) is not int or state.get("schema_version") != 1:
        errors.append("ORCHESTRATION.json.schema_version must be 1")
    state_project_id = require_string(state, "project_id", "ORCHESTRATION.json", errors)
    if project_id and state_project_id and state_project_id != project_id:
        errors.append("project_id differs between PROJECT_MASTER.json and ORCHESTRATION.json")
    revision = state.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("ORCHESTRATION.json.revision must be a positive integer")
    validate_timestamp(state.get("updated_at"), "ORCHESTRATION.json.updated_at", errors)

    governance = require_object(state, "governance", "ORCHESTRATION.json", errors)
    if governance is not None:
        if governance.get("status") not in GOVERNANCE_STATUSES:
            errors.append(
                "ORCHESTRATION.json.governance.status must be healthy, degraded, or blocked"
            )
        require_string(governance, "local_safe_work", "ORCHESTRATION.json.governance", errors)
        require_string(
            governance,
            "external_high_risk_work",
            "ORCHESTRATION.json.governance",
            errors,
        )

    outcomes = require_list(state, "active_outcomes", "ORCHESTRATION.json", errors)
    outcome_keys: set[str] = set()
    child_thread_ids: set[str] = set()
    priorities: set[int] = set()
    if outcomes is not None:
        if len(outcomes) > max_active or len(outcomes) > 3:
            errors.append(
                f"ORCHESTRATION.json.active_outcomes exceeds configured limit {max_active}"
            )
        for index, outcome in enumerate(outcomes):
            where = f"ORCHESTRATION.json.active_outcomes[{index}]"
            if not isinstance(outcome, dict):
                errors.append(f"{where} must be an object")
                continue
            key = require_string(outcome, "outcome_key", where, errors)
            require_string(outcome, "title", where, errors)
            if key:
                if key in outcome_keys:
                    errors.append(f"duplicate outcome_key: {key}")
                outcome_keys.add(key)
            priority = outcome.get("priority")
            if not isinstance(priority, int) or isinstance(priority, bool) or priority < 1:
                errors.append(f"{where}.priority must be a positive integer")
            elif priority in priorities:
                errors.append(f"duplicate active outcome priority: {priority}")
            else:
                priorities.add(priority)
            if outcome.get("route") not in CHILD_ROUTES:
                errors.append(f"{where}.route must be quick_fix or isolated_task")
            if outcome.get("status") not in ACTIVE_STATUSES:
                errors.append(f"{where}.status has an unsupported value")

            thread = require_object(outcome, "thread", where, errors)
            if thread is not None:
                thread_id = require_string(thread, "thread_id", f"{where}.thread", errors)
                require_string(thread, "host_id", f"{where}.thread", errors)
                require_string(thread, "title", f"{where}.thread", errors)
                if thread_id:
                    if thread_id == master_thread_id:
                        errors.append(f"{where}.thread.thread_id must differ from the master")
                    if thread_id in child_thread_ids:
                        errors.append(f"duplicate child thread ID: {thread_id}")
                    child_thread_ids.add(thread_id)

            scope = require_object(outcome, "scope", where, errors)
            if scope is not None:
                validate_absolute_paths(scope.get("allowed"), f"{where}.scope.allowed", errors)
                validate_absolute_paths(scope.get("protected"), f"{where}.scope.protected", errors)
            verified = require_object(outcome, "last_verified", where, errors)
            if verified is not None:
                validate_timestamp(verified.get("at"), f"{where}.last_verified.at", errors)
                require_string(verified, "claim", f"{where}.last_verified", errors)
                evidence = require_list(verified, "evidence", f"{where}.last_verified", errors)
                if evidence is not None and not all(
                    isinstance(item, str) and item.strip() for item in evidence
                ):
                    errors.append(f"{where}.last_verified.evidence must contain non-empty strings")
            require_string(outcome, "next_action", where, errors)

        if priorities and priorities != set(range(1, len(priorities) + 1)):
            errors.append("active outcome priorities must be contiguous from 1")

    gates = require_list(state, "owner_gates", "ORCHESTRATION.json", errors)
    gate_ids: set[str] = set()
    if gates is not None:
        for index, gate in enumerate(gates):
            where = f"ORCHESTRATION.json.owner_gates[{index}]"
            if not isinstance(gate, dict):
                errors.append(f"{where} must be an object")
                continue
            gate_id = require_string(gate, "gate_id", where, errors)
            if gate_id:
                if gate_id in gate_ids:
                    errors.append(f"duplicate owner gate ID: {gate_id}")
                gate_ids.add(gate_id)
            if gate.get("type") not in OWNER_GATE_TYPES:
                errors.append(f"{where}.type must be owner_action or owner_decision")
            if gate.get("status") != "open":
                errors.append(f"{where}.status must be open in live state")
            if not isinstance(gate.get("blocking"), bool):
                errors.append(f"{where}.blocking must be boolean")
            for key in (
                "request",
                "why_owner_only",
                "recommendation",
                "risk",
                "resume_action",
            ):
                require_string(gate, key, where, errors)
            minutes = gate.get("estimated_minutes")
            if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 0:
                errors.append(f"{where}.estimated_minutes must be a non-negative integer")
            related = gate.get("related_outcome_key")
            if related is not None and (not isinstance(related, str) or related not in outcome_keys):
                errors.append(f"{where}.related_outcome_key does not match an active outcome")

    require_list(state, "legacy_sources", "ORCHESTRATION.json", errors)


def validate_root(root_value: str) -> ValidationResult:
    root = Path(root_value).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        errors.append(f"project root is not a directory: {root}")
        return ValidationResult(root, None, None, errors, warnings)

    manifest = load_json(root / "PROJECT_MASTER.json", errors)
    orchestration = load_json(root / "ORCHESTRATION.json", errors)
    project_id: str | None = None
    master_thread_id: str | None = None
    max_active = 3
    if manifest is not None:
        project_id, master_thread_id, max_active = validate_manifest(
            manifest, root, errors, warnings
        )
    if orchestration is not None:
        validate_orchestration(
            orchestration, project_id, master_thread_id, max_active, errors
        )
    return ValidationResult(root, manifest, orchestration, errors, warnings)


def validation_payload(result: ValidationResult) -> dict[str, Any]:
    return {
        "root": str(result.root),
        "valid": result.valid,
        "errors": result.errors,
        "warnings": result.warnings,
    }


def command_validate(args: argparse.Namespace) -> int:
    result = validate_root(args.root)
    if args.json:
        print(json.dumps(validation_payload(result), ensure_ascii=False, indent=2))
    else:
        status = "VALID" if result.valid else "INVALID"
        print(f"{status}: {result.root}")
        for warning in result.warnings:
            print(f"warning: {warning}")
        for error in result.errors:
            print(f"error: {error}")
    return 0 if result.valid else 1


def collect_owner_gates(results: list[ValidationResult]) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    for result in results:
        if not result.valid or result.manifest is None or result.orchestration is None:
            continue
        project_name = result.manifest.get("project_name") or result.manifest.get("project_id")
        for gate in result.orchestration.get("owner_gates", []):
            if isinstance(gate, dict) and gate.get("status") == "open":
                collected.append(
                    {
                        **gate,
                        "project_id": result.manifest.get("project_id"),
                        "project_name": project_name,
                        "project_root": str(result.root),
                    }
                )
    return sorted(
        collected,
        key=lambda gate: (
            0 if gate.get("type") == "owner_action" else 1,
            0 if gate.get("blocking") else 1,
            str(gate.get("project_name")),
            str(gate.get("gate_id")),
        ),
    )


def render_markdown(gates: list[dict[str, Any]]) -> str:
    lines = [
        "# 跨项目人工收件箱",
        "",
        "> 这是从各项目 `ORCHESTRATION.json` 生成的只读视图。项目主编排保留写入权和事实责任。",
        "",
    ]
    sections = (
        ("owner_action", "需要我亲手操作"),
        ("owner_decision", "需要我拍板"),
    )
    for gate_type, title in sections:
        lines.extend([f"## {title}", ""])
        selected = [gate for gate in gates if gate.get("type") == gate_type]
        if not selected:
            lines.extend(["当前没有。", ""])
            continue
        for gate in selected:
            blocking = "阻塞当前结果" if gate.get("blocking") else "不阻塞其他工作"
            lines.extend(
                [
                    f"- **{gate['project_name']} · {gate['gate_id']}**：{gate['request']}",
                    f"  - 状态：{blocking}",
                    f"  - 原因：{gate['why_owner_only']}",
                    f"  - 建议：{gate['recommendation']}",
                    f"  - 风险：{gate['risk']}",
                    f"  - 预计：{gate['estimated_minutes']} 分钟",
                    f"  - 完成后：{gate['resume_action']}",
                    f"  - 项目：`{gate['project_root']}`",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def command_owner_inbox(args: argparse.Namespace) -> int:
    results = [validate_root(root) for root in args.root]
    invalid = [result for result in results if not result.valid]
    if invalid:
        for result in invalid:
            print(json.dumps(validation_payload(result), ensure_ascii=False), file=sys.stderr)
        return 1
    gates = collect_owner_gates(results)
    if args.format == "json":
        print(json.dumps({"owner_gates": gates}, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(gates), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate project-local orchestration files or render an owner inbox."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate one project root")
    validate.add_argument("--root", required=True, help="absolute project governance root")
    validate.add_argument("--json", action="store_true", help="emit machine-readable output")
    validate.set_defaults(handler=command_validate)

    inbox = subparsers.add_parser(
        "owner-inbox", help="render a read-only cross-project owner inbox"
    )
    inbox.add_argument(
        "--root",
        action="append",
        required=True,
        help="project governance root; repeat for multiple projects",
    )
    inbox.add_argument("--format", choices=("markdown", "json"), default="markdown")
    inbox.set_defaults(handler=command_owner_inbox)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    # CLI output is UTF-8 even on legacy Windows locales or redirected pipes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
