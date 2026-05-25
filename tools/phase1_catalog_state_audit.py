#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parent.parent
CAP_DIR = BASE / "capabilities"

READ_VERBS = {
    "read",
    "get",
    "list",
    "fetch",
    "search",
    "retrieve",
    "extract",
    "detect",
    "classify",
    "score",
    "validate",
    "verify",
    "analyze",
    "monitor",
    "inspect",
    "interpret",
}

WRITE_VERBS = {
    "write",
    "store",
    "create",
    "update",
    "delete",
    "upsert",
    "send",
    "assign",
    "approve",
    "reject",
    "schedule",
    "transition",
    "delegate",
    "execute",
    "acknowledge",
    "sync",
}

READ_WRITE_VERBS = {
    "reconcile",
}

STRICT_DOMAINS = {
    "identity",
    "policy",
    "security",
}

COGNITIVE_DOMAINS = {
    "analysis",
    "decision",
    "eval",
    "model",
    "text",
    "provenance",
}

OPERATIONAL_DOMAINS = {
    "audio",
    "code",
    "data",
    "doc",
    "email",
    "fs",
    "image",
    "integration",
    "memory",
    "message",
    "pdf",
    "research",
    "table",
    "video",
    "web",
}

ORCHESTRATION_PREFIXES = {
    "agent.catalog.",
    "agent.flow.",
    "agent.input.",
    "agent.plan.",
    "agent.request.",
    "agent.task.",
}

COGNITIVE_ROLES = {"analyze", "evaluate", "decide", "synthesize", "reflect", "perceive"}

STANDARD_DOMAINS = {
    "agent",
    "analysis",
    "decision",
    "eval",
    "model",
    "ops",
    "provenance",
    "task",
}

STANDARD_OVERRIDE_IDS = {
    "code.diff.extract",
    "code.source.analyze",
    "data.schema.validate",
    "doc.content.generate",
}


def _state_access(cap_id: str, side_effects: bool) -> str:
    parts = cap_id.split(".")
    verb = parts[-1] if parts else ""

    # side_effects is the primary guardrail: non-side-effect capabilities
    # must not be classified as write/read_write state access.
    if not side_effects:
        if verb in READ_VERBS:
            return "read"
        return "none"

    if verb in READ_WRITE_VERBS:
        return "read_write"
    if verb in WRITE_VERBS:
        return "write"
    if verb in READ_VERBS:
        return "read"

    return "write"


def _audit_level(cap_id: str, side_effects: bool, state_access: str) -> str:
    domain = cap_id.split(".")[0]
    verb = cap_id.split(".")[-1]

    if side_effects:
        return "strict"
    if domain == "text":
        return "standard"
    if cap_id in STANDARD_OVERRIDE_IDS:
        return "standard"
    if domain in STRICT_DOMAINS:
        return "strict"
    if verb in WRITE_VERBS or state_access in {"write", "read_write"}:
        return "strict"
    if domain in STANDARD_DOMAINS:
        return "standard"
    return "basic"


def _extract_roles(data: dict[str, Any]) -> set[str]:
    hints = data.get("cognitive_hints")
    if not isinstance(hints, dict):
        return set()
    role = hints.get("role")
    if isinstance(role, str):
        return {role}
    if isinstance(role, list):
        return {r for r in role if isinstance(r, str)}
    return set()


def _layer(cap_id: str, side_effects: bool, roles: set[str]) -> str:
    domain = cap_id.split(".")[0]

    # 1) Governance has highest precedence.
    if domain in STRICT_DOMAINS:
        return "governance"

    # 2) Explicit orchestration families.
    if any(cap_id.startswith(prefix) for prefix in ORCHESTRATION_PREFIXES):
        # Tie-break: explicit cognitive role overrides orchestration default.
        if roles & COGNITIVE_ROLES:
            return "cognitive"
        return "orchestration"

    # 3) Known cognitive domains.
    if domain in COGNITIVE_DOMAINS:
        return "cognitive"

    # 4) Side-effecting capabilities are operational unless governance/orchestration rules matched above.
    if side_effects:
        return "operational"

    # 5) Operational domains.
    if domain in OPERATIONAL_DOMAINS:
        return "operational"

    # 6) Fallback by role.
    if roles & COGNITIVE_ROLES:
        return "cognitive"

    return "operational"


def main() -> int:
    changed = 0
    total = 0

    for path in sorted(CAP_DIR.glob("*.yaml")):
        if path.name == "_index.yaml":
            continue

        data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        cap_id = data.get("id")
        if not isinstance(cap_id, str) or not cap_id:
            continue

        props = data.get("properties")
        if not isinstance(props, dict):
            props = {}
            data["properties"] = props

        metadata = data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
            data["metadata"] = metadata

        side_effects = props.get("side_effects") is True
        state_access = _state_access(cap_id, side_effects)
        audit_level = _audit_level(cap_id, side_effects, state_access)
        roles = _extract_roles(data)
        layer = _layer(cap_id, side_effects, roles)

        old_state = props.get("state_access")
        old_audit = props.get("audit_level")
        old_layer = metadata.get("layer")

        props["state_access"] = state_access
        props["audit_level"] = audit_level
        metadata["layer"] = layer

        total += 1
        if old_state != state_access or old_audit != audit_level or old_layer != layer:
            changed += 1
            path.write_text(
                yaml.safe_dump(data, sort_keys=False, allow_unicode=False),
                encoding="utf-8",
                newline="\n",
            )

    print(f"Capabilities processed: {total}")
    print(f"Capabilities updated: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
